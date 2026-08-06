"""
Tests for EvolvixOS Load Testing + Security Audit
"""

import pytest
import asyncio
import os
import sys
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from load_test import LoadTester, SecurityAuditor, LoadTestResult, RequestResult
from load_test_api import app


# =========================================================================
# Load Tester Tests
# =========================================================================

class TestLoadTester:
    @pytest.fixture
    def tester(self):
        return LoadTester()
    
    def test_init(self, tester):
        assert tester.gateway_url is not None
        assert tester.agent_url is not None
    
    def test_percentile(self, tester):
        vals = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        assert tester._percentile(vals, 0.5) == 50
        assert tester._percentile(vals, 0.9) == 90
        assert tester._percentile(vals, 0.99) == 100
    
    def test_percentile_empty(self, tester):
        assert tester._percentile([], 0.5) == 0
    
    @pytest.mark.asyncio
    async def test_run_test_mock(self, tester):
        """Test run_test with mocked HTTP"""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            result = await tester.run_test(
                name="Mock Test",
                target_url="http://test.example.com/health",
                num_requests=5,
                concurrent=2,
            )
        
        assert result.total_requests == 5
        assert result.successful == 5
        assert result.failed == 0
        assert result.error_rate == 0
        assert result.rps > 0
    
    @pytest.mark.asyncio
    async def test_run_test_with_errors(self, tester):
        """Test run_test with failing requests"""
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Connection error")
            result = await tester.run_test(
                name="Error Test",
                target_url="http://test.example.com/health",
                num_requests=3,
                concurrent=1,
            )
        
        assert result.total_requests == 3
        assert result.failed == 3
        assert result.error_rate == 100
    
    @pytest.mark.asyncio
    async def test_run_test_post(self, tester):
        """Test POST request"""
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp
            result = await tester.run_test(
                name="POST Test",
                target_url="http://test.example.com/create",
                method="POST",
                payload={"data": "test"},
                num_requests=3,
                concurrent=1,
            )
        
        assert result.total_requests == 3
        assert result.successful == 3
    
    @pytest.mark.asyncio
    async def test_load_test_result_to_dict(self, tester):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            result = await tester.run_test("Dict Test", "http://test.com", num_requests=2, concurrent=1)
        
        d = result.to_dict()
        assert d["test_name"] == "Dict Test"
        assert d["total_requests"] == 2
        assert len(d["results"]) <= 100


class TestLoadTestModels:
    def test_request_result(self):
        r = RequestResult(url="http://test.com", method="GET", status_code=200, latency_ms=50.0, success=True)
        assert r.url == "http://test.com"
        assert r.status_code == 200
        assert r.success == True
    
    def test_load_test_result(self):
        r = LoadTestResult(
            test_name="Test", target_url="http://test.com",
            total_requests=100, successful=90, failed=10, error_rate=10.0,
            rps=50.0, latency_p50=100, latency_p95=200, latency_p99=500,
            latency_avg=120, latency_min=50, latency_max=600,
            duration_seconds=2.0, concurrent_users=10,
        )
        assert r.test_name == "Test"
        assert r.total_requests == 100
        assert r.error_rate == 10.0
        d = r.to_dict()
        assert "test_name" in d


# =========================================================================
# Security Auditor Tests
# =========================================================================

class TestSecurityAuditor:
    @pytest.fixture
    def auditor(self):
        return SecurityAuditor()
    
    def test_init(self, auditor):
        assert auditor.gateway_url is not None
    
    @pytest.mark.asyncio
    async def test_audit_all_mock(self, auditor):
        """Test audit with mocked responses"""
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.headers = {}
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get, \
             patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_get.return_value = mock_resp
            mock_post.return_value = mock_resp
            result = await auditor.audit_all()
        
        assert "score" in result
        assert "grade" in result
        assert "checks" in result
        assert "total_checks" in result
    
    @pytest.mark.asyncio
    async def test_check_auth_required_pass(self, auditor):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            result = await auditor._check_auth_required("Test", "http://test.com/admin", "api-key")
        
        assert result["status"] == "pass"
    
    @pytest.mark.asyncio
    async def test_check_auth_required_fail(self, auditor):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {}
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            result = await auditor._check_auth_required("Test", "http://test.com/admin", "api-key")
        
        assert result["status"] == "fail"
        assert result["severity"] == "medium"
    
    @pytest.mark.asyncio
    async def test_check_cors_wildcard(self, auditor):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"access-control-allow-origin": "*"}
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            result = await auditor._check_cors_headers("Test", "http://test.com")
        
        assert result["status"] == "fail"
        assert "Wildcard" in result["detail"]
    
    @pytest.mark.asyncio
    async def test_check_cors_safe(self, auditor):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {}
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            result = await auditor._check_cors_headers("Test", "http://test.com")
        
        assert result["status"] == "pass"
    
    @pytest.mark.asyncio
    async def test_check_security_headers_present(self, auditor):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"x-content-type-options": "nosniff", "x-frame-options": "DENY"}
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            result = await auditor._check_security_headers("Test", "http://test.com")
        
        assert result["status"] == "pass"
    
    @pytest.mark.asyncio
    async def test_check_security_headers_missing(self, auditor):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {}
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            result = await auditor._check_security_headers("Test", "http://test.com")
        
        assert result["status"] == "fail"
    
    @pytest.mark.asyncio
    async def test_check_endpoint_exposure_clean(self, auditor):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            result = await auditor._check_endpoint_exposure("Test", "http://test.com")
        
        assert result["status"] == "pass"
    
    @pytest.mark.asyncio
    async def test_check_endpoint_exposure_exposed(self, auditor):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            result = await auditor._check_endpoint_exposure("Test", "http://test.com")
        
        assert result["status"] == "fail"
        assert result["severity"] == "high"


# =========================================================================
# API Tests
# =========================================================================

class TestLoadTestAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"
    
    def test_load_test_mock(self, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            resp = client.post("/load-test", json={
                "target_url": "http://test.com",
                "num_requests": 5,
                "concurrent": 2,
            })
        
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_requests"] == 5
    
    def test_security_score(self, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.headers = {}
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get, \
             patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_get.return_value = mock_resp
            mock_post.return_value = mock_resp
            resp = client.get("/security-audit/score")
        
        assert resp.status_code == 200
        data = resp.json()
        assert "score" in data
        assert "grade" in data
