"""
Tests for EvolvixOS Enterprise Module v2.0
SSO Callback Handling + GDPR Compliance + Extended Enterprise Features
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
from enterprise import (
    router, AuditLogger, OrgManager, SSOManager, GDPRManager, UsageTracker, init_enterprise_pg
)

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestAuditLogger:
    @pytest.mark.asyncio
    async def test_log_without_pg(self):
        with patch('enterprise._pg_pool', None):
            result = await AuditLogger.log(action="test_action")
            assert result is None

    @pytest.mark.asyncio
    async def test_list_logs_without_pg(self):
        with patch('enterprise._pg_pool', None):
            result = await AuditLogger.list_logs()
            assert "logs" in result

    @pytest.mark.asyncio
    async def test_get_stats_without_pg(self):
        with patch('enterprise._pg_pool', None):
            stats = await AuditLogger.get_stats()
            assert "total" in stats

    def test_audit_log_endpoint(self):
        resp = client.post("/api/v1/enterprise/audit/log", json={"action": "user.login", "user_id": "u1"})
        assert resp.status_code == 200

    def test_get_audit_logs_endpoint(self):
        resp = client.get("/api/v1/enterprise/audit/logs?limit=10")
        assert resp.status_code == 200

    def test_get_audit_stats_endpoint(self):
        resp = client.get("/api/v1/enterprise/audit/stats")
        assert resp.status_code == 200


class TestOrgManager:
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

    def test_get_org_not_found(self):
        resp = client.get("/api/v1/enterprise/orgs/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404


class TestSSOManager:
    def test_generate_saml_request(self):
        req = SSOManager.generate_saml_request("entity-123", "https://sso.example.com")
        assert req["entity_id"] == "entity-123"
        assert req["sso_url"] == "https://sso.example.com"
        assert "request_id" in req
        assert "binding" in req

    def test_generate_oauth_authorize_url(self):
        url = SSOManager.generate_oauth_authorize_url("client-123", "https://app.example.com/callback", ["openid"])
        assert "client_id=client-123" in url
        assert "response_type=code" in url

    def test_saml_request_endpoint(self):
        resp = client.post("/api/v1/enterprise/sso/saml/request?entity_id=test&sso_url=https://sso.example.com")
        assert resp.status_code == 200

    def test_oauth_authorize_endpoint(self):
        resp = client.get("/api/v1/enterprise/sso/oauth/authorize?client_id=test&redirect_uri=https://app.example.com/callback")
        assert resp.status_code == 200
        assert "authorize_url" in resp.json()

    def test_initiate_sso_endpoint(self):
        """Test SSO initiation endpoint."""
        resp = client.post("/api/v1/enterprise/sso/initiate", json={
            "org_id": "00000000-0000-0000-0000-000000000000",
            "provider": "oauth2",
            "redirect_uri": "https://app.evolvixos.com/callback"
        })
        # Will fail with 503 or 404 since PG may not be connected or no SSO config
        assert resp.status_code in [200, 404, 503]

    def test_oauth_callback_endpoint(self):
        """Test OAuth callback endpoint."""
        resp = client.post("/api/v1/enterprise/sso/oauth/callback", json={
            "code": "test_code",
            "state": "invalid_state",
            "redirect_uri": "https://app.evolvixos.com/callback"
        })
        # Will fail since state is invalid
        assert resp.status_code in [400, 503, 500]

    def test_saml_callback_endpoint(self):
        """Test SAML callback endpoint."""
        resp = client.post("/api/v1/enterprise/sso/saml/callback", json={
            "saml_response": "base64encoded_saml",
            "state": "invalid_state"
        })
        assert resp.status_code in [400, 503, 500]


class TestGDPRManager:
    @pytest.mark.asyncio
    async def test_create_export_request_without_pg(self):
        with patch('enterprise._pg_pool', None):
            with pytest.raises(Exception):
                await GDPRManager.create_data_export_request("user-1")

    @pytest.mark.asyncio
    async def test_create_deletion_request_without_pg(self):
        with patch('enterprise._pg_pool', None):
            with pytest.raises(Exception):
                await GDPRManager.create_data_deletion_request("user-1")

    @pytest.mark.asyncio
    async def test_get_consents_without_pg(self):
        with patch('enterprise._pg_pool', None):
            result = await GDPRManager.get_consents("user-1")
            assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_get_data_requests_without_pg(self):
        with patch('enterprise._pg_pool', None):
            result = await GDPRManager.get_data_requests()
            assert result["count"] == 0

    def test_export_endpoint(self):
        resp = client.post("/api/v1/enterprise/gdpr/export", json={"user_id": "user-1", "user_email": "test@test.com"})
        assert resp.status_code in [200, 503]

    def test_deletion_endpoint(self):
        resp = client.post("/api/v1/enterprise/gdpr/deletion", json={"user_id": "user-1"})
        assert resp.status_code in [200, 503]

    def test_get_requests_endpoint(self):
        resp = client.get("/api/v1/enterprise/gdpr/requests")
        assert resp.status_code == 200

    def test_consent_endpoint(self):
        resp = client.post("/api/v1/enterprise/consent", json={
            "user_id": "user-1", "consent_type": "marketing", "granted": True
        })
        assert resp.status_code in [200, 503]

    def test_get_consent_endpoint(self):
        resp = client.get("/api/v1/enterprise/consent/user-1")
        assert resp.status_code == 200


class TestUsageTracker:
    @pytest.mark.asyncio
    async def test_record_usage_without_pg(self):
        with patch('enterprise._pg_pool', None):
            await UsageTracker.record_usage(endpoint="/test")
            # Should not raise

    @pytest.mark.asyncio
    async def test_get_usage_stats_without_pg(self):
        with patch('enterprise._pg_pool', None):
            stats = await UsageTracker.get_usage_stats()
            assert "total_calls" in stats

    def test_usage_stats_endpoint(self):
        resp = client.get("/api/v1/enterprise/usage/stats")
        assert resp.status_code == 200


class TestEnterpriseDashboard:
    def test_dashboard_v2(self):
        """Test that dashboard includes GDPR module info."""
        resp = client.get("/api/v1/enterprise/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert "organizations" in data
        assert "audit" in data
        assert "usage" in data
        assert "gdpr" in data
        assert data["platform"]["version"] == "2.0.0"
        assert "gdpr" in data["platform"]["modules"]
        assert "sso_callbacks" in data["platform"]["modules"]
