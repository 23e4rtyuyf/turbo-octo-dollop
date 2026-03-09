import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestInboundAPI:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "AI Email Router"
        assert data["status"] == "running"

    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_list_rules(self):
        response = client.get("/api/v1/rules/")
        assert response.status_code == 200
        rules = response.json()
        assert "complaint" in rules
        assert "lead" in rules
