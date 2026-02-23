"""
Tests unitaires pour NumericPreprocessor.
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from my_ml_toolkit.preprocessing.numeric_prep import NumericPreprocessor


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

class TestInit:
    def test_standard_scaler_created(self):
        prep = NumericPreprocessor("standard")
        assert isinstance(prep.scaler, StandardScaler)

    def test_minmax_scaler_created(self):
        prep = NumericPreprocessor("minmax")
        assert isinstance(prep.scaler, MinMaxScaler)

    def test_invalid_scaling_method_raises(self):
        with pytest.raises(ValueError):
            NumericPreprocessor("invalid")

    def test_label_encoders_initially_empty(self):
        prep = NumericPreprocessor()
        assert prep.label_encoders == {}

    def test_imputer_initially_none(self):
        prep = NumericPreprocessor()
        assert prep.imputer is None


# ---------------------------------------------------------------------------
# handle_missing_values
# ---------------------------------------------------------------------------

class TestHandleMissingValues:
    def test_no_nans_after_imputation(self, sample_df):
        prep = NumericPreprocessor()
        numeric_df = sample_df[["age", "income", "score"]].copy()
        result = prep.handle_missing_values(numeric_df)
        assert result.isnull().sum().sum() == 0

    def test_columns_preserved(self, sample_df):
        prep = NumericPreprocessor()
        numeric_df = sample_df[["age", "income", "score"]].copy()
        result = prep.handle_missing_values(numeric_df)
        assert list(result.columns) == list(numeric_df.columns)

    def test_returns_dataframe(self, sample_df):
        prep = NumericPreprocessor()
        numeric_df = sample_df[["age", "income", "score"]].copy()
        result = prep.handle_missing_values(numeric_df)
        assert isinstance(result, pd.DataFrame)

    def test_strategy_median(self, sample_df):
        prep = NumericPreprocessor()
        numeric_df = sample_df[["age", "income", "score"]].copy()
        result = prep.handle_missing_values(numeric_df, strategy="median")
        assert result.isnull().sum().sum() == 0

    def test_imputer_reused_on_second_call(self, sample_df):
        prep = NumericPreprocessor()
        numeric_df = sample_df[["age", "income", "score"]].copy()
        prep.handle_missing_values(numeric_df)
        imputer_first = prep.imputer
        prep.handle_missing_values(numeric_df)
        assert prep.imputer is imputer_first  # même objet


# ---------------------------------------------------------------------------
# encode_categorical
# ---------------------------------------------------------------------------

class TestEncodeCategorical:
    def test_object_columns_become_numeric(self, sample_df):
        prep = NumericPreprocessor()
        result = prep.encode_categorical(sample_df[["category"]].copy())
        assert result["category"].dtype != object

    def test_original_df_not_modified(self, sample_df):
        prep = NumericPreprocessor()
        original_dtype = sample_df["category"].dtype
        prep.encode_categorical(sample_df[["category"]].copy())
        assert sample_df["category"].dtype == original_dtype

    def test_encoder_stored(self, sample_df):
        prep = NumericPreprocessor()
        prep.encode_categorical(sample_df[["category"]].copy())
        assert "category" in prep.label_encoders

    def test_encoder_reused_on_second_call(self, sample_df):
        prep = NumericPreprocessor()
        df = sample_df[["category"]].copy()
        prep.encode_categorical(df)
        encoder_first = prep.label_encoders["category"]
        prep.encode_categorical(df)
        assert prep.label_encoders["category"] is encoder_first

    def test_auto_detection_of_object_columns(self, sample_df):
        prep = NumericPreprocessor()
        df = sample_df[["age", "category"]].copy()
        result = prep.encode_categorical(df)
        assert result["category"].dtype != object
        assert result["age"].dtype == sample_df["age"].dtype


# ---------------------------------------------------------------------------
# scale_features
# ---------------------------------------------------------------------------

class TestScaleFeatures:
    def test_standard_scaler_mean_near_zero(self, sample_df_numeric_only):
        prep = NumericPreprocessor("standard")
        result = prep.scale_features(sample_df_numeric_only, fit=True)
        means = result.mean()
        for col in means:
            assert abs(col) < 0.1

    def test_standard_scaler_std_near_one(self, sample_df_numeric_only):
        prep = NumericPreprocessor("standard")
        result = prep.scale_features(sample_df_numeric_only, fit=True)
        stds = result.std()
        for col in stds:
            assert abs(col - 1.0) < 0.1

    def test_minmax_scaler_range(self, sample_df_numeric_only):
        prep = NumericPreprocessor("minmax")
        result = prep.scale_features(sample_df_numeric_only, fit=True)
        assert result.min().min() >= 0.0
        assert result.max().max() <= 1.0

    def test_returns_dataframe(self, sample_df_numeric_only):
        prep = NumericPreprocessor()
        result = prep.scale_features(sample_df_numeric_only, fit=True)
        assert isinstance(result, pd.DataFrame)

    def test_columns_preserved(self, sample_df_numeric_only):
        prep = NumericPreprocessor()
        result = prep.scale_features(sample_df_numeric_only, fit=True)
        assert list(result.columns) == list(sample_df_numeric_only.columns)

    def test_fit_false_uses_existing_scaler(self, sample_df_numeric_only):
        prep = NumericPreprocessor("standard")
        prep.scale_features(sample_df_numeric_only, fit=True)
        # Un 2ème appel avec fit=False ne doit pas crasher
        result = prep.scale_features(sample_df_numeric_only, fit=False)
        assert isinstance(result, pd.DataFrame)


# ---------------------------------------------------------------------------
# preprocess_full
# ---------------------------------------------------------------------------

class TestPreprocessFull:
    def test_returns_tuple(self, sample_df):
        prep = NumericPreprocessor()
        numeric_df = sample_df[["age", "income", "score"]].copy()
        result = prep.preprocess_full(numeric_df)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_target_col_none_returns_none_y(self, sample_df):
        prep = NumericPreprocessor()
        numeric_df = sample_df[["age", "income", "score"]].copy()
        X, y = prep.preprocess_full(numeric_df)
        assert y is None

    def test_target_col_separates_xy(self, sample_df):
        prep = NumericPreprocessor()
        numeric_df = sample_df[["age", "income", "label"]].copy()
        X, y = prep.preprocess_full(numeric_df, target_col="label")
        assert "label" not in X.columns
        assert len(y) == len(numeric_df)

    def test_x_is_dataframe(self, sample_df):
        prep = NumericPreprocessor()
        numeric_df = sample_df[["age", "income", "score"]].copy()
        X, _ = prep.preprocess_full(numeric_df)
        assert isinstance(X, pd.DataFrame)

    def test_no_nans_in_output(self, sample_df):
        prep = NumericPreprocessor()
        numeric_df = sample_df[["age", "income", "score"]].copy()
        X, _ = prep.preprocess_full(numeric_df, handle_missing=True)
        assert X.isnull().sum().sum() == 0

    def test_categorical_encoded(self, sample_df):
        prep = NumericPreprocessor()
        df = sample_df[["age", "category"]].copy()
        X, _ = prep.preprocess_full(df, encode_cat=True)
        assert X["category"].dtype != object
