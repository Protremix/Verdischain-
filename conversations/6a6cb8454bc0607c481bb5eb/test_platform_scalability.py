"""Tests for EvolvixOS Platform Scalability + Paid Plugins + Verification v1.0"""

import pytest
import os
import sys
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from platform_scalability import router, LoadBalancerConfig, PaidPluginManager, PluginVerificationPipeline, \
    PricingRequest, LicenseRequest, PaymentRequest, VerifyLicenseRequest, VerificationRequest

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestLoadBalancerConfig:
    @pytest.mark.asyncio
    async def test_get_config(self):
        config = await LoadBalancerConfig.get_config()
        assert "services" in config
        assert config["total_services"] > 0
        assert config["total_max_replicas"] > 0
    
    @pytest.mark.asyncio
    async def test_nginx_upstream(self):
        config = await LoadBalancerConfig.get_nginx_upstream_config()
        assert "upstream" in config
        assert "ai_gateway" in config
    
    def test_services_have_required_fields(self):
        for service in LoadBalancerConfig.SERVICES:
            assert "name" in service
            assert "port" in service
            assert "min_replicas" in service
            assert "max_replicas" in service
    
    def test_scaling_rules_present(self):
        assert "cpu_threshold_high" in LoadBalancerConfig.SCALING_RULES
        assert "cooldown_seconds" in LoadBalancerConfig.SCALING_RULES


class TestPaidPluginManager:
    @pytest.mark.asyncio
    async def test_set_pricing_no_pg(self):
        with patch('platform_scalability._pg_pool', None):
            with pytest.raises(Exception):
                await PaidPluginManager.set_pricing("00000000-0000-0000-0000-000000000000")
    
    @pytest.mark.asyncio
    async def test_get_pricing_no_pg(self):
        with patch('platform_scalability._pg_pool', None):
            result = await PaidPluginManager.get_pricing("00000000-0000-0000-0000-000000000000")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_verify_license_no_pg(self):
        with patch('platform_scalability._pg_pool', None):
            result = await PaidPluginManager.verify_license("EVX-TEST")
            assert result["valid"] == False
    
    @pytest.mark.asyncio
    async def test_list_priced_plugins_no_pg(self):
        with patch('platform_scalability._pg_pool', None):
            result = await PaidPluginManager.list_priced_plugins()
            assert result["count"] == 0


class TestPluginVerificationPipeline:
    def test_verification_checks_present(self):
        assert len(PluginVerificationPipeline.VERIFICATION_CHECKS) >= 8
    
    def test_verification_checks_have_required_fields(self):
        for check in PluginVerificationPipeline.VERIFICATION_CHECKS:
            assert "id" in check
            assert "name" in check
            assert "severity" in check
    
    @pytest.mark.asyncio
    async def test_run_verification_clean_code(self):
        result = await PluginVerificationPipeline.run_verification(
            "test-plugin",
            "contract Clean { function hello() public {} }",
            {"license": "MIT", "has_tests": True, "documentation": "A well-documented plugin"}
        )
        assert result["verification_status"] in ["verified", "conditional"]
        assert result["total_checks"] >= 8
    
    @pytest.mark.asyncio
    async def test_run_verification_dangerous_code(self):
        result = await PluginVerificationPipeline.run_verification(
            "test-plugin",
            "eval('malicious code'); system('rm -rf /')",
            {"license": "MIT"}
        )
        assert result["verification_status"] == "failed"
        assert result["failed"] > 0
    
    @pytest.mark.asyncio
    async def test_run_verification_empty_code(self):
        result = await PluginVerificationPipeline.run_verification(
            "test-plugin", "", {}
        )
        assert result["score"] < 100
    
    @pytest.mark.asyncio
    async def test_get_verification_checks(self):
        checks = await PluginVerificationPipeline.get_verification_checks()
        assert checks["total_checks"] >= 8
        assert "checks" in checks


class TestModels:
    def test_pricing_request_valid(self):
        req = PricingRequest(plugin_id="test", price_monthly=10.0, pricing_model="monthly")
        assert req.price_monthly == 10.0
    
    def test_pricing_request_negative_price(self):
        with pytest.raises(Exception):
            PricingRequest(plugin_id="test", price_monthly=-1)
    
    def test_license_request(self):
        req = LicenseRequest(plugin_id="test", license_type="premium")
        assert req.license_type == "premium"
    
    def test_payment_request(self):
        req = PaymentRequest(plugin_id="test", amount=29.99)
        assert req.amount == 29.99
    
    def test_payment_request_zero_amount(self):
        with pytest.raises(Exception):
            PaymentRequest(plugin_id="test", amount=0)
    
    def test_verify_license_request(self):
        req = VerifyLicenseRequest(license_key="EVX-TEST123")
        assert req.license_key == "EVX-TEST123"
    
    def test_verification_request(self):
        req = VerificationRequest(plugin_id="test", source_code="contract Test {}")
        assert req.plugin_id == "test"


class TestEndpoints:
    def test_platform_status(self):
        resp = client.get("/api/v1/platform/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "2.0.0"
        assert data["features"]["load_balancing"] == True
        assert data["features"]["paid_plugins"] == True
        assert data["features"]["plugin_verification"] == True
    
    def test_scalability_config(self):
        resp = client.get("/api/v1/platform/scalability/config")
        assert resp.status_code == 200
        assert "services" in resp.json()
    
    def test_nginx_upstream(self):
        resp = client.get("/api/v1/platform/scalability/nginx-upstream")
        assert resp.status_code == 200
        assert "config" in resp.json()
    
    def test_verification_checks(self):
        resp = client.get("/api/v1/platform/verification/checks")
        assert resp.status_code == 200
        assert resp.json()["total_checks"] >= 8
    
    def test_run_verification_endpoint(self):
        resp = client.post("/api/v1/platform/verification/run", json={
            "plugin_id": "test",
            "source_code": "contract Clean {}",
            "metadata": {"license": "MIT", "has_tests": True, "documentation": "docs here"}
        })
        assert resp.status_code == 200
        assert "verification_status" in resp.json()
    
    def test_run_verification_dangerous(self):
        resp = client.post("/api/v1/platform/verification/run", json={
            "plugin_id": "test",
            "source_code": "eval('bad'); system('rm -rf')",
            "metadata": {}
        })
        assert resp.status_code == 200
        assert resp.json()["verification_status"] == "failed"
    
    def test_set_pricing_no_pg(self):
        with patch('platform_scalability._pg_pool', None):
            resp = client.post("/api/v1/platform/pricing", json={
                "plugin_id": "00000000-0000-0000-0000-000000000000",
                "price_monthly": 10.0,
                "pricing_model": "monthly"
            })
            assert resp.status_code == 503
    
    def test_get_pricing_not_found(self):
        with patch('platform_scalability._pg_pool', None):
            resp = client.get("/api/v1/platform/pricing/00000000-0000-0000-0000-000000000000")
            assert resp.status_code == 404
    
    def test_list_priced_plugins(self):
        with patch('platform_scalability._pg_pool', None):
            resp = client.get("/api/v1/platform/pricing")
            assert resp.status_code == 200
    
    def test_create_license_no_pg(self):
        with patch('platform_scalability._pg_pool', None):
            resp = client.post("/api/v1/platform/licenses", json={
                "plugin_id": "00000000-0000-0000-0000-000000000000",
                "license_type": "free"
            })
            assert resp.status_code == 503
    
    def test_verify_license_no_pg(self):
        with patch('platform_scalability._pg_pool', None):
            resp = client.post("/api/v1/platform/licenses/verify", json={
                "license_key": "EVX-TEST"
            })
            assert resp.status_code == 200
            assert resp.json()["valid"] == False
    
    def test_record_payment_no_pg(self):
        with patch('platform_scalability._pg_pool', None):
            resp = client.post("/api/v1/platform/payments", json={
                "plugin_id": "00000000-0000-0000-0000-000000000000",
                "amount": 29.99
            })
            assert resp.status_code == 503
