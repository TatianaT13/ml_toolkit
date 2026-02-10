# 🏗️ Architecture MLOps - Diagramme

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         ML TOOLKIT MLOPS ARCHITECTURE                         │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  📊 DATA LAYER                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐         ┌─────────────────┐                           │
│  │ Malware Samples │         │ Benign Samples  │                           │
│  │  /data/malware  │         │  /data/benign   │                           │
│  └────────┬────────┘         └────────┬────────┘                           │
│           │                           │                                     │
│           └───────────┬───────────────┘                                     │
│                       │                                                     │
│                       ▼                                                     │
│              ┌─────────────────┐                                            │
│              │  DVC (DagsHub)  │◄─── Version Control                       │
│              │  Data Versioning│                                            │
│              └─────────────────┘                                            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

                                      │
                                      ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│  🔄 ORCHESTRATION LAYER (Airflow)                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      ML PIPELINE DAG (Daily)                          │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │                                                                       │  │
│  │  1️⃣  Check Data Availability                                         │  │
│  │       │                                                               │  │
│  │       ├──► Yes (≥10 files) ───► 3️⃣  Extract Features                 │  │
│  │       │                                  │                            │  │
│  │       └──► No (<10 files) ───► 2️⃣  Generate Synthetic Data           │  │
│  │                                  │                                    │  │
│  │                                  └──────────┬─────────────┐           │  │
│  │                                             │             │           │  │
│  │                              BinaryFeatureExtractor       │           │  │
│  │                              • Entropy                    │           │  │
│  │                              • Signatures                 │           │  │
│  │                              • N-grams                    │           │  │
│  │                              • 25+ features                │           │  │
│  │                                             │             │           │  │
│  │                                             ▼             │           │  │
│  │                              4️⃣  Train Model              │           │  │
│  │                                  │                        │           │  │
│  │                              AutoTrainer                  │           │  │
│  │                              • RandomForest               │           │  │
│  │                              • LogisticRegression         │           │  │
│  │                              • GradientBoosting          │           │  │
│  │                              • KNN                        │           │  │
│  │                              • SVM                        │           │  │
│  │                                  │                        │           │  │
│  │                                  ▼                        │           │  │
│  │                              5️⃣  Evaluate Model           │           │  │
│  │                                  │                        │           │  │
│  │                              • Accuracy                   │           │  │
│  │                              • F1-Score                   │           │  │
│  │                              • Confusion Matrix           │           │  │
│  │                                  │                        │           │  │
│  │                                  ▼                        │           │  │
│  │                              6️⃣  Deploy Model             │           │  │
│  │                                  │                        │           │  │
│  │                              Save to:                     │           │  │
│  │                              /models/malware_detector.pkl │           │  │
│  │                                                           │           │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─────────────┐     ┌──────────┐     ┌────────────┐                       │
│  │ Scheduler   │────►│ Worker(s)│────►│ PostgreSQL │                       │
│  │ (Celery)    │     │          │     │   Metadata │                       │
│  └─────────────┘     └──────────┘     └────────────┘                       │
│         │                                                                   │
│         └──────────► Redis (Message Broker)                                │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

                                      │
                                      ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│  🤖 INFERENCE LAYER (BentoML)                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────┐             │
│  │              BentoML REST API (:3000)                       │             │
│  ├────────────────────────────────────────────────────────────┤             │
│  │                                                             │             │
│  │  POST /scan_file                                            │             │
│  │  ┌──────────────────────────────────────────────────────┐  │             │
│  │  │  Input: Binary file                                   │  │             │
│  │  │  ↓                                                     │  │             │
│  │  │  1. Extract features (BinaryFeatureExtractor)         │  │             │
│  │  │  2. Preprocess (NumericPreprocessor)                  │  │             │
│  │  │  3. Predict (Trained Model)                           │  │             │
│  │  │  ↓                                                     │  │             │
│  │  │  Output: {                                            │  │             │
│  │  │    "is_malware": true/false,                          │  │             │
│  │  │    "confidence": 0.95,                                │  │             │
│  │  │    "prediction": "MALWARE",                           │  │             │
│  │  │    "features": {...},                                 │  │             │
│  │  │    "model_info": {...}                                │  │             │
│  │  │  }                                                     │  │             │
│  │  └──────────────────────────────────────────────────────┘  │             │
│  │                                                             │             │
│  │  GET /health                                                │             │
│  │  └──► {"status": "healthy"}                                │             │
│  │                                                             │             │
│  └─────────────────────────────────────────────────────────────┘             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

                                      │
                                      ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│  📈 MONITORING LAYER                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────┐                    │
│  │               Prometheus (:9090)                     │                    │
│  ├─────────────────────────────────────────────────────┤                    │
│  │  Metrics Collection:                                │                    │
│  │  • API Request Rate                                 │                    │
│  │  • Prediction Time                                  │                    │
│  │  • Model Accuracy                                   │                    │
│  │  • Malware Detection Rate                           │                    │
│  │  • System Resources (CPU, RAM)                      │                    │
│  └────────────────────┬────────────────────────────────┘                    │
│                       │                                                     │
│                       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐                    │
│  │                 Grafana (:3001)                      │                    │
│  ├─────────────────────────────────────────────────────┤                    │
│  │  Dashboards:                                        │                    │
│  │  📊 ML Performance                                  │                    │
│  │     • Accuracy over time                            │                    │
│  │     • Confusion matrix                              │                    │
│  │     • False positives/negatives                     │                    │
│  │                                                     │                    │
│  │  📡 API Monitoring                                  │                    │
│  │     • Request rate                                  │                    │
│  │     • Response time                                 │                    │
│  │     • Error rate                                    │                    │
│  │                                                     │                    │
│  │  💻 System Health                                   │                    │
│  │     • CPU usage                                     │                    │
│  │     • Memory usage                                  │                    │
│  │     • Disk space                                    │                    │
│  └─────────────────────────────────────────────────────┘                    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  🔄 CONTINUOUS INTEGRATION                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  GitHub ──► DagsHub ──► DVC ──► Data Versioning                            │
│     │                                                                        │
│     └──► Docker Hub ──► Container Registry                                 │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
  PORTS
═══════════════════════════════════════════════════════════════════════════════

  :8080  → Airflow Webserver      (admin / admin)
  :3000  → BentoML API             (REST API)
  :3001  → Grafana                 (admin / admin)
  :9090  → Prometheus              (Metrics)
  :5432  → PostgreSQL              (Airflow DB)
  :6379  → Redis                   (Message Broker)

═══════════════════════════════════════════════════════════════════════════════
```

## 🔄 Workflow Complet

1. **Daily Schedule** : Airflow déclenche le pipeline à minuit
2. **Data Check** : Vérifie si de nouvelles données sont disponibles
3. **Feature Extraction** : Analyse tous les fichiers et extrait 25+ features
4. **Model Training** : Teste 5 modèles ML et sélectionne le meilleur
5. **Model Deployment** : Sauvegarde le modèle pour l'API
6. **Monitoring** : Prometheus collecte les métriques
7. **Visualization** : Grafana affiche les dashboards
8. **API Serving** : BentoML expose l'API REST pour détection temps réel

## 🎯 Points Clés

- **Automatisation complète** : Zéro intervention manuelle
- **Versioning** : Données et modèles versionnés avec DVC
- **Scalabilité** : Celery workers pour parallélisation
- **Observabilité** : Metrics + Logs + Dashboards
- **Production-ready** : Containerisé avec Docker
