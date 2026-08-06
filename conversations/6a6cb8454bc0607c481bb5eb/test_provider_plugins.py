"""
EvolvixOS Provider Plugin Mock Tests
Tests all 24 provider plugins using httpx mocking — no real API keys needed.
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugin_architecture import (
    PluginRegistry, PluginManager, PluginMetadata, PluginType,
    PluginStatus, Capability, ProviderPlugin
)


def mock_response(json_data: Dict, status_code: int = 200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    resp.text = str(json_data)
    resp.content = b"mock_audio_data"
    return resp


class TestLLMProviders:
    @pytest.fixture
    def registry(self):
        from llm_providers import register_all_providers
        r = PluginRegistry()
        register_all_providers(r)
        return r

    def test_registry_has_10_llm_providers(self, registry):
        providers = registry.list_by_type(PluginType.LLM_PROVIDER)
        assert len(providers) == 10

    def test_all_llm_providers_have_chat_capability(self, registry):
        providers = registry.list_by_capability(Capability.CHAT)
        assert len(providers) >= 10

    @pytest.mark.asyncio
    async def test_openai_provider_execute(self, registry):
        from llm_providers import create_plugin
        plugin = create_plugin("openai")
        assert plugin is not None
        assert plugin.id == "openai"
        assert plugin.is_local == False

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response({
                "choices": [{"message": {"content": "Hello!"}}],
                "usage": {"total_tokens": 50},
            })
            result = await plugin._execute("chat", {"messages": [{"role": "user", "content": "hi"}]}, {})
            assert result["content"] == "Hello!"
            assert result["provider"] == "openai"

    @pytest.mark.asyncio
    async def test_anthropic_provider_execute(self, registry):
        from llm_providers import create_plugin
        plugin = create_plugin("anthropic")
        assert plugin is not None
        assert plugin.id == "anthropic"
        plugin.config["api_key"] = "test-key"

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response({
                "content": [{"text": "Claude response"}],
                "usage": {"input_tokens": 10, "output_tokens": 20},
            })
            result = await plugin._execute("chat", {"messages": [{"role": "user", "content": "hi"}]}, {})
            assert "content" in result
            assert result["provider"] == "anthropic"

    @pytest.mark.asyncio
    async def test_deepseek_provider_execute(self, registry):
        from llm_providers import create_plugin
        plugin = create_plugin("deepseek")
        assert plugin is not None

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response({
                "choices": [{"message": {"content": "DeepSeek says hi"}}],
                "usage": {"total_tokens": 30},
            })
            result = await plugin._execute("chat", {"messages": [{"role": "user", "content": "hi"}]}, {})
            assert result["content"] == "DeepSeek says hi"

    @pytest.mark.asyncio
    async def test_mistral_provider_execute(self, registry):
        from llm_providers import create_plugin
        plugin = create_plugin("mistral")
        assert plugin is not None

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response({
                "choices": [{"message": {"content": "Mistral response"}}],
                "usage": {"total_tokens": 25},
            })
            result = await plugin._execute("chat", {"messages": [{"role": "user", "content": "hi"}]}, {})
            assert result["content"] == "Mistral response"

    def test_google_gemini_provider(self, registry):
        from llm_providers import create_plugin
        plugin = create_plugin("google")
        assert plugin is not None
        assert plugin.id == "google"

    def test_xai_grok_provider(self, registry):
        from llm_providers import create_plugin
        plugin = create_plugin("xai")
        assert plugin is not None
        assert plugin.id == "xai"

    def test_cohere_provider(self, registry):
        from llm_providers import create_plugin
        plugin = create_plugin("cohere")
        assert plugin is not None
        assert plugin.id == "cohere"

    def test_ai21_provider(self, registry):
        from llm_providers import create_plugin
        plugin = create_plugin("ai21")
        assert plugin is not None
        assert plugin.id == "ai21"

    def test_ollama_provider_local(self, registry):
        from llm_providers import create_plugin
        plugin = create_plugin("ollama")
        assert plugin is not None
        assert plugin.id == "ollama"
        assert plugin.is_local == True

    def test_vllm_provider_local(self, registry):
        from llm_providers import create_plugin
        plugin = create_plugin("vllm")
        assert plugin is not None
        assert plugin.id == "vllm"
        assert plugin.is_local == True

    @pytest.mark.asyncio
    async def test_ollama_execute_mock(self, registry):
        from llm_providers import create_plugin
        plugin = create_plugin("ollama")

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response({
                "message": {"content": "Ollama local response"},
                "eval_count": 20,
            })
            result = await plugin._execute("chat", {"messages": [{"role": "user", "content": "hi"}]}, {})
            assert "content" in result


class TestSpecializedProviders:
    @pytest.fixture
    def registry(self):
        from specialized_providers import register_all_specialized
        r = PluginRegistry()
        register_all_specialized(r)
        return r

    def test_registry_has_14_specialized(self, registry):
        stats = registry.stats()
        assert stats["total_plugins"] == 14

    def test_coding_providers(self, registry):
        providers = registry.list_by_type(PluginType.CODING_PROVIDER)
        assert len(providers) == 3

    def test_image_providers(self, registry):
        providers = registry.list_by_type(PluginType.IMAGE_PROVIDER)
        assert len(providers) == 2

    def test_speech_providers(self, registry):
        providers = registry.list_by_type(PluginType.SPEECH_PROVIDER)
        assert len(providers) == 2

    def test_search_providers(self, registry):
        providers = registry.list_by_type(PluginType.SEARCH_PROVIDER)
        assert len(providers) == 2

    @pytest.mark.asyncio
    async def test_codex_provider_execute(self, registry):
        from specialized_providers import create_specialized_plugin
        plugin = create_specialized_plugin("codex")
        assert plugin is not None

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response({
                "choices": [{"message": {"content": "def hello(): pass"}}],
                "usage": {"total_tokens": 40},
            })
            result = await plugin._execute("code_generation", {"prompt": "Write hello world"}, {})
            assert "content" in result

    @pytest.mark.asyncio
    async def test_openai_image_provider(self, registry):
        from specialized_providers import create_specialized_plugin
        plugin = create_specialized_plugin("openai-image")
        assert plugin is not None

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response({
                "data": [{"url": "https://example.com/image.png"}],
            })
            result = await plugin._execute("image_generation", {"prompt": "a cat"}, {})
            assert "image_url" in result

    @pytest.mark.asyncio
    async def test_tavily_search_provider(self, registry):
        from specialized_providers import create_specialized_plugin
        plugin = create_specialized_plugin("tavily")
        assert plugin is not None

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response({
                "results": [{"title": "Test result", "url": "https://example.com"}],
            })
            result = await plugin._execute("search", {"query": "test query"}, {})
            assert "results" in result

    @pytest.mark.asyncio
    async def test_deepl_translation_provider(self, registry):
        from specialized_providers import create_specialized_plugin
        plugin = create_specialized_plugin("deepl")
        assert plugin is not None

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response({
                "translations": [{"text": "Hola mundo", "detected_source_language": "EN"}],
            })
            result = await plugin._execute("translation", {"text": "Hello world"}, {"target_lang": "ES"})
            assert "translation" in result

    @pytest.mark.asyncio
    async def test_openai_embedding_provider(self, registry):
        from specialized_providers import create_specialized_plugin
        plugin = create_specialized_plugin("openai-embedding")
        assert plugin is not None

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response({
                "data": [{"embedding": [0.1, 0.2, 0.3]}],
                "usage": {"total_tokens": 10},
            })
            result = await plugin._execute("embedding", {"texts": ["hello"]}, {})
            assert "embeddings" in result

    @pytest.mark.asyncio
    async def test_qdrant_vector_provider(self, registry):
        from specialized_providers import create_specialized_plugin
        plugin = create_specialized_plugin("qdrant")
        assert plugin is not None
        assert plugin.is_local == True

    @pytest.mark.asyncio
    async def test_whisper_provider(self, registry):
        from specialized_providers import create_specialized_plugin
        plugin = create_specialized_plugin("whisper")
        assert plugin is not None

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response({"text": "This is a transcript"})
            result = await plugin._execute("speech_recognition", {"audio_url": "https://example.com/audio.mp3"}, {})
            assert "transcript" in result

    @pytest.mark.asyncio
    async def test_elevenlabs_provider(self, registry):
        from specialized_providers import create_specialized_plugin
        plugin = create_specialized_plugin("elevenlabs")
        assert plugin is not None

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response({})
            mock_post.return_value.text = "audio_base64_data"
            result = await plugin._execute("speech_synthesis", {"text": "Hello world"}, {})
            assert "provider" in result

    @pytest.mark.asyncio
    async def test_google_vision_ocr(self, registry):
        from specialized_providers import create_specialized_plugin
        plugin = create_specialized_plugin("google-vision")
        assert plugin is not None

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response({
                "responses": [{"fullTextAnnotation": {"text": "Extracted text"}}],
            })
            result = await plugin._execute("ocr", {"image_url": "https://example.com/image.png"}, {})
            assert "text" in result


class TestProviderIntegration:
    @pytest.mark.asyncio
    async def test_router_routes_to_correct_provider(self):
        from intelligent_router import IntelligentRouter, RoutingPolicy
        from llm_providers import register_all_providers

        registry = PluginRegistry()
        register_all_providers(registry)

        policy = RoutingPolicy(prefer_local=True)
        router = IntelligentRouter(registry, policy)

        decision = router.route("chat")
        assert decision.is_local == True
        assert decision.selected_plugin_id == "ollama"

        decision = router.route("chat", prefer_local=False)
        assert decision.selected_plugin_id is not None

    @pytest.mark.asyncio
    async def test_circuit_breaker_prevents_failed_provider(self):
        from intelligent_router import IntelligentRouter
        from llm_providers import register_all_providers

        registry = PluginRegistry()
        register_all_providers(registry)
        router = IntelligentRouter(registry)

        health = router.get_health("ollama")
        for _ in range(3):
            health.record_failure()

        decision = router.route("chat")
        assert decision.selected_plugin_id != "ollama"

    def test_all_24_providers_registered(self):
        from llm_providers import register_all_providers
        from specialized_providers import register_all_specialized

        registry = PluginRegistry()
        register_all_providers(registry)
        register_all_specialized(registry)

        stats = registry.stats()
        assert stats["total_plugins"] == 24

    def test_all_capabilities_covered(self):
        from llm_providers import register_all_providers
        from specialized_providers import register_all_specialized

        registry = PluginRegistry()
        register_all_providers(registry)
        register_all_specialized(registry)

        for cap in [Capability.CHAT, Capability.COMPLETION, Capability.CODE_GENERATION,
                    Capability.IMAGE_GENERATION, Capability.SEARCH, Capability.EMBEDDING,
                    Capability.SPEECH_SYNTHESIS, Capability.SPEECH_RECOGNITION,
                    Capability.OCR, Capability.TRANSLATION, Capability.VECTOR_STORAGE]:
            providers = registry.list_by_capability(cap)
            assert len(providers) > 0, f"No providers for: {cap.value}"
