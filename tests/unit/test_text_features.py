"""
Tests unitaires pour TextFeatureExtractor.
"""

import numpy as np
import pytest

from my_ml_toolkit.feature_extraction.text_features import TextFeatureExtractor


@pytest.fixture
def extractor():
    return TextFeatureExtractor(max_features=50)


SIMPLE_TEXT = "Hello world this is a test sentence with ten words here"


# ---------------------------------------------------------------------------
# extract_basic_features
# ---------------------------------------------------------------------------

class TestBasicFeatures:
    EXPECTED_KEYS = [
        "text_length", "word_count", "char_count",
        "avg_word_length", "sentence_count",
        "uppercase_ratio", "digit_ratio", "special_char_ratio",
    ]

    def test_returns_expected_keys(self, extractor):
        features = extractor.extract_basic_features(SIMPLE_TEXT)
        for key in self.EXPECTED_KEYS:
            assert key in features, f"Clé manquante : {key}"

    def test_text_length_equals_len(self, extractor):
        features = extractor.extract_basic_features(SIMPLE_TEXT)
        assert features["text_length"] == len(SIMPLE_TEXT)

    def test_char_count_equals_len(self, extractor):
        features = extractor.extract_basic_features(SIMPLE_TEXT)
        assert features["char_count"] == len(SIMPLE_TEXT)

    def test_word_count_correct(self, extractor):
        text = "one two three four five"
        features = extractor.extract_basic_features(text)
        assert features["word_count"] == 5

    def test_uppercase_ratio_all_upper(self, extractor):
        text = "ABC DEF GHI"
        features = extractor.extract_basic_features(text)
        # 9 uppercase sur 11 chars (2 espaces) → 9/11
        assert features["uppercase_ratio"] == pytest.approx(9 / 11)

    def test_uppercase_ratio_all_lower(self, extractor):
        text = "abc def ghi"
        features = extractor.extract_basic_features(text)
        assert features["uppercase_ratio"] == pytest.approx(0.0)

    def test_digit_ratio(self, extractor):
        text = "abc123"  # 3 chiffres sur 6 chars
        features = extractor.extract_basic_features(text)
        assert features["digit_ratio"] == pytest.approx(3 / 6)

    def test_special_char_ratio(self, extractor):
        text = "hello!!"  # 2 spéciaux sur 7
        features = extractor.extract_basic_features(text)
        assert features["special_char_ratio"] == pytest.approx(2 / 7)

    def test_avg_word_length_correct(self, extractor):
        text = "hi hello"  # (2+5)/2 = 3.5
        features = extractor.extract_basic_features(text)
        assert features["avg_word_length"] == pytest.approx(3.5)

    def test_empty_text_no_crash(self, extractor):
        features = extractor.extract_basic_features("")
        assert features["word_count"] == 0
        assert features["uppercase_ratio"] == pytest.approx(0.0)
        assert features["digit_ratio"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# extract_statistical_features
# ---------------------------------------------------------------------------

class TestStatisticalFeatures:
    EXPECTED_KEYS = [
        "unique_words", "lexical_diversity",
        "max_word_length", "min_word_length", "std_word_length",
    ]

    def test_returns_expected_keys(self, extractor):
        features = extractor.extract_statistical_features(SIMPLE_TEXT)
        for key in self.EXPECTED_KEYS:
            assert key in features, f"Clé manquante : {key}"

    def test_lexical_diversity_all_unique(self, extractor):
        text = "one two three four five six"
        features = extractor.extract_statistical_features(text)
        assert features["lexical_diversity"] == pytest.approx(1.0)

    def test_lexical_diversity_with_repeats(self, extractor, repeated_text):
        # "word word word ... word" → unique=1, total=10 → diversity=0.1
        features = extractor.extract_statistical_features(repeated_text.strip())
        assert features["lexical_diversity"] < 1.0
        assert features["unique_words"] == 1

    def test_max_min_word_length(self, extractor):
        text = "a bb ccc dddd"
        features = extractor.extract_statistical_features(text)
        assert features["min_word_length"] == 1
        assert features["max_word_length"] == 4

    def test_std_word_length_uniform(self, extractor):
        # Tous les mots de même longueur → std = 0
        text = "abc def ghi jkl"
        features = extractor.extract_statistical_features(text)
        assert features["std_word_length"] == pytest.approx(0.0)

    def test_empty_text_returns_empty_dict(self, extractor):
        features = extractor.extract_statistical_features("")
        assert features == {}


# ---------------------------------------------------------------------------
# extract_all_features
# ---------------------------------------------------------------------------

class TestExtractAllFeatures:
    def test_returns_dict(self, extractor):
        features = extractor.extract_all_features(SIMPLE_TEXT)
        assert isinstance(features, dict)

    def test_contains_basic_and_statistical_keys(self, extractor):
        features = extractor.extract_all_features(SIMPLE_TEXT)
        assert "text_length" in features
        assert "word_count" in features
        assert "unique_words" in features
        assert "lexical_diversity" in features

    def test_minimum_feature_count(self, extractor):
        features = extractor.extract_all_features(SIMPLE_TEXT)
        assert len(features) >= 10


# ---------------------------------------------------------------------------
# TF-IDF vectorizer
# ---------------------------------------------------------------------------

class TestTfIdf:
    def test_fit_transform_shape(self, extractor, sample_texts):
        extractor.fit_tfidf(sample_texts)
        result = extractor.transform_tfidf(sample_texts)
        assert result.shape[0] == len(sample_texts)
        assert result.shape[1] <= extractor.max_features

    def test_transform_without_fit_raises(self, extractor, sample_texts):
        fresh = TextFeatureExtractor()
        with pytest.raises(ValueError):
            fresh.transform_tfidf(sample_texts)

    def test_tfidf_values_non_negative(self, extractor, sample_texts):
        extractor.fit_tfidf(sample_texts)
        result = extractor.transform_tfidf(sample_texts)
        assert np.all(result >= 0)

    def test_fit_then_transform_single_text(self, extractor, sample_texts):
        extractor.fit_tfidf(sample_texts)
        result = extractor.transform_tfidf([sample_texts[0]])
        assert result.shape[0] == 1
