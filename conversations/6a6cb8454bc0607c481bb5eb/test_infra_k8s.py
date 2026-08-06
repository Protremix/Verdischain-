"""Tests for EvolvixOS K8s Migration + SPOF + Notification Delivery v1.0"""

import pytest
import os
import sys
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from infra_k8s import router, K8sManifestGenerator, SPOFRemediation, NotificationDelivery, \
    DeliveryConfigRequest, DeliverNotificationRequest

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestK8sManifestGenerator:
    @pytest.mark.asyncio
    async def test_generate_namespace(self):
        ns = await K8sManifestGenerator.generate_namespace()
        assert ns["kind"] == "Namespace"
        assert ns["metadata"]["name"] == "evolvixos"
    
    @pytest.mark.asyncio
    async def test_generate_configmap(self):
        cm = await K8sManifestGenerator.generate_configmap()
        assert cm["kind"] == "ConfigMap"
        assert "DATABASE_URL" in cm["data"]
    
    @pytest.mark.asyncio
    async def test_generate_deployment(self):
        svc = {"name": "test", "port": 8000, "replicas": 2, "critical": True, "image": "test:latest"}
        dep = await K8sManifestGenerator.generate_deployment(svc)
        assert dep["kind"] == "Deployment"
        assert dep["spec"]["replicas"] == 2
        assert "livenessProbe" in dep["spec"]["template"]["spec"]["containers"][0]
        assert "readinessProbe" in dep["spec"]["template"]["spec"]["containers"][0]
    
    @pytest.mark.asyncio
    async def test_generate_service(self):
        svc = {"name": "test", "port": 8000, "replicas": 2, "critical": True, "image": "test:latest"}
        s = await K8sManifestGenerator.generate_service(svc)
        assert s["kind"] == "Service"
        assert s["spec"]["type"] == "ClusterIP"
    
    @pytest.mark.asyncio
    async def test_generate_hpa(self):
        svc = {"name": "test", "port": 8000, "replicas": 2, "critical": True, "image": "test:latest"}
        hpa = await K8sManifestGenerator.generate_hpa(svc)
        assert hpa["kind"] == "HorizontalPodAutoscaler"
        assert hpa["spec"]["minReplicas"] == 2
        assert hpa["spec"]["maxReplicas"] >= 4
    
    @pytest.mark.asyncio
    async def test_generate_all_manifests(self):
        manifests = await K8sManifestGenerator.generate_all_manifests()
        assert manifests["total_deployments"] > 0
        assert manifests["total_replicas"] > 0
        assert manifests["spof_fixed"] >= 7  # All 7 critical services have 2+ replicas
        assert manifests["spof_remaining"] == 0
        assert "namespace" in manifests
        assert "configmap" in manifests
    
    def test_services_defined(self):
        assert len(K8sManifestGenerator.SERVICES) >= 14
    
    def test_critical_services_have_ha(self):
        critical = [s for s in K8sManifestGenerator.SERVICES if s["critical"]]
        for svc in critical:
            assert svc["replicas"] >= 2, f"{svc['name']} should have 2+ replicas"


class TestSPOFRemediation:
    @pytest.mark.asyncio
    async def test_get_remediation_status(self):
        status = await SPOFRemediation.get_remediation_status()
        assert status["total_critical_services"] > 0
        assert "remediation_progress" in status
        assert status["spof_remaining"] == 0  # All fixed in k8s config
        assert status["status"] == "all_critical_services_have_ha"
    
    @pytest.mark.asyncio
    async def test_health_aggregation(self):
        agg = await SPOFRemediation.get_health_check_aggregation()
        assert agg["total_services"] > 0
        assert agg["failover_ready"] == True
        assert agg["critical_without_ha"] == 0


class TestNotificationDelivery:
    @pytest.mark.asyncio
    async def test_set_delivery_config_no_pg(self):
        with patch('infra_k8s._pg_pool', None):
            with pytest.raises(Exception):
                await NotificationDelivery.set_delivery_config("user-1", email_enabled=True, email_address="test@test.com")
    
    @pytest.mark.asyncio
    async def test_get_delivery_config_no_pg(self):
        with patch('infra_k8s._pg_pool', None):
            result = await NotificationDelivery.get_delivery_config("user-1")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_deliver_notification_no_pg(self):
        with patch('infra_k8s._pg_pool', None):
            result = await NotificationDelivery.deliver_notification("test-id", "user-1", "Title", "Body")
            assert result["delivered"] == False
    
    @pytest.mark.asyncio
    async def test_get_delivery_stats_no_pg(self):
        with patch('infra_k8s._pg_pool', None):
            result = await NotificationDelivery.get_delivery_stats()
            assert result["configured_users"] == 0
    
    @pytest.mark.asyncio
    async def test_send_webhook_invalid_url(self):
        result = await NotificationDelivery._send_webhook("http://invalid.invalid.invalid/hook", {"test": True})
        assert result == False


class TestModels:
    def test_delivery_config_request(self):
        req = DeliveryConfigRequest(user_id="user-1", email_enabled=True, email_address="test@test.com")
        assert req.email_enabled == True
    
    def test_deliver_notification_request(self):
        req = DeliverNotificationRequest(notification_id="test", user_id="user-1", title="Test")
        assert req.notification_type == "general"


class TestEndpoints:
    def test_health(self):
        resp = client.get("/api/v1/infra/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "infra"
        assert "k8s_manifests" in data["features"]
    
    def test_k8s_manifests(self):
        resp = client.get("/api/v1/infra/k8s/manifests")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_deployments"] >= 14
        assert data["spof_remaining"] == 0
        assert data["spof_fixed"] >= 7
    
    def test_k8s_deployments(self):
        resp = client.get("/api/v1/infra/k8s/deployments")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 14
    
    def test_k8s_services(self):
        resp = client.get("/api/v1/infra/k8s/services")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 14
    
    def test_k8s_hpas(self):
        resp = client.get("/api/v1/infra/k8s/hpas")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 14
    
    def test_spof_status(self):
        resp = client.get("/api/v1/infra/spof/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "all_critical_services_have_ha"
        assert data["spof_remaining"] == 0
    
    def test_health_aggregation(self):
        resp = client.get("/api/v1/infra/spof/health-aggregation")
        assert resp.status_code == 200
        data = resp.json()
        assert data["failover_ready"] == True
    
    def test_set_delivery_config_no_pg(self):
        with patch('infra_k8s._pg_pool', None):
            resp = client.post("/api/v1/infra/delivery/config", json={
                "user_id": "user-1", "email_enabled": True, "email_address": "test@test.com"
            })
            assert resp.status_code == 503
    
    def test_get_delivery_config_no_pg(self):
        with patch('infra_k8s._pg_pool', None):
            resp = client.get("/api/v1/infra/delivery/config/user-1")
            assert resp.status_code == 404
    
    def test_deliver_notification_no_pg(self):
        with patch('infra_k8s._pg_pool', None):
            resp = client.post("/api/v1/infra/delivery/send", json={
                "notification_id": "test", "user_id": "user-1", "title": "Test"
            })
            assert resp.status_code == 200
            assert resp.json()["delivered"] == False
    
    def test_delivery_stats(self):
        resp = client.get("/api/v1/infra/delivery/stats")
        assert resp.status_code == 200
