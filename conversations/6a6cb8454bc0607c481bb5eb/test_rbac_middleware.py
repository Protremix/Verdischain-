"""Tests for EvolvixOS RBAC Auth Middleware v1.0"""

import pytest
import os
import sys
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rbac_middleware import RBACMiddleware, require_permission, get_rbac_middleware_config, ROUTE_PERMISSION_MAP, METHOD_ACTION_MAP


class TestRBACMiddleware:
    def test_middleware_config(self):
        config = get_rbac_middleware_config()
        assert config["version"] == "1.0.0"
        assert config["enabled"] == True
        assert config["total_protected_routes"] > 0

    def test_route_permission_map(self):
        assert ("/api/v1/enterprise/orgs", ("org", "read")) in ROUTE_PERMISSION_MAP.items() or \
               "/api/v1/enterprise/orgs" in ROUTE_PERMISSION_MAP
        assert METHOD_ACTION_MAP["GET"] == "read"
        assert METHOD_ACTION_MAP["POST"] == "write"
        assert METHOD_ACTION_MAP["DELETE"] == "delete"

    def test_middleware_disabled(self):
        app = FastAPI()
        app.add_middleware(RBACMiddleware, enabled=False)
        
        @app.get("/protected")
        async def protected():
            return {"ok": True}
        
        client = TestClient(app)
        resp = client.get("/protected")
        assert resp.status_code == 200

    def test_middleware_skips_public_routes(self):
        app = FastAPI()
        app.add_middleware(RBACMiddleware, enabled=True)
        
        @app.get("/health")
        async def health():
            return {"ok": True}
        
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_middleware_skips_options(self):
        app = FastAPI()
        app.add_middleware(RBACMiddleware, enabled=True)
        
        @app.options("/test")
        async def test():
            return {"ok": True}
        
        client = TestClient(app)
        resp = client.options("/test")
        assert resp.status_code == 200

    def test_middleware_no_user_id_allows_access(self):
        """When no X-User-ID header is present, access is allowed (backwards compatible)."""
        app = FastAPI()
        app.add_middleware(RBACMiddleware, enabled=True)
        
        @app.get("/api/v1/agents/list")
        async def agents():
            return {"ok": True}
        
        client = TestClient(app)
        resp = client.get("/api/v1/agents/list")
        assert resp.status_code == 200

    def test_middleware_with_user_id_unmapped_route(self):
        """Unmapped routes are open access."""
        app = FastAPI()
        app.add_middleware(RBACMiddleware, enabled=True)
        
        @app.get("/custom/route")
        async def custom():
            return {"ok": True}
        
        client = TestClient(app)
        resp = client.get("/custom/route", headers={"X-User-ID": "user-1"})
        assert resp.status_code == 200

    def test_require_permission_decorator_no_user(self):
        """The require_permission decorator should allow access when no user is provided."""
        @require_permission("agents", "read")
        async def protected(request: Request):
            return {"ok": True}
        
        # Without a real Request object with headers, the decorator should just call through
        import asyncio
        # Pass a mock request without X-User-ID header
        mock_request = MagicMock()
        mock_request.headers = {}
        result = asyncio.run(protected(request=mock_request))
        assert result["ok"] == True

    def test_permission_mapping_completeness(self):
        """Verify all major resources are mapped."""
        resources = set(v[0] for v in ROUTE_PERMISSION_MAP.values())
        expected = {"org", "audit", "sso", "usage", "gdpr", "rbac", "agents", "api", "blockchain", "contracts", "plugins", "docs", "sdk"}
        for r in expected:
            assert r in resources, f"Missing resource mapping: {r}"

    def test_method_action_mapping(self):
        assert METHOD_ACTION_MAP["GET"] == "read"
        assert METHOD_ACTION_MAP["POST"] == "write"
        assert METHOD_ACTION_MAP["PUT"] == "write"
        assert METHOD_ACTION_MAP["PATCH"] == "write"
        assert METHOD_ACTION_MAP["DELETE"] == "delete"

    def test_exclude_prefixes(self):
        app = FastAPI()
        app.add_middleware(RBACMiddleware, enabled=True, exclude_prefixes=["/custom"])
        
        @app.get("/custom/endpoint")
        async def custom():
            return {"ok": True}
        
        client = TestClient(app)
        resp = client.get("/custom/endpoint", headers={"X-User-ID": "user-1"})
        assert resp.status_code == 200
