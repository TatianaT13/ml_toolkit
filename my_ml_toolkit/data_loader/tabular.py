"""
Module pour charger des données tabulaires (CSV, Excel, etc.)
"""

import pandas as pd
from typing import Union, List


class TabularLoader:
    """Charge des données tabulaires"""
    
    def __init__(self, separator: str = ',', encoding: str = 'utf-8'):
        """
        Args:
            separator: Séparateur pour CSV (virgule par défaut)
            encoding: Encodage du fichier
        """
        self.separator = separator
        self.encoding = encoding
    
    def load_csv(self, filepath: str, **kwargs) -> pd.DataFrame:
        """
        Charge un fichier CSV
        
        Args:
            filepath: Chemin vers le fichier CSV
            **kwargs: Arguments supplémentaires pour pd.read_csv
            
        Returns:
            DataFrame pandas
        """
        return pd.read_csv(
            filepath, 
            sep=self.separator, 
            encoding=self.encoding,
            **kwargs
        )
    
    def load_excel(self, filepath: str, sheet_name: Union[str, int] = 0, **kwargs) -> pd.DataFrame:
        """
        Charge un fichier Excel
        
        Args:
            filepath: Chemin vers le fichier Excel
            sheet_name: Nom ou index de la feuille à charger
            **kwargs: Arguments supplémentaires pour pd.read_excel
            
        Returns:
            DataFrame pandas
        """
        return pd.read_excel(filepath, sheet_name=sheet_name, **kwargs)
    
    def load_json(self, filepath: str, **kwargs) -> pd.DataFrame:
        """Charge un fichier JSON"""
        return pd.read_json(filepath, **kwargs)
    
    def get_info(self, df: pd.DataFrame) -> dict:
        """Retourne des infos sur le DataFrame"""
        return {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }


if __name__ == "__main__":
    loader = TabularLoader()
    print("TabularLoader créé avec succès!")
