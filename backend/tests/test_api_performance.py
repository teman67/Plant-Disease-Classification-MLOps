"""Tests for GET /api/v1/performance/summary"""
from __future__ import annotations

from unittest.mock import patch

import numpy as np


class TestPerformanceSummaryEndpoint:
    def test_returns_200(self, client):
        r = client.get("/api/v1/performance/summary")
        assert r.status_code == 200

    def test_response_is_json(self, client):
        r = client.get("/api/v1/performance/summary")
        assert r.headers["content-type"].startswith("application/json")

    def test_response_has_required_keys(self, client):
        r = client.get("/api/v1/performance/summary")
        body = r.json()
        assert "confusion_matrix" in body
        assert "metrics" in body
        assert "evaluation" in body

    def test_evaluation_has_loss_and_accuracy(self, client):
        r = client.get("/api/v1/performance/summary")
        evaluation = r.json()["evaluation"]
        assert "loss" in evaluation
        assert "accuracy" in evaluation

    def test_with_mocked_summary(self, client):
        """Verify the route correctly passes through the service return value."""
        fake_summary = {
            "confusion_matrix": [[10, 0, 0], [0, 8, 0], [0, 0, 9]],
            "metrics": {"accuracy": 0.95},
            "evaluation": {"loss": 0.15, "accuracy": 0.95},
        }
        with patch("app.api.routes.get_performance_summary", return_value=fake_summary):
            r = client.get("/api/v1/performance/summary")
        assert r.status_code == 200
        body = r.json()
        assert body["evaluation"]["accuracy"] == 0.95
        assert body["evaluation"]["loss"] == 0.15
