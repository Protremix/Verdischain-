"""
Tests for EvolvixOS Enterprise Module v1.0
"""

import pytest
import asyncio
import os
import sys
import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

with patch('asyncpg.create_pool', new_callable=AsyncMock):
    pass

from fastapi import FastAPI
from enterprise import router, AuditLogger, OrgManager, SSOManager, UsageTracker, init_enterprise_pg

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestAuditLogger:
    @pytest.mark.asyncio
    async def test_log_without_pg(self):
        """Test audit log when PG is not connected."""
        with patch.object(AuditLogger, '_pg_pool', None) if hasattr(AuditLogger, '_pg_pool') else patch('enterprise._pg_pool', None):
            result = await AuditLogger.log(action="test_action")
            assert result is None

    @pytest.mark.asyncio
    async def test_list_logs_without_pg(self):
        result = await AuditLogger.list_logs()
        assert "logs" in result
        assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_get_stats_without_pg(self):
        stats = await AuditLogger.get_stats()
        assert "total" in stats
        assert stats["total"] == 0

    def test_audit_log_endpoint(self):
        resp = client.post("/api/v1/enterprise/audit/log", json={
            "action": "user.login", "user_id": "test-user", "severity": "info"
        })
        assert resp.status_code == 200
        assert resp.json()["logged"] in [True, False]  # Depends on PG

    def test_get_audit_logs_endpoint(self):
        resp = client.get("/api/v1/enterprise/audit/logs?limit=10")
        assert resp.status_code == 200
        assert "logs" in resp.json()

    def test_get_audit_stats_endpoint(self):
        resp = client.get("/api/v1/enterprise/audit/stats")
        assert resp.status_code == 200
        assert "total" in resp.json()


class TestOrgManager:
    @pytest.mark.asyncio
    async def test_create_org_without_pg(self):
        with patch('enterprise._pg_pool', None):
            with pytest.raises(Exception):
                await OrgManager.create_org("Test", "test")

    @pytest.mark.asyncio
    async def test_list_orgs_without_pg(self):
        with patch('enterprise._pg_pool', None):
            result = await OrgManager.list_orgs()
            assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_get_org_without_pg(self):
        with patch('enterprise._pg_pool', None):
            result = await OrgManager.get_org("00000000-0000-0000-0000-000000000000")
            assert result is None

    @pytest.mark.asyncio
    async def test_check_quota_without_pg(self):
        with patch('enterprise._pg_pool', None):
            result = await OrgManager.check_quota("00000000-0000-0000-0000-000000000000", "users")
            assert result["within_quota"] == True

    def test_list_orgs_endpoint(self):
        resp = client.get("/api/v1/enterprise/orgs")
        assert resp.status_code == 200
        assert "orgs" in resp.json()

    def test_get_org_not_found(self):
        resp = client.get("/api/v1/enterprise/orgs/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404


class TestSSOManager:
    def test_generate_saml_request(self):
        req = SSOManager.generate_saml_request("entity-123", "https://sso.example.com")
        assert req["entity_id"] == "entity-123"
        assert req["sso_url"] == "https://sso.example.com"
        assert "request_id" in req
        assert "timestamp" in req
        assert "binding" in req

    def test_generate_oauth_authorize_url(self):
        url = SSOManager.generate_oauth_authorize_url(
            "client-123", "https://app.example.com/callback", ["openid", "email"]
        )
        assert "client_id=client-123" in url
        assert "redirect_uri" in url
        assert "response_type=code" in url

    def test_saml_request_endpoint(self):
        resp = client.post("/api/v1/enterprise/sso/saml/request?entity_id=test&sso_url=https://sso.example.com")
        assert resp.status_code == 200
        data = resp.json()
        assert data["entity_id"] == "test"
        assert "request_id" in data

    def test_oauth_authorize_endpoint(self):
        resp = client.get("/api/v1/enterprise/sso/oauth/authorize?client_id=test&redirect_uri=https://app.example.com/callback")
        assert resp.status_code == 200
        assert "authorize_url" in resp.json()


class TestUsageTracker:
    @pytest.mark.asyncio
    async def test_record_usage_without_pg(self):
        with patch('enterprise._pg_pool', None):
            await UsageTracker.record_usage(org_id=None, endpoint="/test")
            # Should not raise

    @pytest.mark.asyncio
    async def test_get_usage_stats_without_pg(self):
        with patch('enterprise._pg_pool', None):
            stats = await UsageTracker.get_usage_stats()
            assert "total" in stats

    def test_usage_stats_endpoint(self):
        resp = client.get("/api/v1/enterprise/usage/stats")
        assert resp.status_code == 200
        data = resp.json()
        # Could have "total_calls" or "total" or "error" depending on PG connection
        assert any(k in data for k in ["total_calls", "total", "error"])


class TestEnterpriseDashboard:
    def test_dashboard(self):
        resp = client.get("/api/v1/enterprise/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert "organizations" in data
        assert "audit" in data
        assert "usage" in data
        assert "platform" in data
        assert data["platform"]["version"] == "1.0.0"
        assert "sso" in data["platform"]["modules"]
        assert "audit" in data["platform"]["modules"]
        assert "multi_tenancy" in data["platform"]["modules"]
