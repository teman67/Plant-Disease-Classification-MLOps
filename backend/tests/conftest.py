"""Shared fixtures for the entire test suite.

The key challenge is that the Keras model is a large binary artifact that
we must NOT load during tests.  We solve this by setting
``model_registry._ctx`` to a mock ``ModelContext`` before the FastAPI
lifespan runs, so ``model_registry.load()`` returns early without ever
touching the filesystem.
"""
from __future__ import annotations

import io

import numpy as np
import pytest
from PIL import Image
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Tiny in-memory images used across many tests
# ---------------------------------------------------------------------------

def _make_rgb_bytes(fmt: str = "JPEG", size: tuple[int, int] = (64, 64)) -> bytes:
    img = Image.new("RGB", size, color=(80, 120, 200))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


@pytest.fixture(scope="session")
def jpeg_bytes() -> bytes:
    """64×64 solid-colour JPEG."""
    return _make_rgb_bytes("JPEG")


@pytest.fixture(scope="session")
def png_bytes() -> bytes:
    """64×64 solid-colour PNG."""
    return _make_rgb_bytes("PNG")


@pytest.fixture(scope="session")
def rgba_png_bytes() -> bytes:
    """64×64 RGBA PNG (exercises RGB-conversion path)."""
    img = Image.new("RGBA", (64, 64), color=(80, 120, 200, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Mock model context (session-scoped – immutable so safe to share)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def mock_model_ctx():
    """A ModelContext whose model.predict always returns 'Healthy' (class 0)."""
    from app.services.model_loader import ModelContext

    mock_model = MagicMock()
    # shape (1, 3) – three disease classes
    mock_model.predict.return_value = np.array([[0.85, 0.10, 0.05]])
    return ModelContext(model=mock_model, image_shape=(64, 64, 3))


# ---------------------------------------------------------------------------
# TestClient with model mocked out
# ---------------------------------------------------------------------------

@pytest.fixture
def client(mock_model_ctx):
    """
    A Starlette TestClient with:
    - model_registry pre-loaded with a mock context (no .h5 read)
    - full lifespan/middleware stack active
    """
    from app.services import model_loader
    from fastapi.testclient import TestClient
    from app.main import app

    original_ctx = model_loader.model_registry._ctx
    model_loader.model_registry._ctx = mock_model_ctx
    try:
        with TestClient(app) as c:
            yield c
    finally:
        model_loader.model_registry._ctx = original_ctx
