"""Tests for app/schemas/prediction.py"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.prediction import (
    AiAssistRequest,
    AiAssistResponse,
    CsvAiData,
    CsvReportRequest,
    PredictionListResponse,
    PredictionResult,
    UrlPredictRequest,
)


# ---------------------------------------------------------------------------
# PredictionResult
# ---------------------------------------------------------------------------

class TestPredictionResult:
    def _valid(self, **overrides) -> dict:
        base = {
            "id": "p-1",
            "source_type": "file",
            "source_name": "leaf.jpg",
            "predicted_class": "Healthy",
            "probabilities": {"Healthy": 0.9, "Powdery": 0.05, "Rust": 0.05},
        }
        base.update(overrides)
        return base

    def test_valid_construction(self):
        pred = PredictionResult(**self._valid())
        assert pred.id == "p-1"
        assert pred.predicted_class == "Healthy"

    def test_defaults_applied(self):
        pred = PredictionResult(**self._valid())
        assert pred.probabilities == {"Healthy": 0.9, "Powdery": 0.05, "Rust": 0.05}
        assert pred.rgb_converted is False
        assert pred.errors == []
        assert pred.treatment_suggestion is None
        assert pred.image_preview is None

    def test_predicted_class_can_be_none(self):
        pred = PredictionResult(**self._valid(predicted_class=None))
        assert pred.predicted_class is None

    def test_errors_list_accepted(self):
        pred = PredictionResult(**self._valid(errors=["error one", "error two"]))
        assert len(pred.errors) == 2

    def test_missing_required_fields_raises(self):
        with pytest.raises(ValidationError):
            PredictionResult(id="p-1")  # missing source_type, source_name

    def test_model_dump_round_trip(self):
        pred = PredictionResult(**self._valid())
        dumped = pred.model_dump()
        pred2 = PredictionResult(**dumped)
        assert pred2.id == pred.id


# ---------------------------------------------------------------------------
# UrlPredictRequest
# ---------------------------------------------------------------------------

class TestUrlPredictRequest:
    def test_valid_https_url_accepted(self):
        req = UrlPredictRequest(urls=["https://example.com/leaf.jpg"])
        assert len(req.urls) == 1

    def test_valid_http_url_accepted(self):
        req = UrlPredictRequest(urls=["http://example.com/leaf.jpg"])
        assert len(req.urls) == 1

    def test_invalid_url_raises_validation_error(self):
        with pytest.raises(ValidationError):
            UrlPredictRequest(urls=["not-a-url"])

    def test_empty_list_accepted(self):
        req = UrlPredictRequest(urls=[])
        assert req.urls == []

    def test_multiple_urls_accepted(self):
        req = UrlPredictRequest(
            urls=[
                "https://example.com/a.jpg",
                "https://example.com/b.jpg",
            ]
        )
        assert len(req.urls) == 2


# ---------------------------------------------------------------------------
# CsvAiData
# ---------------------------------------------------------------------------

class TestCsvAiData:
    def test_defaults(self):
        data = CsvAiData()
        assert data.diagnosis == ""
        assert data.why == ""
        assert data.immediate_actions == []
        assert data.prevention == []

    def test_fields_set(self):
        data = CsvAiData(
            diagnosis="Rust",
            why="Spores",
            immediate_actions=["Step 1"],
            prevention=["Step A"],
        )
        assert data.diagnosis == "Rust"
        assert data.immediate_actions == ["Step 1"]


# ---------------------------------------------------------------------------
# CsvReportRequest
# ---------------------------------------------------------------------------

class TestCsvReportRequest:
    def test_empty_predictions(self):
        req = CsvReportRequest(predictions=[])
        assert req.predictions == []
        assert req.ai_data == {}

    def test_with_predictions(self):
        pred = PredictionResult(
            id="x",
            source_type="file",
            source_name="a.jpg",
            predicted_class="Healthy",
        )
        req = CsvReportRequest(predictions=[pred])
        assert len(req.predictions) == 1


# ---------------------------------------------------------------------------
# AiAssistRequest / AiAssistResponse
# ---------------------------------------------------------------------------

class TestAiAssistRequest:
    def test_valid(self):
        pred = PredictionResult(
            id="ai-1",
            source_type="file",
            source_name="leaf.jpg",
            predicted_class="Powdery",
        )
        req = AiAssistRequest(prediction=pred)
        assert req.prediction.predicted_class == "Powdery"

    def test_missing_prediction_raises(self):
        with pytest.raises(ValidationError):
            AiAssistRequest()


class TestAiAssistResponse:
    def test_valid(self):
        resp = AiAssistResponse(
            model="gpt-4",
            diagnosis="Powdery mildew",
            why="White coating",
            immediate_actions=["Spray sulfur"],
            prevention=["Air circulation"],
        )
        assert resp.model == "gpt-4"
        assert resp.raw_response == ""

    def test_raw_response_default(self):
        resp = AiAssistResponse(
            model="gpt-4",
            diagnosis="x",
            why="y",
        )
        assert resp.raw_response == ""


# ---------------------------------------------------------------------------
# PredictionListResponse
# ---------------------------------------------------------------------------

class TestPredictionListResponse:
    def test_empty_list(self):
        resp = PredictionListResponse(predictions=[])
        assert resp.predictions == []

    def test_with_items(self):
        pred = PredictionResult(
            id="z",
            source_type="url",
            source_name="https://example.com/img.jpg",
            predicted_class="Rust",
        )
        resp = PredictionListResponse(predictions=[pred])
        assert len(resp.predictions) == 1
