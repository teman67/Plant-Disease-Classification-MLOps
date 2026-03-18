"""Tests for app/services/performance.py"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from app.services.performance import (
    _extract_evaluation,
    _normalize_value,
    get_performance_summary,
)


# ---------------------------------------------------------------------------
# _normalize_value
# ---------------------------------------------------------------------------

class TestNormalizeValue:
    def test_numpy_array_to_list(self):
        arr = np.array([1, 2, 3])
        assert _normalize_value(arr) == [1, 2, 3]

    def test_numpy_float32(self):
        val = np.float32(0.95)
        result = _normalize_value(val)
        assert isinstance(result, float)
        assert abs(result - 0.95) < 1e-5

    def test_numpy_float64(self):
        val = np.float64(0.75)
        assert isinstance(_normalize_value(val), float)

    def test_numpy_int32(self):
        val = np.int32(42)
        result = _normalize_value(val)
        assert isinstance(result, int)
        assert result == 42

    def test_numpy_int64(self):
        val = np.int64(100)
        result = _normalize_value(val)
        assert isinstance(result, int)

    def test_dict_with_numpy_values(self):
        d = {"a": np.float32(0.5), "b": np.int32(1)}
        result = _normalize_value(d)
        assert isinstance(result["a"], float)
        assert isinstance(result["b"], int)

    def test_nested_list(self):
        lst = [np.float32(0.1), np.float32(0.2)]
        result = _normalize_value(lst)
        assert all(isinstance(v, float) for v in result)

    def test_tuple_treated_as_list(self):
        result = _normalize_value((np.int32(1), np.int32(2)))
        assert result == [1, 2]

    def test_plain_python_value_passthrough(self):
        assert _normalize_value(42) == 42
        assert _normalize_value("hello") == "hello"
        assert _normalize_value(None) is None

    def test_dataframe_to_records(self):
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        result = _normalize_value(df)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_series_to_dict(self):
        s = pd.Series({"a": 1, "b": 2})
        result = _normalize_value(s)
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# _extract_evaluation
# ---------------------------------------------------------------------------

class TestExtractEvaluation:
    def test_list_form_loss_and_accuracy(self):
        result = _extract_evaluation([0.3, 0.95], None)
        assert abs(result["loss"] - 0.3) < 1e-6
        assert abs(result["accuracy"] - 0.95) < 1e-6

    def test_list_form_numpy_values(self):
        result = _extract_evaluation([np.float32(0.2), np.float32(0.88)], None)
        assert isinstance(result["loss"], float)
        assert isinstance(result["accuracy"], float)

    def test_dict_form_with_loss_accuracy_keys(self):
        result = _extract_evaluation({"loss": 0.4, "accuracy": 0.90}, None)
        assert abs(result["loss"] - 0.4) < 1e-6
        assert abs(result["accuracy"] - 0.90) < 1e-6

    def test_dict_form_with_test_keys(self):
        result = _extract_evaluation({"test_loss": 0.5, "test_accuracy": 0.85}, None)
        assert abs(result["loss"] - 0.5) < 1e-6
        assert abs(result["accuracy"] - 0.85) < 1e-6

    def test_none_evaluation_returns_none_fields(self):
        result = _extract_evaluation(None, None)
        assert result["loss"] is None
        assert result["accuracy"] is None

    def test_accuracy_fallback_from_metrics(self):
        result = _extract_evaluation(None, {"accuracy": 0.92})
        assert abs(result["accuracy"] - 0.92) < 1e-6

    def test_empty_list_returns_none_fields(self):
        result = _extract_evaluation([], None)
        assert result["loss"] is None
        assert result["accuracy"] is None

    def test_single_element_list_returns_none(self):
        # _extract_evaluation requires len >= 2; a single-element list yields None for both
        result = _extract_evaluation([0.7], None)
        assert result["loss"] is None
        assert result["accuracy"] is None


# ---------------------------------------------------------------------------
# get_performance_summary
# ---------------------------------------------------------------------------

class TestGetPerformanceSummary:
    def test_returns_dict_with_expected_keys(self):
        result = get_performance_summary()
        assert isinstance(result, dict)
        assert "confusion_matrix" in result
        assert "metrics" in result
        assert "evaluation" in result

    def test_evaluation_has_loss_and_accuracy_keys(self):
        result = get_performance_summary()
        evaluation = result["evaluation"]
        assert "loss" in evaluation
        assert "accuracy" in evaluation

    def test_missing_files_return_none_gracefully(self, tmp_path):
        """When artifact files don't exist, summary should still return a dict."""
        from app.core.config import get_settings

        s = get_settings()
        original_cm = s.confusion_matrix_path
        original_metrics = s.metrics_path
        s.confusion_matrix_path = tmp_path / "nonexistent_cm.joblib"
        s.metrics_path = tmp_path / "nonexistent_metrics.joblib"
        try:
            result = get_performance_summary()
            assert result["confusion_matrix"] is None
            assert result["metrics"] is None
        finally:
            s.confusion_matrix_path = original_cm
            s.metrics_path = original_metrics
