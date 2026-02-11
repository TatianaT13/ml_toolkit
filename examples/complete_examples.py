"""
Exemples complets d'utilisation du toolkit ML
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loader.tabular import TabularLoader
from data_loader.binary import BinaryLoader
from preprocessing.numeric_prep import NumericPreprocessor
from feature_extraction.binary_features import BinaryFeatureExtractor
from feature_extraction.text_features import TextFeatureExtractor
from modeling.auto_trainer import AutoTrainer

import pandas as pd
import numpy as np

print("\n" + "🚀" * 35)
print("EXEMPLES COMPLETS D'UTILISATION DU TOOLKIT ML")
print("🚀" * 35)

# ============================================================
# EXEMPLE 1: Classification Tabulaire
# ============================================================
print("\n" + "="*70)
print("EXEMPLE 1: Classification de Données Tabulaires")
print("="*70)

np.random.seed(42)
n_samples = 1000

data = {
    'age': np.random.randint(18, 80, n_samples),
    'salary': np.random.randint(20000, 150000, n_samples),
    'credit_score': np.random.randint(300, 850, n_samples),
    'experience': np.random.randint(0, 40, n_samples),
    'target': np.random.choice([0, 1], n_samples)
}

df = pd.DataFrame(data)

print(f"\n📊 Dataset créé: {n_samples} exemples, {len(data)-1} features")

# Préparer les données
X = df.drop(columns=['target'])
y = df['target']

preprocessor = NumericPreprocessor(scaling_method='standard')
X_processed = preprocessor.scale_features(X)

# Entraîner les modèles
trainer = AutoTrainer(task_type='classification')
results = trainer.train_all_models(X_processed, y, verbose=True)

print("\n📈 Résultats:")
print(trainer.get_results_dataframe().to_string(index=False))

# ============================================================
# EXEMPLE 2: Détection de Malwares
# ============================================================
print("\n\n" + "="*70)
print("EXEMPLE 2: Détection de Malwares (Données Binaires)")
print("="*70)

# Créer des données
malware_samples = []
for i in range(50):
    data = bytes(np.random.randint(0, 256, 500))
    malware_samples.append((f'malware_{i}.exe', data))

benign_samples = []
for i in range(50):
    data = b"MZ" + (b"\x00" * 200) + (b"Normal code " * 20)
    benign_samples.append((f'benign_{i}.exe', data))

print(f"\n🔐 {len(malware_samples)} malwares + {len(benign_samples)} légitimes")

# Extraire features
extractor = BinaryFeatureExtractor()
all_features = []

for filename, data in malware_samples + benign_samples:
    features = extractor.extract_all_features(data)
    features['label'] = 1 if 'malware' in filename else 0
    all_features.append(features)

df = pd.DataFrame(all_features)

# Préparer et entraîner
X = df.drop(columns=['label', 'md5', 'sha256'], errors='ignore')
y = df['label']

preprocessor = NumericPreprocessor(scaling_method='standard')
X_processed = preprocessor.scale_features(X)

trainer = AutoTrainer(task_type='classification')
results = trainer.train_all_models(X_processed, y, verbose=True)

print("\n📊 Performance:")
print(trainer.get_results_dataframe().to_string(index=False))

# ============================================================
# EXEMPLE 3: Classification de Texte
# ============================================================
print("\n\n" + "="*70)
print("EXEMPLE 3: Classification de Texte (Sentiments)")
print("="*70)

texts = [
    "Ce produit est excellent, je recommande!",
    "Très déçu, mauvaise qualité.",
    "Parfait, exactement ce que je cherchais.",
    "Nul, ne fonctionne pas.",
] * 30

labels = [1, 0, 1, 0] * 30

print(f"\n📝 {len(texts)} textes")

# Extraire features
extractor = TextFeatureExtractor()
features_list = [extractor.extract_all_features(text) for text in texts]

df = pd.DataFrame(features_list)
X = df
y = pd.Series(labels)

preprocessor = NumericPreprocessor(scaling_method='standard')
X_processed = preprocessor.scale_features(X)

trainer = AutoTrainer(task_type='classification')
results = trainer.train_all_models(X_processed, y, verbose=True)

print("\n📊 Performance:")
print(trainer.get_results_dataframe().to_string(index=False))

print("\n" + "="*70)
print("✅ Tous les exemples terminés!")
print("="*70)
print("\n💡 Utilisez maintenant vos propres données!")
