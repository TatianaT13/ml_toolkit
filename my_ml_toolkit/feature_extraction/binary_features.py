"""
Module d'extraction de features pour données binaires
Spécialisé pour cybersécurité et analyse de malwares
"""

import numpy as np
from scipy import stats
from collections import Counter
from typing import Dict, List, Tuple
import hashlib


class BinaryFeatureExtractor:
    """Extrait des features statistiques et structurelles de fichiers binaires"""
    
    def __init__(self, ngram_size: int = 2):
        """
        Args:
            ngram_size: Taille des n-grams à extraire (2 = bigrams, 3 = trigrams)
        """
        self.ngram_size = ngram_size
    
    def extract_all_features(self, data: bytes) -> Dict:
        """
        Extrait toutes les features d'un fichier binaire
        
        Args:
            data: Données binaires
            
        Returns:
            Dictionnaire de features
        """
        features = {}
        
        # Features de base
        features.update(self.extract_basic_features(data))
        
        # Features statistiques
        features.update(self.extract_statistical_features(data))
        
        # Features de structure
        features.update(self.extract_structural_features(data))
        
        # N-grams (optionnel, peut être lourd)
        # features.update(self.extract_ngram_features(data))
        
        return features
    
    def extract_basic_features(self, data: bytes) -> Dict:
        """Features de base du fichier"""
        return {
            'file_size': len(data),
            'md5': hashlib.md5(data, usedforsecurity=False).hexdigest(),
            'sha256': hashlib.sha256(data).hexdigest()
        }
    
    def extract_statistical_features(self, data: bytes) -> Dict:
        """Features statistiques sur la distribution des bytes"""
        byte_array = np.frombuffer(data, dtype=np.uint8)
        
        features = {
            # Entropie de Shannon (mesure de randomness)
            'entropy': self._calculate_entropy(byte_array),
            
            # Statistiques descriptives
            'mean_byte_value': float(np.mean(byte_array)),
            'std_byte_value': float(np.std(byte_array)),
            'min_byte_value': int(np.min(byte_array)),
            'max_byte_value': int(np.max(byte_array)),
            
            # Distribution
            'unique_bytes_count': len(np.unique(byte_array)),
            'unique_bytes_ratio': len(np.unique(byte_array)) / 256.0,
        }
        
        # Distribution par plages de bytes
        features.update(self._byte_distribution(byte_array))
        
        return features
    
    def extract_structural_features(self, data: bytes) -> Dict:
        """Features liées à la structure du fichier"""
        features = {}
        
        # Détection de magic bytes (signatures de fichiers)
        features.update(self._detect_file_signatures(data))
        
        # Sections avec haute entropie (possiblement chiffré/compressé)
        features['high_entropy_sections'] = self._count_high_entropy_sections(data)
        
        # Séquences répétées
        features['repeated_sequences'] = self._count_repeated_sequences(data)
        
        # Présence de strings lisibles
        features['printable_ratio'] = self._calculate_printable_ratio(data)
        
        return features
    
    def extract_ngram_features(self, data: bytes, top_n: int = 100) -> Dict:
        """
        Extrait les n-grams les plus fréquents
        
        Args:
            data: Données binaires
            top_n: Nombre de n-grams à retourner
            
        Returns:
            Dictionnaire avec fréquences des top n-grams
        """
        ngrams = []
        
        # Créer les n-grams
        for i in range(len(data) - self.ngram_size + 1):
            ngram = data[i:i + self.ngram_size]
            ngrams.append(ngram)
        
        # Compter les fréquences
        ngram_counts = Counter(ngrams)
        
        # Top N n-grams
        features = {}
        for idx, (ngram, count) in enumerate(ngram_counts.most_common(top_n)):
            ngram_hex = ngram.hex()
            features[f'ngram_{idx}_{ngram_hex}'] = count
        
        return features
    
    def _calculate_entropy(self, byte_array: np.ndarray) -> float:
        """Calcule l'entropie de Shannon"""
        # Compter la fréquence de chaque byte
        value_counts = np.bincount(byte_array, minlength=256)
        probabilities = value_counts[value_counts > 0] / len(byte_array)
        
        # Entropie de Shannon
        entropy = -np.sum(probabilities * np.log2(probabilities))
        return float(entropy)
    
    def _byte_distribution(self, byte_array: np.ndarray) -> Dict:
        """Distribution des bytes par catégories"""
        features = {}
        
        # Bytes NULL (0x00)
        features['null_bytes_count'] = int(np.sum(byte_array == 0))
        features['null_bytes_ratio'] = float(np.mean(byte_array == 0))
        
        # Bytes ASCII imprimables (0x20-0x7E)
        printable = (byte_array >= 0x20) & (byte_array <= 0x7E)
        features['printable_bytes_ratio'] = float(np.mean(printable))
        
        # Bytes haute valeur (> 127)
        features['high_bytes_ratio'] = float(np.mean(byte_array > 127))
        
        return features
    
    def _detect_file_signatures(self, data: bytes) -> Dict:
        """Détecte les signatures de fichiers (magic bytes)"""
        signatures = {
            'is_pe': data[:2] == b'MZ',  # Windows PE
            'is_elf': data[:4] == b'\x7fELF',  # Linux ELF
            'is_pdf': data[:4] == b'%PDF',
            'is_zip': data[:2] == b'PK',
            'is_jpg': data[:3] == b'\xff\xd8\xff',
            'is_png': data[:8] == b'\x89PNG\r\n\x1a\n',
            'is_gif': data[:3] == b'GIF',
        }
        
        return {f'signature_{k}': int(v) for k, v in signatures.items()}
    
    def _count_high_entropy_sections(self, data: bytes, window_size: int = 256, threshold: float = 7.5) -> int:
        """Compte le nombre de sections avec haute entropie (possiblement chiffré)"""
        count = 0
        
        for i in range(0, len(data) - window_size, window_size):
            section = data[i:i + window_size]
            byte_array = np.frombuffer(section, dtype=np.uint8)
            entropy = self._calculate_entropy(byte_array)
            
            if entropy > threshold:
                count += 1
        
        return count
    
    def _count_repeated_sequences(self, data: bytes, min_length: int = 4, min_repeats: int = 3) -> int:
        """Compte les séquences répétées (packing, obfuscation)"""
        # Simplifié pour performance
        sequences = {}
        count = 0
        
        for i in range(0, len(data) - min_length, min_length):
            seq = data[i:i + min_length]
            sequences[seq] = sequences.get(seq, 0) + 1
            
            if sequences[seq] == min_repeats:
                count += 1
        
        return count
    
    def _calculate_printable_ratio(self, data: bytes) -> float:
        """Ratio de caractères imprimables (strings, messages)"""
        printable_count = sum(1 for b in data if 32 <= b <= 126)
        return printable_count / len(data) if len(data) > 0 else 0.0


class PEFileFeatureExtractor:
    """Extraction spécifique pour fichiers PE (Windows executables)"""
    
    def __init__(self):
        self.pe_available = False
        try:
            import pefile
            self.pe = pefile
            self.pe_available = True
        except ImportError:
            print("Warning: pefile non installé. Installer avec: pip install pefile")
    
    def extract_pe_features(self, data: bytes) -> Dict:
        """Extrait des features spécifiques aux PE files"""
        if not self.pe_available:
            return {}
        
        try:
            pe = self.pe.PE(data=data)
            
            features = {
                # Header info
                'pe_machine': pe.FILE_HEADER.Machine,
                'pe_timestamp': pe.FILE_HEADER.TimeDateStamp,
                'pe_num_sections': pe.FILE_HEADER.NumberOfSections,
                
                # Sections
                'pe_section_count': len(pe.sections),
                'pe_has_debug': int(hasattr(pe, 'DIRECTORY_ENTRY_DEBUG')),
                
                # Imports/Exports
                'pe_num_imports': len(pe.DIRECTORY_ENTRY_IMPORT) if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT') else 0,
                'pe_num_exports': len(pe.DIRECTORY_ENTRY_EXPORT.symbols) if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT') else 0,
            }
            
            # DLLs importées (indicateurs de comportement)
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                suspicious_dlls = ['ws2_32.dll', 'wininet.dll', 'urlmon.dll']  # Network
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    dll_name = entry.dll.decode().lower()
                    if dll_name in suspicious_dlls:
                        features[f'pe_imports_{dll_name}'] = 1
            
            return features
            
        except Exception as e:
            print(f"Erreur extraction PE: {e}")
            return {}


if __name__ == "__main__":
    # Test avec données fictives
    test_data = b"MZ" + b"\x00" * 100 + b"Hello World" * 10
    
    extractor = BinaryFeatureExtractor(ngram_size=2)
    features = extractor.extract_all_features(test_data)
    
    print("Features extraites:")
    for key, value in features.items():
        print(f"  {key}: {value}")
