"""Shared fixtures for integration tests.

These tests load the REAL Keras model and read real artifact files.
They are slow (model load ~15s) but session-scoped to run only once per
pytest session.

Run with:
    pytest -m integration
"""
from __future__ import annotations

from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Paths derived from Settings (resolved once)
# ---------------------------------------------------------------------------

def _settings():
    from app.core.config import get_settings
    return get_settings()


# Convenience paths used by multiple test files
MODEL_PATH = _settings().model_path
CONFUSION_MATRIX_PATH = _settings().confusion_matrix_path
METRICS_PATH = _settings().metrics_path
IMAGE_SHAPE_PATH = _settings().image_shape_path
DATASET_TEST_PATH = _settings().dataset_test_path


# ---------------------------------------------------------------------------
# Session-level skip if critical artifacts are missing
# ---------------------------------------------------------------------------

def pytest_collection_modifyitems(items):
    """Skip ALL integration tests when the .h5 model file is absent."""
    if MODEL_PATH.exists():
        return
    skip = pytest.mark.skip(reason=f"Real model not found: {MODEL_PATH}")
    for item in items:
        if item.get_closest_marker("integration"):
            item.add_marker(skip)


# ---------------------------------------------------------------------------
# Real TestClient — lifespan loads the actual model
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def real_client():
    """
    A Starlette TestClient backed by the real Keras model.
    The FastAPI lifespan runs on enter, so model_registry.load() is called
    with the actual .h5 file.  Session-scoped so the model loads only once.
    """
    import app.services.model_loader as ml
    from fastapi.testclient import TestClient
    from app.main import app

    # Clear any mock context injected by prior unit tests in the same session.
    ml.model_registry._ctx = None

    with TestClient(app) as c:
        yield c

    # Restore clean state for any tests that follow.
    ml.model_registry._ctx = None


# ---------------------------------------------------------------------------
# Real image bytes from the test dataset
# ---------------------------------------------------------------------------

def _first_image(label: str) -> bytes:
    label_dir = DATASET_TEST_PATH / label
    imgs = sorted(label_dir.glob("*.jpg"))
    if not imgs:
        pytest.skip(f"No test images found for label '{label}'")
    return imgs[0].read_bytes()


@pytest.fixture(scope="session")
def healthy_image_bytes() -> bytes:
    return _first_image("Healthy")


@pytest.fixture(scope="session")
def powdery_image_bytes() -> bytes:
    return _first_image("Powdery")


@pytest.fixture(scope="session")
def rust_image_bytes() -> bytes:
    return _first_image("Rust")
