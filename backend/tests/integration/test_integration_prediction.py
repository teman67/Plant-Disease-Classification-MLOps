"""Integration tests for the model loading and prediction service pipeline.

These tests exercise the full path:
    real .h5 file → ModelRegistry.load() → normalize_image() → model.predict()

No HTTP layer is involved here — services are called directly.
"""
from __future__ import annotations

import pytest

from app.core.constants import CLASS_MAPPING
from app.services.model_loader import model_registry
from app.services.predict import InputItem, predict_input_item
from app.services.preprocess import load_pil_from_bytes, normalize_image


VALID_CLASSES = set(CLASS_MAPPING.values())  # {"Healthy", "Powdery", "Rust"}


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestRealModelLoading:
    def test_model_registry_loads_without_error(self, real_client):
        """Lifespan (via real_client fixture) must load the model."""
        assert model_registry.is_loaded()

    def test_model_context_has_image_shape(self, real_client):
        ctx = model_registry._ctx
        assert ctx is not None
        assert len(ctx.image_shape) == 3
        h, w, c = ctx.image_shape
        assert h > 0 and w > 0 and c == 3

    def test_model_context_has_callable_predict(self, real_client):
        ctx = model_registry._ctx
        assert callable(ctx.model.predict)

    def test_loading_twice_returns_same_context(self, real_client):
        ctx1 = model_registry.load()
        ctx2 = model_registry.load()
        assert ctx1 is ctx2  # cached — no second disk read


# ---------------------------------------------------------------------------
# Direct service-layer prediction (bypasses HTTP)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestRealPredictionService:
    def _predict(self, payload: bytes, label: str) -> object:
        item = InputItem(source_type="file", source_name=f"{label}.jpg", payload=payload)
        return predict_input_item(item, item_id=f"integ-{label}")

    # --- Healthy ---
    def test_healthy_image_returns_valid_class(self, real_client, healthy_image_bytes):
        result = self._predict(healthy_image_bytes, "Healthy")
        assert result.predicted_class in VALID_CLASSES

    def test_healthy_image_no_errors(self, real_client, healthy_image_bytes):
        result = self._predict(healthy_image_bytes, "Healthy")
        assert result.errors == []

    def test_healthy_image_probabilities_sum_to_one(self, real_client, healthy_image_bytes):
        result = self._predict(healthy_image_bytes, "Healthy")
        assert abs(sum(result.probabilities.values()) - 1.0) < 1e-4

    def test_healthy_image_all_probability_keys_present(self, real_client, healthy_image_bytes):
        result = self._predict(healthy_image_bytes, "Healthy")
        assert set(result.probabilities.keys()) == VALID_CLASSES

    def test_healthy_image_all_probabilities_in_range(self, real_client, healthy_image_bytes):
        result = self._predict(healthy_image_bytes, "Healthy")
        for p in result.probabilities.values():
            assert 0.0 <= p <= 1.0

    def test_healthy_image_treatment_suggestion_present(self, real_client, healthy_image_bytes):
        result = self._predict(healthy_image_bytes, "Healthy")
        assert result.treatment_suggestion is not None
        assert len(result.treatment_suggestion) > 0

    def test_healthy_image_thumbnail_attached(self, real_client, healthy_image_bytes):
        result = self._predict(healthy_image_bytes, "Healthy")
        assert result.image_preview is not None
        assert result.image_preview.startswith("data:image/jpeg;base64,")

    # --- Powdery ---
    def test_powdery_image_returns_valid_class(self, real_client, powdery_image_bytes):
        result = self._predict(powdery_image_bytes, "Powdery")
        assert result.predicted_class in VALID_CLASSES

    def test_powdery_image_probabilities_sum_to_one(self, real_client, powdery_image_bytes):
        result = self._predict(powdery_image_bytes, "Powdery")
        assert abs(sum(result.probabilities.values()) - 1.0) < 1e-4

    def test_powdery_image_no_errors(self, real_client, powdery_image_bytes):
        result = self._predict(powdery_image_bytes, "Powdery")
        assert result.errors == []

    # --- Rust ---
    def test_rust_image_returns_valid_class(self, real_client, rust_image_bytes):
        result = self._predict(rust_image_bytes, "Rust")
        assert result.predicted_class in VALID_CLASSES

    def test_rust_image_probabilities_sum_to_one(self, real_client, rust_image_bytes):
        result = self._predict(rust_image_bytes, "Rust")
        assert abs(sum(result.probabilities.values()) - 1.0) < 1e-4

    def test_rust_image_no_errors(self, real_client, rust_image_bytes):
        result = self._predict(rust_image_bytes, "Rust")
        assert result.errors == []

    # --- Accuracy spot-check across all three labels ---
    def test_model_predicts_correct_class_for_each_label(
        self, real_client, healthy_image_bytes, powdery_image_bytes, rust_image_bytes
    ):
        """The model should correctly classify at least 2 out of 3 sample images."""
        samples = [
            ("Healthy", healthy_image_bytes),
            ("Powdery", powdery_image_bytes),
            ("Rust", rust_image_bytes),
        ]
        correct = sum(
            1 for label, payload in samples
            if self._predict(payload, label).predicted_class == label
        )
        assert correct >= 2, f"Model only classified {correct}/3 correctly — accuracy too low."

    # --- Preprocessing integration ---
    def test_normalize_output_feeds_model(self, real_client, healthy_image_bytes):
        """Manually preprocess an image and run model.predict — no exceptions."""
        ctx = model_registry._ctx
        img = load_pil_from_bytes(healthy_image_bytes)
        x, _ = normalize_image(img, ctx.image_shape)
        proba = ctx.model.predict(x, verbose=0)
        assert proba.shape == (1, len(CLASS_MAPPING))
        assert abs(proba[0].sum() - 1.0) < 1e-4
