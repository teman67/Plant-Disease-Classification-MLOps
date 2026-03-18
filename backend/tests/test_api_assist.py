"""Tests for POST /api/v1/assist/prediction"""
from __future__ import annotations

import json
import os
from unittest.mock import MagicMock, patch

from app.schemas.prediction import PredictionResult


def _make_prediction() -> dict:
    return PredictionResult(
        id="assist-1",
        source_type="file",
        source_name="leaf.jpg",
        predicted_class="Rust",
        probabilities={"Healthy": 0.05, "Powdery": 0.05, "Rust": 0.90},
        treatment_suggestion="Apply fungicide.",
    ).model_dump()


class TestAssistPredictionEndpoint:
    def test_no_api_key_returns_400(self, client):
        from app.core.config import get_settings
        original_key = get_settings().openai_api_key
        get_settings().openai_api_key = ""
        try:
            r = client.post(
                "/api/v1/assist/prediction",
                json={"prediction": _make_prediction()},
            )
            assert r.status_code == 400
        finally:
            get_settings().openai_api_key = original_key

    def test_successful_response_schema(self, client):
        ai_payload = {
            "diagnosis": "Rust infection",
            "why": "Orange spores",
            "immediate_actions": ["Remove leaves"],
            "prevention": ["Improve drainage"],
        }
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(ai_payload)}}]
        }

        from app.core.config import get_settings
        s = get_settings()
        s.openai_api_key = "sk-test-key"
        try:
            with patch("app.services.ai_assistant.requests.post", return_value=mock_response):
                r = client.post(
                    "/api/v1/assist/prediction",
                    json={"prediction": _make_prediction()},
                )
        finally:
            s.openai_api_key = ""

        assert r.status_code == 200
        body = r.json()
        assert "model" in body
        assert "diagnosis" in body
        assert "why" in body
        assert "immediate_actions" in body
        assert "prevention" in body

    def test_successful_response_content(self, client):
        ai_payload = {
            "diagnosis": "Rust detected on leaf margins",
            "why": "Hexagonal orange pustules",
            "immediate_actions": ["Isolate plant", "Apply copper spray"],
            "prevention": ["Avoid overhead watering"],
        }
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(ai_payload)}}]
        }

        from app.core.config import get_settings
        s = get_settings()
        s.openai_api_key = "sk-test-key"
        try:
            with patch("app.services.ai_assistant.requests.post", return_value=mock_response):
                r = client.post(
                    "/api/v1/assist/prediction",
                    json={"prediction": _make_prediction()},
                )
        finally:
            s.openai_api_key = ""

        body = r.json()
        assert body["diagnosis"] == "Rust detected on leaf margins"
        assert "Isolate plant" in body["immediate_actions"]

    def test_ai_service_failure_returns_400(self, client):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 503

        from app.core.config import get_settings
        s = get_settings()
        s.openai_api_key = "sk-test-key"
        try:
            with patch("app.services.ai_assistant.requests.post", return_value=mock_response):
                r = client.post(
                    "/api/v1/assist/prediction",
                    json={"prediction": _make_prediction()},
                )
        finally:
            s.openai_api_key = ""

        assert r.status_code == 400
