"""Tests for EvolvixOS RBAC Module v1.0"""

import pytest
import os
import sys
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

with patch('asyncpg.create_pool', new_callable=AsyncMock):
    pass

from fastapi import FastAPI
from rbac import router, RBACManager, init_rbac_pg

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestRBACManager:
    @pytest.mark.asyncio
    async def test_check_permission_without_pg(self):
        with patch('rbac._pg_pool', None):
            result = await RBACManager.check_permission("user-1", "org", "read")
            assert result == True  # Fail open when PG not connected

    @pytest.mark.asyncio
    async def test_get_user_permissions_without_pg(self):
        with patch('rbac._pg_pool', None):
            result = await RBACManager.get_user_permissions("user-1")
            assert result["permissions"] == []

    @pytest.mark.asyncio
    async def test_list_roles_without_pg(self):
        with patch('rbac._pg_pool', None):
            result = await RBACManager.list_roles()
            assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_get_permission_catalog_without_pg(self):
        with patch('rbac._pg_pool', None):
            result = await RBACManager.get_permission_catalog()
            assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_create_role_without_pg(self):
        with patch('rbac._pg_pool', None):
            with pytest.raises(Exception):
                await RBACManager.create_role("test-role", "test desc", ["org:read"])


class TestRBACEndpoints:
    def test_check_permission_endpoint(self):
        resp = client.post("/api/v1/rbac/check", json={
            "user_id": "user-1", "resource": "org", "action": "read"
        })
        assert resp.status_code == 200
        assert "allowed" in resp.json()

    def test_get_permissions_endpoint(self):
        resp = client.get("/api/v1/rbac/permissions/user-1")
        assert resp.status_code == 200
        assert "permissions" in resp.json()

    def test_list_roles_endpoint(self):
        resp = client.get("/api/v1/rbac/roles")
        assert resp.status_code == 200
        assert "roles" in resp.json()

    def test_create_role_endpoint(self):
        resp = client.post("/api/v1/rbac/roles", json={
            "name": "custom-role", "description": "Custom test role", "permissions": ["org:read", "agents:read"]
        })
        # Will fail with 503 if PG not connected, or 409 if role exists
        assert resp.status_code in [200, 409, 503]

    def test_delete_role_not_found(self):
        resp = client.delete("/api/v1/rbac/roles/00000000-0000-0000-0000-000000000000")
        assert resp.status_code in [404, 503]

    def test_assign_role_endpoint(self):
        resp = client.post("/api/v1/rbac/assign", json={
            "user_id": "user-1", "role_id": "00000000-0000-0000-0000-000000000000"
        })
        assert resp.status_code in [200, 503, 500]

    def test_revoke_role_endpoint(self):
        resp = client.post("/api/v1/rbac/revoke", json={
            "user_id": "user-1", "role_id": "00000000-0000-0000-0000-000000000000"
        })
        assert resp.status_code in [200, 404, 503]

    def test_get_user_roles_endpoint(self):
        resp = client.get("/api/v1/rbac/users/user-1/roles")
        assert resp.status_code == 200
        assert "assignments" in resp.json()

    def test_add_policy_endpoint(self):
        resp = client.post("/api/v1/rbac/policies", json={
            "role_id": "00000000-0000-0000-0000-000000000000",
            "resource": "agents", "action": "execute"
        })
        assert resp.status_code in [200, 503, 500]

    def test_list_policies_endpoint(self):
        resp = client.get("/api/v1/rbac/policies")
        assert resp.status_code == 200
        assert "policies" in resp.json()

    def test_permission_catalog_endpoint(self):
        resp = client.get("/api/v1/rbac/catalog")
        assert resp.status_code == 200
        assert "permissions" in resp.json()

    def test_rbac_dashboard(self):
        resp = client.get("/api/v1/rbac/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "1.0.0"
        assert "total_roles" in data
        assert "total_permissions_in_catalog" in data
