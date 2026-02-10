"""
Exemple d'utilisation pour l'analyse de fichiers binaires
Application cybersécurité: Détection de malwares
"""

import sys
import os

# Ajouter le chemin parent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports directs
from data_loader.binary import BinaryLoader
from feature_extraction.binary_features import BinaryFeatureExtractor
import pandas as pd
import numpy as np
import random

print("="*70)
print("DEMO: Extraction de Features de Fichiers Binaires")
print("Application: Détection de Malwares")
print("="*70)

# Créer des exemples
print("\n1. Création de fichiers de test...")

pe_file = b"MZ" + b"\x90" * 100 + b"This program cannot be run in DOS mode" + b"\x00" * 500
random.seed(42)
high_entropy_file = bytes([random.randint(0, 255) for _ in range(1000)])
text_file = b"Hello World! " * 50

files = {
    'suspicious_executable.exe': pe_file,
    'encrypted_data.bin': high_entropy_file,
    'normal_file.txt': text_file
}

print(f"   ✓ {len(files)} fichiers créés")

# Extraire les features
print("\n2. Extraction des features...")

extractor = BinaryFeatureExtractor(ngram_size=2)
features_list = []

for filename, data in files.items():
    print(f"\n   Analyse de: {filename}")
    features = extractor.extract_all_features(data)
    features['filename'] = filename
    
    print(f"      - Taille: {features['file_size']} bytes")
    print(f"      - Entropie: {features['entropy']:.2f} (0=faible, 8=haute)")
    print(f"      - Ratio bytes imprimables: {features['printable_ratio']:.2%}")
    print(f"      - Sections haute entropie: {features['high_entropy_sections']}")
    
    signatures = [k.replace('signature_', '') for k, v in features.items() 
                 if k.startswith('signature_') and v == 1]
    if signatures:
        print(f"      - Signatures détectées: {', '.join(signatures)}")
    
    features_list.append(features)

df = pd.DataFrame(features_list)

print("\n" + "="*70)
print("3. Résumé des Features Extraites")
print("="*70)

display_cols = ['filename', 'file_size', 'entropy', 'printable_ratio', 
                'high_entropy_sections', 'unique_bytes_ratio']

print("\n" + df[display_cols].to_string(index=False))

print("\n" + "="*70)
print("✅ Démo terminée avec succès!")
print("="*70)
