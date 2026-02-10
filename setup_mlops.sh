#!/bin/bash

# Script de setup automatique pour ML Toolkit MLOps
# Usage: ./setup_mlops.sh

set -e

echo "════════════════════════════════════════════════════════"
echo "🚀 ML Toolkit MLOps - Setup Automatique"
echo "════════════════════════════════════════════════════════"
echo ""

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    echo "   Installez Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé"
    echo "   Installez Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker et Docker Compose sont installés"
echo ""

# Créer la structure de dossiers
echo "📁 Création de la structure de dossiers..."
mkdir -p docker
mkdir -p airflow/{dags,logs,plugins}
mkdir -p bentoml
mkdir -p monitoring
mkdir -p data/{malware_samples,benign_samples}
mkdir -p models
mkdir -p .dvc

echo "✅ Dossiers créés"
echo ""

# Vérifier les fichiers nécessaires
echo "📄 Vérification des fichiers..."

required_files=(
    "Dockerfile"
    "docker-compose.yml"
    "docker/Dockerfile.airflow"
    "airflow/dags/ml_pipeline_dag.py"
    "bentoml/service.py"
    "bentoml/Dockerfile.bentoml"
    "monitoring/prometheus.yml"
    "monitoring/grafana-datasources.yml"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Fichiers manquants:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    echo ""
    echo "💡 Copiez tous les fichiers MLOps dans le projet"
    exit 1
fi

echo "✅ Tous les fichiers nécessaires sont présents"
echo ""

# Créer .env si nécessaire
if [ ! -f .env ]; then
    echo "📝 Création du fichier .env..."
    cat > .env << EOF
# Configuration MLOps
AIRFLOW_UID=$(id -u)
AIRFLOW_GID=0

# Airflow
AIRFLOW__CORE__EXECUTOR=CeleryExecutor
AIRFLOW__CORE__FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || echo "")

# PostgreSQL
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow

# BentoML
MODEL_PATH=/app/models/malware_detector.pkl
EOF
    echo "✅ Fichier .env créé"
else
    echo "✅ Fichier .env existe déjà"
fi
echo ""

# Copier le code source
if [ -d "my_ml_toolkit" ]; then
    echo "✅ Code source my_ml_toolkit trouvé"
else
    echo "⚠️  Dossier my_ml_toolkit non trouvé"
    echo "   Assurez-vous que le code ML est dans ./my_ml_toolkit/"
fi
echo ""

# Construire les images Docker
echo "🐳 Construction des images Docker..."
echo "   (Ceci peut prendre 5-10 minutes la première fois)"
echo ""

docker-compose build

echo ""
echo "✅ Images Docker construites avec succès"
echo ""

# Démarrer les services
echo "🚀 Démarrage des services..."
echo ""

docker-compose up -d

echo ""
echo "✅ Services démarrés"
echo ""

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage complet (30 secondes)..."
sleep 30

# Vérifier l'état des services
echo ""
echo "📊 État des services:"
echo ""
docker-compose ps

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ Setup terminé avec succès !"
echo "════════════════════════════════════════════════════════"
echo ""
echo "🌐 Accès aux interfaces:"
echo ""
echo "   Airflow:     http://localhost:8080"
echo "                Login: admin / admin"
echo ""
echo "   Grafana:     http://localhost:3001"
echo "                Login: admin / admin"
echo ""
echo "   Prometheus:  http://localhost:9090"
echo ""
echo "   BentoML API: http://localhost:3000"
echo ""
echo "════════════════════════════════════════════════════════"
echo ""
echo "📚 Prochaines étapes:"
echo ""
echo "   1. Ouvrir Airflow: http://localhost:8080"
echo "   2. Activer le DAG: ml_malware_detection_pipeline"
echo "   3. Trigger le pipeline manuellement"
echo "   4. Consulter README_MLOPS.md pour plus d'infos"
echo ""
echo "🛑 Pour arrêter: docker-compose down"
echo ""
