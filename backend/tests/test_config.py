"""Tests for app/core/config.py and app/core/constants.py"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.core.constants import (
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_IMAGE_MIME_TYPES,
    CLASS_MAPPING,
    TREATMENT_SUGGESTIONS,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestClassMapping:
    def test_has_three_classes(self):
        assert len(CLASS_MAPPING) == 3

    def test_class_names(self):
        assert CLASS_MAPPING[0] == "Healthy"
        assert CLASS_MAPPING[1] == "Powdery"
        assert CLASS_MAPPING[2] == "Rust"

    def test_indices_are_integers(self):
        assert all(isinstance(k, int) for k in CLASS_MAPPING)


class TestTreatmentSuggestions:
    def test_all_classes_have_suggestions(self):
        for name in CLASS_MAPPING.values():
            assert name in TREATMENT_SUGGESTIONS

    def test_healthy_suggestion(self):
        assert "No treatment" in TREATMENT_SUGGESTIONS["Healthy"]

    def test_powdery_suggestion_not_empty(self):
        assert len(TREATMENT_SUGGESTIONS["Powdery"]) > 0

    def test_rust_suggestion_not_empty(self):
        assert len(TREATMENT_SUGGESTIONS["Rust"]) > 0


class TestAllowedImageTypes:
    def test_jpg_extension_allowed(self):
        assert ".jpg" in ALLOWED_IMAGE_EXTENSIONS

    def test_jpeg_extension_allowed(self):
        assert ".jpeg" in ALLOWED_IMAGE_EXTENSIONS

    def test_png_extension_allowed(self):
        assert ".png" in ALLOWED_IMAGE_EXTENSIONS

    def test_jpeg_mime_allowed(self):
        assert "image/jpeg" in ALLOWED_IMAGE_MIME_TYPES

    def test_png_mime_allowed(self):
        assert "image/png" in ALLOWED_IMAGE_MIME_TYPES


# ---------------------------------------------------------------------------
# Settings / get_settings
# ---------------------------------------------------------------------------

class TestSettings:
    def test_get_settings_returns_settings(self):
        from app.core.config import Settings, get_settings
        s = get_settings()
        assert isinstance(s, Settings)

    def test_get_settings_is_cached(self):
        from app.core.config import get_settings
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_default_app_name(self):
        from app.core.config import get_settings
        s = get_settings()
        assert "Plant" in s.app_name

    def test_default_version_string(self):
        from app.core.config import get_settings
        s = get_settings()
        assert isinstance(s.app_version, str)
        assert len(s.app_version) > 0

    def test_model_path_is_path_object(self):
        from app.core.config import get_settings
        s = get_settings()
        assert isinstance(s.model_path, Path)

    def test_max_upload_size_positive(self):
        from app.core.config import get_settings
        s = get_settings()
        assert s.max_upload_size_mb > 0

    def test_max_files_per_request_positive(self):
        from app.core.config import get_settings
        s = get_settings()
        assert s.max_files_per_request > 0

    def test_max_urls_per_request_positive(self):
        from app.core.config import get_settings
        s = get_settings()
        assert s.max_urls_per_request > 0

    def test_allowed_origins_is_list(self):
        from app.core.config import get_settings
        s = get_settings()
        assert isinstance(s.allowed_origins, list)

    def test_from_env_overrides_app_name(self):
        """Settings.from_env() reads APP_NAME from environment."""
        from app.core.config import Settings
        os.environ["APP_NAME"] = "Test App Name"
        try:
            s = Settings.from_env()
            assert s.app_name == "Test App Name"
        finally:
            del os.environ["APP_NAME"]

    def test_from_env_overrides_max_upload(self):
        from app.core.config import Settings
        os.environ["MAX_UPLOAD_SIZE_MB"] = "25"
        try:
            s = Settings.from_env()
            assert s.max_upload_size_mb == 25
        finally:
            del os.environ["MAX_UPLOAD_SIZE_MB"]

    def test_from_env_parses_allowed_origins(self):
        from app.core.config import Settings
        os.environ["ALLOWED_ORIGINS"] = "https://app.example.com,https://admin.example.com"
        try:
            s = Settings.from_env()
            assert "https://app.example.com" in s.allowed_origins
            assert "https://admin.example.com" in s.allowed_origins
        finally:
            del os.environ["ALLOWED_ORIGINS"]
