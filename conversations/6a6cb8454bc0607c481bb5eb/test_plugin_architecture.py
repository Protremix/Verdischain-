"""
Tests for EvolvixOS Universal Plugin Architecture + Intelligent Router
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugin_architecture import (
    UniversalPlugin, ProviderPlugin, PluginMetadata, PluginType,
    PluginStatus, Capability, PluginRegistry, PluginManager
)
from intelligent_router import (
    IntelligentRouter, RoutingPolicy, RoutingDecision, ProviderHealth
)


# =========================================================================
# Plugin Architecture Tests
# =========================================================================

class TestPluginMetadata:
    def test_creation(self):
        meta = PluginMetadata(
            id="test-llm",
            name="Test LLM",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            capabilities=[Capability.CHAT, Capability.COMPLETION],
        )
        assert meta.id == "test-llm"
        assert meta.plugin_type == PluginType.LLM_PROVIDER
        assert len(meta.capabilities) == 2
    
    def test_to_dict(self):
        meta = PluginMetadata(
            id="test",
            name="Test",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
        )
        d = meta.to_dict()
        assert d["plugin_type"] == "llm_provider"
        assert d["id"] == "test"


class TestPluginEnums:
    def test_plugin_types(self):
        assert PluginType.LLM_PROVIDER.value == "llm_provider"
        assert PluginType.IMAGE_PROVIDER.value == "image_provider"
        assert PluginType.AGENT.value == "agent"
        assert PluginType.SERVICE.value == "service"
    
    def test_plugin_statuses(self):
        assert PluginStatus.REGISTERED.value == "registered"
        assert PluginStatus.ACTIVE.value == "active"
        assert PluginStatus.ERROR.value == "error"
    
    def test_capabilities(self):
        assert Capability.CHAT.value == "chat"
        assert Capability.CODE_GENERATION.value == "code_generation"
        assert Capability.IMAGE_GENERATION.value == "image_generation"
        assert Capability.STREAMING.value == "streaming"


class TestProviderPlugin:
    def test_creation(self):
        meta = PluginMetadata(
            id="test-provider",
            name="Test Provider",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            capabilities=[Capability.CHAT],
            requires_api_key=True,
            api_key_env="TEST_API_KEY",
        )
        
        class TestProvider(ProviderPlugin):
            async def initialize(self):
                self.status = PluginStatus.ACTIVE
            
            async def _execute(self, capability, input_data, options):
                return {"content": "test response", "provider": self.id}
        
        plugin = TestProvider(meta)
        assert plugin.id == "test-provider"
        assert plugin.is_local == False
    
    @pytest.mark.asyncio
    async def test_invoke(self):
        meta = PluginMetadata(
            id="test-invoke",
            name="Test",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            capabilities=[Capability.CHAT],
        )
        
        class TestProvider(ProviderPlugin):
            async def initialize(self):
                self.status = PluginStatus.ACTIVE
            
            async def _execute(self, capability, input_data, options):
                return {"content": "hello", "provider": self.id}
        
        plugin = TestProvider(meta)
        await plugin.initialize()
        result = await plugin.invoke("chat", {"messages": []})
        assert result["content"] == "hello"
        assert plugin._metrics["invocations"] == 1
    
    @pytest.mark.asyncio
    async def test_invoke_error(self):
        meta = PluginMetadata(
            id="test-error",
            name="Test",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            capabilities=[Capability.CHAT],
        )
        
        class ErrorProvider(ProviderPlugin):
            async def initialize(self):
                self.status = PluginStatus.ACTIVE
            
            async def _execute(self, capability, input_data, options):
                raise Exception("API error")
        
        plugin = ErrorProvider(meta)
        await plugin.initialize()
        with pytest.raises(Exception):
            await plugin.invoke("chat", {})
        assert plugin._metrics["errors"] == 1
    
    def test_supports_capability(self):
        meta = PluginMetadata(
            id="test-caps",
            name="Test",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            capabilities=[Capability.CHAT, Capability.COMPLETION],
        )
        
        class TestProvider(ProviderPlugin):
            async def initialize(self): pass
            async def _execute(self, c, i, o): return {}
        
        plugin = TestProvider(meta)
        assert plugin.supports_capability("chat") == True
        assert plugin.supports_capability("completion") == True
        assert plugin.supports_capability("vision") == False
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        meta = PluginMetadata(
            id="test-health",
            name="Test",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
        )
        
        class TestProvider(ProviderPlugin):
            async def initialize(self): self.status = PluginStatus.ACTIVE
            async def _execute(self, c, i, o): return {}
        
        plugin = TestProvider(meta)
        await plugin.initialize()
        health = await plugin.health_check()
        assert health["healthy"] == True


# =========================================================================
# Plugin Registry Tests
# =========================================================================

class TestPluginRegistry:
    @pytest.fixture
    def registry(self):
        return PluginRegistry()
    
    @pytest.fixture
    def test_plugin(self):
        meta = PluginMetadata(
            id="reg-test",
            name="Registry Test",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            capabilities=[Capability.CHAT, Capability.COMPLETION],
        )
        
        class TestProvider(ProviderPlugin):
            async def initialize(self): self.status = PluginStatus.ACTIVE
            async def _execute(self, c, i, o): return {}
        
        return TestProvider(meta)
    
    def test_register(self, registry, test_plugin):
        registry.register(test_plugin)
        assert registry.get("reg-test") is not None
        assert len(registry.list_all()) == 1
    
    def test_register_metadata_only(self, registry):
        meta = PluginMetadata(
            id="meta-only",
            name="Meta Only",
            version="1.0.0",
            plugin_type=PluginType.AGENT,
        )
        registry.register_metadata(meta)
        assert registry.get_metadata("meta-only") is not None
        assert registry.get("meta-only") is None
    
    def test_unregister(self, registry, test_plugin):
        registry.register(test_plugin)
        assert registry.unregister("reg-test") == True
        assert registry.get("reg-test") is None
        assert registry.unregister("nonexistent") == False
    
    def test_list_by_type(self, registry, test_plugin):
        registry.register(test_plugin)
        llm_plugins = registry.list_by_type(PluginType.LLM_PROVIDER)
        assert len(llm_plugins) == 1
        assert llm_plugins[0].id == "reg-test"
    
    def test_list_by_capability(self, registry, test_plugin):
        registry.register(test_plugin)
        chat_plugins = registry.list_by_capability(Capability.CHAT)
        assert len(chat_plugins) == 1
    
    def test_find_providers(self, registry, test_plugin):
        registry.register(test_plugin)
        # Add a local provider
        local_meta = PluginMetadata(
            id="local-test",
            name="Local",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            capabilities=[Capability.CHAT],
            is_local=True,
            priority=80,
        )
        
        class LocalProvider(ProviderPlugin):
            async def initialize(self): self.status = PluginStatus.ACTIVE
            async def _execute(self, c, i, o): return {}
        
        registry.register(LocalProvider(local_meta))
        
        # Local should be preferred
        providers = registry.find_providers("chat", prefer_local=True)
        assert providers[0].id == "local-test"
        
        # Without local preference
        providers = registry.find_providers("chat", prefer_local=False)
        # Higher priority first
        assert providers[0].id == "local-test"  # priority=80 > priority=50
    
    def test_stats(self, registry, test_plugin):
        registry.register(test_plugin)
        stats = registry.stats()
        assert stats["total_plugins"] == 1
        assert "llm_provider" in stats["by_type"]


# =========================================================================
# Plugin Manager Tests
# =========================================================================

class TestPluginManager:
    @pytest.fixture
    def setup(self):
        registry = PluginRegistry()
        manager = PluginManager(registry)
        return registry, manager
    
    @pytest.fixture
    def test_plugin(self):
        meta = PluginMetadata(
            id="mgr-test",
            name="Manager Test",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            capabilities=[Capability.CHAT],
        )
        
        class TestProvider(ProviderPlugin):
            async def initialize(self): self.status = PluginStatus.ACTIVE
            async def _execute(self, c, i, o): return {"content": "ok"}
        
        return TestProvider(meta)
    
    @pytest.mark.asyncio
    async def test_load_plugin(self, setup, test_plugin):
        registry, manager = setup
        registry.register(test_plugin)
        result = await manager.load_plugin("mgr-test")
        assert result == True
        assert test_plugin.status == PluginStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_unload_plugin(self, setup, test_plugin):
        registry, manager = setup
        registry.register(test_plugin)
        await manager.load_plugin("mgr-test")
        result = await manager.unload_plugin("mgr-test")
        assert result == True
        assert test_plugin.status == PluginStatus.INACTIVE
    
    @pytest.mark.asyncio
    async def test_reload_plugin(self, setup, test_plugin):
        registry, manager = setup
        registry.register(test_plugin)
        await manager.load_plugin("mgr-test")
        result = await manager.reload_plugin("mgr-test")
        assert result == True
    
    @pytest.mark.asyncio
    async def test_load_not_registered(self, setup):
        registry, manager = setup
        result = await manager.load_plugin("nonexistent")
        assert result == False
    
    @pytest.mark.asyncio
    async def test_invoke_plugin(self, setup, test_plugin):
        registry, manager = setup
        registry.register(test_plugin)
        await manager.load_plugin("mgr-test")
        result = await manager.invoke_plugin("mgr-test", "chat", {"messages": []})
        assert result["content"] == "ok"
    
    @pytest.mark.asyncio
    async def test_invoke_not_active(self, setup, test_plugin):
        registry, manager = setup
        registry.register(test_plugin)
        with pytest.raises(ValueError):
            await manager.invoke_plugin("mgr-test", "chat", {})
    
    @pytest.mark.asyncio
    async def test_load_all(self, setup):
        registry, manager = setup
        for i in range(3):
            meta = PluginMetadata(
                id=f"batch-{i}",
                name=f"Batch {i}",
                version="1.0.0",
                plugin_type=PluginType.LLM_PROVIDER,
                capabilities=[Capability.CHAT],
            )
            
            class TestProvider(ProviderPlugin):
                async def initialize(self): self.status = PluginStatus.ACTIVE
                async def _execute(self, c, d, o): return {}
            
            registry.register(TestProvider(meta))
        
        results = await manager.load_all()
        assert all(results.values())


# =========================================================================
# Intelligent Router Tests
# =========================================================================

class TestIntelligentRouter:
    @pytest.fixture
    def setup(self):
        registry = PluginRegistry()
        policy = RoutingPolicy(prefer_local=True)
        router = IntelligentRouter(registry, policy)
        return registry, router
    
    def _make_provider(self, id, caps, is_local=False, priority=50, cost=0.01):
        meta = PluginMetadata(
            id=id,
            name=id.replace("-", " ").title(),
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            capabilities=[Capability(c) for c in caps],
            is_local=is_local,
            priority=priority,
            cost_per_1k_tokens=cost,
        )
        
        class Provider(ProviderPlugin):
            async def initialize(self): self.status = PluginStatus.ACTIVE
            async def _execute(self, c, i, o): return {"content": "test", "provider": self.id}
        
        return Provider(meta)
    
    def test_provider_health(self, setup):
        _, router = setup
        health = router.get_health("test-provider")
        assert health.healthy == True
        assert health.consecutive_failures == 0
    
    def test_health_record_success(self, setup):
        _, router = setup
        health = router.get_health("test")
        health.record_success(100)
        assert health.avg_latency_ms > 0
        assert health.total_requests == 1
    
    def test_health_record_failure(self, setup):
        _, router = setup
        health = router.get_health("test")
        health.record_failure()
        assert health.consecutive_failures == 1
        health.record_failure()
        health.record_failure()
        assert health.circuit_open == True
        assert health.healthy == False
    
    def test_circuit_recovery(self, setup):
        _, router = setup
        health = router.get_health("test")
        for _ in range(3):
            health.record_failure()
        assert health.circuit_open == True
        health.record_success(100)
        assert health.circuit_open == False
        assert health.consecutive_failures == 0
    
    def test_route_single_provider(self, setup):
        registry, router = setup
        plugin = self._make_provider("single", ["chat"], priority=80)
        registry.register(plugin)
        
        decision = router.route("chat")
        assert decision.selected_plugin_id == "single"
        assert len(decision.fallback_chain) == 0
    
    def test_route_prefers_local(self, setup):
        registry, router = setup
        cloud = self._make_provider("cloud-1", ["chat"], is_local=False, priority=90, cost=0.03)
        local = self._make_provider("local-1", ["chat"], is_local=True, priority=50, cost=0.0)
        registry.register(cloud)
        registry.register(local)
        
        decision = router.route("chat")
        assert decision.is_local == True
        assert decision.selected_plugin_id == "local-1"
    
    def test_route_with_fallback_chain(self, setup):
        registry, router = setup
        for i in range(3):
            p = self._make_provider(f"provider-{i}", ["chat"], priority=70 - i * 10)
            registry.register(p)
        
        decision = router.route("chat")
        assert decision.selected_plugin_id == "provider-0"
        assert len(decision.fallback_chain) == 2
    
    def test_route_excludes_circuit_broken(self, setup):
        registry, router = setup
        p1 = self._make_provider("p1", ["chat"], priority=90)
        p2 = self._make_provider("p2", ["chat"], priority=50)
        registry.register(p1)
        registry.register(p2)
        
        # Break circuit on p1
        health = router.get_health("p1")
        for _ in range(3):
            health.record_failure()
        
        decision = router.route("chat")
        assert decision.selected_plugin_id == "p2"
    
    def test_route_no_providers(self, setup):
        _, router = setup
        with pytest.raises(ValueError):
            router.route("nonexistent_capability")
    
    @pytest.mark.asyncio
    async def test_route_and_invoke(self, setup):
        registry, router = setup
        plugin = self._make_provider("invoke-test", ["chat"])
        registry.register(plugin)
        await plugin.initialize()
        
        result = await router.route_and_invoke("chat", {"messages": [{"role": "user", "content": "hi"}]})
        assert result["output"]["content"] == "test"
        assert result["provider"] == "invoke-test"
        assert result["fallback_used"] == False
    
    @pytest.mark.asyncio
    async def test_route_and_invoke_with_fallback(self, setup):
        registry, router = setup
        
        meta_bad = PluginMetadata(
            id="bad-provider",
            name="Bad Provider",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            capabilities=[Capability.CHAT],
            priority=90,
        )
        
        class BadProvider(ProviderPlugin):
            async def initialize(self): self.status = PluginStatus.ACTIVE
            async def _execute(self, c, i, o): raise Exception("API down")
        
        good = self._make_provider("good-provider", ["chat"], priority=50)
        registry.register(BadProvider(meta_bad))
        registry.register(good)
        await BadProvider(meta_bad).initialize()
        await good.initialize()
        
        # Route should try bad-provider first (higher priority), fail, then fallback
        result = await router.route_and_invoke("chat", {})
        assert result["fallback_used"] == True
        assert result["provider"] == "good-provider"
    
    def test_routing_stats(self, setup):
        registry, router = setup
        plugin = self._make_provider("stats-test", ["chat"])
        registry.register(plugin)
        
        router.route("chat")
        stats = router.stats()
        assert stats["total_routes"] == 1
    
    def test_routing_policy_weights(self):
        policy = RoutingPolicy(weights={"capability_match": 50.0, "reliability": 30.0})
        assert policy.weights["capability_match"] == 50.0
    
    def test_routing_policy_score(self, setup):
        registry, router = setup
        meta = PluginMetadata(
            id="score-test",
            name="Score Test",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            capabilities=[Capability.CHAT],
            priority=80,
            cost_per_1k_tokens=0.02,
        )
        health = ProviderHealth(plugin_id="score-test")
        health.avg_latency_ms = 500
        
        score = router.policy.score_provider(meta, health, "chat")
        assert score > 0
