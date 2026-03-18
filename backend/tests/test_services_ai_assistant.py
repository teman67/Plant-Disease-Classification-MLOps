"""Tests for app/services/ai_assistant.py"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from app.schemas.prediction import PredictionResult
from app.services.ai_assistant import _normalize_sections, generate_prediction_guidance


def _make_prediction(klass: str = "Rust") -> PredictionResult:
    return PredictionResult(
        id="test-1",
        source_type="file",
        source_name="leaf.jpg",
        predicted_class=klass,
        probabilities={"Healthy": 0.1, "Powdery": 0.1, "Rust": 0.8},
        treatment_suggestion="Apply fungicide.",
    )


# ---------------------------------------------------------------------------
# _normalize_sections
# ---------------------------------------------------------------------------

class TestNormalizeSections:
    def test_all_fields_present(self):
        payload = {
            "diagnosis": "Rust detected",
            "why": "Spores on leaf",
            "immediate_actions": ["Remove leaves", "Apply fungicide"],
            "prevention": ["Rotate crops"],
        }
        result = _normalize_sections(payload, "raw")
        assert result["diagnosis"] == "Rust detected"
        assert result["why"] == "Spores on leaf"
        assert result["immediate_actions"] == ["Remove leaves", "Apply fungicide"]
        assert result["prevention"] == ["Rotate crops"]
        assert result["raw_response"] == "raw"

    def test_missing_fields_use_defaults(self):
        result = _normalize_sections({}, "raw")
        assert result["diagnosis"] == "Not provided."
        assert result["why"] == "Not provided."
        assert result["immediate_actions"] == []
        assert result["prevention"] == []

    def test_non_list_actions_becomes_empty(self):
        payload = {"immediate_actions": "Do something", "prevention": 42}
        result = _normalize_sections(payload, "")
        assert result["immediate_actions"] == []
        assert result["prevention"] == []

    def test_filters_blank_action_strings(self):
        payload = {"immediate_actions": ["  ", "Step 1", ""]}
        result = _normalize_sections(payload, "")
        assert result["immediate_actions"] == ["Step 1"]

    def test_strips_whitespace_from_fields(self):
        payload = {"diagnosis": "  Rust  ", "why": "  Because  "}
        result = _normalize_sections(payload, "")
        assert result["diagnosis"] == "Rust"
        assert result["why"] == "Because"

    def test_action_items_cast_to_str(self):
        payload = {"immediate_actions": [1, 2, 3]}
        result = _normalize_sections(payload, "")
        assert result["immediate_actions"] == ["1", "2", "3"]


# ---------------------------------------------------------------------------
# generate_prediction_guidance
# ---------------------------------------------------------------------------

class TestGeneratePredictionGuidance:
    def test_raises_value_error_when_no_api_key(self):
        from app.core.config import get_settings
        get_settings.cache_clear()
        import os
        original = os.environ.pop("OPENAI_API_KEY", None)
        try:
            get_settings.cache_clear()
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                generate_prediction_guidance(_make_prediction())
        finally:
            if original is not None:
                os.environ["OPENAI_API_KEY"] = original
            get_settings.cache_clear()

    def test_successful_response_returns_model_and_dict(self):
        ai_payload = {
            "diagnosis": "Rust infection",
            "why": "Orange spores present",
            "immediate_actions": ["Remove affected leaves"],
            "prevention": ["Improve airflow"],
        }
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(ai_payload)}}]
        }

        import os
        os.environ["OPENAI_API_KEY"] = "sk-test-key"
        from app.core.config import get_settings
        get_settings.cache_clear()
        try:
            with patch("app.services.ai_assistant.requests.post", return_value=mock_response):
                model_name, advice = generate_prediction_guidance(_make_prediction())
        finally:
            os.environ.pop("OPENAI_API_KEY", None)
            get_settings.cache_clear()

        assert isinstance(model_name, str)
        assert advice["diagnosis"] == "Rust infection"
        assert advice["why"] == "Orange spores present"
        assert "Remove affected leaves" in advice["immediate_actions"]

    def test_failed_http_response_raises_value_error(self):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 500

        import os
        os.environ["OPENAI_API_KEY"] = "sk-test-key"
        from app.core.config import get_settings
        get_settings.cache_clear()
        try:
            with patch("app.services.ai_assistant.requests.post", return_value=mock_response):
                with pytest.raises(ValueError, match="AI assistant request failed"):
                    generate_prediction_guidance(_make_prediction())
        finally:
            os.environ.pop("OPENAI_API_KEY", None)
            get_settings.cache_clear()

    def test_empty_content_returns_fallback(self):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"choices": [{"message": {"content": ""}}]}

        import os
        os.environ["OPENAI_API_KEY"] = "sk-test-key"
        from app.core.config import get_settings
        get_settings.cache_clear()
        try:
            with patch("app.services.ai_assistant.requests.post", return_value=mock_response):
                model_name, advice = generate_prediction_guidance(_make_prediction())
        finally:
            os.environ.pop("OPENAI_API_KEY", None)
            get_settings.cache_clear()

        assert "Not provided." in advice["diagnosis"] or advice["raw_response"] == "No AI response was returned."

    def test_non_json_content_uses_fallback_diagnosis(self):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"choices": [{"message": {"content": "Plain text response"}}]}

        import os
        os.environ["OPENAI_API_KEY"] = "sk-test-key"
        from app.core.config import get_settings
        get_settings.cache_clear()
        try:
            with patch("app.services.ai_assistant.requests.post", return_value=mock_response):
                _, advice = generate_prediction_guidance(_make_prediction())
        finally:
            os.environ.pop("OPENAI_API_KEY", None)
            get_settings.cache_clear()

        assert advice["diagnosis"] == "Plain text response"
