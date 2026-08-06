"""Tests for EvolvixOS Plugin Security + Dependencies + Versioning v2.0"""

import pytest
import os
import sys
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from plugins_security import router, InputSanitizer, DependencyManager, VersionManager, PluginAnalytics, SafeReviewRequest, SafePublishRequest, SafeInstallRequest

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestInputSanitizer:
    def test_sanitize_text_basic(self):
        assert InputSanitizer.sanitize_text("hello") == "hello"
    
    def test_sanitize_text_strips_xss(self):
        result = InputSanitizer.sanitize_text("<script>alert('xss')</script>hello")
        assert "<script>" not in result
        assert "hello" in result
    
    def test_sanitize_text_max_length(self):
        result = InputSanitizer.sanitize_text("a" * 5000, max_length=100)
        assert len(result) == 100
    
    def test_sanitize_name(self):
        assert InputSanitizer.sanitize_name("test-123_name") == "test-123_name"
        assert InputSanitizer.sanitize_name("test!@#name") == "testname"
    
    def test_sanitize_name_empty(self):
        assert InputSanitizer.sanitize_name("") == ""
    
    def test_validate_rating_valid(self):
        assert InputSanitizer.validate_rating(1) == 1
        assert InputSanitizer.validate_rating(5) == 5
    
    def test_validate_rating_invalid(self):
        with pytest.raises(ValueError):
            InputSanitizer.validate_rating(0)
        with pytest.raises(ValueError):
            InputSanitizer.validate_rating(6)
    
    def test_check_sql_injection_clean(self):
        assert InputSanitizer.check_sql_injection("hello world") == False
    
    def test_check_sql_injection_detected(self):
        assert InputSanitizer.check_sql_injection("DROP TABLE users") == True
    
    def test_sanitize_plugin_source_valid(self):
        assert InputSanitizer.sanitize_plugin_source("https://github.com/test") == "https://github.com/test"
    
    def test_sanitize_plugin_source_invalid(self):
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_plugin_source("http://evil.com")
    
    def test_sanitize_plugin_source_empty(self):
        assert InputSanitizer.sanitize_plugin_source("") == ""


class TestSafeModels:
    def test_safe_review_valid(self):
        req = SafeReviewRequest(user_id="user-1", rating=5, review_text="Great plugin")
        assert req.rating == 5
    
    def test_safe_review_sanitize_xss(self):
        req = SafeReviewRequest(user_id="user-1", rating=4, review_text="<script>alert(1)</script>good")
        assert "<script>" not in req.review_text
    
    def test_safe_review_invalid_rating(self):
        with pytest.raises(Exception):
            SafeReviewRequest(user_id="user-1", rating=0)
    
    def test_safe_publish_valid(self):
        req = SafePublishRequest(name="test-plugin", display_name="Test Plugin", description="A test")
        assert req.name == "test-plugin"
    
    def test_safe_publish_sanitize_name(self):
        req = SafePublishRequest(name="test!@#plugin", display_name="Test")
        assert "!" not in req.name
    
    def test_safe_publish_tags_sanitized(self):
        req = SafePublishRequest(name="test", display_name="Test", tags=["good-tag", "bad!tag"])
        assert "!" not in req.tags[1]
    
    def test_safe_install_valid(self):
        req = SafeInstallRequest(plugin_name="test-plugin")
        assert req.plugin_name == "test-plugin"
    
    def test_safe_install_sanitize(self):
        req = SafeInstallRequest(plugin_name="test!@#plugin")
        assert "!" not in req.plugin_name


class TestDependencyManager:
    @pytest.mark.asyncio
    async def test_get_dependencies_no_pg(self):
        with patch('plugins_security._pg_pool', None), patch('plugins_security._marketplace_pool', None):
            result = await DependencyManager.get_dependencies("00000000-0000-0000-0000-000000000000")
            assert result == []
    
    @pytest.mark.asyncio
    async def test_check_dependencies_no_deps(self):
        with patch.object(DependencyManager, 'get_dependencies', new_callable=AsyncMock, return_value=[]):
            result = await DependencyManager.check_dependencies_met("test", [])
            assert result["all_met"] == True
    
    @pytest.mark.asyncio
    async def test_check_dependencies_unmet(self):
        with patch.object(DependencyManager, 'get_dependencies', new_callable=AsyncMock, return_value=[
            {"dependency_name": "redis-cache", "required": True, "min_version": "1.0.0"}
        ]):
            result = await DependencyManager.check_dependencies_met("test", [])
            assert result["all_met"] == False
            assert "redis-cache" in result["unmet"]
    
    @pytest.mark.asyncio
    async def test_check_dependencies_met(self):
        with patch.object(DependencyManager, 'get_dependencies', new_callable=AsyncMock, return_value=[
            {"dependency_name": "redis-cache", "required": True, "min_version": "1.0.0"}
        ]):
            result = await DependencyManager.check_dependencies_met("test", ["redis-cache"])
            assert result["all_met"] == True


class TestVersionManager:
    @pytest.mark.asyncio
    async def test_get_versions_no_pg(self):
        with patch('plugins_security._pg_pool', None), patch('plugins_security._marketplace_pool', None):
            result = await VersionManager.get_versions("00000000-0000-0000-0000-000000000000")
            assert result["count"] == 0


class TestPluginAnalytics:
    @pytest.mark.asyncio
    async def test_record_event_no_pg(self):
        with patch('plugins_security._pg_pool', None), patch('plugins_security._marketplace_pool', None):
            result = await PluginAnalytics.record_event("test", "install")
            assert result == False
    
    @pytest.mark.asyncio
    async def test_get_analytics_no_pg(self):
        with patch('plugins_security._pg_pool', None), patch('plugins_security._marketplace_pool', None):
            result = await PluginAnalytics.get_analytics()
            assert "events" in result


class TestSecurityEndpoints:
    def test_security_status(self):
        resp = client.get("/api/v1/plugins/security/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "2.0.0"
        assert data["input_sanitization"] == True
        assert data["xss_protection"] == True
        assert data["sql_injection_detection"] == True
        assert data["plugin_dependencies"] == True
        assert data["versioning"] == True
        assert data["rollback"] == True
        assert data["analytics"] == True
    
    def test_safe_review_no_pg(self):
        with patch('plugins_security._pg_pool', None), patch('plugins_security._marketplace_pool', None):
            resp = client.post("/api/v1/plugins/00000000-0000-0000-0000-000000000000/safe-review", json={
                "user_id": "user-1", "rating": 5, "review_text": "Great!"
            })
            assert resp.status_code == 503
    
    def test_safe_review_sql_injection(self):
        with patch('plugins_security._pg_pool', None), patch('plugins_security._marketplace_pool', None):
            resp = client.post("/api/v1/plugins/00000000-0000-0000-0000-000000000000/safe-review", json={
                "user_id": "user-1", "rating": 5, "review_text": "DROP TABLE users"
            })
            assert resp.status_code in [400, 503]
    
    def test_safe_publish_no_pg(self):
        with patch('plugins_security._pg_pool', None), patch('plugins_security._marketplace_pool', None):
            resp = client.post("/api/v1/plugins/safe-publish", json={
                "name": "test-plugin", "display_name": "Test Plugin"
            })
            assert resp.status_code == 503
    
    def test_safe_install_no_pg(self):
        with patch('plugins_security._pg_pool', None), patch('plugins_security._marketplace_pool', None):
            resp = client.post("/api/v1/plugins/safe-install", json={
                "plugin_name": "test-plugin"
            })
            assert resp.status_code == 503
    
    def test_get_dependencies(self):
        resp = client.get("/api/v1/plugins/00000000-0000-0000-0000-000000000000/dependencies")
        assert resp.status_code == 200
        assert "dependencies" in resp.json()
    
    def test_get_versions(self):
        resp = client.get("/api/v1/plugins/00000000-0000-0000-0000-000000000000/versions")
        assert resp.status_code == 200
        assert "versions" in resp.json()
    
    def test_analytics_overview(self):
        resp = client.get("/api/v1/plugins/analytics/overview")
        assert resp.status_code == 200
        assert "events" in resp.json()
    
    def test_plugin_analytics(self):
        resp = client.get("/api/v1/plugins/00000000-0000-0000-0000-000000000000/analytics")
        assert resp.status_code == 200
        assert "events" in resp.json()
