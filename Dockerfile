FROM python:3.10-slim

LABEL maintainer="TatianaT13"
LABEL description="ML Toolkit pour détection de malwares"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Installer le package en mode développement
RUN pip install -e .

# Créer les dossiers nécessaires
RUN mkdir -p /app/data/malware_samples /app/data/benign_samples /app/models

EXPOSE 3000

CMD ["python", "examples/complete_examples_fixed.py"]
