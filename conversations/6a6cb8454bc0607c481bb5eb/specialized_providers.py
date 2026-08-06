"""
EvolvixOS Specialized Provider Plugins
Coding, Image, Speech, OCR, Search, Translation, Embedding, Vector Memory providers
"""

import os
import time
import httpx
import asyncio
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import asdict

from plugin_architecture import (
    ProviderPlugin, PluginMetadata, PluginType, PluginStatus,
    Capability, PluginRegistry
)
import structlog

logger = structlog.get_logger()


# =========================================================================
# CODING PROVIDERS
# =========================================================================

class CodexProvider(ProviderPlugin):
    """OpenAI Codex — code generation"""
    
    def __init__(self, config=None):
        meta = PluginMetadata(
            id="codex",
            name="OpenAI Codex",
            version="1.0.0",
            plugin_type=PluginType.CODING_PROVIDER,
            description="OpenAI code generation model",
            capabilities=[Capability.CODE_GENERATION, Capability.COMPLETION, Capability.CHAT],
            requires_api_key=True,
            api_key_env="OPENAI_API_KEY",
            is_local=False,
            priority=85,
            cost_per_1k_tokens=0.03,
            max_context_window=16384,
            max_output_tokens=4096,
            tags=["coding", "openai"],
        )
        super().__init__(meta, config)
    
    async def initialize(self):
        self._api_key = os.getenv(self.metadata.api_key_env)
        self._base_url = "https://api.openai.com/v1"
        self.status = PluginStatus.ACTIVE
    
    async def _execute(self, capability, input_data, options):
        prompt = input_data.get("prompt", input_data.get("code", ""))
        messages = input_data.get("messages", [{"role": "user", "content": prompt}])
        
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"model": "gpt-4o", "messages": messages, "temperature": 0.2},
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "model": "codex",
                "tokens_used": data["usage"]["total_tokens"],
                "provider": self.id,
            }


class DeepSeekCoderProvider(ProviderPlugin):
    """DeepSeek Coder — code generation"""
    
    def __init__(self, config=None):
        meta = PluginMetadata(
            id="deepseek-coder",
            name="DeepSeek Coder",
            version="1.0.0",
            plugin_type=PluginType.CODING_PROVIDER,
            description="DeepSeek specialized coding model",
            capabilities=[Capability.CODE_GENERATION, Capability.COMPLETION],
            requires_api_key=True,
            api_key_env="DEEPSEEK_API_KEY",
            is_local=False,
            priority=75,
            cost_per_1k_tokens=0.002,
            max_context_window=16384,
            max_output_tokens=4096,
            tags=["coding", "deepseek"],
        )
        super().__init__(meta, config)
    
    async def initialize(self):
        self._api_key = os.getenv(self.metadata.api_key_env)
        self._base_url = "https://api.deepseek.com/v1"
        self.status = PluginStatus.ACTIVE
    
    async def _execute(self, capability, input_data, options):
        prompt = input_data.get("prompt", input_data.get("code", ""))
        
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"model": "deepseek-coder", "messages": [{"role": "user", "content": prompt}]},
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "model": "deepseek-coder",
                "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                "provider": self.id,
            }


class CodestralProvider(ProviderPlugin):
    """Mistral Codestral — code generation"""
    
    def __init__(self, config=None):
        meta = PluginMetadata(
            id="codestral",
            name="Codestral",
            version="1.0.0",
            plugin_type=PluginType.CODING_PROVIDER,
            description="Mistral AI's coding model",
            capabilities=[Capability.CODE_GENERATION, Capability.COMPLETION],
            requires_api_key=True,
            api_key_env="MISTRAL_API_KEY",
            is_local=False,
            priority=70,
            cost_per_1k_tokens=0.01,
            max_context_window=32768,
            max_output_tokens=4096,
            tags=["coding", "mistral"],
        )
        super().__init__(meta, config)
    
    async def initialize(self):
        self._api_key = os.getenv(self.metadata.api_key_env)
        self._base_url = "https://api.mistral.ai/v1"
        self.status = PluginStatus.ACTIVE
    
    async def _execute(self, capability, input_data, options):
        prompt = input_data.get("prompt", "")
        
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"model": "codestral-latest", "messages": [{"role": "user", "content": prompt}]},
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "model": "codestral",
                "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                "provider": self.id,
            }


# =========================================================================
# IMAGE PROVIDERS
# =========================================================================

class OpenAIImageProvider(ProviderPlugin):
    """OpenAI DALL-E image generation"""
    
    def __init__(self, config=None):
        meta = PluginMetadata(
            id="openai-image",
            name="OpenAI Images",
            version="1.0.0",
            plugin_type=PluginType.IMAGE_PROVIDER,
            description="DALL-E 3 image generation",
            capabilities=[Capability.IMAGE_GENERATION],
            requires_api_key=True,
            api_key_env="OPENAI_API_KEY",
            is_local=False,
            priority=80,
            cost_per_1k_tokens=0.04,
            tags=["image", "openai"],
        )
        super().__init__(meta, config)
    
    async def initialize(self):
        self._api_key = os.getenv(self.metadata.api_key_env)
        self._base_url = "https://api.openai.com/v1"
        self.status = PluginStatus.ACTIVE
    
    async def _execute(self, capability, input_data, options):
        prompt = input_data.get("prompt", "")
        size = options.get("size", "1024x1024")
        
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self._base_url}/images/generations",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"prompt": prompt, "n": 1, "size": size, "model": "dall-e-3"},
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "image_url": data["data"][0]["url"],
                "revised_prompt": data["data"][0].get("revised_prompt", prompt),
                "provider": self.id,
            }


class StabilityAIProvider(ProviderPlugin):
    """Stability AI image generation"""
    
    def __init__(self, config=None):
        meta = PluginMetadata(
            id="stability-ai",
            name="Stability AI",
            version="1.0.0",
            plugin_type=PluginType.IMAGE_PROVIDER,
            description="Stable Diffusion image generation",
            capabilities=[Capability.IMAGE_GENERATION],
            requires_api_key=True,
            api_key_env="STABILITY_API_KEY",
            is_local=False,
            priority=75,
            cost_per_1k_tokens=0.02,
            tags=["image", "stability"],
        )
        super().__init__(meta, config)
    
    async def initialize(self):
        self._api_key = os.getenv(self.metadata.api_key_env)
        self._base_url = "https://api.stability.ai/v1"
        self.status = PluginStatus.ACTIVE
    
    async def _execute(self, capability, input_data, options):
        prompt = input_data.get("prompt", "")
        
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self._base_url}/generation/stable-image/core/1.0/text-to-image",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"prompt": prompt, "output_format": "png"},
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "image_url": data.get("image", ""),
                "provider": self.id,
            }


# =========================================================================
# SPEECH PROVIDERS
# =========================================================================

class ElevenLabsProvider(ProviderPlugin):
    """ElevenLabs text-to-speech"""
    
    def __init__(self, config=None):
        meta = PluginMetadata(
            id="elevenlabs",
            name="ElevenLabs",
            version="1.0.0",
            plugin_type=PluginType.SPEECH_PROVIDER,
            description="High-quality text-to-speech",
            capabilities=[Capability.SPEECH_SYNTHESIS],
            requires_api_key=True,
            api_key_env="ELEVENLABS_API_KEY",
            is_local=False,
            priority=85,
            cost_per_1k_tokens=0.05,
            tags=["speech", "tts"],
        )
        super().__init__(meta, config)
    
    async def initialize(self):
        self._api_key = os.getenv(self.metadata.api_key_env)
        self._base_url = "https://api.elevenlabs.io/v1"
        self.status = PluginStatus.ACTIVE
    
    async def _execute(self, capability, input_data, options):
        text = input_data.get("text", "")
        voice_id = options.get("voice_id", "21m00Tcm4TlvDq8ikWAM")
        
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self._base_url}/text-to-speech/{voice_id}",
                headers={"xi-api-key": self._api_key},
                json={"text": text, "model_id": "eleven_multilingual_v2"},
            )
            resp.raise_for_status()
            return {
                "audio_base64": resp.text[:100] + "...",  # truncated
                "provider": self.id,
            }


class OpenAISpeechProvider(ProviderPlugin):
    """OpenAI TTS"""
    
    def __init__(self, config=None):
        meta = PluginMetadata(
            id="openai-speech",
            name="OpenAI Speech",
            version="1.0.0",
            plugin_type=PluginType.SPEECH_PROVIDER,
            description="OpenAI text-to-speech",
            capabilities=[Capability.SPEECH_SYNTHESIS],
            requires_api_key=True,
            api_key_env="OPENAI_API_KEY",
            is_local=False,
            priority=75,
            cost_per_1k_tokens=0.015,
            tags=["speech", "openai"],
        )
        super().__init__(meta, config)
    
    async def initialize(self):
        self._api_key = os.getenv(self.metadata.api_key_env)
        self._base_url = "https://api.openai.com/v1"
        self.status = PluginStatus.ACTIVE
    
    async def _execute(self, capability, input_data, options):
        text = input_data.get("text", "")
        voice = options.get("voice", "alloy")
        
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self._base_url}/audio/speech",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"model": "tts-1", "voice": voice, "input": text},
            )
            resp.raise_for_status()
            return {"audio_size": len(resp.content), "provider": self.id}


# =========================================================================
# SPEECH RECOGNITION PROVIDERS
# =========================================================================

class WhisperProvider(ProviderPlugin):
    """OpenAI Whisper speech recognition"""
    
    def __init__(self, config=None):
        meta = PluginMetadata(
            id="whisper",
            name="Whisper",
            version="1.0.0",
            plugin_type=PluginType.SPEECH_RECOGNITION,
            description="OpenAI Whisper speech-to-text",
            capabilities=[Capability.SPEECH_RECOGNITION],
            requires_api_key=True,
            api_key_env="OPENAI_API_KEY",
            is_local=False,
            priority=85,
            cost_per_1k_tokens=0.006,
            tags=["stt", "whisper"],
        )
        super().__init__(meta, config)
    
    async def initialize(self):
        self._api_key = os.getenv(self.metadata.api_key_env)
        self._base_url = "https://api.openai.com/v1"
        self.status = PluginStatus.ACTIVE
    
    async def _execute(self, capability, input_data, options):
        # input_data should contain audio file path or URL
        audio_url = input_data.get("audio_url")
        audio_file = input_data.get("audio_file")
        
        async with httpx.AsyncClient(timeout=120) as client:
            if audio_file:
                with open(audio_file, "rb") as f:
                    resp = await client.post(
                        f"{self._base_url}/audio/transcriptions",
                        headers={"Authorization": f"Bearer {self._api_key}"},
                        files={"file": (os.path.basename(audio_file), f, "audio/mpeg")},
                        data={"model": "whisper-1"},
                    )
            else:
                resp = await client.post(
                    f"{self._base_url}/audio/transcriptions",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={"model": "whisper-1", "url": audio_url},
                )
            resp.raise_for_status()
            data = resp.json()
            return {"transcript": data.get("text", ""), "provider": self.id}


# =========================================================================
# SEARCH PROVIDERS
# =========================================================================

class TavilyProvider(ProviderPlugin):
    """Tavily AI search"""
    
    def __init__(self, config=None):
        meta = PluginMetadata(
            id="tavily",
            name="Tavily Search",
            version="1.0.0",
            plugin_type=PluginType.SEARCH_PROVIDER,
            description="AI-optimized web search",
            capabilities=[Capability.SEARCH],
            requires_api_key=True,
            api_key_env="TAVILY_API_KEY",
            is_local=False,
            priority=80,
            cost_per_1k_tokens=0.01,
            tags=["search"],
        )
        super().__init__(meta, config)
    
    async def initialize(self):
        self._api_key = os.getenv(self.metadata.api_key_env)
        self._base_url = "https://api.tavily.com"
        self.status = PluginStatus.ACTIVE
    
    async def _execute(self, capability, input_data, options):
        query = input_data.get("query", input_data.get("q", ""))
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self._base_url}/search",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"query": query, "max_results": options.get("max_results", 5)},
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "results": data.get("results", []),
                "query": query,
                "provider": self.id,
            }


class BraveSearchProvider(ProviderPlugin):
    """Brave Search API"""
    
    def __init__(self, config=None):
        meta = PluginMetadata(
            id="brave-search",
            name="Brave Search",
            version="1.0.0",
            plugin_type=PluginType.SEARCH_PROVIDER,
            description="Privacy-focused web search",
            capabilities=[Capability.SEARCH],
            requires_api_key=True,
            api_key_env="BRAVE_SEARCH_API_KEY",
            is_local=False,
            priority=70,
            cost_per_1k_tokens=0.005,
            tags=["search"],
        )
        super().__init__(meta, config)
    
    async def initialize(self):
        self._api_key = os.getenv(self.metadata.api_key_env)
        self._base_url = "https://api.search.brave.com"
        self.status = PluginStatus.ACTIVE
    
    async def _execute(self, capability, input_data, options):
        query = input_data.get("query", input_data.get("q", ""))
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self._base_url}/res/v1/web/search",
                headers={"X-Subscription-Token": self._api_key},
                params={"q": query, "count": options.get("max_results", 5)},
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "results": data.get("results", data.get("web", {}).get("results", [])),
                "query": query,
                "provider": self.id,
            }


# =========================================================================
# TRANSLATION PROVIDERS
# =========================================================================

class DeepLProvider(ProviderPlugin):
    """DeepL translation"""
    
    def __init__(self, config=None):
        meta = PluginMetadata(
            id="deepl",
            name="DeepL",
            version="1.0.0",
            plugin_type=PluginType.TRANSLATION_PROVIDER,
            description="High-quality machine translation",
            capabilities=[Capability.TRANSLATION],
            requires_api_key=True,
            api_key_env="DEEPL_API_KEY",
            is_local=False,
            priority=85,
            cost_per_1k_tokens=0.02,
            tags=["translation"],
        )
        super().__init__(meta, config)
    
    async def initialize(self):
        self._api_key = os.getenv(self.metadata.api_key_env)
        self._base_url = "https://api-free.deepl.com/v2"
        self.status = PluginStatus.ACTIVE
    
    async def _execute(self, capability, input_data, options):
        text = input_data.get("text", "")
        target_lang = options.get("target_lang", "EN")
        source_lang = options.get("source_lang")
        
        params = {"text": text, "target_lang": target_lang}
        if source_lang:
            params["source_lang"] = source_lang
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self._base_url}/translate",
                headers={"Authorization": f"DeepL-Auth-Key {self._api_key}"},
                data=params,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "translation": data["translations"][0]["text"],
                "detected_source": data["translations"][0].get("detected_source_language", ""),
                "provider": self.id,
            }


# =========================================================================
# EMBEDDING PROVIDERS
# =========================================================================

class OpenAIEmbeddingProvider(ProviderPlugin):
    """OpenAI embeddings"""
    
    def __init__(self, config=None):
        meta = PluginMetadata(
            id="openai-embedding",
            name="OpenAI Embeddings",
            version="1.0.0",
            plugin_type=PluginType.EMBEDDING_PROVIDER,
            description="text-embedding-3-large",
            capabilities=[Capability.EMBEDDING],
            requires_api_key=True,
            api_key_env="OPENAI_API_KEY",
            is_local=False,
            priority=80,
            cost_per_1k_tokens=0.00013,
            tags=["embedding", "openai"],
        )
        super().__init__(meta, config)
    
    async def initialize(self):
        self._api_key = os.getenv(self.metadata.api_key_env)
        self._base_url = "https://api.openai.com/v1"
        self.status = PluginStatus.ACTIVE
    
    async def _execute(self, capability, input_data, options):
        texts = input_data.get("texts", [input_data.get("text", "")])
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self._base_url}/embeddings",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"model": "text-embedding-3-large", "input": texts},
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "embeddings": [e["embedding"] for e in data["data"]],
                "model": "text-embedding-3-large",
                "tokens_used": data["usage"]["total_tokens"],
                "provider": self.id,
            }


# =========================================================================
# OCR PROVIDERS
# =========================================================================

class GoogleVisionProvider(ProviderPlugin):
    """Google Cloud Vision OCR"""
    
    def __init__(self, config=None):
        meta = PluginMetadata(
            id="google-vision",
            name="Google Vision",
            version="1.0.0",
            plugin_type=PluginType.OCR_PROVIDER,
            description="Google Cloud Vision OCR",
            capabilities=[Capability.OCR, Capability.VISION],
            requires_api_key=True,
            api_key_env="GOOGLE_API_KEY",
            is_local=False,
            priority=80,
            cost_per_1k_tokens=0.0015,
            tags=["ocr", "vision"],
        )
        super().__init__(meta, config)
    
    async def initialize(self):
        self._api_key = os.getenv(self.metadata.api_key_env)
        self._base_url = "https://vision.googleapis.com/v1"
        self.status = PluginStatus.ACTIVE
    
    async def _execute(self, capability, input_data, options):
        image_url = input_data.get("image_url", "")
        
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self._base_url}/images:annotate?key={self._api_key}",
                json={
                    "requests": [{
                        "image": {"source": {"imageUri": image_url}},
                        "features": [{"type": "TEXT_DETECTION"}],
                    }]
                },
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["responses"][0].get("fullTextAnnotation", {}).get("text", "")
            return {"text": text, "provider": self.id}


# =========================================================================
# VECTOR MEMORY PROVIDERS
# =========================================================================

class QdrantProvider(ProviderPlugin):
    """Qdrant vector database"""
    
    def __init__(self, config=None):
        meta = PluginMetadata(
            id="qdrant",
            name="Qdrant",
            version="1.0.0",
            plugin_type=PluginType.VECTOR_MEMORY,
            description="Vector similarity search",
            capabilities=[Capability.VECTOR_STORAGE],
            requires_api_key=False,
            is_local=True,
            priority=80,
            tags=["vector", "memory"],
        )
        super().__init__(meta, config)
    
    async def initialize(self):
        self._base_url = self.config.get("base_url", "http://localhost:6333")
        self.status = PluginStatus.ACTIVE
    
    async def _execute(self, capability, input_data, options):
        operation = options.get("operation", "search")
        
        if operation == "upsert":
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.put(
                    f"{self._base_url}/collections/{options.get('collection', 'default')}/points",
                    json={
                        "points": [{
                            "id": p.get("id"),
                            "vector": p["vector"],
                            "payload": p.get("payload", {}),
                        } for p in input_data.get("points", [])],
                    },
                )
                resp.raise_for_status()
                return {"status": "upserted", "count": len(input_data.get("points", [])), "provider": self.id}
        
        elif operation == "search":
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self._base_url}/collections/{options.get('collection', 'default')}/points/search",
                    json={
                        "vector": input_data.get("vector"),
                        "limit": options.get("limit", 10),
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return {"results": data.get("result", []), "provider": self.id}
        
        return {"error": f"Unknown operation: {operation}", "provider": self.id}


# =========================================================================
# Provider Registration
# =========================================================================

SPECIALIZED_PROVIDERS = [
    CodexProvider, DeepSeekCoderProvider, CodestralProvider,
    OpenAIImageProvider, StabilityAIProvider,
    ElevenLabsProvider, OpenAISpeechProvider,
    WhisperProvider,
    TavilyProvider, BraveSearchProvider,
    DeepLProvider,
    OpenAIEmbeddingProvider,
    GoogleVisionProvider,
    QdrantProvider,
]


def register_all_specialized(registry: PluginRegistry):
    """Register all specialized provider metadata."""
    for provider_cls in SPECIALIZED_PROVIDERS:
        instance = provider_cls()
        registry.register_metadata(instance.metadata)
    return len(SPECIALIZED_PROVIDERS)


def create_specialized_plugin(provider_id: str, config=None) -> Optional[ProviderPlugin]:
    """Create a specialized provider instance by ID."""
    for provider_cls in SPECIALIZED_PROVIDERS:
        instance = provider_cls(config)
        if instance.id == provider_id:
            return instance
    return None
