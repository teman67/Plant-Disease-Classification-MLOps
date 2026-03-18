"""Tests for POST /api/v1/reports/csv"""
from __future__ import annotations

import csv
import io

from app.schemas.prediction import PredictionResult


def _make_prediction(pred_id: str = "r-1") -> PredictionResult:
    return PredictionResult(
        id=pred_id,
        source_type="file",
        source_name="leaf.jpg",
        predicted_class="Healthy",
        probabilities={"Healthy": 0.9, "Powdery": 0.05, "Rust": 0.05},
        treatment_suggestion="No treatment needed",
    )


class TestReportsCsvEndpoint:
    def test_returns_200(self, client):
        r = client.post(
            "/api/v1/reports/csv",
            json={"predictions": [], "ai_data": {}},
        )
        assert r.status_code == 200

    def test_content_type_is_csv(self, client):
        r = client.post(
            "/api/v1/reports/csv",
            json={"predictions": [], "ai_data": {}},
        )
        assert "text/csv" in r.headers["content-type"]

    def test_content_disposition_attachment(self, client):
        r = client.post(
            "/api/v1/reports/csv",
            json={"predictions": [], "ai_data": {}},
        )
        disposition = r.headers.get("content-disposition", "")
        assert "attachment" in disposition
        assert "analysis_report.csv" in disposition

    def test_csv_has_correct_headers(self, client):
        r = client.post(
            "/api/v1/reports/csv",
            json={"predictions": [], "ai_data": {}},
        )
        # Response uses utf-8-sig (BOM); decode explicitly to strip it.
        text = r.content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        assert "Name/Source" in reader.fieldnames
        assert "Diagnosis" in reader.fieldnames
        assert "Errors" in reader.fieldnames

    def test_single_prediction_produces_one_row(self, client):
        pred = _make_prediction()
        r = client.post(
            "/api/v1/reports/csv",
            json={
                "predictions": [pred.model_dump()],
                "ai_data": {},
            },
        )
        text = r.content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["Name/Source"] == "leaf.jpg"

    def test_ai_data_written_to_row(self, client):
        pred = _make_prediction(pred_id="ai-row")
        r = client.post(
            "/api/v1/reports/csv",
            json={
                "predictions": [pred.model_dump()],
                "ai_data": {
                    "ai-row": {
                        "diagnosis": "Leaf is healthy",
                        "why": "No fungal markers",
                        "immediate_actions": ["Monitor weekly"],
                        "prevention": [],
                    }
                },
            },
        )
        reader = csv.DictReader(io.StringIO(r.text))
        row = list(reader)[0]
        assert row["Diagnosis"] == "Leaf is healthy"

    def test_multiple_predictions_produce_multiple_rows(self, client):
        preds = [_make_prediction(f"r-{i}").model_dump() for i in range(3)]
        r = client.post(
            "/api/v1/reports/csv",
            json={"predictions": preds, "ai_data": {}},
        )
        reader = csv.DictReader(io.StringIO(r.text))
        assert len(list(reader)) == 3
