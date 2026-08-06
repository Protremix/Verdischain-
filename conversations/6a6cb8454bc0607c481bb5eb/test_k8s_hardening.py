"""Tests for Phase 126: K8s Hardening + Security Audit + Notification Channels"""

import pytest, os, sys
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from k8s_hardening import router, K8sHardening, SecurityAuditor, NotificationChannels, AddChannelRequest, DeliverChannelRequest

app = FastAPI()
app.include_router(router)
client = TestClient(app)

class TestK8sHardening:
    @pytest.mark.asyncio
    async def test_generate_secret(self):
        s = await K8sHardening.generate_secret_manifest()
        assert s["kind"] == "Secret"
        assert "DATABASE_URL" in s["data"]

    @pytest.mark.asyncio
    async def test_generate_pg_secret(self):
        s = await K8sHardening.generate_pg_secret()
        assert s["kind"] == "Secret"
        assert "url" in s["data"]

    @pytest.mark.asyncio
    async def test_generate_ingress(self):
        ing = await K8sHardening.generate_ingress()
        assert ing["kind"] == "Ingress"
        assert len(ing["spec"]["tls"]) > 0
        assert "cert-manager.io/cluster-issuer" in ing["metadata"]["annotations"]

    @pytest.mark.asyncio
    async def test_generate_network_policies(self):
        np = await K8sHardening.generate_network_policies()
        assert np["total"] == 5
        assert any(p["metadata"]["name"] == "deny-all" for p in np["policies"])

    @pytest.mark.asyncio
    async def test_generate_pdbs(self):
        pdbs = await K8sHardening.generate_pdbs()
        assert pdbs["total"] == 7
        assert all(p["spec"]["minAvailable"] == 1 for p in pdbs["pdbs"])

    @pytest.mark.asyncio
    async def test_get_all(self):
        all_m = await K8sHardening.get_all()
        assert all_m["summary"]["secrets"] == 2
        assert all_m["summary"]["ingress_routes"] == 14
        assert all_m["summary"]["network_policies"] == 5
        assert all_m["summary"]["pdbs"] == 7
        assert all_m["summary"]["tls"] == True

class TestSecurityAuditor:
    @pytest.mark.asyncio
    async def test_run_audit(self):
        audit = await SecurityAuditor.run_audit()
        assert audit["total_checks"] >= 18
        assert audit["passed"] >= 16
        assert audit["score"] >= 80
        assert "checks" in audit
        assert len(audit["medium_findings"]) <= 2

class TestNotificationChannels:
    @pytest.mark.asyncio
    async def test_init_tables_no_pg(self):
        with patch('k8s_hardening._pg_pool', None):
            result = await NotificationChannels.init_tables()
            assert result == False

    @pytest.mark.asyncio
    async def test_add_channel_no_pg(self):
        with patch('k8s_hardening._pg_pool', None):
            with pytest.raises(Exception):
                await NotificationChannels.add_channel("user-1", "slack", {"webhook_url": "test"})

    @pytest.mark.asyncio
    async def test_get_channels_no_pg(self):
        with patch('k8s_hardening._pg_pool', None):
            result = await NotificationChannels.get_channels("user-1")
            assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_deliver_no_pg(self):
        with patch('k8s_hardening._pg_pool', None):
            result = await NotificationChannels.deliver("user-1", "slack", "Test", "Body")
            assert result["delivered"] == False

    @pytest.mark.asyncio
    async def test_get_supported(self):
        result = await NotificationChannels.get_supported()
        assert result["total"] == 5
        assert result["available"] == 4

    @pytest.mark.asyncio
    async def test_send_slack_invalid_url(self):
        result = await NotificationChannels._send_slack("", "title", "body")
        assert result == False

    @pytest.mark.asyncio
    async def test_send_discord_invalid_url(self):
        result = await NotificationChannels._send_discord("", "title", "body")
        assert result == False

class TestModels:
    def test_add_channel_request(self):
        req = AddChannelRequest(user_id="user-1", channel_type="slack", config={"webhook_url":"test"})
        assert req.channel_type == "slack"

    def test_add_channel_invalid_type(self):
        with pytest.raises(Exception):
            AddChannelRequest(user_id="user-1", channel_type="invalid")

    def test_deliver_channel_request(self):
        req = DeliverChannelRequest(user_id="user-1", channel_type="discord", title="Test")
        assert req.notification_type == "general"

class TestEndpoints:
    def test_health(self):
        resp = client.get("/api/v1/hardening/health")
        assert resp.status_code == 200
        assert "k8s_secrets" in resp.json()["features"]

    def test_k8s_secrets(self):
        resp = client.get("/api/v1/hardening/k8s/secrets")
        assert resp.status_code == 200
        assert "app_secret" in resp.json()

    def test_k8s_ingress(self):
        resp = client.get("/api/v1/hardening/k8s/ingress")
        assert resp.status_code == 200
        assert resp.json()["kind"] == "Ingress"

    def test_k8s_network_policies(self):
        resp = client.get("/api/v1/hardening/k8s/network-policies")
        assert resp.status_code == 200
        assert resp.json()["total"] == 5

    def test_k8s_pdbs(self):
        resp = client.get("/api/v1/hardening/k8s/pdbs")
        assert resp.status_code == 200
        assert resp.json()["total"] == 7

    def test_k8s_all(self):
        resp = client.get("/api/v1/hardening/k8s/all")
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"]["ingress_routes"] == 14

    def test_security_audit(self):
        resp = client.get("/api/v1/hardening/security/audit")
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] >= 80
        assert data["passed"] >= 16

    def test_channels_supported(self):
        resp = client.get("/api/v1/hardening/channels/supported")
        assert resp.status_code == 200
        assert resp.json()["total"] == 5

    def test_get_channels_no_pg(self):
        with patch('k8s_hardening._pg_pool', None):
            resp = client.get("/api/v1/hardening/channels/user-1")
            assert resp.status_code == 200
            assert resp.json()["count"] == 0

    def test_add_channel_no_pg(self):
        with patch('k8s_hardening._pg_pool', None):
            resp = client.post("/api/v1/hardening/channels", json={
                "user_id": "user-1", "channel_type": "slack", "config": {"webhook_url": "test"}
            })
            assert resp.status_code == 503

    def test_deliver_channel_no_pg(self):
        with patch('k8s_hardening._pg_pool', None):
            resp = client.post("/api/v1/hardening/channels/deliver", json={
                "user_id": "user-1", "channel_type": "slack", "title": "Test"
            })
            assert resp.status_code == 200
            assert resp.json()["delivered"] == False
