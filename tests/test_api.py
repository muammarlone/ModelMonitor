"""ModelMonitor API regression tests."""
from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from api import app

@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c

class TestHealth:
    def test_health_returns_200(self, client):
        assert client.get("/health").status_code == 200

    def test_health_body(self, client):
        b = client.get("/health").json()
        assert b["status"] == "healthy"
        assert b["service"] == "ModelMonitor"

class TestAnalyze:
    def test_analyze_happy_path(self, client):
        r = client.post("/api/v1/monitor/analyze",
                        json={"intent": "detect data drift in churn prediction model",
                              "workflow_id": "test-wf-001"})
        assert r.status_code == 200

    def test_analyze_response_shape(self, client):
        b = client.post("/api/v1/monitor/analyze",
                        json={"intent": "bias detection in credit scoring model",
                              "workflow_id": "test-wf-002"}).json()
        assert "report_id"           in b
        assert "workflow_id"         in b
        assert "source"              in b
        assert "drift_detected"      in b
        assert "drift_type"          in b
        assert "severity"            in b
        assert "retrain_recommended" in b
        assert "retrain_urgency"     in b
        assert "summary"             in b
        assert "actions"             in b

    def test_drift_detected_is_bool(self, client):
        b = client.post("/api/v1/monitor/analyze",
                        json={"intent": "model drift analysis"}).json()
        assert isinstance(b["drift_detected"], bool)

    def test_retrain_recommended_is_bool(self, client):
        b = client.post("/api/v1/monitor/analyze",
                        json={"intent": "feature drift evaluation"}).json()
        assert isinstance(b["retrain_recommended"], bool)

    def test_severity_is_valid_value(self, client):
        b = client.post("/api/v1/monitor/analyze",
                        json={"intent": "model performance degradation"}).json()
        assert b["severity"] in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "NONE")

    def test_urgency_is_valid_value(self, client):
        b = client.post("/api/v1/monitor/analyze",
                        json={"intent": "retraining trigger for demand forecasting"}).json()
        assert b["retrain_urgency"] in ("IMMEDIATE", "SOON", "SCHEDULED", "NOT_NEEDED")

    def test_report_id_is_deterministic(self, client):
        payload = {"intent": "drift check", "workflow_id": "wf-det-001"}
        id1 = client.post("/api/v1/monitor/analyze", json=payload).json()["report_id"]
        id2 = client.post("/api/v1/monitor/analyze", json=payload).json()["report_id"]
        assert id1 == id2

    def test_bias_flags_is_list(self, client):
        b = client.post("/api/v1/monitor/analyze",
                        json={"intent": "fairness check"}).json()
        assert isinstance(b["bias_flags"], list)

class TestReports:
    def test_reports_returns_list(self, client):
        b = client.get("/api/v1/monitor/reports").json()
        assert "reports" in b
        assert "count"   in b
        assert isinstance(b["reports"], list)
