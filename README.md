# 🚀 ML Toolkit MLOps - Architecture Complète

Système automatisé de détection de malwares avec pipeline MLOps complet.

## 📋 Table des Matières

- [Architecture](#architecture)
- [Services](#services)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Monitoring](#monitoring)
- [API](#api)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MLOPS ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Data Collection                                         │
│  └─> Malware samples + Benign files                         │
│       └─> DVC (Data Version Control)                        │
│                                                             │
│  🔄 Airflow Pipeline (Daily)                                │
│  ├─> Check Data Availability                                │
│  ├─> Extract Features (binary_features.py)                  │
│  ├─> Train Model (auto_trainer.py)                          │
│  ├─> Evaluate Performance                                   │
│  └─> Deploy Model                                           │
│                                                             │
│  🤖 BentoML API                                             │
│  └─> REST API for malware detection                         │
│       POST /scan_file → {is_malware, confidence}            │
│                                                             │
│  📈 Monitoring                                              │
│  ├─> Prometheus (Metrics)                                   │
│  └─> Grafana (Dashboards)                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Services

### 1. **ML Toolkit** (Port: interne)
Application principale de Machine Learning
- Extraction de features binaires
- Entraînement automatique de modèles
- Support multi-types de données

### 2. **Airflow** (Port: 8080)
Orchestration du pipeline ML
- **Webserver**: Interface de gestion
- **Scheduler**: Planification des tâches
- **Worker**: Exécution des jobs
- **Login**: `admin` / `admin`

### 3. **BentoML** (Port: 3000)
API REST pour détection en temps réel
- Endpoint: `POST /scan_file`
- Analyse de fichiers suspects
- Réponse avec confiance et features

### 4. **PostgreSQL** (Port: 5432)
Base de données pour Airflow
- Stockage métadonnées des DAGs
- Historique des exécutions

### 5. **Redis** (Port: 6379)
Message broker pour Celery (Airflow)
- File d'attente des tâches
- Communication inter-workers

### 6. **Prometheus** (Port: 9090)
Collecte de métriques
- Performance des modèles
- Santé des services
- Utilisation ressources

### 7. **Grafana** (Port: 3001)
Visualisation et dashboards
- **Login**: `admin` / `admin`
- Métriques temps réel
- Alertes personnalisées

---

## ⚙️ Installation

### Prérequis

- Docker & Docker Compose
- Git
- 8GB RAM minimum
- 20GB espace disque

### 🚀 Démarrage Rapide

```bash
# 1. Cloner le repository
git clone git@github.com:TatianaT13/ml_toolkit.git
cd ml_toolkit

# 2. Copier les fichiers MLOps
# (Les fichiers Dockerfile, docker-compose.yml, etc.)

# 3. Créer la structure de données
mkdir -p data/{malware_samples,benign_samples} models

# 4. Lancer tous les services
docker-compose up -d

# 5. Vérifier que tout est démarré
docker-compose ps
```

### 📊 Initialisation d'Airflow

```bash
# Attendre que tous les services soient UP (~2 minutes)
docker-compose logs -f airflow-webserver

# Quand vous voyez "Airflow Webserver started"
# Ouvrir http://localhost:8080
# Login: admin / admin
```

---

## 🎯 Utilisation

### 1️⃣ Pipeline Automatique (Airflow)

Le pipeline s'exécute **automatiquement chaque jour** :

1. **Vérification des données** : Compte les fichiers disponibles
2. **Génération synthétique** : Si pas assez de données
3. **Extraction features** : Analyse tous les fichiers
4. **Entraînement** : Teste 5 modèles ML
5. **Évaluation** : Génère un rapport
6. **Déploiement** : Met à jour l'API

**Lancer manuellement** :
```bash
# Via l'interface Airflow
# http://localhost:8080 → DAGs → ml_malware_detection_pipeline → Trigger

# Ou via CLI
docker exec airflow-webserver airflow dags trigger ml_malware_detection_pipeline
```

### 2️⃣ API de Détection (BentoML)

**Scanner un fichier suspect** :

```bash
# Test avec curl
curl -X POST http://localhost:3000/scan_file \
  -F "file=@suspicious_file.exe"

# Réponse
{
  "is_malware": true,
  "confidence": 0.95,
  "prediction": "MALWARE",
  "features": {
    "entropy": 7.82,
    "file_size": 1024,
    "printable_ratio": 0.15
  },
  "model_info": {
    "name": "RandomForest",
    "trained_at": "2024-02-10T19:00:00"
  }
}
```

**Python Client** :

```python
import requests

with open('file_to_scan.exe', 'rb') as f:
    response = requests.post(
        'http://localhost:3000/scan_file',
        files={'file': f}
    )

result = response.json()
if result['is_malware']:
    print(f"⚠️  MALWARE détecté ! Confiance: {result['confidence']:.2%}")
else:
    print(f"✅ Fichier légitime. Confiance: {result['confidence']:.2%}")
```

### 3️⃣ Ajouter Vos Données

```bash
# Copier vos fichiers malwares
cp /path/to/malwares/* data/malware_samples/

# Copier vos fichiers légitimes
cp /path/to/benign/* data/benign_samples/

# Le prochain run du pipeline les utilisera automatiquement
```

### 4️⃣ Versioning avec DVC

```bash
# Installer DVC
pip install dvc

# Initialiser DVC dans le projet
dvc init

# Tracker les données
dvc add data/malware_samples
dvc add data/benign_samples
dvc add models/

# Pousser vers DagsHub
dvc push

# Git commit
git add .
git commit -m "Update datasets and models"
git push
```

---

## 📊 Monitoring

### Prometheus (http://localhost:9090)

**Métriques disponibles** :
- Taux de prédictions malware vs benign
- Temps de réponse API
- Accuracy du modèle actuel
- Utilisation CPU/RAM

**Exemples de queries** :
```promql
# Nombre total de prédictions
sum(prediction_counter)

# Taux de malwares détectés
rate(malware_detected[5m])

# Temps moyen de prédiction
avg(prediction_duration_seconds)
```

### Grafana (http://localhost:3001)

**Login** : `admin` / `admin`

**Dashboards à créer** :
1. **ML Performance**
   - Accuracy over time
   - Confusion matrix
   - False positives/negatives

2. **API Monitoring**
   - Request rate
   - Response time
   - Error rate

3. **System Health**
   - CPU usage
   - Memory usage
   - Disk space

---

## 🔧 Commandes Utiles

```bash
# Voir les logs d'un service
docker-compose logs -f airflow-webserver
docker-compose logs -f bentoml

# Redémarrer un service
docker-compose restart airflow-scheduler

# Accéder au shell d'un container
docker exec -it ml_toolkit_app bash

# Voir l'état des services
docker-compose ps

# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes (⚠️ perte de données)
docker-compose down -v
```

---

## 📁 Structure du Projet

```
ml_toolkit_mlops/
├── docker/
│   └── Dockerfile.airflow           # Image Airflow personnalisée
├── airflow/
│   ├── dags/
│   │   └── ml_pipeline_dag.py       # Pipeline ML automatisé
│   ├── logs/                        # Logs Airflow
│   └── plugins/                     # Plugins personnalisés
├── bentoml/
│   ├── service.py                   # Service API
│   └── Dockerfile.bentoml           # Image BentoML
├── monitoring/
│   ├── prometheus.yml               # Config Prometheus
│   └── grafana-datasources.yml      # Datasources Grafana
├── data/
│   ├── malware_samples/             # Fichiers malveillants
│   └── benign_samples/              # Fichiers légitimes
├── models/                          # Modèles entraînés
├── my_ml_toolkit/                   # Code source du toolkit
├── Dockerfile                       # Image principale
├── docker-compose.yml               # Orchestration
└── README.md                        # Ce fichier
```

---

## 🎓 Cas d'Usage

### 1. **Détection de Malwares en Production**
- Upload de fichiers suspects via API
- Analyse automatique en temps réel
- Alertes si malware détecté

### 2. **Recherche en Cybersécurité**
- Dataset versionné avec DVC
- Expérimentation de nouvelles features
- Comparaison de modèles

### 3. **Formation et Apprentissage**
- Pipeline ML complet de bout en bout
- Best practices MLOps
- Monitoring et observabilité

---

## 🐛 Troubleshooting

### Airflow ne démarre pas
```bash
# Réinitialiser la DB
docker-compose down -v
docker-compose up -d
```

### BentoML erreur "Model not found"
```bash
# Vérifier que le modèle existe
ls -la models/malware_detector.pkl

# Lancer le pipeline Airflow pour générer un modèle
```

### Prometheus ne collecte pas de métriques
```bash
# Vérifier la config
docker exec prometheus cat /etc/prometheus/prometheus.yml

# Redémarrer Prometheus
docker-compose restart prometheus
```

---

## 🚀 Prochaines Améliorations

- [ ] Intégration CI/CD (GitHub Actions)
- [ ] Tests automatisés du pipeline
- [ ] Dashboard Grafana préconfiguré
- [ ] Alertes Slack/Email
- [ ] Support pour datasets externes (VirusTotal)
- [ ] A/B testing de modèles
- [ ] Export de métriques custom

---

## 📄 License

MIT License - Utilisation libre

---

## 👤 Auteur

**Tetyana Tarasenko**  
GitHub: [@TatianaT13](https://github.com/TatianaT13)

---

## 🙏 Contribution

Les contributions sont les bienvenues !

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing`)
5. Ouvrir une Pull Request

---

**🎉 Bon apprentissage MLOps !**
