"""
Module pour charger des données binaires (fichiers exécutables, pcap, etc.)
"""

import os
import numpy as np
from pathlib import Path
from typing import List, Union, Tuple


class BinaryLoader:
    """Charge des fichiers binaires pour analyse"""
    
    def __init__(self, max_bytes: int = None):
        """
        Args:
            max_bytes: Nombre maximum de bytes à lire (None = tout lire)
        """
        self.max_bytes = max_bytes
        
    def load_file(self, filepath: str) -> bytes:
        """
        Charge un fichier binaire
        
        Args:
            filepath: Chemin vers le fichier
            
        Returns:
            Contenu binaire du fichier
        """
        with open(filepath, 'rb') as f:
            if self.max_bytes:
                return f.read(self.max_bytes)
            return f.read()
    
    def load_directory(self, dirpath: str, extensions: List[str] = None) -> List[Tuple[str, bytes]]:
        """
        Charge tous les fichiers binaires d'un répertoire
        
        Args:
            dirpath: Chemin vers le répertoire
            extensions: Liste d'extensions à filtrer (ex: ['.exe', '.dll'])
            
        Returns:
            Liste de tuples (nom_fichier, contenu_binaire)
        """
        files_data = []
        
        for root, dirs, files in os.walk(dirpath):
            for filename in files:
                # Filtrer par extension si spécifié
                if extensions:
                    if not any(filename.lower().endswith(ext) for ext in extensions):
                        continue
                
                filepath = os.path.join(root, filename)
                try:
                    data = self.load_file(filepath)
                    files_data.append((filename, data))
                except Exception as e:
                    print(f"Erreur lors du chargement de {filename}: {e}")
        
        return files_data
    
    def bytes_to_array(self, data: bytes) -> np.ndarray:
        """
        Convertit bytes en array numpy
        
        Args:
            data: Données binaires
            
        Returns:
            Array numpy de type uint8
        """
        return np.frombuffer(data, dtype=np.uint8)


if __name__ == "__main__":
    # Test
    loader = BinaryLoader(max_bytes=1024)
    print("BinaryLoader créé avec succès!")
