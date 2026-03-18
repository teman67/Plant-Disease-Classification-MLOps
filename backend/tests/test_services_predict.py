"""Tests for app/services/predict.py"""
from __future__ import annotations

import io
import socket
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from PIL import Image

from app.services.predict import (
    InputItem,
    _is_public_hostname,
    _make_thumbnail_data_url,
    filename_or_fallback,
    predict_input_item,
    validate_url,
)


# ---------------------------------------------------------------------------
# filename_or_fallback
# ---------------------------------------------------------------------------

class TestFilenameOrFallback:
    def test_none_returns_indexed_default(self):
        assert filename_or_fallback(None, 0) == "image_1.png"

    def test_empty_string_returns_indexed_default(self):
        assert filename_or_fallback("", 2) == "image_3.png"

    def test_simple_filename_returned_as_is(self):
        assert filename_or_fallback("leaf.jpg", 0) == "leaf.jpg"

    def test_strips_directory_components(self):
        assert filename_or_fallback("/uploads/plants/leaf.jpg", 0) == "leaf.jpg"

    def test_windows_path_stripped(self):
        result = filename_or_fallback("C:\\Users\\User\\leaf.png", 0)
        assert result == "leaf.png"

    def test_index_zero_based(self):
        assert filename_or_fallback(None, 4) == "image_5.png"


# ---------------------------------------------------------------------------
# _is_public_hostname
# ---------------------------------------------------------------------------

class TestIsPublicHostname:
    def test_private_ip_returns_false(self):
        with patch("socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [(None, None, None, None, ("192.168.1.1", 0))]
            assert _is_public_hostname("private-host") is False

    def test_loopback_returns_false(self):
        with patch("socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [(None, None, None, None, ("127.0.0.1", 0))]
            assert _is_public_hostname("localhost") is False

    def test_public_ip_returns_true(self):
        with patch("socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [(None, None, None, None, ("142.250.80.46", 0))]
            assert _is_public_hostname("google.com") is True

    def test_dns_failure_returns_false(self):
        with patch("socket.getaddrinfo", side_effect=socket.gaierror):
            assert _is_public_hostname("bad-host") is False

    def test_link_local_returns_false(self):
        with patch("socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [(None, None, None, None, ("169.254.0.1", 0))]
            assert _is_public_hostname("link-local") is False


# ---------------------------------------------------------------------------
# validate_url
# ---------------------------------------------------------------------------

class TestValidateUrl:
    def _public_gai(self, *args, **kwargs):
        return [(None, None, None, None, ("142.250.80.46", 0))]

    def test_valid_https_url_passes(self):
        with patch("socket.getaddrinfo", side_effect=self._public_gai):
            validate_url("https://example.com/image.jpg")  # should not raise

    def test_valid_http_url_passes(self):
        with patch("socket.getaddrinfo", side_effect=self._public_gai):
            validate_url("http://example.com/image.jpg")

    def test_ftp_scheme_raises(self):
        with pytest.raises(ValueError, match="http/https"):
            validate_url("ftp://example.com/image.jpg")

    def test_file_scheme_raises(self):
        with pytest.raises(ValueError, match="http/https"):
            validate_url("file:///etc/passwd")

    def test_localhost_raises(self):
        with patch("socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [(None, None, None, None, ("127.0.0.1", 0))]
            with pytest.raises(ValueError, match="not allowed"):
                validate_url("http://localhost/image.jpg")

    def test_private_ip_raises(self):
        with patch("socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [(None, None, None, None, ("10.0.0.1", 0))]
            with pytest.raises(ValueError, match="not allowed"):
                validate_url("http://internal/image.jpg")


# ---------------------------------------------------------------------------
# _make_thumbnail_data_url
# ---------------------------------------------------------------------------

class TestMakeThumbnailDataUrl:
    def test_valid_jpeg_returns_data_url(self, jpeg_bytes):
        result = _make_thumbnail_data_url(jpeg_bytes)
        assert result is not None
        assert result.startswith("data:image/jpeg;base64,")

    def test_valid_png_returns_data_url(self, png_bytes):
        result = _make_thumbnail_data_url(png_bytes)
        assert result is not None
        assert result.startswith("data:image/jpeg;base64,")

    def test_invalid_bytes_returns_none(self):
        result = _make_thumbnail_data_url(b"garbage")
        assert result is None

    def test_empty_bytes_returns_none(self):
        result = _make_thumbnail_data_url(b"")
        assert result is None

    def test_rgba_image_converted_before_saving(self, rgba_png_bytes):
        # RGBA → RGB conversion must succeed without raising
        result = _make_thumbnail_data_url(rgba_png_bytes)
        assert result is not None


# ---------------------------------------------------------------------------
# predict_input_item
# ---------------------------------------------------------------------------

class TestPredictInputItem:
    def _make_item(self, payload: bytes, source_type: str = "file") -> InputItem:
        return InputItem(source_type=source_type, source_name="test.jpg", payload=payload)

    def test_success_returns_healthy_class(self, jpeg_bytes, mock_model_ctx):
        from app.services import model_loader

        original_ctx = model_loader.model_registry._ctx
        model_loader.model_registry._ctx = mock_model_ctx
        try:
            result = predict_input_item(self._make_item(jpeg_bytes), item_id="t-1")
        finally:
            model_loader.model_registry._ctx = original_ctx

        assert result.predicted_class == "Healthy"
        assert result.errors == []
        assert result.id == "t-1"
        assert result.treatment_suggestion is not None

    def test_probabilities_sum_to_one(self, jpeg_bytes, mock_model_ctx):
        from app.services import model_loader

        original_ctx = model_loader.model_registry._ctx
        model_loader.model_registry._ctx = mock_model_ctx
        try:
            result = predict_input_item(self._make_item(jpeg_bytes), item_id="t-2")
        finally:
            model_loader.model_registry._ctx = original_ctx

        total = sum(result.probabilities.values())
        assert abs(total - 1.0) < 1e-5

    def test_invalid_payload_returns_errors(self, mock_model_ctx):
        from app.services import model_loader

        original_ctx = model_loader.model_registry._ctx
        model_loader.model_registry._ctx = mock_model_ctx
        try:
            result = predict_input_item(self._make_item(b"not-an-image"), item_id="t-3")
        finally:
            model_loader.model_registry._ctx = original_ctx

        assert result.predicted_class is None
        assert len(result.errors) > 0

    def test_source_metadata_preserved(self, jpeg_bytes, mock_model_ctx):
        from app.services import model_loader

        original_ctx = model_loader.model_registry._ctx
        model_loader.model_registry._ctx = mock_model_ctx
        try:
            item = InputItem(source_type="url", source_name="https://example.com/leaf.jpg", payload=jpeg_bytes)
            result = predict_input_item(item, item_id="t-4")
        finally:
            model_loader.model_registry._ctx = original_ctx

        assert result.source_type == "url"
        assert result.source_name == "https://example.com/leaf.jpg"

    def test_rgba_input_sets_rgb_converted(self, rgba_png_bytes, mock_model_ctx):
        from app.services import model_loader

        original_ctx = model_loader.model_registry._ctx
        model_loader.model_registry._ctx = mock_model_ctx
        try:
            result = predict_input_item(self._make_item(rgba_png_bytes), item_id="t-5")
        finally:
            model_loader.model_registry._ctx = original_ctx

        assert result.rgb_converted is True

    def test_image_preview_attached(self, jpeg_bytes, mock_model_ctx):
        from app.services import model_loader

        original_ctx = model_loader.model_registry._ctx
        model_loader.model_registry._ctx = mock_model_ctx
        try:
            result = predict_input_item(self._make_item(jpeg_bytes), item_id="t-6")
        finally:
            model_loader.model_registry._ctx = original_ctx

        assert result.image_preview is not None
        assert result.image_preview.startswith("data:image/jpeg;base64,")
