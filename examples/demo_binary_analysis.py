"""
Exemple d'utilisation du toolkit pour l'analyse de fichiers binaires
Application cybersécurité: Détection de malwares
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from my_ml_toolkit.data_loader.binary import BinaryLoader
from my_ml_toolkit.feature_extraction.binary_features import BinaryFeatureExtractor
import pandas as pd


def demo_binary_analysis():
    """Démontre l'extraction de features de fichiers binaires"""
    
    print("="*70)
    print("DEMO: Extraction de Features de Fichiers Binaires")
    print("Application: Détection de Malwares")
    print("="*70)
    
    # Créer des exemples de fichiers binaires fictifs
    print("\n1. Création de fichiers de test...")
    
    # Simuler un fichier PE (Windows executable)
    pe_file = b"MZ" + b"\x90" * 100 + b"This program cannot be run in DOS mode" + b"\x00" * 500
    
    # Simuler un fichier avec haute entropie (potentiellement chiffré/compressé)
    import random
    random.seed(42)
    high_entropy_file = bytes([random.randint(0, 255) for _ in range(1000)])
    
    # Simuler un fichier texte normal
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
        
        # Afficher quelques features importantes
        print(f"      - Taille: {features['file_size']} bytes")
        print(f"      - Entropie: {features['entropy']:.2f} (0=faible, 8=haute)")
        print(f"      - Ratio bytes imprimables: {features['printable_ratio']:.2%}")
        print(f"      - Sections haute entropie: {features['high_entropy_sections']}")
        
        # Signatures détectées
        signatures = [k.replace('signature_', '') for k, v in features.items() 
                     if k.startswith('signature_') and v == 1]
        if signatures:
            print(f"      - Signatures détectées: {', '.join(signatures)}")
        
        features_list.append(features)
    
    # Créer un DataFrame
    df = pd.DataFrame(features_list)
    
    print("\n" + "="*70)
    print("3. Résumé des Features Extraites")
    print("="*70)
    
    # Colonnes à afficher
    display_cols = ['filename', 'file_size', 'entropy', 'printable_ratio', 
                    'high_entropy_sections', 'unique_bytes_ratio']
    
    print("\n" + df[display_cols].to_string(index=False))
    
    print("\n" + "="*70)
    print("4. Interprétation pour Cybersécurité")
    print("="*70)
    
    print("""
    Indicateurs de Malware:
    
    🔴 Haute Entropie (>7.5):
       → Fichier possiblement chiffré/compressé/obfusqué
       → Technique commune de packing de malwares
    
    🔴 Sections avec haute entropie:
       → Code potentiellement obfusqué
       → Payload chiffrée
    
    🔴 Faible ratio de bytes imprimables (<0.1):
       → Fichier binaire pur (normal pour .exe)
       → Mais suspect si combiné avec haute entropie
    
    🟢 Signatures de fichiers (PE, ELF):
       → Type de fichier identifié
       → Permet validation de l'extension
    
    📊 Dans cet exemple:
       - suspicious_executable.exe: Signature PE détectée ✓
       - encrypted_data.bin: TRÈS haute entropie → SUSPECT
       - normal_file.txt: Faible entropie, haute lisibilité → Normal
    """)
    
    print("\n" + "="*70)
    print("5. Prochaines Étapes")
    print("="*70)
    
    print("""
    Pour un système de détection de malwares complet:
    
    1. Collecter des datasets:
       - Malwares connus (VirusTotal, MalwareBazaar)
       - Fichiers légitimes (Windows System32, etc.)
    
    2. Extraire toutes les features:
       - Features statistiques (entropie, distribution)
       - N-grams binaires
       - Imports/Exports PE (avec pefile)
       - Patterns d'opcodes
    
    3. Entraîner un modèle:
       - Random Forest (bon pour features binaires)
       - XGBoost (meilleure performance)
       - Neural Networks (pour grandes datasets)
    
    4. Déployer:
       - Scanner en temps réel
       - Analyse de fichiers suspects
       - Intégration avec antivirus
    """)
    
    return df


def demo_pe_analysis():
    """Exemple spécifique pour fichiers PE (nécessite pefile)"""
    
    print("\n" + "="*70)
    print("BONUS: Analyse Spécifique PE Files")
    print("="*70)
    
    try:
        from my_ml_toolkit.feature_extraction.binary_features import PEFileFeatureExtractor
        
        print("\n✓ Module PE disponible")
        print("\nPour analyser des vrais fichiers PE:")
        print("  1. Installer: pip install pefile")
        print("  2. Utiliser: PEFileFeatureExtractor().extract_pe_features(data)")
        print("\nFeatures PE extraites:")
        print("  - Type de machine (x86, x64, ARM)")
        print("  - Timestamp de compilation")
        print("  - Nombre de sections")
        print("  - DLLs importées (ws2_32.dll = réseau, etc.)")
        print("  - Fonctions exportées")
        
    except Exception as e:
        print(f"\n⚠️  Module PE non disponible: {e}")


if __name__ == "__main__":
    # Exécuter la démo
    df = demo_binary_analysis()
    demo_pe_analysis()
    
    print("\n" + "="*70)
    print("✅ Démo terminée!")
    print("="*70)
