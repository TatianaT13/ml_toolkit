"""
Tests unitaires pour TabularLoader et BinaryLoader.
"""

import numpy as np
import pandas as pd
import pytest

from my_ml_toolkit.data_loader.tabular import TabularLoader
from my_ml_toolkit.data_loader.binary import BinaryLoader


# ---------------------------------------------------------------------------
# TabularLoader
# ---------------------------------------------------------------------------

class TestTabularLoader:
    def test_load_csv_returns_dataframe(self, tmp_csv):
        loader = TabularLoader()
        df = loader.load_csv(tmp_csv)
        assert isinstance(df, pd.DataFrame)

    def test_load_csv_correct_shape(self, tmp_csv):
        loader = TabularLoader()
        df = loader.load_csv(tmp_csv)
        assert df.shape[0] == 20       # 20 lignes définies dans la fixture
        assert df.shape[1] == 3        # colonnes x1, x2, target

    def test_load_csv_correct_columns(self, tmp_csv):
        loader = TabularLoader()
        df = loader.load_csv(tmp_csv)
        assert "x1" in df.columns
        assert "x2" in df.columns
        assert "target" in df.columns

    def test_load_csv_semicolon_separator(self, tmp_csv_semicolon):
        loader = TabularLoader(separator=";")
        df = loader.load_csv(tmp_csv_semicolon)
        assert df.shape == (3, 2)

    def test_load_csv_wrong_path_raises(self):
        loader = TabularLoader()
        with pytest.raises(Exception):
            loader.load_csv("/nonexistent/path/file.csv")

    def test_get_info_returns_expected_keys(self, tmp_csv):
        loader = TabularLoader()
        df = loader.load_csv(tmp_csv)
        info = loader.get_info(df)
        expected_keys = {"shape", "columns", "dtypes", "missing_values", "memory_usage"}
        assert expected_keys == set(info.keys())

    def test_get_info_shape_correct(self, tmp_csv):
        loader = TabularLoader()
        df = loader.load_csv(tmp_csv)
        info = loader.get_info(df)
        assert info["shape"] == (20, 3)

    def test_get_info_columns_list(self, tmp_csv):
        loader = TabularLoader()
        df = loader.load_csv(tmp_csv)
        info = loader.get_info(df)
        assert isinstance(info["columns"], list)
        assert "x1" in info["columns"]

    def test_get_info_missing_values_is_dict(self, tmp_csv):
        loader = TabularLoader()
        df = loader.load_csv(tmp_csv)
        info = loader.get_info(df)
        assert isinstance(info["missing_values"], dict)

    def test_get_info_memory_usage_positive(self, tmp_csv):
        loader = TabularLoader()
        df = loader.load_csv(tmp_csv)
        info = loader.get_info(df)
        assert info["memory_usage"] > 0


# ---------------------------------------------------------------------------
# BinaryLoader
# ---------------------------------------------------------------------------

class TestBinaryLoader:
    def test_load_file_returns_bytes(self, tmp_binary_file):
        loader = BinaryLoader()
        data = loader.load_file(tmp_binary_file)
        assert isinstance(data, bytes)

    def test_load_file_correct_size(self, tmp_binary_file, binary_benign):
        loader = BinaryLoader()
        data = loader.load_file(tmp_binary_file)
        assert len(data) == len(binary_benign)

    def test_load_file_with_max_bytes(self, tmp_binary_file):
        loader = BinaryLoader(max_bytes=50)
        data = loader.load_file(tmp_binary_file)
        assert len(data) == 50

    def test_load_file_wrong_path_raises(self):
        loader = BinaryLoader()
        with pytest.raises(Exception):
            loader.load_file("/nonexistent/file.bin")

    def test_load_directory_returns_list(self, tmp_binary_dir):
        loader = BinaryLoader()
        result = loader.load_directory(tmp_binary_dir)
        assert isinstance(result, list)

    def test_load_directory_all_files_loaded(self, tmp_binary_dir):
        loader = BinaryLoader()
        result = loader.load_directory(tmp_binary_dir)
        # 4 fichiers créés dans la fixture (mal1.bin, mal2.bin, ben1.exe, readme.txt)
        assert len(result) == 4

    def test_load_directory_returns_tuples(self, tmp_binary_dir):
        loader = BinaryLoader()
        result = loader.load_directory(tmp_binary_dir)
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 2
            name, data = item
            assert isinstance(name, str)
            assert isinstance(data, bytes)

    def test_load_directory_filter_by_extension(self, tmp_binary_dir):
        loader = BinaryLoader()
        result = loader.load_directory(tmp_binary_dir, extensions=[".bin"])
        names = [name for name, _ in result]
        assert all(name.endswith(".bin") for name in names)
        assert len(result) == 2  # mal1.bin et mal2.bin

    def test_load_directory_filter_exe(self, tmp_binary_dir):
        loader = BinaryLoader()
        result = loader.load_directory(tmp_binary_dir, extensions=[".exe"])
        assert len(result) == 1
        assert result[0][0] == "ben1.exe"

    def test_bytes_to_array_type(self, binary_benign):
        loader = BinaryLoader()
        arr = loader.bytes_to_array(binary_benign)
        assert arr.dtype == np.uint8

    def test_bytes_to_array_size(self, binary_benign):
        loader = BinaryLoader()
        arr = loader.bytes_to_array(binary_benign)
        assert len(arr) == len(binary_benign)

    def test_bytes_to_array_values_range(self, binary_benign):
        loader = BinaryLoader()
        arr = loader.bytes_to_array(binary_benign)
        assert arr.min() >= 0
        assert arr.max() <= 255
