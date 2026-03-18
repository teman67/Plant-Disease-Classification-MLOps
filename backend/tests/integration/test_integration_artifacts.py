"""Integration tests for real on-disk artifacts.

Verifies that joblib / pkl files load correctly and their contents are
semantically valid (correct shapes, value ranges, expected keys).
Tests the /performance/summary endpoint with real data.
Tests the visualizer service against the real dataset.
"""
from __future__ import annotations

import joblib
import numpy as np
import pytest

from tests.integration.conftest import (
    CONFUSION_MATRIX_PATH,
    DATASET_TEST_PATH,
    IMAGE_SHAPE_PATH,
    METRICS_PATH,
)


# ---------------------------------------------------------------------------
# image_shape.pkl
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestImageShapeArtifact:
    def test_image_shape_file_loads(self):
        shape = joblib.load(str(IMAGE_SHAPE_PATH))
        assert shape is not None

    def test_image_shape_has_three_dims(self):
        shape = joblib.load(str(IMAGE_SHAPE_PATH))
        assert len(shape) == 3

    def test_image_shape_channels_is_three(self):
        shape = joblib.load(str(IMAGE_SHAPE_PATH))
        assert shape[2] == 3

    def test_image_shape_spatial_dims_positive(self):
        shape = joblib.load(str(IMAGE_SHAPE_PATH))
        assert shape[0] > 0 and shape[1] > 0


# ---------------------------------------------------------------------------
# confusion_matrix.joblib
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestConfusionMatrixArtifact:
    def _cm(self):
        return joblib.load(str(CONFUSION_MATRIX_PATH))

    def test_confusion_matrix_loads(self):
        assert self._cm() is not None

    def test_confusion_matrix_is_3x3(self):
        cm = np.array(self._cm())
        assert cm.shape == (3, 3)

    def test_confusion_matrix_non_negative(self):
        cm = np.array(self._cm())
        assert (cm >= 0).all()

    def test_confusion_matrix_diagonal_dominant(self):
        """A well-trained model should have most predictions on the diagonal."""
        cm = np.array(self._cm(), dtype=float)
        diagonal_sum = np.trace(cm)
        total = cm.sum()
        assert total > 0
        accuracy = diagonal_sum / total
        assert accuracy >= 0.7, f"Confusion matrix accuracy {accuracy:.2%} < 70%"


# ---------------------------------------------------------------------------
# metrics.joblib
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestMetricsArtifact:
    def _metrics(self):
        return joblib.load(str(METRICS_PATH))

    def test_metrics_loads(self):
        assert self._metrics() is not None

    def test_metrics_is_dict_or_array(self):
        m = self._metrics()
        assert isinstance(m, (dict, list, np.ndarray))

    def test_metrics_accuracy_in_range(self):
        """If metrics is a dict with 'accuracy', it should be 0–1."""
        m = self._metrics()
        if isinstance(m, dict) and "accuracy" in m:
            acc = float(m["accuracy"])
            assert 0.0 <= acc <= 1.0


# ---------------------------------------------------------------------------
# GET /api/v1/performance/summary  —  real artifacts
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestPerformanceSummaryEndpointReal:
    def test_returns_200(self, real_client):
        assert real_client.get("/api/v1/performance/summary").status_code == 200

    def test_confusion_matrix_not_null(self, real_client):
        body = real_client.get("/api/v1/performance/summary").json()
        assert body["confusion_matrix"] is not None

    def test_confusion_matrix_is_3x3(self, real_client):
        cm = real_client.get("/api/v1/performance/summary").json()["confusion_matrix"]
        assert len(cm) == 3
        assert all(len(row) == 3 for row in cm)

    def test_metrics_not_null(self, real_client):
        body = real_client.get("/api/v1/performance/summary").json()
        assert body["metrics"] is not None

    def test_evaluation_accuracy_in_range(self, real_client):
        evaluation = real_client.get("/api/v1/performance/summary").json()["evaluation"]
        acc = evaluation.get("accuracy")
        if acc is not None:
            assert 0.0 <= acc <= 1.0

    def test_evaluation_loss_non_negative(self, real_client):
        evaluation = real_client.get("/api/v1/performance/summary").json()["evaluation"]
        loss = evaluation.get("loss")
        if loss is not None:
            assert loss >= 0.0


# ---------------------------------------------------------------------------
# Visualizer service  —  real dataset images
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestVisualizerRealDataset:
    def test_dataset_test_path_exists(self):
        assert DATASET_TEST_PATH.exists()

    def test_all_three_label_dirs_exist(self):
        for label in ("Healthy", "Powdery", "Rust"):
            assert (DATASET_TEST_PATH / label).is_dir(), f"Missing label dir: {label}"

    def test_each_label_has_images(self):
        for label in ("Healthy", "Powdery", "Rust"):
            images = list((DATASET_TEST_PATH / label).glob("*.jpg"))
            assert len(images) > 0, f"No .jpg images in {label}"

    def test_build_montage_healthy_returns_bytes(self):
        from app.services.visualizer import build_montage
        result = build_montage("Healthy", rows=2, cols=2)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_build_montage_powdery_is_valid_png(self):
        import io
        from PIL import Image
        from app.services.visualizer import build_montage
        result = build_montage("Powdery", rows=2, cols=2)
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"

    def test_build_montage_rust_correct_dimensions(self):
        import io
        from PIL import Image
        from app.services.visualizer import build_montage
        rows, cols = 3, 3
        result = build_montage("Rust", rows=rows, cols=cols)
        img = Image.open(io.BytesIO(result))
        assert img.width > 0 and img.height > 0
        # Each tile has the same size, so the grid dimensions are exact multiples.
        assert img.width % cols == 0, f"Width {img.width} not divisible by cols={cols}"
        assert img.height % rows == 0, f"Height {img.height} not divisible by rows={rows}"

    def test_list_visualizer_assets_returns_entries(self):
        from app.services.visualizer import list_visualizer_assets
        assets = list_visualizer_assets()
        assert isinstance(assets, list)
        assert len(assets) > 0

    def test_visualizer_assets_have_png_url(self):
        from app.services.visualizer import list_visualizer_assets
        assets = list_visualizer_assets()
        for entry in assets:
            assert entry["url"].startswith("/static/")
            assert "name" in entry
