"""
Tests for EvolvixOS Monitoring + Documentation System
"""

import pytest
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitoring_metrics import MetricsCollector, metrics
from monitoring_api import app

client = TestClient(app)


# =========================================================================
# Metrics Collector Tests
# =========================================================================

class TestMetricsCollector:
    def setup_method(self):
        self.mc = MetricsCollector()

    def test_init_default_metrics(self):
        assert self.mc._gauges["evolvixos_gateway_active_plugins"] == 0
        assert self.mc._gauges["evolvixos_agent_total"] == 0
        assert self.mc._counters["evolvixos_gateway_requests_total"] == 0

    def test_increment(self):
        self.mc.increment("test_counter")
        assert self.mc._counters["test_counter"] == 1
        self.mc.increment("test_counter", 5)
        assert self.mc._counters["test_counter"] == 6

    def test_set_gauge(self):
        self.mc.set_gauge("test_gauge", 42)
        assert self.mc._gauges["test_gauge"] == 42

    def test_observe(self):
        self.mc.observe("test_hist", 100)
        self.mc.observe("test_hist", 200)
        assert len(self.mc._histograms["test_hist"]) == 2

    def test_record_latency(self):
        self.mc.record_latency("gateway", 50.5)
        assert "gateway_latency_ms" in self.mc._histograms
        assert 50.5 in self.mc._histograms["gateway_latency_ms"]

    def test_export_prometheus_format(self):
        self.mc.increment("evolvixos_gateway_requests_total", 10)
        self.mc.set_gauge("evolvixos_agent_total", 5)
        output = self.mc.export_prometheus()
        assert "# TYPE evolvixos_gateway_requests_total counter" in output
        assert "evolvixos_gateway_requests_total 10" in output
        assert "# TYPE evolvixos_agent_total gauge" in output
        assert "evolvixos_agent_total 5" in output

    def test_export_prometheus_histograms(self):
        for i in range(30):
            self.mc.observe("latency_test", float(i * 10))
        output = self.mc.export_prometheus()
        assert "# TYPE latency_test summary" in output
        assert 'latency_test{quantile="0.5"}' in output
        assert "latency_test_count 30" in output

    def test_get_stats(self):
        self.mc.increment("test_counter", 3)
        self.mc.set_gauge("test_gauge", 7)
        stats = self.mc.get_stats()
        assert "counters" in stats
        assert "gauges" in stats
        assert stats["counters"]["test_counter"] == 3
        assert stats["gauges"]["test_gauge"] == 7

    def test_histogram_capping(self):
        for i in range(1500):
            self.mc.observe("cap_test", float(i))
        assert len(self.mc._histograms["cap_test"]) <= 1000

    def test_thread_safety(self):
        import threading
        def increment_loop():
            for _ in range(100):
                self.mc.increment("thread_test")
        
        threads = [threading.Thread(target=increment_loop) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert self.mc._counters["thread_test"] == 1000


# =========================================================================
# Monitoring API Tests
# =========================================================================

class TestMonitoringAPI:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"

    def test_metrics_endpoint(self):
        resp = client.get("/metrics")
        assert resp.status_code == 200
        assert "text/plain" in resp.headers.get("content-type", "")
        assert "evolvixos_gateway_requests_total" in resp.text

    def test_metrics_json(self):
        resp = client.get("/metrics/json")
        assert resp.status_code == 200
        data = resp.json()
        assert "counters" in data
        assert "gauges" in data

    def test_increment_metric(self):
        resp = client.post("/metrics/increment/test_metric?value=5")
        assert resp.status_code == 200
        assert resp.json()["value"] == 5

    def test_set_gauge(self):
        resp = client.post("/metrics/gauge/test_gauge?value=42")
        assert resp.status_code == 200
        assert resp.json()["value"] == 42

    def test_observe_metric(self):
        resp = client.post("/metrics/observe/test_obs?value=100")
        assert resp.status_code == 200

    def test_metrics_content_type(self):
        """Test that /metrics returns proper Prometheus content type"""
        resp = client.get("/metrics")
        ct = resp.headers.get("content-type", "")
        assert "text/plain" in ct


# =========================================================================
# Documentation API Tests
# =========================================================================

class TestDocumentationAPI:
    def test_get_architecture(self):
        resp = client.get("/architecture")
        assert resp.status_code == 200
        data = resp.json()
        assert "title" in data
        assert "components" in data
        assert data["total_tests"] == 419

    def test_get_api_reference_all(self):
        resp = client.get("/api-reference")
        assert resp.status_code == 200
        data = resp.json()
        assert "ai_gateway" in data
        assert "agent_framework" in data
        assert "blockchain" in data

    def test_get_api_reference_specific(self):
        resp = client.get("/api-reference?service=ai_gateway")
        assert resp.status_code == 200
        data = resp.json()
        assert "endpoints" in data
        assert len(data["endpoints"]) > 0

    def test_get_api_reference_not_found(self):
        resp = client.get("/api-reference?service=nonexistent")
        assert resp.status_code == 404

    def test_list_guides(self):
        resp = client.get("/guides")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 5

    def test_get_guide(self):
        resp = client.get("/guides/quickstart")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "quickstart"
        assert "steps" in data

    def test_get_guide_not_found(self):
        resp = client.get("/guides/nonexistent")
        assert resp.status_code == 404

    def test_list_faqs(self):
        resp = client.get("/faq")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 5

    def test_list_runbooks(self):
        resp = client.get("/runbooks")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 3

    def test_get_runbook(self):
        resp = client.get("/runbooks/gateway-down")
        assert resp.status_code == 200
        data = resp.json()
        assert data["severity"] == "critical"
        assert "steps" in data

    def test_get_runbook_not_found(self):
        resp = client.get("/runbooks/nonexistent")
        assert resp.status_code == 404

    def test_sdk_quickstart_python(self):
        resp = client.get("/sdk/quickstart?language=python")
        assert resp.status_code == 200
        data = resp.json()
        assert data["language"] == "python"
        assert "evolvixos_sdk" in data["code"]

    def test_sdk_quickstart_typescript(self):
        resp = client.get("/sdk/quickstart?language=typescript")
        assert resp.status_code == 200
        data = resp.json()
        assert data["language"] == "typescript"
        assert "EvolvixOSClient" in data["code"]

    def test_sdk_quickstart_invalid(self):
        resp = client.get("/sdk/quickstart?language=ruby")
        assert resp.status_code == 400

    def test_doc_stats(self):
        resp = client.get("/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "architecture_components" in data
        assert "api_endpoints" in data
        assert "total_tests" in data
