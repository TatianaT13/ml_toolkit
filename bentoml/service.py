"""
Service BentoML pour API de détection de malwares
"""

import bentoml
from bentoml.io import File, JSON
import numpy as np
import pickle
import sys
import os

# Ajouter le path
sys.path.insert(0, '/app/my_ml_toolkit')

from feature_extraction.binary_features import BinaryFeatureExtractor

# Charger le modèle
MODEL_PATH = os.getenv('MODEL_PATH', '/app/models/malware_detector.pkl')

class MalwareDetectorRunnable(bentoml.Runnable):
    """Runnable personnalisé pour la détection de malwares"""
    
    SUPPORTED_RESOURCES = ("cpu",)
    SUPPORTS_CPU_MULTI_THREADING = True
    
    def __init__(self):
        # Charger le modèle et les métadonnées
        with open(MODEL_PATH, 'rb') as f:
            data = pickle.load(  # nosec B301f)
            self.model = data['model']
            self.preprocessor = data['preprocessor']
            self.feature_columns = data['feature_columns']
            self.info = data['info']
        
        self.extractor = BinaryFeatureExtractor()
    
    @bentoml.Runnable.method(batchable=False)
    def predict(self, file_data: bytes) -> dict:
        """Prédire si un fichier est un malware"""
        
        # Extraire les features
        features = self.extractor.extract_all_features(file_data)
        
        # Préparer pour prédiction
        import pandas as pd
        df = pd.DataFrame([features])
        
        # Garder seulement les colonnes utilisées pour l'entraînement
        X = df[self.feature_columns]
        
        # Prétraiter
        X_processed = self.preprocessor.scaler.transform(X)
        
        # Prédire
        prediction = self.model.predict(X_processed)[0]
        proba = self.model.predict_proba(X_processed)[0]
        
        # Construire la réponse
        result = {
            'is_malware': bool(prediction == 1),
            'confidence': float(proba[1] if prediction == 1 else proba[0]),
            'prediction': 'MALWARE' if prediction == 1 else 'BENIGN',
            'features': {
                'entropy': features['entropy'],
                'file_size': features['file_size'],
                'printable_ratio': features['printable_ratio'],
            },
            'model_info': {
                'name': self.info['model_name'],
                'trained_at': self.info['timestamp']
            }
        }
        
        return result


# Créer le runner
malware_detector_runner = bentoml.Runner(
    MalwareDetectorRunnable,
    name="malware_detector",
    max_batch_size=10,
)

# Créer le service
svc = bentoml.Service("malware_detection_service", runners=[malware_detector_runner])


@svc.api(input=File(), output=JSON())
async def scan_file(file_data: bytes) -> dict:
    """
    Endpoint pour scanner un fichier
    
    Args:
        file_data: Contenu binaire du fichier
        
    Returns:
        Résultat de l'analyse avec prédiction et confiance
    """
    result = await malware_detector_runner.predict.async_run(file_data)
    return result


@svc.api(input=JSON(), output=JSON())
async def health() -> dict:
    """Endpoint de santé"""
    return {
        "status": "healthy",
        "service": "malware_detection_service",
        "model": malware_detector_runner._runner_handle.info['model_name'] if hasattr(malware_detector_runner, '_runner_handle') else "loaded"
    }
