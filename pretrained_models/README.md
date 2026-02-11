# Pre-trained Malware Detection Models

## 📦 Quick Start
```python
import pickle

# Load the pre-trained model
with open('malware_detector_v1.pkl', 'rb') as f:
    pipeline = pickle.load(f)

# Predict on new data
predictions = pipeline.predict_new_data('your_data.csv')
```

## 📊 Performance

Trained on 10,000 samples (5,000 malware + 5,000 benign)

| Model | Accuracy | Precision | Recall | F1 |
|-------|----------|-----------|--------|-----|
| RandomForest | 100.0% | 100.0% | 100.0% | 0.0% |
| LogisticRegression | 100.0% | 100.0% | 100.0% | 0.0% |
| GradientBoosting | 100.0% | 100.0% | 100.0% | 0.0% |
| KNN | 100.0% | 100.0% | 100.0% | 0.0% |
| SVM | 100.0% | 100.0% | 100.0% | 0.0% |

**Best Model:** RandomForest (100.0% accuracy)

## 🎯 Features Expected

The model expects CSV with these columns:
- `file_size`: Size in bytes
- `entropy`: Shannon entropy (0-8)
- `num_sections`: Number of PE sections
- `num_imports`: Number of imported functions
- `num_exports`: Number of exported functions
- `has_debug_info`: 0 or 1
- `is_packed`: 0 or 1
- `num_suspicious_strings`: Count
- `code_section_entropy`: Entropy of .text
- `data_section_entropy`: Entropy of .data

## 📥 Download
```bash
# Clone repo
git clone https://github.com/TatianaT13/ml_toolkit.git
cd ml_toolkit/pretrained_models

# Use model
python -c "import pickle; model = pickle.load(open('malware_detector_v1.pkl', 'rb'))"
```

## 📝 License

MIT - Free for commercial and non-commercial use
