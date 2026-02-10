"""
Exemple complet d'utilisation du pipeline ML
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from my_ml_toolkit import MLPipeline
import pandas as pd
import numpy as np


def example_classification_tabular():
    """Exemple avec données tabulaires - Classification"""
    
    print("\n" + "="*70)
    print("EXEMPLE 1: Classification de Données Tabulaires")
    print("="*70)
    
    # Créer un dataset fictif (normalement vous chargeriez un vrai fichier)
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'age': np.random.randint(18, 80, n_samples),
        'salary': np.random.randint(20000, 150000, n_samples),
        'credit_score': np.random.randint(300, 850, n_samples),
        'experience': np.random.randint(0, 40, n_samples),
        'target': np.random.choice([0, 1], n_samples)  # 0=Non, 1=Oui
    }
    
    df = pd.DataFrame(data)
    
    # Sauvegarder temporairement
    df.to_csv('/home/claude/temp_data.csv', index=False)
    
    print("\n📊 Dataset créé:")
    print(f"   - {n_samples} exemples")
    print(f"   - {len(data)-1} features")
    print(f"   - Task: Classification (prédit si client va acheter)")
    
    # Créer et exécuter le pipeline
    pipeline = MLPipeline(data_type='tabular', task_type='classification')
    
    results = pipeline.run_full_pipeline(
        filepath='/home/claude/temp_data.csv',
        target_col='target',
        verbose=True
    )
    
    # Afficher les résultats
    print("\n📈 Résultats détaillés:")
    results_df = pipeline.trainer.get_results_dataframe()
    print(results_df.to_string(index=False))
    
    # Nettoyer
    os.remove('/home/claude/temp_data.csv')
    
    return pipeline


def example_binary_malware_detection():
    """Exemple avec données binaires - Détection de malwares"""
    
    print("\n\n" + "="*70)
    print("EXEMPLE 2: Détection de Malwares (Données Binaires)")
    print("="*70)
    
    from my_ml_toolkit.data_loader.binary import BinaryLoader
    from my_ml_toolkit.feature_extraction.binary_features import BinaryFeatureExtractor
    
    # Simuler des fichiers malveillants et légitimes
    print("\n🔐 Création de fichiers de test...")
    
    # Fichiers malveillants simulés (haute entropie)
    malware_samples = []
    for i in range(50):
        # Haute entropie = chiffré/obfusqué
        data = bytes(np.random.randint(0, 256, 500))
        malware_samples.append((f'malware_{i}.exe', data))
    
    # Fichiers légitimes simulés (basse entropie)
    benign_samples = []
    for i in range(50):
        # Basse entropie = code normal
        data = b"MZ" + (b"\x00" * 200) + (b"Normal code here " * 20)
        benign_samples.append((f'benign_{i}.exe', data))
    
    print(f"   ✓ {len(malware_samples)} malwares simulés")
    print(f"   ✓ {len(benign_samples)} fichiers légitimes simulés")
    
    # Extraire features
    print("\n🔍 Extraction des features...")
    extractor = BinaryFeatureExtractor()
    
    all_features = []
    
    for filename, data in malware_samples:
        features = extractor.extract_all_features(data)
        features['label'] = 1  # Malware
        features['filename'] = filename
        all_features.append(features)
    
    for filename, data in benign_samples:
        features = extractor.extract_all_features(data)
        features['label'] = 0  # Légitime
        features['filename'] = filename
        all_features.append(features)
    
    df = pd.DataFrame(all_features)
    print(f"   ✓ {len(df)} fichiers analysés")
    print(f"   ✓ {df.shape[1]-1} features extraites par fichier")
    
    # Préparer les données
    print("\n⚙️  Préparation pour ML...")
    cols_to_drop = ['label', 'md5', 'sha256', 'filename']
    X = df.drop(columns=cols_to_drop)
    y = df['label']
    
    # Créer pipeline et entraîner
    pipeline = MLPipeline(data_type='binary', task_type='classification')
    X_processed, y = pipeline.preprocess(X, y)
    
    print("\n🤖 Entraînement des modèles...")
    results = pipeline.train(X_processed, y, verbose=True)
    
    # Résultats
    print("\n📊 Performance des Modèles:")
    results_df = pipeline.trainer.get_results_dataframe()
    print(results_df.to_string(index=False))
    
    # Tester sur un nouveau fichier
    print("\n🧪 Test sur un nouveau fichier suspect...")
    new_malware = bytes(np.random.randint(0, 256, 500))
    new_features = extractor.extract_all_features(new_malware)
    
    # Préparer pour prédiction
    new_df = pd.DataFrame([new_features])
    new_df = new_df.drop(columns=['md5', 'sha256'], errors='ignore')
    new_X, _ = pipeline.preprocess(new_df)
    
    prediction = pipeline.trainer.predict(new_X)
    
    print(f"   Entropie du fichier: {new_features['entropy']:.2f}")
    print(f"   Prédiction: {'🔴 MALWARE' if prediction[0] == 1 else '🟢 LÉGITIME'}")
    
    return pipeline


def example_text_classification():
    """Exemple avec données texte - Classification de sentiments"""
    
    print("\n\n" + "="*70)
    print("EXEMPLE 3: Classification de Texte (Sentiments)")
    print("="*70)
    
    from my_ml_toolkit.feature_extraction.text_features import TextFeatureExtractor
    
    # Données d'exemple
    texts = [
        "Ce produit est excellent, je recommande vivement!",
        "Très déçu, mauvaise qualité.",
        "Parfait, exactement ce que je cherchais.",
        "Nul, ne fonctionne pas correctement.",
        "Superbe article, livraison rapide.",
        "Horrible, j'ai retourné le produit.",
    ] * 20  # Répéter pour avoir plus de données
    
    labels = [1, 0, 1, 0, 1, 0] * 20  # 1=Positif, 0=Négatif
    
    print(f"\n📝 Dataset créé:")
    print(f"   - {len(texts)} textes")
    print(f"   - 2 classes (Positif/Négatif)")
    
    # Extraire features
    print("\n🔍 Extraction des features...")
    extractor = TextFeatureExtractor()
    
    features_list = []
    for text in texts:
        features = extractor.extract_all_features(text)
        features_list.append(features)
    
    df = pd.DataFrame(features_list)
    df['label'] = labels
    
    print(f"   ✓ {df.shape[1]-1} features extraites par texte")
    
    # Entraîner
    X = df.drop(columns=['label'])
    y = df['label']
    
    pipeline = MLPipeline(data_type='text', task_type='classification')
    X_processed, y = pipeline.preprocess(X, y)
    
    print("\n🤖 Entraînement des modèles...")
    results = pipeline.train(X_processed, y, verbose=True)
    
    # Résultats
    print("\n📊 Performance des Modèles:")
    results_df = pipeline.trainer.get_results_dataframe()
    print(results_df.to_string(index=False))
    
    return pipeline


if __name__ == "__main__":
    print("\n" + "🚀" * 35)
    print("EXEMPLES COMPLETS D'UTILISATION DU TOOLKIT ML")
    print("🚀" * 35)
    
    # Exécuter les exemples
    example_classification_tabular()
    example_binary_malware_detection()
    example_text_classification()
    
    print("\n" + "="*70)
    print("✅ Tous les exemples exécutés avec succès!")
    print("="*70)
    print("\n💡 Prochaines étapes:")
    print("   1. Utilisez vos propres données")
    print("   2. Ajustez les paramètres selon vos besoins")
    print("   3. Exportez et déployez vos modèles")
    print("\n📚 Consultez le README.md pour plus d'infos")
