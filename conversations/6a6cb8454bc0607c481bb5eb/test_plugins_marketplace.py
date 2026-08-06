"""Tests for EvolvixOS Plugin Marketplace v1.0"""

import pytest
import os
import sys
import json
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from plugins_marketplace import router, PluginMarketplace, init_plugins_pg, PublishPluginRequest, InstallPluginRequest, ReviewPluginRequest

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestPluginMarketplace:
    @pytest.mark.asyncio
    async def test_list_plugins_without_pg(self):
        with patch('plugins_marketplace._pg_pool', None):
            result = await PluginMarketplace.list_plugins()
            assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_get_plugin_without_pg(self):
        with patch('plugins_marketplace._pg_pool', None):
            result = await PluginMarketplace.get_plugin("00000000-0000-0000-0000-000000000000")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_name_without_pg(self):
        with patch('plugins_marketplace._pg_pool', None):
            result = await PluginMarketplace.get_by_name("test-plugin")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_featured_without_pg(self):
        with patch('plugins_marketplace._pg_pool', None):
            result = await PluginMarketplace.get_featured()
            assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_get_categories_without_pg(self):
        with patch('plugins_marketplace._pg_pool', None):
            result = await PluginMarketplace.get_categories()
            assert result["categories"] == []

    @pytest.mark.asyncio
    async def test_get_installed_without_pg(self):
        with patch('plugins_marketplace._pg_pool', None):
            result = await PluginMarketplace.get_installed()
            assert result["count"] == 0


class TestMarketplaceEndpoints:
    def test_dashboard(self):
        resp = client.get("/api/v1/plugins/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "1.0.0"
        assert "total_plugins" in data
        assert "categories" in data

    def test_list_plugins(self):
        resp = client.get("/api/v1/plugins/")
        assert resp.status_code == 200
        assert "plugins" in resp.json()

    def test_get_plugin_not_found(self):
        resp = client.get("/api/v1/plugins/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    def test_publish_plugin_no_pg(self):
        with patch('plugins_marketplace._pg_pool', None):
            resp = client.post("/api/v1/plugins/", json={
                "name": "test-plugin",
                "display_name": "Test Plugin",
                "description": "A test plugin",
                "category": "general",
                "plugin_type": "utility",
            })
            assert resp.status_code == 503

    def test_install_plugin_no_pg(self):
        with patch('plugins_marketplace._pg_pool', None):
            resp = client.post("/api/v1/plugins/install", json={
                "plugin_name": "test-plugin",
            })
            assert resp.status_code == 503

    def test_get_reviews_not_found(self):
        with patch('plugins_marketplace._pg_pool', None):
            resp = client.get("/api/v1/plugins/00000000-0000-0000-0000-000000000000/reviews")
            assert resp.status_code == 200
            assert "reviews" in resp.json()

    def test_featured(self):
        resp = client.get("/api/v1/plugins/featured")
        assert resp.status_code == 200
        assert "plugins" in resp.json()

    def test_categories(self):
        resp = client.get("/api/v1/plugins/categories")
        assert resp.status_code == 200
        assert "categories" in resp.json()

    def test_installed(self):
        resp = client.get("/api/v1/plugins/installed")
        assert resp.status_code == 200
        assert "installed" in resp.json()

    def test_uninstall_plugin_no_pg(self):
        with patch('plugins_marketplace._pg_pool', None):
            resp = client.delete("/api/v1/plugins/uninstall/test-plugin")
            assert resp.status_code == 503

    def test_review_plugin_no_pg(self):
        with patch('plugins_marketplace._pg_pool', None):
            resp = client.post("/api/v1/plugins/00000000-0000-0000-0000-000000000000/review", json={
                "user_id": "user-1",
                "rating": 5,
                "review_text": "Great plugin!",
            })
            assert resp.status_code == 503

    def test_delete_plugin_no_pg(self):
        with patch('plugins_marketplace._pg_pool', None):
            resp = client.delete("/api/v1/plugins/00000000-0000-0000-0000-000000000000")
            assert resp.status_code == 503


class TestModels:
    def test_publish_plugin_request(self):
        req = PublishPluginRequest(
            name="test", display_name="Test", description="desc",
            category="utility", plugin_type="tool", version="1.0.0",
            tags=["test", "demo"],
        )
        assert req.name == "test"
        assert req.license == "MIT"

    def test_install_plugin_request(self):
        req = InstallPluginRequest(plugin_name="test-plugin")
        assert req.plugin_name == "test-plugin"
        assert req.config == {}

    def test_review_plugin_request_valid(self):
        req = ReviewPluginRequest(user_id="user-1", rating=5, review_text="Great")
        assert req.rating == 5

    def test_review_plugin_request_invalid_rating(self):
        with pytest.raises(Exception):
            ReviewPluginRequest(user_id="user-1", rating=0)

    def test_review_plugin_request_invalid_rating_high(self):
        with pytest.raises(Exception):
            ReviewPluginRequest(user_id="user-1", rating=6)
