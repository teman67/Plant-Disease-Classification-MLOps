"""Tests for app/services/preprocess.py"""
from __future__ import annotations

import io

import numpy as np
import pytest
from PIL import Image

from app.services.preprocess import load_pil_from_bytes, normalize_image


# ---------------------------------------------------------------------------
# load_pil_from_bytes
# ---------------------------------------------------------------------------

class TestLoadPilFromBytes:
    def test_valid_jpeg(self, jpeg_bytes):
        img = load_pil_from_bytes(jpeg_bytes)
        assert img is not None
        assert img.size == (64, 64)

    def test_valid_png(self, png_bytes):
        img = load_pil_from_bytes(png_bytes)
        assert img.size == (64, 64)

    def test_rgba_png(self, rgba_png_bytes):
        img = load_pil_from_bytes(rgba_png_bytes)
        assert img.mode == "RGBA"

    def test_invalid_bytes_raises_value_error(self):
        with pytest.raises(ValueError, match="Unsupported or corrupt"):
            load_pil_from_bytes(b"not an image at all")

    def test_empty_bytes_raises_value_error(self):
        with pytest.raises(ValueError):
            load_pil_from_bytes(b"")


# ---------------------------------------------------------------------------
# normalize_image
# ---------------------------------------------------------------------------

class TestNormalizeImage:
    def _rgb_img(self, size: tuple[int, int] = (32, 32)) -> Image.Image:
        return Image.new("RGB", size, color=(100, 150, 200))

    def _rgba_img(self) -> Image.Image:
        return Image.new("RGBA", (32, 32), color=(100, 150, 200, 255))

    def _grayscale_img(self) -> Image.Image:
        return Image.new("L", (32, 32), color=128)

    def test_rgb_no_conversion(self):
        img = self._rgb_img()
        _, rgb_converted = normalize_image(img, (64, 64, 3))
        assert rgb_converted is False

    def test_rgba_converted_to_rgb(self):
        img = self._rgba_img()
        _, rgb_converted = normalize_image(img, (64, 64, 3))
        assert rgb_converted is True

    def test_grayscale_converted_to_rgb(self):
        img = self._grayscale_img()
        _, rgb_converted = normalize_image(img, (64, 64, 3))
        assert rgb_converted is True

    def test_output_shape(self):
        img = self._rgb_img()
        x, _ = normalize_image(img, (64, 64, 3))
        assert x.shape == (1, 64, 64, 3)

    def test_pixel_values_in_unit_range(self):
        img = self._rgb_img()
        x, _ = normalize_image(img, (64, 64, 3))
        assert float(x.min()) >= 0.0
        assert float(x.max()) <= 1.0

    def test_output_dtype_float32(self):
        img = self._rgb_img()
        x, _ = normalize_image(img, (64, 64, 3))
        assert x.dtype == np.float32

    def test_resizes_to_target_dimensions(self):
        img = self._rgb_img(size=(128, 128))
        x, _ = normalize_image(img, (32, 40, 3))
        # height=32, width=40
        assert x.shape == (1, 32, 40, 3)
