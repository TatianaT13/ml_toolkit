"""
Fixtures partagées pour tous les tests.
"""

import os
import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Données binaires
# ---------------------------------------------------------------------------

@pytest.fixture
def binary_malware():
    """Bytes aléatoires → haute entropie (~7.9), typique malware."""
    rng = np.random.default_rng(42)
    return bytes(rng.integers(0, 256, size=1024, dtype=np.uint8).tolist())


@pytest.fixture
def binary_benign():
    """Fichier PE synthétique → basse entropie, typique bénin."""
    return b"MZ" + b"\x00" * 200 + b"Hello World! This is a benign file. " * 20


@pytest.fixture
def binary_elf():
    """Faux en-tête ELF."""
    return b"\x7fELF" + b"\x01\x02\x03" + b"\x00" * 100


# ---------------------------------------------------------------------------
# DataFrames tabulaires
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_df():
    """DataFrame avec colonnes numériques, catégorielles et valeurs manquantes."""
    rng = np.random.default_rng(0)
    n = 50
    return pd.DataFrame({
        "age":      rng.integers(18, 70, size=n).astype(float),
        "income":   rng.normal(50000, 15000, size=n),
        "score":    np.where(rng.random(n) < 0.1, np.nan, rng.random(n)),  # 10 % NaN
        "category": rng.choice(["A", "B", "C"], size=n),
        "label":    rng.integers(0, 2, size=n),
    })


@pytest.fixture
def sample_df_numeric_only():
    """DataFrame purement numérique, sans NaN."""
    rng = np.random.default_rng(1)
    n = 40
    return pd.DataFrame({
        "f1": rng.normal(0, 1, size=n),
        "f2": rng.normal(5, 2, size=n),
        "f3": rng.uniform(0, 10, size=n),
    })


# ---------------------------------------------------------------------------
# Textes
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_texts():
    return [
        "This is a simple test sentence with some words.",
        "Machine learning is a fascinating field of study.",
        "Binary malware detection uses statistical features.",
    ]


@pytest.fixture
def repeated_text():
    return "word " * 10  # Tous les mots identiques → lexical_diversity == 1/10


# ---------------------------------------------------------------------------
# Fichiers temporaires
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_csv(tmp_path):
    """Fichier CSV temporaire avec 20 lignes."""
    rng = np.random.default_rng(2)
    df = pd.DataFrame({
        "x1":     rng.normal(0, 1, 20),
        "x2":     rng.normal(1, 0.5, 20),
        "target": rng.integers(0, 2, 20),
    })
    path = tmp_path / "sample.csv"
    df.to_csv(path, index=False)
    return str(path)


@pytest.fixture
def tmp_csv_no_target(tmp_path):
    """Fichier CSV temporaire sans colonne cible (pour la prédiction)."""
    rng = np.random.default_rng(2)
    df = pd.DataFrame({
        "x1": rng.normal(0, 1, 20),
        "x2": rng.normal(1, 0.5, 20),
    })
    path = tmp_path / "predict.csv"
    df.to_csv(path, index=False)
    return str(path)


@pytest.fixture
def tmp_csv_semicolon(tmp_path):
    """CSV avec séparateur point-virgule."""
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    path = tmp_path / "semicolon.csv"
    df.to_csv(path, sep=";", index=False)
    return str(path)


@pytest.fixture
def tmp_binary_file(tmp_path, binary_benign):
    """Fichier binaire temporaire."""
    path = tmp_path / "sample.bin"
    path.write_bytes(binary_benign)
    return str(path)


@pytest.fixture
def tmp_binary_dir(tmp_path, binary_malware, binary_benign):
    """Répertoire avec plusieurs fichiers binaires."""
    (tmp_path / "mal1.bin").write_bytes(binary_malware)
    (tmp_path / "mal2.bin").write_bytes(binary_malware[:512])
    (tmp_path / "ben1.exe").write_bytes(binary_benign)
    (tmp_path / "readme.txt").write_bytes(b"not a binary")
    return str(tmp_path)


# ---------------------------------------------------------------------------
# Dataset sklearn pour AutoTrainer
# ---------------------------------------------------------------------------

@pytest.fixture
def classification_dataset():
    from sklearn.datasets import make_classification
    X, y = make_classification(
        n_samples=200, n_features=10, n_informative=5,
        random_state=42
    )
    return pd.DataFrame(X, columns=[f"f{i}" for i in range(10)]), pd.Series(y)


@pytest.fixture
def regression_dataset():
    from sklearn.datasets import make_regression
    X, y = make_regression(
        n_samples=200, n_features=10, noise=0.1,
        random_state=42
    )
    return pd.DataFrame(X, columns=[f"f{i}" for i in range(10)]), pd.Series(y)
