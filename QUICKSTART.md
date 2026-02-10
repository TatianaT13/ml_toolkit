# 🚀 Guide de Démarrage Rapide

## Installation en 2 minutes

```bash
# 1. Installer les dépendances
pip install numpy pandas scikit-learn scipy

# 2. Optionnel: Pour analyse de fichiers PE
pip install pefile
```

## Utilisation Simple

### 🎯 En Une Ligne !

```python
from my_ml_toolkit import MLPipeline

# Créer + Entraîner + Évaluer
pipeline = MLPipeline(data_type='tabular', task_type='classification')
results = pipeline.run_full_pipeline('data.csv', target_col='target')
```

C'est tout ! Le meilleur modèle est automatiquement sélectionné.

---

## 📊 Exemples par Type de Données

### 1️⃣ CSV / Excel (Données Tabulaires)

```python
from my_ml_toolkit import MLPipeline

# Classification
pipeline = MLPipeline(data_type='tabular', task_type='classification')
results = pipeline.run_full_pipeline('customers.csv', target_col='will_buy')

# Régression
pipeline = MLPipeline(data_type='tabular', task_type='regression')
results = pipeline.run_full_pipeline('houses.csv', target_col='price')

# Prédire sur nouvelles données
predictions = pipeline.predict_new_data('new_customers.csv')
```

### 2️⃣ Fichiers Binaires (Cybersécurité)

```python
from my_ml_toolkit.data_loader.binary import BinaryLoader
from my_ml_toolkit.feature_extraction.binary_features import BinaryFeatureExtractor

# Analyser UN fichier
loader = BinaryLoader()
data = loader.load_file('suspicious.exe')

extractor = BinaryFeatureExtractor()
features = extractor.extract_all_features(data)

print(f"Entropie: {features['entropy']:.2f}")
print(f"Type: {'PE' if features['signature_is_pe'] else 'Inconnu'}")

# Analyser UN DOSSIER complet
files = loader.load_directory('malware_samples/', extensions=['.exe', '.dll'])
```

### 3️⃣ Texte

```python
from my_ml_toolkit.feature_extraction.text_features import TextFeatureExtractor

extractor = TextFeatureExtractor()

text = "Votre texte ici..."
features = extractor.extract_all_features(text)

print(features)
```

---

## 🔥 Features Principales

| Feature | Description |
|---------|-------------|
| ✅ **Automatique** | Teste plusieurs modèles automatiquement |
| ✅ **Polyvalent** | Tabulaire, texte, binaire |
| ✅ **Prétraitement** | Gère valeurs manquantes, encodage, normalisation |
| ✅ **Comparaison** | Compare les modèles et sélectionne le meilleur |
| ✅ **Cyber** | Features spécifiques pour détection de malwares |

---

## 🎓 Prochaines Étapes

1. **Testez avec vos données** : Remplacez `'data.csv'` par votre fichier
2. **Ajustez les paramètres** : Modifiez `task_type`, `test_size`, etc.
3. **Explorez les résultats** : Utilisez `pipeline.trainer.get_results_dataframe()`
4. **Déployez** : Sauvegardez votre modèle avec `pickle` ou `joblib`

---

## 📚 Documentation Complète

Consultez le [README.md](README.md) pour:
- Structure complète du projet
- Détails sur chaque module
- Cas d'usage avancés
- Exemples de code

---

## 🆘 Besoin d'Aide ?

```bash
# Exécuter les exemples complets
python examples/complete_examples.py

# Démo analyse binaire (cyber)
python examples/demo_binary_analysis.py
```

---

**💡 Astuce:** Le toolkit choisit automatiquement les bons prétraitements selon le type de données. Vous n'avez qu'à spécifier `data_type` !
