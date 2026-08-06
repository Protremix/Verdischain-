"""Tests for EvolvixOS Smart Contract Platform v1.0"""

import pytest
import os
import sys
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

with patch('asyncpg.create_pool', new_callable=AsyncMock):
    pass

from fastapi import FastAPI
from contracts import router, ContractManager, init_contracts_pg, AIGenerateRequest

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestContractManager:
    @pytest.mark.asyncio
    async def test_list_contracts_without_pg(self):
        with patch('contracts._pg_pool', None):
            result = await ContractManager.list_contracts()
            assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_get_contract_without_pg(self):
        with patch('contracts._pg_pool', None):
            result = await ContractManager.get_contract("00000000-0000-0000-0000-000000000000")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_templates_without_pg(self):
        with patch('contracts._pg_pool', None):
            result = await ContractManager.get_templates()
            assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_ai_generate_token(self):
        result = await ContractManager.ai_generate(
            AIGenerateRequest(description="Create a custom token", contract_type="token")
        )
        assert result["generated"] == True
        assert "source_code" in result
        assert "name" in result

    @pytest.mark.asyncio
    async def test_ai_generate_eco(self):
        result = await ContractManager.ai_generate(
            AIGenerateRequest(description="Carbon tracking contract", contract_type="eco")
        )
        assert result["generated"] == True
        assert "CarbonTracker" in result["name"]

    @pytest.mark.asyncio
    async def test_ai_generate_default(self):
        result = await ContractManager.ai_generate(
            AIGenerateRequest(description="Unknown type", contract_type="unknown")
        )
        assert result["generated"] == True


class TestContractEndpoints:
    def test_dashboard(self):
        resp = client.get("/api/v1/contracts/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "1.0.0"
        assert "total_contracts" in data
        assert "total_templates" in data
        assert "blockchain" in data

    def test_list_contracts(self):
        resp = client.get("/api/v1/contracts/")
        assert resp.status_code == 200
        assert "contracts" in resp.json()

    def test_create_contract_no_pg(self):
        resp = client.post("/api/v1/contracts/", json={
            "name": "TestContract",
            "source_code": "contract TestContract {}",
        })
        assert resp.status_code in [200, 503]

    def test_get_contract_not_found(self):
        resp = client.get("/api/v1/contracts/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    def test_get_templates(self):
        resp = client.get("/api/v1/contracts/templates/all")
        assert resp.status_code == 200
        assert "templates" in resp.json()

    def test_get_template_not_found(self):
        resp = client.get("/api/v1/contracts/templates/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    def test_ai_generate(self):
        resp = client.post("/api/v1/contracts/ai/generate", json={
            "description": "Create an ERC20 token with staking",
            "contract_type": "token",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["generated"] == True
        assert "source_code" in data

    def test_ai_generate_eco(self):
        resp = client.post("/api/v1/contracts/ai/generate", json={
            "description": "Carbon credit tracking",
            "contract_type": "eco",
        })
        assert resp.status_code == 200
        assert "CarbonTracker" in resp.json()["name"]

    def test_deploy_contract_no_pg(self):
        resp = client.post("/api/v1/contracts/00000000-0000-0000-0000-000000000000/deploy", json={
            "contract_id": "00000000-0000-0000-0000-000000000000",
        })
        assert resp.status_code in [404, 503]

    def test_run_test_no_pg(self):
        resp = client.post("/api/v1/contracts/00000000-0000-0000-0000-000000000000/test", json={
            "contract_id": "00000000-0000-0000-0000-000000000000",
            "test_name": "test_deployment",
        })
        assert resp.status_code in [404, 503]

    def test_verify_contract_no_pg(self):
        resp = client.post("/api/v1/contracts/00000000-0000-0000-0000-000000000000/verify")
        assert resp.status_code in [404, 503]

    def test_get_deployments_no_pg(self):
        resp = client.get("/api/v1/contracts/00000000-0000-0000-0000-000000000000/deployments")
        assert resp.status_code == 200
        assert "deployments" in resp.json()

    def test_get_tests_no_pg(self):
        resp = client.get("/api/v1/contracts/00000000-0000-0000-0000-000000000000/tests")
        assert resp.status_code == 200
        assert "tests" in resp.json()
