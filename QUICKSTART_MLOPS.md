# 🚀 Guide de Démarrage Rapide MLOps

## Installation en 5 minutes

### 1️⃣ Cloner et Préparer

```bash
# Cloner votre repo
git clone git@github.com:TatianaT13/ml_toolkit.git
cd ml_toolkit

# Créer les dossiers MLOps
mkdir -p docker airflow/{dags,logs,plugins} bentoml monitoring data/{malware_samples,benign_samples} models
```

### 2️⃣ Copier les Fichiers MLOps

Copiez tous les fichiers que je viens de créer dans votre projet :

```
ml_toolkit/
├── Dockerfile
├── docker-compose.yml
├── docker/
│   └── Dockerfile.airflow
├── airflow/
│   └── dags/
│       └── ml_pipeline_dag.py
├── bentoml/
│   ├── service.py
│   └── Dockerfile.bentoml
├── monitoring/
│   ├── prometheus.yml
│   └── grafana-datasources.yml
└── README_MLOPS.md
```

### 3️⃣ Lancer l'Infrastructure

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier que tout est UP
docker-compose ps

# Suivre les logs
docker-compose logs -f
```

### 4️⃣ Accéder aux Interfaces

**Airflow** : http://localhost:8080
- Login: `admin` / `admin`
- Activer le DAG `ml_malware_detection_pipeline`

**Grafana** : http://localhost:3001
- Login: `admin` / `admin`

**Prometheus** : http://localhost:9090

**BentoML API** : http://localhost:3000

---

## 📊 Tester le Pipeline

### Option 1 : Via Airflow UI

1. Ouvrir http://localhost:8080
2. Aller dans **DAGs**
3. Cliquer sur `ml_malware_detection_pipeline`
4. Cliquer sur **▶ Trigger DAG**
5. Observer l'exécution en temps réel

### Option 2 : Via CLI

```bash
docker exec airflow-webserver airflow dags trigger ml_malware_detection_pipeline
```

---

## 🧪 Tester l'API

```bash
# Créer un fichier test
echo "MZ fake executable" > test.exe

# Scanner le fichier
curl -X POST http://localhost:3000/scan_file \
  -F "file=@test.exe"
```

---

## 📈 Voir les Résultats

**Modèle entraîné** :
```bash
docker exec ml_toolkit_app ls -la /app/models/
```

**Rapport d'entraînement** :
```bash
docker exec ml_toolkit_app cat /app/models/model_metadata.json
```

**Logs du pipeline** :
```bash
docker-compose logs airflow-worker
```

---

## 🛑 Arrêter les Services

```bash
# Arrêt propre
docker-compose down

# Arrêt + suppression des volumes (⚠️ perte de données)
docker-compose down -v
```

---

## ✅ Checklist de Démarrage

- [ ] Docker et Docker Compose installés
- [ ] Projet cloné depuis GitHub
- [ ] Dossiers créés (data, models, etc.)
- [ ] `docker-compose up -d` exécuté
- [ ] Airflow accessible sur :8080
- [ ] DAG visible et activé
- [ ] Pipeline exécuté avec succès
- [ ] API BentoML testée
- [ ] Grafana accessible

---

**🎉 Félicitations ! Votre infrastructure MLOps est opérationnelle !**

Next: Consultez le README_MLOPS.md pour l'utilisation avancée.
