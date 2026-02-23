"""
Pipeline ML complet - Orchestre toutes les étapes du ML
"""

import pandas as pd
import numpy as np
from typing import Union, Dict, List

from .data_loader.tabular import TabularLoader
from .data_loader.binary import BinaryLoader
from .preprocessing.numeric_prep import NumericPreprocessor
from .feature_extraction.binary_features import BinaryFeatureExtractor
from .feature_extraction.text_features import TextFeatureExtractor
from .modeling.auto_trainer import AutoTrainer


class MLPipeline:
    """Pipeline ML end-to-end pour tous types de données"""
    
    def __init__(self, data_type: str = 'tabular', task_type: str = 'classification'):
        """
        Args:
            data_type: 'tabular', 'binary', ou 'text'
            task_type: 'classification' ou 'regression'
        """
        self.data_type = data_type
        self.task_type = task_type
        
        # Initialiser les composants
        self.loader = None
        self.preprocessor = None
        self.feature_extractor = None
        self.trainer = None
        
        self._init_components()
    
    def _init_components(self):
        """Initialise les composants selon le type de données"""
        # Loader
        if self.data_type == 'tabular':
            self.loader = TabularLoader()
            self.preprocessor = NumericPreprocessor()
        elif self.data_type == 'binary':
            self.loader = BinaryLoader()
            self.feature_extractor = BinaryFeatureExtractor()
        elif self.data_type == 'text':
            self.feature_extractor = TextFeatureExtractor()
        
        # Trainer
        self.trainer = AutoTrainer(task_type=self.task_type)
    
    def load_data(self, filepath: str, **kwargs) -> Union[pd.DataFrame, bytes, str]:
        """
        Charge les données selon le type
        
        Args:
            filepath: Chemin vers le fichier
            **kwargs: Arguments supplémentaires
            
        Returns:
            Données chargées
        """
        if self.data_type == 'tabular':
            if filepath.endswith('.csv'):
                return self.loader.load_csv(filepath, **kwargs)
            elif filepath.endswith(('.xlsx', '.xls')):
                return self.loader.load_excel(filepath, **kwargs)
            else:
                raise ValueError("Format non supporté. Utilisez .csv ou .xlsx")
        
        elif self.data_type == 'binary':
            return self.loader.load_file(filepath)
        
        elif self.data_type == 'text':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        
        else:
            raise ValueError(f"Type de données inconnu: {self.data_type}")
    
    def extract_features(self, data: Union[pd.DataFrame, bytes, str, List]) -> pd.DataFrame:
        """
        Extrait les features selon le type de données
        
        Args:
            data: Données brutes
            
        Returns:
            DataFrame avec features
        """
        if self.data_type == 'tabular':
            # Déjà sous forme de DataFrame
            return data
        
        elif self.data_type == 'binary':
            if isinstance(data, list):
                # Multiple fichiers
                features_list = []
                for filename, binary_data in data:
                    features = self.feature_extractor.extract_all_features(binary_data)
                    features['filename'] = filename
                    features_list.append(features)
                return pd.DataFrame(features_list)
            else:
                # Un seul fichier
                features = self.feature_extractor.extract_all_features(data)
                return pd.DataFrame([features])
        
        elif self.data_type == 'text':
            if isinstance(data, list):
                # Multiple textes
                features_list = []
                for text in data:
                    features = self.feature_extractor.extract_all_features(text)
                    features_list.append(features)
                return pd.DataFrame(features_list)
            else:
                # Un seul texte
                features = self.feature_extractor.extract_all_features(data)
                return pd.DataFrame([features])
    
    def preprocess(self, X: pd.DataFrame, y: pd.Series = None) -> tuple:
        """
        Prétraite les données
        
        Args:
            X: Features
            y: Target (optionnel)
            
        Returns:
            (X, y) prétraités
        """
        if self.data_type == 'tabular':
            # Supprimer toutes les colonnes non-numériques (md5, sha256, filename, etc.)
            cols_to_drop = [col for col in X.columns
                            if not pd.api.types.is_numeric_dtype(X[col])]

            X_processed = X.drop(columns=cols_to_drop, errors='ignore')

            # Prétraiter
            X_processed, _ = self.preprocessor.preprocess_full(
                X_processed,
                handle_missing=True,
                encode_cat=True,
                scale=True
            )

            return X_processed, y
        else:
            # Pour binary et text, les features sont déjà numériques
            # Mais on peut quand même normaliser
            if self.preprocessor is None:
                self.preprocessor = NumericPreprocessor()

            # Supprimer colonnes non-numériques (compatible pandas 2.x et 3.x)
            cols_to_drop = [col for col in X.columns
                            if not pd.api.types.is_numeric_dtype(X[col])]

            X_processed = X.drop(columns=cols_to_drop, errors='ignore')
            
            X_processed = self.preprocessor.scale_features(X_processed, fit=True)
            return X_processed, y
    
    def train(self, X: pd.DataFrame, y: pd.Series, verbose: bool = True) -> Dict:
        """
        Entraîne les modèles
        
        Args:
            X: Features
            y: Target
            verbose: Afficher les résultats
            
        Returns:
            Résultats d'entraînement
        """
        return self.trainer.train_all_models(X, y, verbose=verbose)
    
    def run_full_pipeline(self, filepath: str, target_col: str = None, verbose: bool = True):
        """
        Exécute le pipeline complet: load → extract → preprocess → train
        
        Args:
            filepath: Chemin vers les données
            target_col: Nom de la colonne cible (pour tabular)
            verbose: Afficher les étapes
            
        Returns:
            Résultats finaux
        """
        if verbose:
            print("🚀 Démarrage du pipeline ML complet\n")
        
        # 1. Chargement
        if verbose:
            print("📁 Étape 1/4: Chargement des données...")
        data = self.load_data(filepath)
        if verbose:
            print("   ✓ Données chargées\n")
        
        # 2. Extraction de features (si nécessaire)
        if verbose:
            print("🔍 Étape 2/4: Extraction des features...")
        df = self.extract_features(data)
        if verbose:
            print(f"   ✓ {df.shape[1]} features extraites\n")
        
        # 3. Prétraitement
        if verbose:
            print("⚙️  Étape 3/4: Prétraitement...")
        
        if self.data_type == 'tabular' and target_col:
            y = df[target_col]
            X = df.drop(columns=[target_col])
        else:
            X = df
            y = None
        
        X, y = self.preprocess(X, y)
        if verbose:
            print(f"   ✓ Données prétraitées: {X.shape}\n")
        
        # 4. Entraînement
        if verbose:
            print("🤖 Étape 4/4: Entraînement des modèles...")
        
        if y is None:
            print("   ⚠️  Pas de target fournie, impossible d'entraîner")
            return None
        
        results = self.train(X, y, verbose=verbose)
        
        if verbose:
            print("\n✅ Pipeline terminé avec succès!")
        
        return results
    
    def predict_new_data(self, filepath: str) -> np.ndarray:
        """
        Prédit sur de nouvelles données
        
        Args:
            filepath: Chemin vers les nouvelles données
            
        Returns:
            Prédictions
        """
        # Charger et prétraiter comme avant
        data = self.load_data(filepath)
        df = self.extract_features(data)
        X, _ = self.preprocess(df)
        
        # Prédire avec le meilleur modèle
        predictions = self.trainer.predict(X)
        
        return predictions


if __name__ == "__main__":
    print("MLPipeline créé avec succès!")
    print("\nUtilisation:")
    print("  pipeline = MLPipeline(data_type='tabular', task_type='classification')")
    print("  pipeline.run_full_pipeline('data.csv', target_col='target')")
