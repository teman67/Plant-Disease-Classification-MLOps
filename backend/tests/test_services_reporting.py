"""Tests for app/services/reporting.py"""
from __future__ import annotations

import csv
import io

import pytest

from app.schemas.prediction import CsvAiData, PredictionResult
from app.services.reporting import CSV_COLUMNS, build_csv_report


def _make_prediction(pred_id: str = "p-1", klass: str = "Healthy") -> PredictionResult:
    return PredictionResult(
        id=pred_id,
        source_type="file",
        source_name="leaf.jpg",
        predicted_class=klass,
        probabilities={"Healthy": 0.9, "Powdery": 0.05, "Rust": 0.05},
        treatment_suggestion="No treatment needed",
    )


class TestBuildCsvReport:
    def test_returns_string(self):
        result = build_csv_report([])
        assert isinstance(result, str)

    def test_empty_predictions_only_header(self):
        result = build_csv_report([])
        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)
        assert rows == []

    def test_csv_columns_match_spec(self):
        result = build_csv_report([])
        reader = csv.DictReader(io.StringIO(result))
        assert list(reader.fieldnames) == CSV_COLUMNS

    def test_single_prediction_row(self):
        pred = _make_prediction()
        result = build_csv_report([pred])
        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["Name/Source"] == "leaf.jpg"

    def test_multiple_predictions_row_count(self):
        preds = [_make_prediction(f"p-{i}") for i in range(5)]
        result = build_csv_report(preds)
        reader = csv.DictReader(io.StringIO(result))
        assert len(list(reader)) == 5

    def test_ai_data_written_to_row(self):
        pred = _make_prediction(pred_id="ai-1")
        ai = CsvAiData(
            diagnosis="Healthy plant",
            why="No symptoms visible",
            immediate_actions=["Water regularly"],
            prevention=["Use clean tools"],
        )
        result = build_csv_report([pred], ai_data={"ai-1": ai})
        reader = csv.DictReader(io.StringIO(result))
        row = list(reader)[0]
        assert row["Diagnosis"] == "Healthy plant"
        assert row["Why"] == "No symptoms visible"
        assert "Water regularly" in row["Immediate Actions"]
        assert "Use clean tools" in row["Prevention"]

    def test_missing_ai_data_empty_diagnosis(self):
        pred = _make_prediction(pred_id="no-ai")
        result = build_csv_report([pred])
        reader = csv.DictReader(io.StringIO(result))
        row = list(reader)[0]
        assert row["Diagnosis"] == ""
        assert row["Why"] == ""

    def test_errors_joined_with_pipe(self):
        pred = _make_prediction()
        pred = pred.model_copy(update={"errors": ["err one", "err two"]})
        result = build_csv_report([pred])
        reader = csv.DictReader(io.StringIO(result))
        row = list(reader)[0]
        assert "err one" in row["Errors"]
        assert "err two" in row["Errors"]

    def test_no_errors_empty_errors_column(self):
        pred = _make_prediction()
        result = build_csv_report([pred])
        reader = csv.DictReader(io.StringIO(result))
        row = list(reader)[0]
        assert row["Errors"] == ""

    def test_multiple_immediate_actions_joined_by_semicolon(self):
        pred = _make_prediction(pred_id="x")
        ai = CsvAiData(immediate_actions=["Step 1", "Step 2", "Step 3"])
        result = build_csv_report([pred], ai_data={"x": ai})
        reader = csv.DictReader(io.StringIO(result))
        row = list(reader)[0]
        assert row["Immediate Actions"] == "Step 1; Step 2; Step 3"
