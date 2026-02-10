"""
Module d'entraînement automatique de modèles ML
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, r2_score, classification_report
from typing import Dict, List, Tuple, Union


class AutoTrainer:
    """Entraîne et compare automatiquement plusieurs modèles"""
    
    def __init__(self, task_type: str = 'classification', test_size: float = 0.2, random_state: int = 42):
        """
        Args:
            task_type: 'classification' ou 'regression'
            test_size: Proportion des données pour le test
            random_state: Seed pour reproductibilité
        """
        self.task_type = task_type
        self.test_size = test_size
        self.random_state = random_state
        self.models = {}
        self.best_model = None
        self.best_score = None
        self.results = {}
        
        # Initialiser les modèles selon le type de tâche
        self._init_models()
    
    def _init_models(self):
        """Initialise la liste de modèles à tester"""
        if self.task_type == 'classification':
            self.models = {
                'RandomForest': RandomForestClassifier(n_estimators=100, random_state=self.random_state),
                'LogisticRegression': LogisticRegression(max_iter=1000, random_state=self.random_state),
                'GradientBoosting': GradientBoostingClassifier(random_state=self.random_state),
                'KNN': KNeighborsClassifier(n_neighbors=5),
                'SVM': SVC(kernel='rbf', random_state=self.random_state)
            }
        elif self.task_type == 'regression':
            self.models = {
                'RandomForest': RandomForestRegressor(n_estimators=100, random_state=self.random_state),
                'LinearRegression': LinearRegression(),
                'SVR': SVR(kernel='rbf'),
            }
        else:
            raise ValueError("task_type doit être 'classification' ou 'regression'")
    
    def train_all_models(self, X: Union[np.ndarray, pd.DataFrame], 
                        y: Union[np.ndarray, pd.Series],
                        verbose: bool = True) -> Dict:
        """
        Entraîne tous les modèles et compare leurs performances
        
        Args:
            X: Features
            y: Target
            verbose: Afficher les résultats
            
        Returns:
            Dictionnaire avec résultats de tous les modèles
        """
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state
        )
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Entraînement de {len(self.models)} modèles ({self.task_type})")
            print(f"Train: {X_train.shape[0]} samples | Test: {X_test.shape[0]} samples")
            print(f"{'='*60}\n")
        
        # Entraîner chaque modèle
        for name, model in self.models.items():
            if verbose:
                print(f"⏳ Entraînement: {name}...", end=' ')
            
            try:
                # Entraînement
                model.fit(X_train, y_train)
                
                # Prédictions
                y_pred = model.predict(X_test)
                
                # Métriques
                if self.task_type == 'classification':
                    score = accuracy_score(y_test, y_pred)
                    f1 = f1_score(y_test, y_pred, average='weighted')
                    
                    self.results[name] = {
                        'model': model,
                        'accuracy': score,
                        'f1_score': f1,
                        'predictions': y_pred
                    }
                    
                    if verbose:
                        print(f"✓ Accuracy: {score:.4f} | F1: {f1:.4f}")
                
                else:  # regression
                    mse = mean_squared_error(y_test, y_pred)
                    r2 = r2_score(y_test, y_pred)
                    
                    self.results[name] = {
                        'model': model,
                        'mse': mse,
                        'rmse': np.sqrt(mse),
                        'r2': r2,
                        'predictions': y_pred
                    }
                    
                    if verbose:
                        print(f"✓ RMSE: {np.sqrt(mse):.4f} | R²: {r2:.4f}")
                
                # Garder le meilleur modèle
                current_score = score if self.task_type == 'classification' else r2
                if self.best_score is None or current_score > self.best_score:
                    self.best_score = current_score
                    self.best_model = model
                    self.best_model_name = name
                    
            except Exception as e:
                if verbose:
                    print(f"✗ Erreur: {e}")
                self.results[name] = {'error': str(e)}
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"🏆 Meilleur modèle: {self.best_model_name}")
            print(f"   Score: {self.best_score:.4f}")
            print(f"{'='*60}\n")
        
        return self.results
    
    def get_best_model(self) -> Tuple[str, object]:
        """Retourne le meilleur modèle"""
        if self.best_model is None:
            raise ValueError("Aucun modèle entraîné. Appelez train_all_models() d'abord.")
        return self.best_model_name, self.best_model
    
    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Prédit avec le meilleur modèle"""
        if self.best_model is None:
            raise ValueError("Aucun modèle entraîné. Appelez train_all_models() d'abord.")
        return self.best_model.predict(X)
    
    def get_results_dataframe(self) -> pd.DataFrame:
        """Retourne les résultats sous forme de DataFrame"""
        results_list = []
        
        for name, result in self.results.items():
            if 'error' in result:
                continue
            
            row = {'Model': name}
            
            if self.task_type == 'classification':
                row['Accuracy'] = result['accuracy']
                row['F1_Score'] = result['f1_score']
            else:
                row['RMSE'] = result['rmse']
                row['R2'] = result['r2']
            
            results_list.append(row)
        
        df = pd.DataFrame(results_list)
        
        # Trier par meilleure performance
        if self.task_type == 'classification':
            df = df.sort_values('Accuracy', ascending=False)
        else:
            df = df.sort_values('R2', ascending=False)
        
        return df


if __name__ == "__main__":
    # Test avec données fictives
    from sklearn.datasets import make_classification
    
    X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
    
    trainer = AutoTrainer(task_type='classification')
    results = trainer.train_all_models(X, y, verbose=True)
    
    print("\nRésultats sous forme de DataFrame:")
    print(trainer.get_results_dataframe())
