"""Tests for /api/v1/predict/files, /predict/urls, and /predict/mixed"""
from __future__ import annotations

import json
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _file_tuple(data: bytes, name: str = "leaf.jpg", mime: str = "image/jpeg"):
    return ("files", (name, data, mime))


# ---------------------------------------------------------------------------
# POST /api/v1/predict/files
# ---------------------------------------------------------------------------

class TestPredictFiles:
    def test_single_valid_image_returns_200(self, client, jpeg_bytes):
        r = client.post("/api/v1/predict/files", files=[_file_tuple(jpeg_bytes)])
        assert r.status_code == 200

    def test_response_schema(self, client, jpeg_bytes):
        r = client.post("/api/v1/predict/files", files=[_file_tuple(jpeg_bytes)])
        body = r.json()
        assert "predictions" in body
        assert len(body["predictions"]) == 1

    def test_prediction_fields_present(self, client, jpeg_bytes):
        r = client.post("/api/v1/predict/files", files=[_file_tuple(jpeg_bytes)])
        pred = r.json()["predictions"][0]
        assert "id" in pred
        assert "predicted_class" in pred
        assert "probabilities" in pred
        assert "treatment_suggestion" in pred
        assert "errors" in pred

    def test_prediction_class_is_healthy(self, client, jpeg_bytes):
        # Mock model always returns [0.85, 0.10, 0.05] → class 0 = Healthy
        r = client.post("/api/v1/predict/files", files=[_file_tuple(jpeg_bytes)])
        assert r.json()["predictions"][0]["predicted_class"] == "Healthy"

    def test_multiple_files_returned(self, client, jpeg_bytes, png_bytes):
        r = client.post(
            "/api/v1/predict/files",
            files=[_file_tuple(jpeg_bytes, "a.jpg"), _file_tuple(png_bytes, "b.png", "image/png")],
        )
        assert len(r.json()["predictions"]) == 2

    def test_ids_are_unique(self, client, jpeg_bytes, png_bytes):
        r = client.post(
            "/api/v1/predict/files",
            files=[_file_tuple(jpeg_bytes, "a.jpg"), _file_tuple(png_bytes, "b.png", "image/png")],
        )
        ids = [p["id"] for p in r.json()["predictions"]]
        assert len(ids) == len(set(ids))

    def test_too_many_files_returns_400(self, client, jpeg_bytes):
        from app.core.config import get_settings
        limit = get_settings().max_files_per_request
        files = [_file_tuple(jpeg_bytes, f"f{i}.jpg") for i in range(limit + 1)]
        r = client.post("/api/v1/predict/files", files=files)
        assert r.status_code == 400
        assert "Too many files" in r.json()["detail"]

    def test_file_too_large_returns_413(self, client):
        from app.core.config import get_settings
        limit_bytes = get_settings().max_upload_size_mb * 1024 * 1024
        oversized = b"x" * (limit_bytes + 1)
        r = client.post("/api/v1/predict/files", files=[_file_tuple(oversized)])
        assert r.status_code == 413

    def test_invalid_image_bytes_returns_errors_in_result(self, client):
        r = client.post("/api/v1/predict/files", files=[_file_tuple(b"not-an-image-at-all")])
        assert r.status_code == 200
        pred = r.json()["predictions"][0]
        assert len(pred["errors"]) > 0
        assert pred["predicted_class"] is None

    def test_rgba_image_sets_rgb_converted(self, client, rgba_png_bytes):
        r = client.post(
            "/api/v1/predict/files",
            files=[_file_tuple(rgba_png_bytes, "rgba.png", "image/png")],
        )
        pred = r.json()["predictions"][0]
        assert pred["rgb_converted"] is True

    def test_source_type_is_file(self, client, jpeg_bytes):
        r = client.post("/api/v1/predict/files", files=[_file_tuple(jpeg_bytes)])
        assert r.json()["predictions"][0]["source_type"] == "file"


# ---------------------------------------------------------------------------
# POST /api/v1/predict/urls
# ---------------------------------------------------------------------------

class TestPredictUrls:
    def test_valid_url_returns_200(self, client, jpeg_bytes):
        with patch("app.api.routes.fetch_url_image", return_value=jpeg_bytes):
            r = client.post(
                "/api/v1/predict/urls",
                json={"urls": ["https://example.com/leaf.jpg"]},
            )
        assert r.status_code == 200

    def test_response_has_one_prediction(self, client, jpeg_bytes):
        with patch("app.api.routes.fetch_url_image", return_value=jpeg_bytes):
            r = client.post(
                "/api/v1/predict/urls",
                json={"urls": ["https://example.com/leaf.jpg"]},
            )
        assert len(r.json()["predictions"]) == 1

    def test_prediction_class_correct(self, client, jpeg_bytes):
        with patch("app.api.routes.fetch_url_image", return_value=jpeg_bytes):
            r = client.post(
                "/api/v1/predict/urls",
                json={"urls": ["https://example.com/leaf.jpg"]},
            )
        assert r.json()["predictions"][0]["predicted_class"] == "Healthy"

    def test_source_type_is_url(self, client, jpeg_bytes):
        url = "https://example.com/leaf.jpg"
        with patch("app.api.routes.fetch_url_image", return_value=jpeg_bytes):
            r = client.post("/api/v1/predict/urls", json={"urls": [url]})
        assert r.json()["predictions"][0]["source_type"] == "url"

    def test_too_many_urls_returns_400(self, client, jpeg_bytes):
        from app.core.config import get_settings
        limit = get_settings().max_urls_per_request
        urls = [f"https://example.com/leaf_{i}.jpg" for i in range(limit + 1)]
        with patch("app.api.routes.fetch_url_image", return_value=jpeg_bytes):
            r = client.post("/api/v1/predict/urls", json={"urls": urls})
        assert r.status_code == 400
        assert "Too many URLs" in r.json()["detail"]

    def test_fetch_error_recorded_in_prediction(self, client):
        with patch("app.api.routes.fetch_url_image", side_effect=ValueError("fetch failed")):
            r = client.post(
                "/api/v1/predict/urls",
                json={"urls": ["https://example.com/broken.jpg"]},
            )
        assert r.status_code == 200
        pred = r.json()["predictions"][0]
        assert len(pred["errors"]) > 0

    def test_multiple_urls_returned(self, client, jpeg_bytes):
        with patch("app.api.routes.fetch_url_image", return_value=jpeg_bytes):
            r = client.post(
                "/api/v1/predict/urls",
                json={
                    "urls": [
                        "https://example.com/leaf1.jpg",
                        "https://example.com/leaf2.jpg",
                    ]
                },
            )
        assert len(r.json()["predictions"]) == 2

    def test_empty_url_list_returns_empty_predictions(self, client):
        r = client.post("/api/v1/predict/urls", json={"urls": []})
        assert r.status_code == 200
        assert r.json()["predictions"] == []


# ---------------------------------------------------------------------------
# POST /api/v1/predict/mixed
# ---------------------------------------------------------------------------

class TestPredictMixed:
    def test_file_and_url_combined(self, client, jpeg_bytes):
        with patch("app.api.routes.fetch_url_image", return_value=jpeg_bytes):
            r = client.post(
                "/api/v1/predict/mixed",
                data={"urls_json": json.dumps(["https://example.com/leaf.jpg"])},
                files=[_file_tuple(jpeg_bytes)],
            )
        assert r.status_code == 200
        assert len(r.json()["predictions"]) == 2

    def test_file_only(self, client, jpeg_bytes):
        r = client.post(
            "/api/v1/predict/mixed",
            data={"urls_json": "[]"},
            files=[_file_tuple(jpeg_bytes)],
        )
        assert r.status_code == 200
        assert len(r.json()["predictions"]) == 1

    def test_url_only(self, client, jpeg_bytes):
        with patch("app.api.routes.fetch_url_image", return_value=jpeg_bytes):
            r = client.post(
                "/api/v1/predict/mixed",
                data={"urls_json": json.dumps(["https://example.com/leaf.jpg"])},
            )
        assert r.status_code == 200
        assert len(r.json()["predictions"]) == 1

    def test_invalid_urls_json_returns_400(self, client, jpeg_bytes):
        r = client.post(
            "/api/v1/predict/mixed",
            data={"urls_json": "not-valid-json"},
            files=[_file_tuple(jpeg_bytes)],
        )
        assert r.status_code == 400

    def test_urls_json_not_array_returns_400(self, client, jpeg_bytes):
        r = client.post(
            "/api/v1/predict/mixed",
            data={"urls_json": json.dumps({"key": "value"})},
            files=[_file_tuple(jpeg_bytes)],
        )
        assert r.status_code == 400

    def test_ids_prefixed_correctly(self, client, jpeg_bytes):
        with patch("app.api.routes.fetch_url_image", return_value=jpeg_bytes):
            r = client.post(
                "/api/v1/predict/mixed",
                data={"urls_json": json.dumps(["https://example.com/leaf.jpg"])},
                files=[_file_tuple(jpeg_bytes)],
            )
        ids = [p["id"] for p in r.json()["predictions"]]
        assert any("mixed-file" in i for i in ids)
        assert any("mixed-url" in i for i in ids)
