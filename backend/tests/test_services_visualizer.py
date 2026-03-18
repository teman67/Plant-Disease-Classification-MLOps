"""Tests for app/services/visualizer.py"""
from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from app.services.visualizer import build_montage, list_visualizer_assets


def _write_test_images(directory: Path, count: int = 6) -> None:
    """Write `count` tiny JPEG images to `directory`."""
    directory.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        img = Image.new("RGB", (32, 32), color=(i * 30, 100, 150))
        img.save(directory / f"plant_{i}.jpg", format="JPEG")


# ---------------------------------------------------------------------------
# list_visualizer_assets
# ---------------------------------------------------------------------------

class TestListVisualizerAssets:
    def test_returns_list(self):
        result = list_visualizer_assets()
        assert isinstance(result, list)

    def test_missing_directory_returns_empty_list(self, tmp_path):
        from app.core.config import get_settings
        s = get_settings()
        original = s.visualizer_assets_path
        s.visualizer_assets_path = tmp_path / "nonexistent"
        try:
            result = list_visualizer_assets()
            assert result == []
        finally:
            s.visualizer_assets_path = original

    def test_image_entries_have_name_and_url(self, tmp_path):
        asset_dir = tmp_path / "v1"
        _write_test_images(asset_dir, count=2)

        from app.core.config import get_settings
        s = get_settings()
        original = s.visualizer_assets_path
        s.visualizer_assets_path = asset_dir
        try:
            result = list_visualizer_assets()
            assert len(result) == 2
            for entry in result:
                assert "name" in entry
                assert "url" in entry
                assert entry["url"].startswith("/static/")
        finally:
            s.visualizer_assets_path = original

    def test_non_image_files_excluded(self, tmp_path):
        asset_dir = tmp_path / "v1"
        asset_dir.mkdir()
        (asset_dir / "readme.txt").write_text("ignore me")
        img = Image.new("RGB", (32, 32), color=(0, 0, 0))
        img.save(asset_dir / "plant.png")

        from app.core.config import get_settings
        s = get_settings()
        original = s.visualizer_assets_path
        s.visualizer_assets_path = asset_dir
        try:
            result = list_visualizer_assets()
            names = [e["name"] for e in result]
            assert "plant.png" in names
            assert "readme.txt" not in names
        finally:
            s.visualizer_assets_path = original


# ---------------------------------------------------------------------------
# build_montage
# ---------------------------------------------------------------------------

class TestBuildMontage:
    def test_returns_bytes(self, tmp_path):
        label_dir = tmp_path / "Healthy"
        _write_test_images(label_dir, count=9)

        from app.core.config import get_settings
        s = get_settings()
        original = s.dataset_test_path
        s.dataset_test_path = tmp_path
        try:
            result = build_montage("Healthy", rows=3, cols=3)
            assert isinstance(result, bytes)
            assert len(result) > 0
        finally:
            s.dataset_test_path = original

    def test_output_is_valid_png(self, tmp_path):
        label_dir = tmp_path / "Rust"
        _write_test_images(label_dir, count=4)

        from app.core.config import get_settings
        s = get_settings()
        original = s.dataset_test_path
        s.dataset_test_path = tmp_path
        try:
            result = build_montage("Rust", rows=2, cols=2)
            img = Image.open(io.BytesIO(result))
            assert img.format == "PNG"
        finally:
            s.dataset_test_path = original

    def test_missing_label_directory_raises(self, tmp_path):
        from app.core.config import get_settings
        s = get_settings()
        original = s.dataset_test_path
        s.dataset_test_path = tmp_path
        try:
            with pytest.raises(FileNotFoundError):
                build_montage("Nonexistent")
        finally:
            s.dataset_test_path = original

    def test_empty_label_directory_raises(self, tmp_path):
        label_dir = tmp_path / "Empty"
        label_dir.mkdir()

        from app.core.config import get_settings
        s = get_settings()
        original = s.dataset_test_path
        s.dataset_test_path = tmp_path
        try:
            with pytest.raises(FileNotFoundError, match="No images found"):
                build_montage("Empty")
        finally:
            s.dataset_test_path = original

    def test_fewer_images_than_grid_size(self, tmp_path):
        label_dir = tmp_path / "Powdery"
        _write_test_images(label_dir, count=2)

        from app.core.config import get_settings
        s = get_settings()
        original = s.dataset_test_path
        s.dataset_test_path = tmp_path
        try:
            # Request 3×3 but only 2 images available – should still succeed
            result = build_montage("Powdery", rows=3, cols=3)
            assert isinstance(result, bytes)
        finally:
            s.dataset_test_path = original
