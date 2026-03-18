"""Integration tests for the HTTP API with the real Keras model.

These send actual HTTP requests through the full FastAPI stack:
    HTTP request → router → service → real model → response

No components are mocked.
"""
from __future__ import annotations

import json

import pytest

from app.core.constants import CLASS_MAPPING

VALID_CLASSES = set(CLASS_MAPPING.values())


def _file_tuple(data: bytes, name: str = "leaf.jpg"):
    return ("files", (name, data, "image/jpeg"))


# ---------------------------------------------------------------------------
# Health endpoint (real model)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestHealthWithRealModel:
    def test_returns_200(self, real_client):
        assert real_client.get("/api/v1/health").status_code == 200

    def test_model_loaded_is_true(self, real_client):
        assert real_client.get("/api/v1/health").json()["model_loaded"] is True

    def test_status_is_ok(self, real_client):
        assert real_client.get("/api/v1/health").json()["status"] == "ok"


# ---------------------------------------------------------------------------
# POST /api/v1/predict/files  —  real images, real model
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestPredictFilesRealModel:
    def test_healthy_upload_returns_200(self, real_client, healthy_image_bytes):
        r = real_client.post("/api/v1/predict/files", files=[_file_tuple(healthy_image_bytes)])
        assert r.status_code == 200

    def test_healthy_upload_prediction_structure(self, real_client, healthy_image_bytes):
        pred = real_client.post(
            "/api/v1/predict/files", files=[_file_tuple(healthy_image_bytes)]
        ).json()["predictions"][0]
        assert pred["predicted_class"] in VALID_CLASSES
        assert pred["errors"] == []
        assert pred["treatment_suggestion"] is not None
        assert pred["image_preview"].startswith("data:image/jpeg;base64,")

    def test_powdery_upload_returns_valid_class(self, real_client, powdery_image_bytes):
        pred = real_client.post(
            "/api/v1/predict/files", files=[_file_tuple(powdery_image_bytes, "powdery.jpg")]
        ).json()["predictions"][0]
        assert pred["predicted_class"] in VALID_CLASSES
        assert pred["errors"] == []

    def test_rust_upload_returns_valid_class(self, real_client, rust_image_bytes):
        pred = real_client.post(
            "/api/v1/predict/files", files=[_file_tuple(rust_image_bytes, "rust.jpg")]
        ).json()["predictions"][0]
        assert pred["predicted_class"] in VALID_CLASSES
        assert pred["errors"] == []

    def test_batch_upload_three_images(
        self, real_client, healthy_image_bytes, powdery_image_bytes, rust_image_bytes
    ):
        r = real_client.post(
            "/api/v1/predict/files",
            files=[
                _file_tuple(healthy_image_bytes, "healthy.jpg"),
                _file_tuple(powdery_image_bytes, "powdery.jpg"),
                _file_tuple(rust_image_bytes, "rust.jpg"),
            ],
        )
        preds = r.json()["predictions"]
        assert len(preds) == 3
        for pred in preds:
            assert pred["predicted_class"] in VALID_CLASSES
            assert pred["errors"] == []

    def test_probabilities_all_in_unit_range(self, real_client, healthy_image_bytes):
        pred = real_client.post(
            "/api/v1/predict/files", files=[_file_tuple(healthy_image_bytes)]
        ).json()["predictions"][0]
        for p in pred["probabilities"].values():
            assert 0.0 <= p <= 1.0

    def test_probabilities_sum_to_one(self, real_client, healthy_image_bytes):
        pred = real_client.post(
            "/api/v1/predict/files", files=[_file_tuple(healthy_image_bytes)]
        ).json()["predictions"][0]
        total = sum(pred["probabilities"].values())
        assert abs(total - 1.0) < 1e-4

    def test_source_name_preserved(self, real_client, healthy_image_bytes):
        pred = real_client.post(
            "/api/v1/predict/files",
            files=[_file_tuple(healthy_image_bytes, "myplant.jpg")],
        ).json()["predictions"][0]
        assert pred["source_name"] == "myplant.jpg"

    def test_ids_unique_in_batch(
        self, real_client, healthy_image_bytes, powdery_image_bytes
    ):
        preds = real_client.post(
            "/api/v1/predict/files",
            files=[
                _file_tuple(healthy_image_bytes, "a.jpg"),
                _file_tuple(powdery_image_bytes, "b.jpg"),
            ],
        ).json()["predictions"]
        ids = [p["id"] for p in preds]
        assert len(ids) == len(set(ids))

    def test_corrupt_file_returns_error_not_500(self, real_client):
        r = real_client.post(
            "/api/v1/predict/files",
            files=[_file_tuple(b"not-an-image-at-all", "broken.jpg")],
        )
        assert r.status_code == 200
        pred = r.json()["predictions"][0]
        assert pred["predicted_class"] is None
        assert len(pred["errors"]) > 0


# ---------------------------------------------------------------------------
# POST /api/v1/predict/mixed  —  real file, no URL fetch
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestPredictMixedRealModel:
    def test_file_only_mixed(self, real_client, healthy_image_bytes):
        r = real_client.post(
            "/api/v1/predict/mixed",
            data={"urls_json": "[]"},
            files=[_file_tuple(healthy_image_bytes)],
        )
        assert r.status_code == 200
        pred = r.json()["predictions"][0]
        assert pred["predicted_class"] in VALID_CLASSES

    def test_empty_mixed_returns_empty(self, real_client):
        r = real_client.post("/api/v1/predict/mixed", data={"urls_json": "[]"})
        assert r.status_code == 200
        assert r.json()["predictions"] == []


# ---------------------------------------------------------------------------
# POST /api/v1/reports/csv  —  real predictions from model
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestCsvReportRealPredictions:
    def test_csv_report_from_real_prediction(self, real_client, healthy_image_bytes):
        # Step 1: get a real prediction
        pred = real_client.post(
            "/api/v1/predict/files", files=[_file_tuple(healthy_image_bytes)]
        ).json()["predictions"][0]

        # Step 2: generate CSV from it
        r = real_client.post(
            "/api/v1/reports/csv",
            json={"predictions": [pred], "ai_data": {}},
        )
        assert r.status_code == 200
        text = r.content.decode("utf-8-sig")
        assert "Name/Source" in text
        assert pred["source_name"] in text

    def test_csv_contains_all_three_labels(
        self, real_client, healthy_image_bytes, powdery_image_bytes, rust_image_bytes
    ):
        preds = real_client.post(
            "/api/v1/predict/files",
            files=[
                _file_tuple(healthy_image_bytes, "h.jpg"),
                _file_tuple(powdery_image_bytes, "p.jpg"),
                _file_tuple(rust_image_bytes, "r.jpg"),
            ],
        ).json()["predictions"]

        r = real_client.post(
            "/api/v1/reports/csv",
            json={"predictions": preds, "ai_data": {}},
        )
        assert r.status_code == 200
        import csv, io
        rows = list(csv.DictReader(io.StringIO(r.content.decode("utf-8-sig"))))
        assert len(rows) == 3
