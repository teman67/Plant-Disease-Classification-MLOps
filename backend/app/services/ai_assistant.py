from __future__ import annotations

import json

import requests

from app.core.config import get_settings
from app.schemas.prediction import PredictionResult


def _normalize_sections(payload: dict, raw_text: str) -> dict:
    diagnosis = str(payload.get("diagnosis", "")).strip() or "Not provided."
    why = str(payload.get("why", "")).strip() or "Not provided."

    immediate_actions = payload.get("immediate_actions", [])
    if not isinstance(immediate_actions, list):
        immediate_actions = []
    immediate_actions = [str(item).strip() for item in immediate_actions if str(item).strip()]

    prevention = payload.get("prevention", [])
    if not isinstance(prevention, list):
        prevention = []
    prevention = [str(item).strip() for item in prevention if str(item).strip()]

    return {
        "diagnosis": diagnosis,
        "why": why,
        "immediate_actions": immediate_actions,
        "prevention": prevention,
        "raw_response": raw_text,
    }


def generate_prediction_guidance(prediction: PredictionResult) -> tuple[str, dict]:
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured on backend")

    system_prompt = (
        "You are an agricultural disease assistant. "
        "Given a model prediction for a leaf image, explain likely issue, confidence caveats, "
        "and practical next steps. Keep response concise, structured, and safe."
    )

    user_payload = {
        "source_name": prediction.source_name,
        "predicted_class": prediction.predicted_class,
        "probabilities": prediction.probabilities,
        "rgb_converted": prediction.rgb_converted,
        "treatment_suggestion": prediction.treatment_suggestion,
        "errors": prediction.errors,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.openai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Based on this prediction JSON, return ONLY valid JSON with keys: "
                        "diagnosis (string), why (string), immediate_actions (array of strings), prevention (array of strings).\n"
                        + json.dumps(user_payload)
                    ),
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "plant_diagnosis",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "diagnosis": {"type": "string"},
                            "why": {"type": "string"},
                            "immediate_actions": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "prevention": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["diagnosis", "why", "immediate_actions", "prevention"],
                        "additionalProperties": False,
                    },
                },
            },
            "temperature": 0.3,
        },
        timeout=settings.openai_timeout_sec,
    )

    if not response.ok:
        raise ValueError(f"AI assistant request failed: {response.status_code}")

    data = response.json()
    choices = data.get("choices", [])
    output_text = ""
    if choices:
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, str):
            output_text = content.strip()

    if not output_text:
        return settings.openai_model, _normalize_sections({}, "No AI response was returned.")

    try:
        payload = json.loads(output_text)
        if isinstance(payload, dict):
            return settings.openai_model, _normalize_sections(payload, output_text)
    except Exception:
        pass

    # Fallback if model returned non-JSON text.
    return settings.openai_model, _normalize_sections({"diagnosis": output_text}, output_text)
