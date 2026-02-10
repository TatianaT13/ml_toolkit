"""
Module de prétraitement pour données numériques/tabulaires
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from typing import Union, List


class NumericPreprocessor:
    """Prétraite les données numériques"""
    
    def __init__(self, scaling_method: str = 'standard'):
        """
        Args:
            scaling_method: 'standard' (StandardScaler) ou 'minmax' (MinMaxScaler)
        """
        self.scaling_method = scaling_method
        self.scaler = None
        self.imputer = None
        self.label_encoders = {}
        
        if scaling_method == 'standard':
            self.scaler = StandardScaler()
        elif scaling_method == 'minmax':
            self.scaler = MinMaxScaler()
        else:
            raise ValueError("scaling_method doit être 'standard' ou 'minmax'")
    
    def handle_missing_values(self, X: pd.DataFrame, strategy: str = 'mean') -> pd.DataFrame:
        """
        Gère les valeurs manquantes
        
        Args:
            X: DataFrame avec données
            strategy: 'mean', 'median', 'most_frequent', ou 'constant'
            
        Returns:
            DataFrame sans valeurs manquantes
        """
        if self.imputer is None:
            self.imputer = SimpleImputer(strategy=strategy)
            X_imputed = self.imputer.fit_transform(X)
        else:
            X_imputed = self.imputer.transform(X)
        
        return pd.DataFrame(X_imputed, columns=X.columns, index=X.index)
    
    def encode_categorical(self, df: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
        """
        Encode les variables catégorielles
        
        Args:
            df: DataFrame
            columns: Liste des colonnes à encoder (None = auto-détection)
            
        Returns:
            DataFrame avec colonnes encodées
        """
        df_copy = df.copy()
        
        # Auto-détection des colonnes catégorielles
        if columns is None:
            columns = df_copy.select_dtypes(include=['object', 'category']).columns.tolist()
        
        for col in columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df_copy[col] = self.label_encoders[col].fit_transform(df_copy[col].astype(str))
            else:
                df_copy[col] = self.label_encoders[col].transform(df_copy[col].astype(str))
        
        return df_copy
    
    def scale_features(self, X: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """
        Normalise/standardise les features
        
        Args:
            X: DataFrame avec features numériques
            fit: Si True, fit le scaler, sinon juste transform
            
        Returns:
            DataFrame normalisé
        """
        if fit:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        return pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
    
    def preprocess_full(self, df: pd.DataFrame, target_col: str = None, 
                       handle_missing: bool = True, encode_cat: bool = True, 
                       scale: bool = True) -> tuple:
        """
        Pipeline complet de prétraitement
        
        Args:
            df: DataFrame complet
            target_col: Nom de la colonne cible (y)
            handle_missing: Gérer les valeurs manquantes
            encode_cat: Encoder les variables catégorielles
            scale: Normaliser les features
            
        Returns:
            (X, y) preprocessés
        """
        df_copy = df.copy()
        
        # Séparer X et y
        if target_col:
            y = df_copy[target_col]
            X = df_copy.drop(columns=[target_col])
        else:
            X = df_copy
            y = None
        
        # Encoder les catégorielles
        if encode_cat:
            X = self.encode_categorical(X)
        
        # Gérer les valeurs manquantes
        if handle_missing:
            X = self.handle_missing_values(X)
        
        # Normaliser
        if scale:
            X = self.scale_features(X)
        
        return X, y


if __name__ == "__main__":
    # Test
    preprocessor = NumericPreprocessor(scaling_method='standard')
    print("NumericPreprocessor créé avec succès!")
