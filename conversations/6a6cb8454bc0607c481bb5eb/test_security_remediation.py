"""Tests for Phase 127: Security Remediation + PenTest + Stability"""

import pytest, os, sys
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from security_remediation import router, ExternalSecretsManager, SMTPChecker, PenetrationTester, StabilityChecker

app = FastAPI()
app.include_router(router)
client = TestClient(app)

class TestExternalSecrets:
    @pytest.mark.asyncio
    async def test_generate_external_secret(self):
        es = await ExternalSecretsManager.generate_external_secret()
        assert es["kind"] == "ExternalSecret"
        assert len(es["spec"]["data"]) >= 6

    @pytest.mark.asyncio
    async def test_generate_secret_store(self):
        ss = await ExternalSecretsManager.generate_secret_store()
        assert ss["kind"] == "SecretStore"
        assert "vault" in ss["spec"]["provider"]

    @pytest.mark.asyncio
    async def test_generate_sealed_secret(self):
        sealed = await ExternalSecretsManager.generate_sealed_secret()
        assert sealed["kind"] == "SealedSecret"
        assert "encryptedData" in sealed["spec"]

    @pytest.mark.asyncio
    async def test_remediation_status(self):
        status = await ExternalSecretsManager.get_remediation_status()
        assert status["total_findings"] == 2
        assert status["resolved"] == 2
        assert status["remaining"] == 0

class TestSMTPChecker:
    @pytest.mark.asyncio
    async def test_check_smtp_config(self):
        status = await SMTPChecker.check_smtp_config()
        assert "configured" in status
        assert "smtp_host" in status
        assert "status" in status

class TestPenetrationTester:
    @pytest.mark.asyncio
    async def test_run_pentest(self):
        result = await PenetrationTester.run_pentest()
        assert result["total_tests"] >= 18
        assert result["passed"] >= 17
        assert result["score"] >= 90
        assert len(result["tests"]) >= 18

    @pytest.mark.asyncio
    async def test_pentest_categories(self):
        result = await PenetrationTester.run_pentest()
        categories = set(t["category"] for t in result["tests"])
        assert "Authentication" in categories
        assert "Input Validation" in categories
        assert "Network Security" in categories

class TestStabilityChecker:
    @pytest.mark.asyncio
    async def test_check_all_services(self):
        result = await StabilityChecker.check_all_services()
        assert result["total_services"] >= 16
        assert result["all_healthy"] == True

    @pytest.mark.asyncio
    async def test_circuit_breakers(self):
        result = await StabilityChecker.get_circuit_breaker_status()
        assert result["all_closed"] == True
        assert result["open_breakers"] == 0

    @pytest.mark.asyncio
    async def test_stability_report(self):
        result = await StabilityChecker.get_stability_report()
        assert "health_check" in result
        assert "circuit_breakers" in result
        assert result["overall_stability"] == "excellent"

class TestEndpoints:
    def test_health(self):
        resp = client.get("/api/v1/security/health")
        assert resp.status_code == 200
        assert "pentest" in resp.json()["features"]

    def test_external_secret(self):
        resp = client.get("/api/v1/security/external-secrets/manifest")
        assert resp.status_code == 200
        assert resp.json()["kind"] == "ExternalSecret"

    def test_secret_store(self):
        resp = client.get("/api/v1/security/external-secrets/store")
        assert resp.status_code == 200
        assert resp.json()["kind"] == "SecretStore"

    def test_sealed_secret(self):
        resp = client.get("/api/v1/security/external-secrets/sealed")
        assert resp.status_code == 200
        assert resp.json()["kind"] == "SealedSecret"

    def test_remediation_status(self):
        resp = client.get("/api/v1/security/remediation/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["resolved"] == 2
        assert data["remaining"] == 0

    def test_smtp_status(self):
        resp = client.get("/api/v1/security/smtp/status")
        assert resp.status_code == 200
        assert "configured" in resp.json()

    def test_pentest(self):
        resp = client.get("/api/v1/security/pentest/run")
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] >= 90
        assert data["total_tests"] >= 18

    def test_stability_services(self):
        resp = client.get("/api/v1/security/stability/services")
        assert resp.status_code == 200
        assert resp.json()["all_healthy"] == True

    def test_circuit_breakers(self):
        resp = client.get("/api/v1/security/stability/circuit-breakers")
        assert resp.status_code == 200
        assert resp.json()["all_closed"] == True

    def test_stability_report(self):
        resp = client.get("/api/v1/security/stability/report")
        assert resp.status_code == 200
        assert resp.json()["overall_stability"] == "excellent"
