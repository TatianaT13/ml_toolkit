"""
Tests unitaires pour AutoTrainer.
"""

import io
import sys

import numpy as np
import pandas as pd
import pytest

from my_ml_toolkit.modeling.auto_trainer import AutoTrainer


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

class TestInit:
    def test_classification_initializes_5_models(self):
        trainer = AutoTrainer("classification")
        assert len(trainer.models) == 5

    def test_regression_initializes_3_models(self):
        trainer = AutoTrainer("regression")
        assert len(trainer.models) == 3

    def test_invalid_task_type_raises(self):
        with pytest.raises(ValueError):
            AutoTrainer("clustering")

    def test_best_model_initially_none(self):
        trainer = AutoTrainer("classification")
        assert trainer.best_model is None

    def test_best_score_initially_none(self):
        trainer = AutoTrainer("classification")
        assert trainer.best_score is None

    def test_results_initially_empty(self):
        trainer = AutoTrainer("classification")
        assert trainer.results == {}

    def test_classification_model_names(self):
        trainer = AutoTrainer("classification")
        expected = {"RandomForest", "LogisticRegression", "GradientBoosting", "KNN", "SVM"}
        assert set(trainer.models.keys()) == expected

    def test_regression_model_names(self):
        trainer = AutoTrainer("regression")
        expected = {"RandomForest", "LinearRegression", "SVR"}
        assert set(trainer.models.keys()) == expected


# ---------------------------------------------------------------------------
# Avant entraînement
# ---------------------------------------------------------------------------

class TestBeforeTraining:
    def test_predict_before_training_raises(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, _ = classification_dataset
        with pytest.raises(ValueError):
            trainer.predict(X)

    def test_get_best_model_before_training_raises(self):
        trainer = AutoTrainer("classification")
        with pytest.raises(ValueError):
            trainer.get_best_model()


# ---------------------------------------------------------------------------
# train_all_models — classification
# ---------------------------------------------------------------------------

class TestTrainClassification:
    def test_returns_dict(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, y = classification_dataset
        results = trainer.train_all_models(X, y, verbose=False)
        assert isinstance(results, dict)

    def test_result_keys_match_models(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, y = classification_dataset
        results = trainer.train_all_models(X, y, verbose=False)
        assert set(results.keys()) == set(trainer.models.keys())

    def test_results_contain_accuracy(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, y = classification_dataset
        results = trainer.train_all_models(X, y, verbose=False)
        for name, res in results.items():
            if "error" not in res:
                assert "accuracy" in res
                assert "f1_score" in res

    def test_accuracy_between_0_and_1(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, y = classification_dataset
        results = trainer.train_all_models(X, y, verbose=False)
        for name, res in results.items():
            if "error" not in res:
                assert 0.0 <= res["accuracy"] <= 1.0

    def test_best_model_set_after_training(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, y = classification_dataset
        trainer.train_all_models(X, y, verbose=False)
        assert trainer.best_model is not None

    def test_best_score_set_after_training(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, y = classification_dataset
        trainer.train_all_models(X, y, verbose=False)
        assert isinstance(trainer.best_score, float)
        assert 0.0 <= trainer.best_score <= 1.0

    def test_verbose_false_no_stdout(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, y = classification_dataset
        captured = io.StringIO()
        sys.stdout = captured
        try:
            trainer.train_all_models(X, y, verbose=False)
        finally:
            sys.stdout = sys.__stdout__
        assert captured.getvalue() == ""


# ---------------------------------------------------------------------------
# train_all_models — regression
# ---------------------------------------------------------------------------

class TestTrainRegression:
    def test_results_contain_rmse_r2(self, regression_dataset):
        trainer = AutoTrainer("regression")
        X, y = regression_dataset
        results = trainer.train_all_models(X, y, verbose=False)
        for name, res in results.items():
            if "error" not in res:
                assert "rmse" in res
                assert "r2" in res
                assert "mse" in res

    def test_rmse_non_negative(self, regression_dataset):
        trainer = AutoTrainer("regression")
        X, y = regression_dataset
        results = trainer.train_all_models(X, y, verbose=False)
        for name, res in results.items():
            if "error" not in res:
                assert res["rmse"] >= 0.0


# ---------------------------------------------------------------------------
# predict
# ---------------------------------------------------------------------------

class TestPredict:
    def test_predict_returns_array(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, y = classification_dataset
        trainer.train_all_models(X, y, verbose=False)
        predictions = trainer.predict(X)
        assert isinstance(predictions, np.ndarray)

    def test_predict_correct_length(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, y = classification_dataset
        trainer.train_all_models(X, y, verbose=False)
        predictions = trainer.predict(X)
        assert len(predictions) == len(X)


# ---------------------------------------------------------------------------
# get_best_model
# ---------------------------------------------------------------------------

class TestGetBestModel:
    def test_returns_tuple(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, y = classification_dataset
        trainer.train_all_models(X, y, verbose=False)
        result = trainer.get_best_model()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_name_is_string(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, y = classification_dataset
        trainer.train_all_models(X, y, verbose=False)
        name, _ = trainer.get_best_model()
        assert isinstance(name, str)
        assert name in trainer.models

    def test_model_has_predict(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, y = classification_dataset
        trainer.train_all_models(X, y, verbose=False)
        _, model = trainer.get_best_model()
        assert hasattr(model, "predict")


# ---------------------------------------------------------------------------
# get_results_dataframe
# ---------------------------------------------------------------------------

class TestGetResultsDataframe:
    def test_returns_dataframe(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, y = classification_dataset
        trainer.train_all_models(X, y, verbose=False)
        df = trainer.get_results_dataframe()
        assert isinstance(df, pd.DataFrame)

    def test_classification_columns(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, y = classification_dataset
        trainer.train_all_models(X, y, verbose=False)
        df = trainer.get_results_dataframe()
        assert "Model" in df.columns
        assert "Accuracy" in df.columns
        assert "F1_Score" in df.columns

    def test_regression_columns(self, regression_dataset):
        trainer = AutoTrainer("regression")
        X, y = regression_dataset
        trainer.train_all_models(X, y, verbose=False)
        df = trainer.get_results_dataframe()
        assert "RMSE" in df.columns
        assert "R2" in df.columns

    def test_sorted_by_accuracy_descending(self, classification_dataset):
        trainer = AutoTrainer("classification")
        X, y = classification_dataset
        trainer.train_all_models(X, y, verbose=False)
        df = trainer.get_results_dataframe()
        accuracies = df["Accuracy"].tolist()
        assert accuracies == sorted(accuracies, reverse=True)
