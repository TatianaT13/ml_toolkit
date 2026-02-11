"""
API REST pour le ML Toolkit - Détection de Malwares
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime

from my_ml_toolkit.pipeline import MLPipeline

# Initialiser FastAPI
app = FastAPI(
    title="ML Toolkit API - Malware Detection",
    description="API REST pour la détection de malwares avec Machine Learning",
    version="1.0.0"
)

# Store global pour les pipelines
pipelines = {}
current_pipeline_id = None

class TrainRequest(BaseModel):
    data_type: str = "tabular"
    task_type: str = "classification"
    target_column: str

class PredictRequest(BaseModel):
    pipeline_id: str

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "🛡️ ML Toolkit API - Malware Detection",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "train": "/train",
            "predict": "/predict",
            "models": "/models",
            "pipeline": "/pipeline/{pipeline_id}"
        }
    }

@app.get("/health")
async def health_check():
    """Vérifier que l'API fonctionne"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_pipelines": len(pipelines)
    }

@app.post("/train")
async def train_model(
    file: UploadFile = File(...),
    data_type: str = "tabular",
    task_type: str = "classification",
    target_column: str = "label"
):
    """
    Entraîner un nouveau modèle
    
    Args:
        file: Fichier CSV avec les données
        data_type: Type de données (tabular, binary, text)
        task_type: Type de tâche (classification, regression)
        target_column: Nom de la colonne cible
    
    Returns:
        Résultats d'entraînement et ID du pipeline
    """
    try:
        # Sauvegarder le fichier temporairement
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Créer et entraîner le pipeline
        pipeline = MLPipeline(data_type=data_type, task_type=task_type)
        results = pipeline.run_full_pipeline(
            temp_path, 
            target_col=target_column, 
            verbose=False
        )
        
        if results is None:
            raise HTTPException(status_code=400, detail="Training failed")
        
        # Générer un ID unique
        pipeline_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Stocker le pipeline
        pipelines[pipeline_id] = {
            "pipeline": pipeline,
            "results": results,
            "created_at": datetime.now().isoformat(),
            "data_type": data_type,
            "task_type": task_type
        }
        
        global current_pipeline_id
        current_pipeline_id = pipeline_id
        
        # Nettoyer
        os.remove(temp_path)
        
        # Formater les résultats
        best_model = max(results.items(), key=lambda x: x[1]['accuracy'])
        
        return {
            "pipeline_id": pipeline_id,
            "status": "success",
            "best_model": best_model[0],
            "best_accuracy": float(best_model[1]['accuracy']),
            "all_results": {k: {
                "accuracy": float(v['accuracy']),
                "precision": float(v['precision']),
                "recall": float(v['recall']),
                "f1": float(v['f1'])
            } for k, v in results.items()},
            "message": f"✅ Modèle entraîné avec succès! Meilleur modèle: {best_model[0]}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/{pipeline_id}")
async def predict(
    pipeline_id: str,
    file: UploadFile = File(...)
):
    """
    Faire une prédiction avec un pipeline entraîné
    
    Args:
        pipeline_id: ID du pipeline à utiliser
        file: Fichier CSV avec les données à prédire
    
    Returns:
        Prédictions
    """
    try:
        # Vérifier que le pipeline existe
        if pipeline_id not in pipelines:
            raise HTTPException(
                status_code=404, 
                detail=f"Pipeline {pipeline_id} not found"
            )
        
        # Sauvegarder le fichier temporairement
        temp_path = f"/tmp/predict_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Charger les données
        df = pd.read_csv(temp_path)
        
        # Faire la prédiction
        pipeline = pipelines[pipeline_id]["pipeline"]
        predictions = pipeline.predict_new_data(temp_path)
        
        # Nettoyer
        os.remove(temp_path)
        
        # Retourner les résultats
        results_df = df.copy()
        results_df['prediction'] = predictions.tolist()
        
        return {
            "pipeline_id": pipeline_id,
            "num_predictions": len(predictions),
            "predictions": results_df.to_dict(orient='records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """Lister tous les pipelines disponibles"""
    return {
        "total_pipelines": len(pipelines),
        "current_pipeline": current_pipeline_id,
        "pipelines": [{
            "pipeline_id": pid,
            "created_at": info["created_at"],
            "data_type": info["data_type"],
            "task_type": info["task_type"],
            "best_model": max(info["results"].items(), key=lambda x: x[1]['accuracy'])[0]
        } for pid, info in pipelines.items()]
    }

@app.get("/pipeline/{pipeline_id}")
async def get_pipeline_info(pipeline_id: str):
    """Obtenir les informations d'un pipeline spécifique"""
    if pipeline_id not in pipelines:
        raise HTTPException(
            status_code=404, 
            detail=f"Pipeline {pipeline_id} not found"
        )
    
    info = pipelines[pipeline_id]
    return {
        "pipeline_id": pipeline_id,
        "created_at": info["created_at"],
        "data_type": info["data_type"],
        "task_type": info["task_type"],
        "results": {k: {
            "accuracy": float(v['accuracy']),
            "precision": float(v['precision']),
            "recall": float(v['recall']),
            "f1": float(v['f1'])
        } for k, v in info["results"].items()}
    }

@app.delete("/pipeline/{pipeline_id}")
async def delete_pipeline(pipeline_id: str):
    """Supprimer un pipeline"""
    if pipeline_id not in pipelines:
        raise HTTPException(
            status_code=404, 
            detail=f"Pipeline {pipeline_id} not found"
        )
    
    del pipelines[pipeline_id]
    
    global current_pipeline_id
    if current_pipeline_id == pipeline_id:
        current_pipeline_id = None
    
    return {
        "message": f"Pipeline {pipeline_id} supprimé",
        "remaining_pipelines": len(pipelines)
    }

@app.post("/validate/{pipeline_id}")
async def validate_with_virustotal(
    pipeline_id: str,
    file: UploadFile = File(...),
    vt_api_key: str = None
):
    """
    Prédire ET valider avec VirusTotal
    """
    if not vt_api_key:
        raise HTTPException(400, "VirusTotal API key required")
    
    # Faire la prédiction ML
    # ... (code existant)
    
    # Valider avec VirusTotal
    from my_ml_toolkit.integrations.virustotal import VirusTotalIntegration
    
    vt = VirusTotalIntegration(vt_api_key)
    comparison = vt.compare_with_ml_prediction(temp_path, prediction[0])
    vt.close()
    
    return {
        "ml_result": prediction,
        "virustotal_validation": comparison
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
