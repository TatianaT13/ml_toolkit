"""
Tests d'intégration pour MLPipeline (pipeline end-to-end).
"""

import numpy as np
import pandas as pd
import pytest

from my_ml_toolkit.pipeline import MLPipeline
from my_ml_toolkit.data_loader.tabular import TabularLoader
from my_ml_toolkit.data_loader.binary import BinaryLoader
from my_ml_toolkit.preprocessing.numeric_prep import NumericPreprocessor
from my_ml_toolkit.feature_extraction.binary_features import BinaryFeatureExtractor
from my_ml_toolkit.feature_extraction.text_features import TextFeatureExtractor


# ---------------------------------------------------------------------------
# Initialisation des composants
# ---------------------------------------------------------------------------

class TestPipelineInit:
    def test_tabular_pipeline_loader(self):
        pipeline = MLPipeline(data_type="tabular")
        assert isinstance(pipeline.loader, TabularLoader)

    def test_tabular_pipeline_preprocessor(self):
        pipeline = MLPipeline(data_type="tabular")
        assert isinstance(pipeline.preprocessor, NumericPreprocessor)

    def test_binary_pipeline_loader(self):
        pipeline = MLPipeline(data_type="binary")
        assert isinstance(pipeline.loader, BinaryLoader)

    def test_binary_pipeline_feature_extractor(self):
        pipeline = MLPipeline(data_type="binary")
        assert isinstance(pipeline.feature_extractor, BinaryFeatureExtractor)

    def test_text_pipeline_feature_extractor(self):
        pipeline = MLPipeline(data_type="text")
        assert isinstance(pipeline.feature_extractor, TextFeatureExtractor)

    def test_trainer_always_created(self):
        for dt in ["tabular", "binary", "text"]:
            pipeline = MLPipeline(data_type=dt)
            assert pipeline.trainer is not None

    def test_task_type_stored(self):
        pipeline = MLPipeline(data_type="tabular", task_type="regression")
        assert pipeline.task_type == "regression"


# ---------------------------------------------------------------------------
# extract_features
# ---------------------------------------------------------------------------

class TestExtractFeatures:
    def test_tabular_returns_df_unchanged(self):
        pipeline = MLPipeline(data_type="tabular")
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        result = pipeline.extract_features(df)
        pd.testing.assert_frame_equal(result, df)

    def test_binary_single_returns_one_row(self, binary_benign):
        pipeline = MLPipeline(data_type="binary")
        result = pipeline.extract_features(binary_benign)
        assert isinstance(result, pd.DataFrame)
        assert result.shape[0] == 1

    def test_binary_single_has_expected_columns(self, binary_benign):
        pipeline = MLPipeline(data_type="binary")
        result = pipeline.extract_features(binary_benign)
        assert "file_size" in result.columns
        assert "entropy" in result.columns

    def test_binary_list_returns_multiple_rows(self, binary_malware, binary_benign):
        pipeline = MLPipeline(data_type="binary")
        data = [("mal.bin", binary_malware), ("ben.exe", binary_benign)]
        result = pipeline.extract_features(data)
        assert result.shape[0] == 2
        assert "filename" in result.columns

    def test_text_single_returns_one_row(self):
        pipeline = MLPipeline(data_type="text")
        result = pipeline.extract_features("This is a test sentence.")
        assert isinstance(result, pd.DataFrame)
        assert result.shape[0] == 1

    def test_text_list_returns_multiple_rows(self, sample_texts):
        pipeline = MLPipeline(data_type="text")
        result = pipeline.extract_features(sample_texts)
        assert result.shape[0] == len(sample_texts)

    def test_text_features_has_word_count(self):
        pipeline = MLPipeline(data_type="text")
        result = pipeline.extract_features("Hello world test")
        assert "word_count" in result.columns


# ---------------------------------------------------------------------------
# load_data
# ---------------------------------------------------------------------------

class TestLoadData:
    def test_load_csv(self, tmp_csv):
        pipeline = MLPipeline(data_type="tabular")
        df = pipeline.load_data(tmp_csv)
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] == 20

    def test_load_unsupported_format_raises(self, tmp_path):
        pipeline = MLPipeline(data_type="tabular")
        p = tmp_path / "file.json"
        p.write_text("{}")
        with pytest.raises(ValueError):
            pipeline.load_data(str(p))

    def test_load_binary_file(self, tmp_binary_file):
        pipeline = MLPipeline(data_type="binary")
        data = pipeline.load_data(tmp_binary_file)
        assert isinstance(data, bytes)


# ---------------------------------------------------------------------------
# run_full_pipeline
# ---------------------------------------------------------------------------

class TestRunFullPipeline:
    def test_returns_dict_with_target(self, tmp_csv):
        pipeline = MLPipeline(data_type="tabular", task_type="classification")
        results = pipeline.run_full_pipeline(tmp_csv, target_col="target", verbose=False)
        assert isinstance(results, dict)

    def test_results_contain_model_names(self, tmp_csv):
        pipeline = MLPipeline(data_type="tabular", task_type="classification")
        results = pipeline.run_full_pipeline(tmp_csv, target_col="target", verbose=False)
        assert len(results) > 0

    def test_returns_none_without_target(self, tmp_csv):
        pipeline = MLPipeline(data_type="tabular", task_type="classification")
        result = pipeline.run_full_pipeline(tmp_csv, target_col=None, verbose=False)
        assert result is None

    def test_best_model_set_after_pipeline(self, tmp_csv):
        pipeline = MLPipeline(data_type="tabular", task_type="classification")
        pipeline.run_full_pipeline(tmp_csv, target_col="target", verbose=False)
        assert pipeline.trainer.best_model is not None


# ---------------------------------------------------------------------------
# predict_new_data
# ---------------------------------------------------------------------------

class TestPredictNewData:
    def test_predict_returns_array(self, tmp_csv, tmp_csv_no_target):
        pipeline = MLPipeline(data_type="tabular", task_type="classification")
        pipeline.run_full_pipeline(tmp_csv, target_col="target", verbose=False)
        predictions = pipeline.predict_new_data(tmp_csv_no_target)
        assert isinstance(predictions, np.ndarray)

    def test_predict_correct_length(self, tmp_csv, tmp_csv_no_target):
        pipeline = MLPipeline(data_type="tabular", task_type="classification")
        pipeline.run_full_pipeline(tmp_csv, target_col="target", verbose=False)
        predictions = pipeline.predict_new_data(tmp_csv_no_target)
        assert len(predictions) == 20  # taille du CSV de test


# ---------------------------------------------------------------------------
# Pipeline binaire end-to-end (sans entraînement complet)
# ---------------------------------------------------------------------------

class TestBinaryPipelineExtraction:
    def test_malware_vs_benign_entropy_feature(self, binary_malware, binary_benign):
        pipeline = MLPipeline(data_type="binary")
        df_mal = pipeline.extract_features(binary_malware)
        df_ben = pipeline.extract_features(binary_benign)
        assert df_mal["entropy"].iloc[0] > df_ben["entropy"].iloc[0]

    def test_preprocess_binary_features(self, binary_malware, binary_benign):
        pipeline = MLPipeline(data_type="binary")
        data = [("mal.bin", binary_malware), ("ben.exe", binary_benign)]
        df = pipeline.extract_features(data)
        X, y = pipeline.preprocess(df)
        assert isinstance(X, pd.DataFrame)
        assert X.isnull().sum().sum() == 0
