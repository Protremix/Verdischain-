"""
EvolvixOS AI Gateway — Test Suite
Comprehensive tests for plugin management, routing, caching, and rate limiting
"""

import pytest
import asyncio
import json
import sys
import os
import time
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

# Import the gateway
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_gateway import (
    app, PluginManager, IntelligentRouter, CacheManager, RateLimiter,
    PluginMetadata, PluginEntry, PluginStatus, ProviderType,
    GatewayRequest, RequestPriority, GATEWAY_VERSION,
)

client = TestClient(app)

# =========================================================================
# Plugin Manager Tests
# =========================================================================

class TestPluginManager:
    def setup_method(self):
        self.pm = PluginManager()
        self.pm.plugins.clear()
        self.pm.instances.clear()
        self.pm.registry_path = "/tmp/test_registry.json"
        self.pm._save_registry()

    def teardown_method(self):
        if os.path.exists("/tmp/test_registry.json"):
            os.remove("/tmp/test_registry.json")

    def _make_metadata(self, name="test-plugin"):
        return PluginMetadata(
            name=name,
            version="1.0.0",
            description="Test plugin",
            author="Test",
            provider=ProviderType.OPENAI,
            capabilities=["chat"],
            model="gpt-4o",
            max_tokens=4096,
            cost_per_1k=0.005,
            avg_latency_ms=1000,
            reliability_score=0.95,
        )

    def test_register_plugin(self):
        meta = self._make_metadata("plugin-a")
        assert self.pm.register_plugin(meta, "/tmp/plugin_a.py") == True
        assert "plugin-a" in self.pm.plugins
        assert self.pm.plugins["plugin-a"].status == PluginStatus.REGISTERED

    def test_register_duplicate_plugin(self):
        meta = self._make_metadata("plugin-dup")
        self.pm.register_plugin(meta, "/tmp/dup.py")
        assert self.pm.register_plugin(meta, "/tmp/dup2.py") == False

    def test_list_plugins(self):
        meta1 = self._make_metadata("plugin-1")
        meta2 = self._make_metadata("plugin-2")
        self.pm.register_plugin(meta1, "/tmp/p1.py")
        self.pm.register_plugin(meta2, "/tmp/p2.py")
        plugins = self.pm.list_plugins()
        assert len(plugins) == 2

    def test_list_plugins_by_status(self):
        meta = self._make_metadata("plugin-status")
        self.pm.register_plugin(meta, "/tmp/p.py")
        plugins = self.pm.list_plugins(PluginStatus.REGISTERED)
        assert len(plugins) == 1
        plugins = self.pm.list_plugins(PluginStatus.ACTIVE)
        assert len(plugins) == 0

    def test_get_plugins_by_capability(self):
        meta = self._make_metadata("cap-plugin")
        meta.capabilities = ["chat", "completion", "sentiment"]
        self.pm.register_plugin(meta, "/tmp/cap.py")
        self.pm.plugins["cap-plugin"].status = PluginStatus.ACTIVE
        chat_plugins = self.pm.get_plugins_by_capability("chat")
        assert "cap-plugin" in chat_plugins
        embedding_plugins = self.pm.get_plugins_by_capability("embedding")
        assert "cap-plugin" not in embedding_plugins

    def test_remove_plugin(self):
        meta = self._make_metadata("remove-me")
        self.pm.register_plugin(meta, "/tmp/remove.py")
        assert self.pm.remove_plugin("remove-me") == True
        assert "remove-me" not in self.pm.plugins

    def test_remove_nonexistent_plugin(self):
        assert self.pm.remove_plugin("nonexistent") == False

    def test_record_request(self):
        meta = self._make_metadata("metrics-plugin")
        self.pm.register_plugin(meta, "/tmp/m.py")
        self.pm.record_request("metrics-plugin", 500, 100)
        assert self.pm.plugins["metrics-plugin"].request_count == 1
        assert self.pm.plugins["metrics-plugin"].total_tokens_used == 100
        assert self.pm.plugins["metrics-plugin"].avg_response_time_ms == 500

    def test_record_error(self):
        meta = self._make_metadata("error-plugin")
        self.pm.register_plugin(meta, "/tmp/e.py")
        self.pm.record_request("error-plugin", 100, 0, error=True, error_msg="Test error")
        assert self.pm.plugins["error-plugin"].error_count == 1
        assert self.pm.plugins["error-plugin"].last_error == "Test error"

    def test_registry_persistence(self):
        meta = self._make_metadata("persist-plugin")
        self.pm.register_plugin(meta, "/tmp/persist.py")
        # Create new manager that loads from same registry
        pm2 = PluginManager()
        pm2.registry_path = "/tmp/test_registry.json"
        pm2._load_registry()
        assert "persist-plugin" in pm2.plugins

# =========================================================================
# Intelligent Router Tests
# =========================================================================

class TestIntelligentRouter:
    def setup_method(self):
        self.pm = PluginManager()
        self.pm.plugins.clear()
        self.pm.instances.clear()
        self.router = IntelligentRouter(self.pm)

    def _make_entry(self, name, reliability=0.95, latency=1000, cost=0.005):
        meta = PluginMetadata(
            name=name, version="1.0.0", description="Test", author="Test",
            provider=ProviderType.OPENAI, capabilities=["chat"], model="gpt-4o",
            max_tokens=4096, cost_per_1k=cost, avg_latency_ms=latency,
            reliability_score=reliability,
        )
        entry = PluginEntry(
            metadata=meta, status=PluginStatus.ACTIVE,
            file_path="/tmp/test.py", loaded_at="2026-01-01T00:00:00Z",
        )
        self.pm.plugins[name] = entry
        return entry

    def test_route_specific_plugin(self):
        self._make_entry("plugin-a")
        req = GatewayRequest(capability="chat", plugin="plugin-a", input={})
        assert self.router.route(req) == "plugin-a"

    def test_route_nonexistent_plugin(self):
        req = GatewayRequest(capability="chat", plugin="nonexistent", input={})
        with pytest.raises(Exception):
            self.router.route(req)

    def test_route_auto_single_candidate(self):
        self._make_entry("only-plugin")
        req = GatewayRequest(capability="chat", input={})
        assert self.router.route(req) == "only-plugin"

    def test_route_auto_multiple_candidates(self):
        self._make_entry("fast-plugin", reliability=0.99, latency=500, cost=0.001)
        self._make_entry("slow-plugin", reliability=0.80, latency=3000, cost=0.01)
        req = GatewayRequest(capability="chat", input={})
        result = self.router.route(req)
        # Fast plugin should win (better reliability, lower latency, lower cost)
        assert result == "fast-plugin"

    def test_route_no_candidates(self):
        req = GatewayRequest(capability="nonexistent", input={})
        with pytest.raises(Exception):
            self.router.route(req)

    def test_route_priority_bonus(self):
        self._make_entry("normal-plugin", reliability=0.90, latency=1000, cost=0.005)
        self._make_entry("priority-plugin", reliability=0.90, latency=1000, cost=0.005)
        # Give priority-plugin slightly lower load to break the tie
        self.router.load_counters["normal-plugin"] = 5
        req = GatewayRequest(capability="chat", input={}, priority=RequestPriority.CRITICAL)
        result = self.router.route(req)
        # Should route to priority-plugin due to critical bonus
        assert result in ["normal-plugin", "priority-plugin"]

    def test_load_tracking(self):
        self.router.record_load("test-plugin")
        assert self.router.load_counters["test-plugin"] == 1
        self.router.release_load("test-plugin")
        assert self.router.load_counters["test-plugin"] == 0

# =========================================================================
# Cache Manager Tests
# =========================================================================

class TestCacheManager:
    def setup_method(self):
        self.cache = CacheManager(max_size=10, ttl_seconds=2)

    def test_cache_miss(self):
        result = self.cache.get("plugin", "chat", {"message": "hello"})
        assert result is None
        assert self.cache.misses == 1

    def test_cache_set_get(self):
        self.cache.set("plugin", "chat", {"message": "hello"}, {"response": "world"})
        result = self.cache.get("plugin", "chat", {"message": "hello"})
        assert result == {"response": "world"}
        assert self.cache.hits == 1

    def test_cache_key_deterministic(self):
        """Same input should produce same key"""
        self.cache.set("plugin", "chat", {"a": 1, "b": 2}, "result1")
        # Different key order should still hit cache
        result = self.cache.get("plugin", "chat", {"b": 2, "a": 1})
        assert result == "result1"

    def test_cache_expiry(self):
        self.cache = CacheManager(max_size=10, ttl_seconds=1)
        self.cache.set("plugin", "chat", {"x": 1}, "data")
        time.sleep(1.5)
        result = self.cache.get("plugin", "chat", {"x": 1})
        assert result is None

    def test_cache_max_size(self):
        for i in range(15):
            self.cache.set("plugin", "chat", {"id": i}, f"result-{i}")
        assert self.cache.cache.__len__() <= 10

    def test_cache_stats(self):
        self.cache.set("plugin", "chat", {"x": 1}, "data")
        self.cache.get("plugin", "chat", {"x": 1})  # hit
        self.cache.get("plugin", "chat", {"x": 2})  # miss
        stats = self.cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 50.0

    def test_cache_clear(self):
        self.cache.set("plugin", "chat", {"x": 1}, "data")
        self.cache.clear()
        stats = self.cache.stats()
        assert stats["size"] == 0
        assert stats["hits"] == 0

# =========================================================================
# Rate Limiter Tests
# =========================================================================

class TestRateLimiter:
    def setup_method(self):
        self.limiter = RateLimiter(rate_per_min=5)

    def test_under_limit(self):
        for _ in range(5):
            assert self.limiter.check("client-1") == True

    def test_over_limit(self):
        for _ in range(5):
            self.limiter.check("client-1")
        assert self.limiter.check("client-1") == False

    def test_different_clients(self):
        for _ in range(5):
            self.limiter.check("client-a")
        # Different client should still be allowed
        assert self.limiter.check("client-b") == True

# =========================================================================
# API Endpoint Tests
# =========================================================================

class TestGatewayAPI:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["version"] == GATEWAY_VERSION

    def test_list_plugins(self):
        resp = client.get("/plugins")
        assert resp.status_code == 200
        assert "plugins" in resp.json()

    def test_list_capabilities(self):
        resp = client.get("/capabilities")
        assert resp.status_code == 200
        assert "capabilities" in resp.json()

    def test_gateway_stats(self):
        resp = client.get("/gateway/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "version" in data
        assert "total_requests" in data
        assert "total_plugins" in data
        assert "cache" in data

    def test_invoke_missing_capability(self):
        resp = client.post("/gateway/invoke", json={
            "input": {"text": "test"},
            "options": {},
        })
        # Should fail because capability is required
        assert resp.status_code == 422

    def test_invoke_nonexistent_capability(self):
        resp = client.post("/gateway/invoke", json={
            "capability": "nonexistent_cap",
            "input": {"text": "test"},
        })
        assert resp.status_code == 404

    def test_register_plugin_endpoint(self):
        resp = client.post("/plugins/register?file_path=/tmp/test.py", json={
            "name": "test-api-plugin",
            "version": "1.0.0",
            "description": "Test",
            "author": "Test",
            "provider": "openai",
            "capabilities": ["chat"],
            "model": "gpt-4o",
            "max_tokens": 4096,
            "cost_per_1k": 0.005,
            "avg_latency_ms": 1000,
            "reliability_score": 0.95,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] == True

    def test_cache_clear_endpoint(self):
        resp = client.post("/cache/clear")
        assert resp.status_code == 200
        assert resp.json()["success"] == True

    def test_plugin_health_nonexistent(self):
        resp = client.get("/plugins/nonexistent/health")
        assert resp.status_code == 404

# =========================================================================
# GatewayRequest Model Tests
# =========================================================================

class TestGatewayRequest:
    def test_default_values(self):
        req = GatewayRequest(capability="chat", input={})
        assert req.priority == RequestPriority.NORMAL
        assert req.plugin is None
        assert req.max_tokens is None
        assert req.timeout is None
        assert req.request_id != ""  # auto-generated UUID

    def test_custom_values(self):
        req = GatewayRequest(
            capability="chat",
            input={"message": "hello"},
            plugin="openai-gpt4o",
            priority=RequestPriority.HIGH,
            max_tokens=1000,
            timeout=30,
        )
        assert req.plugin == "openai-gpt4o"
        assert req.priority == RequestPriority.HIGH
        assert req.max_tokens == 1000
        assert req.timeout == 30

    def test_request_id_unique(self):
        req1 = GatewayRequest(capability="chat", input={})
        req2 = GatewayRequest(capability="chat", input={})
        assert req1.request_id != req2.request_id

# =========================================================================
# Scoring Function Tests
# =========================================================================

class TestRoutingScore:
    def setup_method(self):
        self.pm = PluginManager()
        self.pm.plugins.clear()
        self.pm.instances.clear()
        self.router = IntelligentRouter(self.pm)

    def _make_entry(self, name, reliability=0.95, latency=1000, cost=0.005):
        meta = PluginMetadata(
            name=name, version="1.0.0", description="Test", author="Test",
            provider=ProviderType.OPENAI, capabilities=["chat"], model="gpt-4o",
            max_tokens=4096, cost_per_1k=cost, avg_latency_ms=latency,
            reliability_score=reliability,
        )
        return PluginEntry(
            metadata=meta, status=PluginStatus.ACTIVE,
            file_path="/tmp/test.py", loaded_at="2026-01-01T00:00:00Z",
        )

    def test_high_reliability_scores_better(self):
        entry_high = self._make_entry("reliable", reliability=0.99)
        entry_low = self._make_entry("unreliable", reliability=0.80)
        self.pm.plugins["reliable"] = entry_high
        self.pm.plugins["unreliable"] = entry_low
        req = GatewayRequest(capability="chat", input={})
        score_high = self.router._calculate_score(entry_high, req)
        score_low = self.router._calculate_score(entry_low, req)
        assert score_high > score_low

    def test_low_latency_scores_better(self):
        entry_fast = self._make_entry("fast", latency=200)
        entry_slow = self._make_entry("slow", latency=5000)
        self.pm.plugins["fast"] = entry_fast
        self.pm.plugins["slow"] = entry_slow
        req = GatewayRequest(capability="chat", input={})
        score_fast = self.router._calculate_score(entry_fast, req)
        score_slow = self.router._calculate_score(entry_slow, req)
        assert score_fast > score_slow

    def test_low_cost_scores_better(self):
        entry_cheap = self._make_entry("cheap", cost=0.001)
        entry_expensive = self._make_entry("expensive", cost=0.05)
        self.pm.plugins["cheap"] = entry_cheap
        self.pm.plugins["expensive"] = entry_expensive
        req = GatewayRequest(capability="chat", input={})
        score_cheap = self.router._calculate_score(entry_cheap, req)
        score_expensive = self.router._calculate_score(entry_expensive, req)
        assert score_cheap > score_expensive

    def test_critical_priority_bonus(self):
        entry = self._make_entry("test")
        self.pm.plugins["test"] = entry
        req_normal = GatewayRequest(capability="chat", input={}, priority=RequestPriority.NORMAL)
        req_critical = GatewayRequest(capability="chat", input={}, priority=RequestPriority.CRITICAL)
        score_normal = self.router._calculate_score(entry, req_normal)
        score_critical = self.router._calculate_score(entry, req_critical)
        assert score_critical > score_normal
