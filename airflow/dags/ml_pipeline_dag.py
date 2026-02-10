"""
DAG Airflow pour pipeline ML automatisé de détection de malwares
Exécution quotidienne : Collecte → Extraction → Entraînement → Déploiement
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os
import logging

# Ajouter le path pour importer le toolkit
sys.path.insert(0, '/opt/airflow/my_ml_toolkit')

from data_loader.binary import BinaryLoader
from feature_extraction.binary_features import BinaryFeatureExtractor
from preprocessing.numeric_prep import NumericPreprocessor
from modeling.auto_trainer import AutoTrainer
import pandas as pd
import pickle
import json

# Configuration
DATA_DIR = '/opt/airflow/data'
MODELS_DIR = '/opt/airflow/models'
MALWARE_DIR = f'{DATA_DIR}/malware_samples'
BENIGN_DIR = f'{DATA_DIR}/benign_samples'

default_args = {
    'owner': 'tatiana',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'ml_malware_detection_pipeline',
    default_args=default_args,
    description='Pipeline automatisé de détection de malwares',
    schedule_interval='@daily',  # Exécution quotidienne
    catchup=False,
    tags=['ml', 'cybersecurity', 'malware'],
)


def check_data_availability(**context):
    """Vérifier si de nouvelles données sont disponibles"""
    logging.info("🔍 Vérification de la disponibilité des données...")
    
    # Créer les dossiers s'ils n'existent pas
    os.makedirs(MALWARE_DIR, exist_ok=True)
    os.makedirs(BENIGN_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Compter les fichiers
    malware_count = len([f for f in os.listdir(MALWARE_DIR) if os.path.isfile(os.path.join(MALWARE_DIR, f))])
    benign_count = len([f for f in os.listdir(BENIGN_DIR) if os.path.isfile(os.path.join(BENIGN_DIR, f))])
    
    logging.info(f"   Malwares trouvés: {malware_count}")
    logging.info(f"   Fichiers légitimes trouvés: {benign_count}")
    
    # Pousser les infos vers XCom
    context['ti'].xcom_push(key='malware_count', value=malware_count)
    context['ti'].xcom_push(key='benign_count', value=benign_count)
    
    if malware_count < 10 or benign_count < 10:
        logging.warning("⚠️  Pas assez de données, génération de données synthétiques...")
        return 'generate_synthetic_data'
    
    return 'extract_features'


def generate_synthetic_data(**context):
    """Générer des données synthétiques pour la démo"""
    import numpy as np
    
    logging.info("🔧 Génération de données synthétiques...")
    
    # Générer 50 malwares simulés (haute entropie)
    for i in range(50):
        data = bytes(np.random.randint(0, 256, 1000))
        filepath = os.path.join(MALWARE_DIR, f'synthetic_malware_{i}.bin')
        with open(filepath, 'wb') as f:
            f.write(data)
    
    # Générer 50 fichiers légitimes simulés (basse entropie)
    for i in range(50):
        data = b"MZ" + (b"\x00" * 300) + (b"Normal executable code " * 30)
        filepath = os.path.join(BENIGN_DIR, f'synthetic_benign_{i}.exe')
        with open(filepath, 'wb') as f:
            f.write(data)
    
    logging.info("✅ Données synthétiques générées avec succès")


def extract_features(**context):
    """Extraire les features de tous les fichiers"""
    logging.info("🔍 Extraction des features...")
    
    loader = BinaryLoader()
    extractor = BinaryFeatureExtractor()
    
    all_features = []
    
    # Charger et extraire features des malwares
    logging.info("   Traitement des malwares...")
    malware_files = loader.load_directory(MALWARE_DIR)
    for filename, data in malware_files:
        features = extractor.extract_all_features(data)
        features['label'] = 1  # Malware
        features['filename'] = filename
        all_features.append(features)
    
    # Charger et extraire features des fichiers légitimes
    logging.info("   Traitement des fichiers légitimes...")
    benign_files = loader.load_directory(BENIGN_DIR)
    for filename, data in benign_files:
        features = extractor.extract_all_features(data)
        features['label'] = 0  # Légitime
        features['filename'] = filename
        all_features.append(features)
    
    # Sauvegarder les features
    df = pd.DataFrame(all_features)
    features_path = f'{DATA_DIR}/features.csv'
    df.to_csv(features_path, index=False)
    
    logging.info(f"✅ Features extraites: {len(df)} fichiers, {df.shape[1]} features")
    
    # Pousser le chemin vers XCom
    context['ti'].xcom_push(key='features_path', value=features_path)


def train_model(**context):
    """Entraîner le modèle de détection"""
    logging.info("🤖 Entraînement du modèle...")
    
    # Récupérer le chemin des features
    features_path = context['ti'].xcom_pull(task_ids='extract_features', key='features_path')
    
    # Charger les features
    df = pd.read_csv(features_path)
    
    # Préparer les données
    X = df.drop(columns=['label', 'md5', 'sha256', 'filename'], errors='ignore')
    y = df['label']
    
    # Prétraiter
    preprocessor = NumericPreprocessor(scaling_method='standard')
    X_processed = preprocessor.scale_features(X)
    
    # Entraîner
    trainer = AutoTrainer(task_type='classification', random_state=42)
    results = trainer.train_all_models(X_processed, y, verbose=True)
    
    # Sauvegarder le meilleur modèle
    best_model_name, best_model = trainer.get_best_model()
    
    model_info = {
        'model_name': best_model_name,
        'accuracy': trainer.best_score,
        'timestamp': datetime.now().isoformat(),
        'n_samples': len(df),
        'n_features': X_processed.shape[1]
    }
    
    # Sauvegarder le modèle
    model_path = f'{MODELS_DIR}/malware_detector.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump({
            'model': best_model,
            'preprocessor': preprocessor,
            'feature_columns': list(X.columns),
            'info': model_info
        }, f)
    
    # Sauvegarder les métadonnées
    metadata_path = f'{MODELS_DIR}/model_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(model_info, f, indent=2)
    
    logging.info(f"✅ Modèle entraîné: {best_model_name}")
    logging.info(f"   Accuracy: {trainer.best_score:.4f}")
    logging.info(f"   Sauvegardé: {model_path}")
    
    # Pousser les résultats
    context['ti'].xcom_push(key='model_path', value=model_path)
    context['ti'].xcom_push(key='model_info', value=model_info)


def evaluate_model(**context):
    """Évaluer le modèle et générer un rapport"""
    logging.info("📊 Évaluation du modèle...")
    
    model_info = context['ti'].xcom_pull(task_ids='train_model', key='model_info')
    
    # Créer un rapport d'évaluation
    report = f"""
    ════════════════════════════════════════════════════
    📊 RAPPORT D'ENTRAÎNEMENT - DÉTECTION DE MALWARES
    ════════════════════════════════════════════════════
    
    📅 Date: {model_info['timestamp']}
    
    🤖 Modèle: {model_info['model_name']}
    
    📈 Performance:
       - Accuracy: {model_info['accuracy']:.4f}
    
    📊 Dataset:
       - Nombre d'échantillons: {model_info['n_samples']}
       - Nombre de features: {model_info['n_features']}
    
    ════════════════════════════════════════════════════
    """
    
    logging.info(report)
    
    # Sauvegarder le rapport
    report_path = f'{MODELS_DIR}/training_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(report_path, 'w') as f:
        f.write(report)
    
    logging.info(f"✅ Rapport sauvegardé: {report_path}")


def deploy_model(**context):
    """Déployer le modèle (placeholder pour intégration BentoML)"""
    logging.info("🚀 Déploiement du modèle...")
    
    model_path = context['ti'].xcom_pull(task_ids='train_model', key='model_path')
    
    logging.info(f"   Modèle prêt pour déploiement: {model_path}")
    logging.info("   TODO: Intégration avec BentoML pour API REST")
    
    # Ici on pourrait déclencher un build BentoML
    # bentoml build && bentoml containerize
    
    logging.info("✅ Modèle déployé avec succès")


# ==========================================
# Définition des tâches
# ==========================================

check_data = PythonOperator(
    task_id='check_data_availability',
    python_callable=check_data_availability,
    provide_context=True,
    dag=dag,
)

generate_data = PythonOperator(
    task_id='generate_synthetic_data',
    python_callable=generate_synthetic_data,
    provide_context=True,
    dag=dag,
)

extract = PythonOperator(
    task_id='extract_features',
    python_callable=extract_features,
    provide_context=True,
    dag=dag,
)

train = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    provide_context=True,
    dag=dag,
)

evaluate = PythonOperator(
    task_id='evaluate_model',
    python_callable=evaluate_model,
    provide_context=True,
    dag=dag,
)

deploy = PythonOperator(
    task_id='deploy_model',
    python_callable=deploy_model,
    provide_context=True,
    dag=dag,
)

# ==========================================
# Définition du workflow
# ==========================================

check_data >> [generate_data, extract]
generate_data >> extract
extract >> train >> evaluate >> deploy
