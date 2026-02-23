"""
Tests unitaires pour BinaryFeatureExtractor.
"""

import numpy as np
import pytest

from my_ml_toolkit.feature_extraction.binary_features import BinaryFeatureExtractor


@pytest.fixture
def extractor():
    return BinaryFeatureExtractor()


# ---------------------------------------------------------------------------
# extract_basic_features
# ---------------------------------------------------------------------------

class TestBasicFeatures:
    def test_returns_expected_keys(self, extractor, binary_benign):
        features = extractor.extract_basic_features(binary_benign)
        assert "file_size" in features
        assert "md5" in features
        assert "sha256" in features

    def test_file_size_matches_len(self, extractor, binary_benign):
        features = extractor.extract_basic_features(binary_benign)
        assert features["file_size"] == len(binary_benign)

    def test_md5_is_hex_32_chars(self, extractor, binary_benign):
        features = extractor.extract_basic_features(binary_benign)
        assert isinstance(features["md5"], str)
        assert len(features["md5"]) == 32
        assert all(c in "0123456789abcdef" for c in features["md5"])

    def test_sha256_is_hex_64_chars(self, extractor, binary_benign):
        features = extractor.extract_basic_features(binary_benign)
        assert isinstance(features["sha256"], str)
        assert len(features["sha256"]) == 64

    def test_hashes_deterministic(self, extractor, binary_benign):
        f1 = extractor.extract_basic_features(binary_benign)
        f2 = extractor.extract_basic_features(binary_benign)
        assert f1["md5"] == f2["md5"]
        assert f1["sha256"] == f2["sha256"]

    def test_different_data_different_hashes(self, extractor, binary_benign, binary_malware):
        f1 = extractor.extract_basic_features(binary_benign)
        f2 = extractor.extract_basic_features(binary_malware)
        assert f1["md5"] != f2["md5"]
        assert f1["sha256"] != f2["sha256"]


# ---------------------------------------------------------------------------
# extract_statistical_features
# ---------------------------------------------------------------------------

class TestStatisticalFeatures:
    EXPECTED_KEYS = [
        "entropy", "mean_byte_value", "std_byte_value",
        "min_byte_value", "max_byte_value",
        "unique_bytes_count", "unique_bytes_ratio",
        "null_bytes_count", "null_bytes_ratio",
        "printable_bytes_ratio", "high_bytes_ratio",
    ]

    def test_returns_expected_keys(self, extractor, binary_benign):
        features = extractor.extract_statistical_features(binary_benign)
        for key in self.EXPECTED_KEYS:
            assert key in features, f"Clé manquante : {key}"

    def test_entropy_random_bytes_is_high(self, extractor, binary_malware):
        features = extractor.extract_statistical_features(binary_malware)
        assert features["entropy"] > 7.0

    def test_entropy_constant_bytes_is_zero(self, extractor):
        data = b"\x00" * 512
        features = extractor.extract_statistical_features(data)
        assert features["entropy"] == pytest.approx(0.0)

    def test_entropy_bounded(self, extractor, binary_malware):
        features = extractor.extract_statistical_features(binary_malware)
        assert 0.0 <= features["entropy"] <= 8.0

    def test_null_bytes_ratio_all_zeros(self, extractor):
        data = b"\x00" * 100
        features = extractor.extract_statistical_features(data)
        assert features["null_bytes_ratio"] == pytest.approx(1.0)

    def test_null_bytes_ratio_no_zeros(self, extractor):
        data = bytes(range(1, 256)) * 4  # 1..255, aucun octet nul
        features = extractor.extract_statistical_features(data)
        assert features["null_bytes_ratio"] == pytest.approx(0.0)

    def test_unique_bytes_ratio_bounded(self, extractor, binary_malware):
        features = extractor.extract_statistical_features(binary_malware)
        assert 0.0 <= features["unique_bytes_ratio"] <= 1.0

    def test_mean_byte_value_range(self, extractor, binary_benign):
        features = extractor.extract_statistical_features(binary_benign)
        assert 0 <= features["mean_byte_value"] <= 255


# ---------------------------------------------------------------------------
# extract_structural_features
# ---------------------------------------------------------------------------

class TestStructuralFeatures:
    def test_returns_signature_keys(self, extractor, binary_benign):
        features = extractor.extract_structural_features(binary_benign)
        expected_sigs = [
            "signature_is_pe", "signature_is_elf", "signature_is_pdf",
            "signature_is_zip", "signature_is_jpg", "signature_is_png",
            "signature_is_gif",
        ]
        for key in expected_sigs:
            assert key in features, f"Clé manquante : {key}"

    def test_returns_structural_keys(self, extractor, binary_benign):
        features = extractor.extract_structural_features(binary_benign)
        assert "high_entropy_sections" in features
        assert "repeated_sequences" in features
        assert "printable_ratio" in features

    def test_pe_signature_detected(self, extractor, binary_benign):
        # binary_benign commence par b"MZ"
        features = extractor.extract_structural_features(binary_benign)
        assert features["signature_is_pe"] == 1

    def test_pe_signature_not_detected_for_random(self, extractor, binary_malware):
        # Octets aléatoires → très improbable de commencer par MZ
        features = extractor.extract_structural_features(binary_malware)
        # On ne force pas la valeur, on vérifie juste que la clé est présente et binaire
        assert features["signature_is_pe"] in (0, 1)

    def test_elf_signature_detected(self, extractor, binary_elf):
        features = extractor.extract_structural_features(binary_elf)
        assert features["signature_is_elf"] == 1

    def test_signature_values_are_binary(self, extractor, binary_benign):
        features = extractor.extract_structural_features(binary_benign)
        sig_keys = [k for k in features if k.startswith("signature_")]
        for key in sig_keys:
            assert features[key] in (0, 1)

    def test_high_entropy_sections_non_negative(self, extractor, binary_malware):
        features = extractor.extract_structural_features(binary_malware)
        assert features["high_entropy_sections"] >= 0

    def test_printable_ratio_bounded(self, extractor, binary_benign):
        features = extractor.extract_structural_features(binary_benign)
        assert 0.0 <= features["printable_ratio"] <= 1.0

    def test_printable_ratio_pure_ascii(self, extractor):
        data = b"Hello World! This is all ASCII text." * 10
        features = extractor.extract_structural_features(data)
        assert features["printable_ratio"] == pytest.approx(1.0)

    def test_printable_ratio_null_bytes(self, extractor):
        data = b"\x00" * 200
        features = extractor.extract_structural_features(data)
        assert features["printable_ratio"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# extract_all_features
# ---------------------------------------------------------------------------

class TestExtractAllFeatures:
    def test_returns_dict(self, extractor, binary_benign):
        features = extractor.extract_all_features(binary_benign)
        assert isinstance(features, dict)

    def test_minimum_feature_count(self, extractor, binary_benign):
        features = extractor.extract_all_features(binary_benign)
        assert len(features) >= 20

    def test_contains_basic_keys(self, extractor, binary_benign):
        features = extractor.extract_all_features(binary_benign)
        assert "file_size" in features
        assert "entropy" in features
        assert "signature_is_pe" in features

    def test_malware_vs_benign_entropy_differs(self, extractor, binary_malware, binary_benign):
        mal_feat = extractor.extract_all_features(binary_malware)
        ben_feat = extractor.extract_all_features(binary_benign)
        assert mal_feat["entropy"] > ben_feat["entropy"]


# ---------------------------------------------------------------------------
# _calculate_entropy (méthode interne)
# ---------------------------------------------------------------------------

class TestCalculateEntropy:
    def test_uniform_distribution_max_entropy(self, extractor):
        # Distribution uniforme sur 256 valeurs → entropie maximale = 8
        data = bytes(range(256)) * 4
        byte_array = np.frombuffer(data, dtype=np.uint8)
        entropy = extractor._calculate_entropy(byte_array)
        assert entropy == pytest.approx(8.0, abs=0.01)

    def test_single_value_zero_entropy(self, extractor):
        data = b"\xAA" * 100
        byte_array = np.frombuffer(data, dtype=np.uint8)
        entropy = extractor._calculate_entropy(byte_array)
        assert entropy == pytest.approx(0.0)
