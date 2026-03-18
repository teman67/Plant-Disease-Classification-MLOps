"""Tests for GET /api/v1/health"""
from __future__ import annotations


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        r = client.get("/api/v1/health")
        assert r.status_code == 200

    def test_health_status_ok(self, client):
        r = client.get("/api/v1/health")
        assert r.json()["status"] == "ok"

    def test_health_contains_version(self, client):
        r = client.get("/api/v1/health")
        assert "version" in r.json()

    def test_health_model_loaded_true(self, client):
        r = client.get("/api/v1/health")
        assert r.json()["model_loaded"] is True

    def test_root_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_root_contains_docs_link(self, client):
        r = client.get("/")
        assert "docs" in r.json()
