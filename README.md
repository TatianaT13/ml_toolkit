# 🚀 My ML Toolkit

Outil ML/DL polyvalent pour automatiser toutes les tâches de Machine Learning, du prétraitement à la prédiction.

**Supporte 3 types de données:**
- 📊 **Tabulaires** (CSV, Excel)
- 📝 **Texte** (TXT, JSON)
- 🔐 **Binaires** (Fichiers exécutables, données cybersécurité)

---

## 🎯 Fonctionnalités

✅ Chargement automatique de données  
✅ Extraction de features adaptée au type de données  
✅ Prétraitement complet (valeurs manquantes, encodage, normalisation)  
✅ Entraînement automatique de plusieurs modèles  
✅ Comparaison et sélection du meilleur modèle  
✅ Prédictions sur nouvelles données  

**Spécial Cybersécurité:**
- Extraction de features de fichiers binaires
- Analyse d'entropie (détection de chiffrement)
- Détection de signatures (PE, ELF, PDF, etc.)
- N-grams binaires
- Support pour fichiers PE (malware analysis)

---

## 📦 Installation

```bash
# Cloner ou copier le projet
cd my_ml_toolkit

# Installer les dépendances de base
pip install -r requirements.txt

# Optionnel: Pour analyse de fichiers PE (Windows)
pip install pefile
```

---

## 🚀 Utilisation Rapide

### 1️⃣ Données Tabulaires (CSV, Excel)

```python
from my_ml_toolkit import MLPipeline

# Créer le pipeline
pipeline = MLPipeline(data_type='tabular', task_type='classification')

# Exécuter tout le pipeline en une ligne !
results = pipeline.run_full_pipeline(
    filepath='data.csv',
    target_col='target',  # Colonne à prédire
    verbose=True
)

# Le meilleur modèle est automatiquement sélectionné
best_name, best_model = pipeline.trainer.get_best_model()
print(f"Meilleur modèle: {best_name}")

# Prédire sur nouvelles données
predictions = pipeline.predict_new_data('new_data.csv')
```

### 2️⃣ Données Binaires (Cybersécurité)

```python
from my_ml_toolkit.data_loader.binary import BinaryLoader
from my_ml_toolkit.feature_extraction.binary_features import BinaryFeatureExtractor

# Charger un fichier binaire
loader = BinaryLoader()
data = loader.load_file('suspicious_file.exe')

# Extraire les features
extractor = BinaryFeatureExtractor()
features = extractor.extract_all_features(data)

print(f"Entropie: {features['entropy']:.2f}")
print(f"Type de fichier détecté: {features}")

# Analyser un répertoire complet
files_data = loader.load_directory('malware_samples/', extensions=['.exe', '.dll'])
```

### 3️⃣ Données Texte

```python
from my_ml_toolkit.feature_extraction.text_features import TextFeatureExtractor

extractor = TextFeatureExtractor()

# Extraire features d'un texte
text = "Votre texte ici..."
features = extractor.extract_all_features(text)

print(f"Longueur: {features['text_length']}")
print(f"Nombre de mots: {features['word_count']}")
```

---

## 📁 Structure du Projet

```
my_ml_toolkit/
├── __init__.py              # Point d'entrée principal
├── pipeline.py              # Pipeline ML complet
│
├── data_loader/             # Chargement de données
│   ├── tabular.py          # CSV, Excel, JSON
│   └── binary.py           # Fichiers binaires
│
├── preprocessing/           # Prétraitement
│   └── numeric_prep.py     # Normalisation, encodage, etc.
│
├── feature_extraction/      # Extraction de features
│   ├── binary_features.py  # Features binaires (cyber)
│   └── text_features.py    # Features textuelles
│
├── modeling/                # Modélisation
│   └── auto_trainer.py     # Entraînement automatique
│
├── examples/                # Exemples d'utilisation
│   └── demo_binary_analysis.py
│
├── requirements.txt         # Dépendances
└── README.md               # Ce fichier
```

---

## 🔐 Cas d'Usage Cybersécurité

### Détection de Malwares

```python
from my_ml_toolkit import MLPipeline
import pandas as pd

# 1. Collecter des samples (malwares + fichiers légitimes)
# 2. Extraire les features
pipeline = MLPipeline(data_type='binary', task_type='classification')

loader = pipeline.loader
extractor = pipeline.feature_extractor

# Charger malwares
malware_files = loader.load_directory('malware_samples/', extensions=['.exe'])
malware_features = []
for filename, data in malware_files:
    features = extractor.extract_all_features(data)
    features['label'] = 1  # Malware
    malware_features.append(features)

# Charger fichiers légitimes
benign_files = loader.load_directory('benign_samples/', extensions=['.exe'])
benign_features = []
for filename, data in benign_files:
    features = extractor.extract_all_features(data)
    features['label'] = 0  # Légitime
    benign_features.append(features)

# Créer dataset
df = pd.DataFrame(malware_features + benign_features)

# Entraîner
X = df.drop(columns=['label', 'md5', 'sha256', 'filename'])
y = df['label']

X_processed, y = pipeline.preprocess(X, y)
results = pipeline.train(X_processed, y)

# Le modèle peut maintenant détecter de nouveaux malwares !
```

### Features Importantes pour Détection

| Feature | Description | Utilité |
|---------|-------------|---------|
| `entropy` | Entropie de Shannon (0-8) | Détecte chiffrement/packing |
| `high_entropy_sections` | Sections avec haute entropie | Code obfusqué |
| `signature_is_pe` | Fichier PE détecté | Type de fichier |
| `printable_ratio` | Ratio de caractères lisibles | Distingue binaire/texte |
| `null_bytes_ratio` | Ratio de bytes NULL | Padding, structure |

---

## 🧪 Tester l'Extraction de Features

```bash
# Exécuter la démo d'analyse binaire
python examples/demo_binary_analysis.py
```

Cette démo montre:
- ✅ Extraction de features de 3 types de fichiers
- ✅ Calcul d'entropie
- ✅ Détection de signatures
- ✅ Interprétation pour cybersécurité

---

## 🎓 Prochaines Améliorations

**À venir:**
- [ ] Support pour images (CNN)
- [ ] Deep Learning (LSTM pour séquences)
- [ ] Hyperparameter tuning automatique
- [ ] Explainability (SHAP, LIME)
- [ ] API REST pour déploiement
- [ ] Dashboard de monitoring
- [ ] Support pour séries temporelles

---

## 📚 Ressources

**Cybersécurité & Malware Analysis:**
- [VirusTotal](https://www.virustotal.com) - Dataset de malwares
- [MalwareBazaar](https://bazaar.abuse.ch) - Échantillons de malwares
- [pefile documentation](https://github.com/erocarrera/pefile) - Analyse de PE files

**Machine Learning:**
- [Scikit-learn](https://scikit-learn.org)
- [Pandas](https://pandas.pydata.org)

---

## 📝 License

MIT License - Utilisez librement !

---

## 👤 Auteur

Créé pour automatiser les tâches répétitives de ML et faciliter l'analyse de données en cybersécurité.

**Questions? Suggestions?** N'hésitez pas à contribuer !
