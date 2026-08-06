"""
EvolvixOS LLM Providers Plugin Module
Implements LLM provider plugins for major cloud AI services and local LLMs.
Each provider extends ProviderPlugin from plugin_architecture.py.
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator

import httpx
import structlog

from plugin_architecture import (
    ProviderPlugin,
    PluginMetadata,
    PluginType,
    Capability,
    PluginRegistry,
    PluginStatus,
)

logger = structlog.get_logger()


# =========================================================================
# OpenAI-Compatible Base Plugin Class
# =========================================================================

class OpenAICompatiblePlugin(ProviderPlugin):
    """Base provider plugin for OpenAI-compatible REST APIs."""

    def _get_api_key(self) -> Optional[str]:
        if self._api_key:
            return self._api_key
        if "api_key" in self.config:
            return self.config["api_key"]
        if self.metadata.api_key_env:
            return os.getenv(self.metadata.api_key_env)
        return None

    def _get_base_url(self) -> str:
        if self._base_url:
            return self._base_url
        return self.config.get("base_url") or self.metadata.default_config.get("base_url", "")

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        api_key = self._get_api_key()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    async def initialize(self) -> None:
        await super().initialize()
        if not self._api_key and "api_key" in self.config:
            self._api_key = self.config["api_key"]
            self.status = PluginStatus.ACTIVE
        if not self._base_url:
            self._base_url = self._get_base_url()

    async def _execute(
        self, capability: str, input_data: Dict[str, Any], options: Dict[str, Any]
    ) -> Dict[str, Any]:
        base_url = self._get_base_url()
        model = options.get("model") or self.config.get("model") or self.metadata.default_config.get("model", "")
        temperature = options.get("temperature", 0.7)
        max_tokens = options.get("max_tokens", self.metadata.max_output_tokens)
        headers = self._get_headers()

        cap = capability.lower()
        if cap in (Capability.CHAT.value, "chat"):
            messages = input_data.get("messages")
            if not messages:
                text = input_data.get("prompt") or input_data.get("text", "")
                messages = [{"role": "user", "content": text}]

            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            url = f"{base_url.rstrip('/')}/chat/completions"

            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    choices = data.get("choices", [])
                    content = choices[0].get("message", {}).get("content", "") if choices else ""
                    tokens = data.get("usage", {}).get("total_tokens", 0)
                    return {
                        "content": content,
                        "model": data.get("model", model),
                        "tokens_used": tokens,
                        "provider": self.id,
                    }
            except Exception as e:
                logger.error(f"Error executing chat for {self.id}: {e}")
                raise

        elif cap in (Capability.COMPLETION.value, "completion"):
            prompt = input_data.get("prompt") or input_data.get("text")
            if not prompt and "messages" in input_data:
                prompt = "\n".join(m.get("content", "") for m in input_data["messages"])

            payload = {
                "model": model,
                "prompt": prompt or "",
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            url = f"{base_url.rstrip('/')}/completions"

            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    choices = data.get("choices", [])
                    content = choices[0].get("text", "") if choices else ""
                    tokens = data.get("usage", {}).get("total_tokens", 0)
                    return {
                        "content": content,
                        "model": data.get("model", model),
                        "tokens_used": tokens,
                        "provider": self.id,
                    }
            except Exception as e:
                logger.error(f"Error executing completion for {self.id}: {e}")
                raise
        else:
            raise ValueError(f"Capability '{capability}' is not supported by {self.id}")

    async def stream(
        self, capability: str, input_data: Dict[str, Any], options: Dict[str, Any] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        options = options or {}
        base_url = self._get_base_url()
        model = options.get("model") or self.config.get("model") or self.metadata.default_config.get("model", "")
        temperature = options.get("temperature", 0.7)
        max_tokens = options.get("max_tokens", self.metadata.max_output_tokens)
        headers = self._get_headers()

        messages = input_data.get("messages")
        if not messages:
            text = input_data.get("prompt") or input_data.get("text", "")
            messages = [{"role": "user", "content": text}]

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        url = f"{base_url.rstrip('/')}/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            line_data = line[6:].strip()
                            if line_data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(line_data)
                                choices = chunk.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {}).get("content", "")
                                    if delta:
                                        yield {
                                            "delta": delta,
                                            "content": delta,
                                            "provider": self.id,
                                            "model": model,
                                        }
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Error in stream for {self.id}: {e}")
            raise


# =========================================================================
# 1. OpenAI Provider Plugin
# =========================================================================

class OpenAIPlugin(OpenAICompatiblePlugin):
    """OpenAI Provider Plugin (GPT-4o, GPT-4o-mini)."""

    def __init__(self, config: Dict[str, Any] = None):
        metadata = PluginMetadata(
            id="openai",
            name="OpenAI",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            description="OpenAI LLM provider supporting GPT-4o and GPT-4o-mini",
            author="EvolvixOS",
            capabilities=[Capability.CHAT, Capability.COMPLETION, Capability.STREAMING],
            requires_api_key=True,
            api_key_env="OPENAI_API_KEY",
            is_local=False,
            cost_per_1k_tokens=0.0025,
            max_context_window=128000,
            max_output_tokens=4096,
            tags=["openai", "gpt-4o", "gpt-4o-mini", "llm"],
            default_config={
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o",
            },
        )
        merged_config = metadata.default_config.copy()
        if config:
            merged_config.update(config)
        super().__init__(metadata, merged_config)


# =========================================================================
# 2. Anthropic Claude Provider Plugin
# =========================================================================

class AnthropicPlugin(ProviderPlugin):
    """Anthropic Claude Provider Plugin (claude-3-opus, claude-3-sonnet)."""

    def __init__(self, config: Dict[str, Any] = None):
        metadata = PluginMetadata(
            id="anthropic",
            name="Anthropic Claude",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            description="Anthropic Claude provider supporting claude-3-opus and claude-3-sonnet",
            author="EvolvixOS",
            capabilities=[Capability.CHAT, Capability.COMPLETION, Capability.STREAMING],
            requires_api_key=True,
            api_key_env="ANTHROPIC_API_KEY",
            is_local=False,
            cost_per_1k_tokens=0.003,
            max_context_window=200000,
            max_output_tokens=4096,
            tags=["anthropic", "claude", "claude-3-opus", "claude-3-sonnet", "llm"],
            default_config={
                "base_url": "https://api.anthropic.com/v1",
                "model": "claude-3-sonnet-20240229",
            },
        )
        merged_config = metadata.default_config.copy()
        if config:
            merged_config.update(config)
        super().__init__(metadata, merged_config)

    def _get_api_key(self) -> Optional[str]:
        if self._api_key:
            return self._api_key
        if "api_key" in self.config:
            return self.config["api_key"]
        return os.getenv("ANTHROPIC_API_KEY")

    def _get_base_url(self) -> str:
        if self._base_url:
            return self._base_url
        return self.config.get("base_url") or "https://api.anthropic.com/v1"

    async def initialize(self) -> None:
        await super().initialize()
        if not self._api_key and "api_key" in self.config:
            self._api_key = self.config["api_key"]
            self.status = PluginStatus.ACTIVE
        if not self._base_url:
            self._base_url = self._get_base_url()

    async def _execute(
        self, capability: str, input_data: Dict[str, Any], options: Dict[str, Any]
    ) -> Dict[str, Any]:
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError("Anthropic API key is not configured")

        base_url = self._get_base_url()
        model = options.get("model") or self.config.get("model") or "claude-3-sonnet-20240229"
        temperature = options.get("temperature", 0.7)
        max_tokens = options.get("max_tokens", self.metadata.max_output_tokens)

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        system_prompt = input_data.get("system", "")
        chat_messages = []
        raw_messages = input_data.get("messages")
        if raw_messages:
            for m in raw_messages:
                role = m.get("role", "user")
                if role == "system":
                    system_prompt = m.get("content", "")
                else:
                    chat_messages.append({"role": role, "content": m.get("content", "")})
        else:
            text = input_data.get("prompt") or input_data.get("text", "")
            chat_messages = [{"role": "user", "content": text}]

        body = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": chat_messages,
            "temperature": temperature,
        }
        if system_prompt:
            body["system"] = system_prompt

        url = f"{base_url.rstrip('/')}/messages"
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, headers=headers, json=body)
                resp.raise_for_status()
                data = resp.json()
                content = ""
                if data.get("content") and len(data["content"]) > 0:
                    content = data["content"][0].get("text", "")
                usage = data.get("usage", {})
                tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                return {
                    "content": content,
                    "model": data.get("model", model),
                    "tokens_used": tokens,
                    "provider": self.id,
                }
        except Exception as e:
            logger.error(f"Error executing {capability} for Anthropic: {e}")
            raise

    async def stream(
        self, capability: str, input_data: Dict[str, Any], options: Dict[str, Any] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        options = options or {}
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError("Anthropic API key is not configured")

        base_url = self._get_base_url()
        model = options.get("model") or self.config.get("model") or "claude-3-sonnet-20240229"
        temperature = options.get("temperature", 0.7)
        max_tokens = options.get("max_tokens", self.metadata.max_output_tokens)

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        system_prompt = input_data.get("system", "")
        chat_messages = []
        raw_messages = input_data.get("messages")
        if raw_messages:
            for m in raw_messages:
                role = m.get("role", "user")
                if role == "system":
                    system_prompt = m.get("content", "")
                else:
                    chat_messages.append({"role": role, "content": m.get("content", "")})
        else:
            text = input_data.get("prompt") or input_data.get("text", "")
            chat_messages = [{"role": "user", "content": text}]

        body = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": chat_messages,
            "temperature": temperature,
            "stream": True,
        }
        if system_prompt:
            body["system"] = system_prompt

        url = f"{base_url.rstrip('/')}/messages"
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, headers=headers, json=body) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                event_data = json.loads(line[6:].strip())
                                if event_data.get("type") == "content_block_delta":
                                    delta = event_data.get("delta", {}).get("text", "")
                                    if delta:
                                        yield {
                                            "delta": delta,
                                            "content": delta,
                                            "provider": self.id,
                                            "model": model,
                                        }
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Error streaming from Anthropic: {e}")
            raise


# =========================================================================
# 3. Google Gemini Provider Plugin
# =========================================================================

class GoogleGeminiPlugin(ProviderPlugin):
    """Google Gemini Provider Plugin (gemini-1.5-pro)."""

    def __init__(self, config: Dict[str, Any] = None):
        metadata = PluginMetadata(
            id="google",
            name="Google Gemini",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            description="Google Gemini provider supporting gemini-1.5-pro",
            author="EvolvixOS",
            capabilities=[Capability.CHAT, Capability.COMPLETION, Capability.STREAMING],
            requires_api_key=True,
            api_key_env="GOOGLE_API_KEY",
            is_local=False,
            cost_per_1k_tokens=0.00125,
            max_context_window=1000000,
            max_output_tokens=8192,
            tags=["google", "gemini", "gemini-1.5-pro", "llm"],
            default_config={
                "base_url": "https://generativelanguage.googleapis.com/v1",
                "model": "gemini-1.5-pro",
            },
        )
        merged_config = metadata.default_config.copy()
        if config:
            merged_config.update(config)
        super().__init__(metadata, merged_config)

    def _get_api_key(self) -> Optional[str]:
        if self._api_key:
            return self._api_key
        if "api_key" in self.config:
            return self.config["api_key"]
        return os.getenv("GOOGLE_API_KEY")

    def _get_base_url(self) -> str:
        if self._base_url:
            return self._base_url
        return self.config.get("base_url") or "https://generativelanguage.googleapis.com/v1"

    async def initialize(self) -> None:
        await super().initialize()
        if not self._api_key and "api_key" in self.config:
            self._api_key = self.config["api_key"]
            self.status = PluginStatus.ACTIVE
        if not self._base_url:
            self._base_url = self._get_base_url()

    async def _execute(
        self, capability: str, input_data: Dict[str, Any], options: Dict[str, Any]
    ) -> Dict[str, Any]:
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError("Google API key is not configured")

        base_url = self._get_base_url()
        model = options.get("model") or self.config.get("model") or "gemini-1.5-pro"
        temperature = options.get("temperature", 0.7)
        max_tokens = options.get("max_tokens", self.metadata.max_output_tokens)

        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        }

        contents = []
        raw_messages = input_data.get("messages")
        if raw_messages:
            for m in raw_messages:
                role = "model" if m.get("role") == "assistant" else "user"
                contents.append({"role": role, "parts": [{"text": m.get("content", "")}]})
        else:
            text = input_data.get("prompt") or input_data.get("text", "")
            contents.append({"role": "user", "parts": [{"text": text}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        url = f"{base_url.rstrip('/')}/models/{model}:generateContent"
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = ""
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts:
                        content = parts[0].get("text", "")
                tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
                return {
                    "content": content,
                    "model": model,
                    "tokens_used": tokens,
                    "provider": self.id,
                }
        except Exception as e:
            logger.error(f"Error executing {capability} for Gemini: {e}")
            raise

    async def stream(
        self, capability: str, input_data: Dict[str, Any], options: Dict[str, Any] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        options = options or {}
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError("Google API key is not configured")

        base_url = self._get_base_url()
        model = options.get("model") or self.config.get("model") or "gemini-1.5-pro"
        temperature = options.get("temperature", 0.7)
        max_tokens = options.get("max_tokens", self.metadata.max_output_tokens)

        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        }

        contents = []
        raw_messages = input_data.get("messages")
        if raw_messages:
            for m in raw_messages:
                role = "model" if m.get("role") == "assistant" else "user"
                contents.append({"role": role, "parts": [{"text": m.get("content", "")}]})
        else:
            text = input_data.get("prompt") or input_data.get("text", "")
            contents.append({"role": "user", "parts": [{"text": text}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        url = f"{base_url.rstrip('/')}/models/{model}:streamGenerateContent?alt=sse"
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                chunk = json.loads(line[6:].strip())
                                candidates = chunk.get("candidates", [])
                                if candidates and "content" in candidates[0]:
                                    parts = candidates[0]["content"].get("parts", [])
                                    if parts:
                                        delta = parts[0].get("text", "")
                                        if delta:
                                            yield {
                                                "delta": delta,
                                                "content": delta,
                                                "provider": self.id,
                                                "model": model,
                                            }
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Error streaming from Gemini: {e}")
            raise


# =========================================================================
# 4. xAI Grok Provider Plugin
# =========================================================================

class XAIGrokPlugin(OpenAICompatiblePlugin):
    """xAI Grok Provider Plugin (grok-beta)."""

    def __init__(self, config: Dict[str, Any] = None):
        metadata = PluginMetadata(
            id="xai",
            name="xAI Grok",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            description="xAI Grok provider supporting grok-beta",
            author="EvolvixOS",
            capabilities=[Capability.CHAT, Capability.COMPLETION, Capability.STREAMING],
            requires_api_key=True,
            api_key_env="XAI_API_KEY",
            is_local=False,
            cost_per_1k_tokens=0.005,
            max_context_window=131072,
            max_output_tokens=4096,
            tags=["xai", "grok", "grok-beta", "llm"],
            default_config={
                "base_url": "https://api.x.ai/v1",
                "model": "grok-beta",
            },
        )
        merged_config = metadata.default_config.copy()
        if config:
            merged_config.update(config)
        super().__init__(metadata, merged_config)


# =========================================================================
# 5. DeepSeek Provider Plugin
# =========================================================================

class DeepSeekPlugin(OpenAICompatiblePlugin):
    """DeepSeek Provider Plugin (deepseek-chat)."""

    def __init__(self, config: Dict[str, Any] = None):
        metadata = PluginMetadata(
            id="deepseek",
            name="DeepSeek",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            description="DeepSeek provider supporting deepseek-chat",
            author="EvolvixOS",
            capabilities=[Capability.CHAT, Capability.COMPLETION, Capability.STREAMING],
            requires_api_key=True,
            api_key_env="DEEPSEEK_API_KEY",
            is_local=False,
            cost_per_1k_tokens=0.00014,
            max_context_window=64000,
            max_output_tokens=4096,
            tags=["deepseek", "deepseek-chat", "llm"],
            default_config={
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
            },
        )
        merged_config = metadata.default_config.copy()
        if config:
            merged_config.update(config)
        super().__init__(metadata, merged_config)


# =========================================================================
# 6. Cohere Provider Plugin
# =========================================================================

class CoherePlugin(ProviderPlugin):
    """Cohere Provider Plugin (command-r-plus)."""

    def __init__(self, config: Dict[str, Any] = None):
        metadata = PluginMetadata(
            id="cohere",
            name="Cohere",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            description="Cohere provider supporting command-r-plus",
            author="EvolvixOS",
            capabilities=[Capability.CHAT, Capability.COMPLETION, Capability.STREAMING],
            requires_api_key=True,
            api_key_env="COHERE_API_KEY",
            is_local=False,
            cost_per_1k_tokens=0.003,
            max_context_window=128000,
            max_output_tokens=4096,
            tags=["cohere", "command-r-plus", "llm"],
            default_config={
                "base_url": "https://api.cohere.ai/v1",
                "model": "command-r-plus",
            },
        )
        merged_config = metadata.default_config.copy()
        if config:
            merged_config.update(config)
        super().__init__(metadata, merged_config)

    def _get_api_key(self) -> Optional[str]:
        if self._api_key:
            return self._api_key
        if "api_key" in self.config:
            return self.config["api_key"]
        return os.getenv("COHERE_API_KEY")

    def _get_base_url(self) -> str:
        if self._base_url:
            return self._base_url
        return self.config.get("base_url") or "https://api.cohere.ai/v1"

    async def initialize(self) -> None:
        await super().initialize()
        if not self._api_key and "api_key" in self.config:
            self._api_key = self.config["api_key"]
            self.status = PluginStatus.ACTIVE
        if not self._base_url:
            self._base_url = self._get_base_url()

    async def _execute(
        self, capability: str, input_data: Dict[str, Any], options: Dict[str, Any]
    ) -> Dict[str, Any]:
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError("Cohere API key is not configured")

        base_url = self._get_base_url()
        model = options.get("model") or self.config.get("model") or "command-r-plus"
        temperature = options.get("temperature", 0.7)
        max_tokens = options.get("max_tokens", self.metadata.max_output_tokens)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        raw_messages = input_data.get("messages")
        if raw_messages and len(raw_messages) > 0:
            message = raw_messages[-1].get("content", "")
            chat_history = []
            for m in raw_messages[:-1]:
                role = (
                    "USER"
                    if m.get("role") == "user"
                    else ("CHATBOT" if m.get("role") == "assistant" else "SYSTEM")
                )
                chat_history.append({"role": role, "message": m.get("content", "")})
        else:
            message = input_data.get("prompt") or input_data.get("text", "")
            chat_history = []

        payload = {
            "model": model,
            "message": message,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if chat_history:
            payload["chat_history"] = chat_history

        url = f"{base_url.rstrip('/')}/chat"
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = data.get("text", "")
                tokens_meta = data.get("meta", {}).get("tokens", {})
                tokens = tokens_meta.get("input_tokens", 0) + tokens_meta.get("output_tokens", 0)
                return {
                    "content": content,
                    "model": model,
                    "tokens_used": tokens,
                    "provider": self.id,
                }
        except Exception as e:
            logger.error(f"Error executing {capability} for Cohere: {e}")
            raise

    async def stream(
        self, capability: str, input_data: Dict[str, Any], options: Dict[str, Any] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        options = options or {}
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError("Cohere API key is not configured")

        base_url = self._get_base_url()
        model = options.get("model") or self.config.get("model") or "command-r-plus"
        temperature = options.get("temperature", 0.7)
        max_tokens = options.get("max_tokens", self.metadata.max_output_tokens)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        raw_messages = input_data.get("messages")
        if raw_messages and len(raw_messages) > 0:
            message = raw_messages[-1].get("content", "")
            chat_history = []
            for m in raw_messages[:-1]:
                role = (
                    "USER"
                    if m.get("role") == "user"
                    else ("CHATBOT" if m.get("role") == "assistant" else "SYSTEM")
                )
                chat_history.append({"role": role, "message": m.get("content", "")})
        else:
            message = input_data.get("prompt") or input_data.get("text", "")
            chat_history = []

        payload = {
            "model": model,
            "message": message,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if chat_history:
            payload["chat_history"] = chat_history

        url = f"{base_url.rstrip('/')}/chat"
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        line_str = line[6:].strip() if line.startswith("data: ") else line.strip()
                        if not line_str:
                            continue
                        try:
                            event_data = json.loads(line_str)
                            if event_data.get("event_type") == "text-generation":
                                delta = event_data.get("text", "")
                                if delta:
                                    yield {
                                        "delta": delta,
                                        "content": delta,
                                        "provider": self.id,
                                        "model": model,
                                    }
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Error streaming from Cohere: {e}")
            raise


# =========================================================================
# 7. AI21 Provider Plugin
# =========================================================================

class AI21Plugin(ProviderPlugin):
    """AI21 Provider Plugin (j2-ultra)."""

    def __init__(self, config: Dict[str, Any] = None):
        metadata = PluginMetadata(
            id="ai21",
            name="AI21 Studio",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            description="AI21 Studio provider supporting j2-ultra",
            author="EvolvixOS",
            capabilities=[Capability.CHAT, Capability.COMPLETION],
            requires_api_key=True,
            api_key_env="AI21_API_KEY",
            is_local=False,
            cost_per_1k_tokens=0.015,
            max_context_window=8192,
            max_output_tokens=2048,
            tags=["ai21", "j2-ultra", "llm"],
            default_config={
                "base_url": "https://api.ai21.com/v2",
                "model": "j2-ultra",
            },
        )
        merged_config = metadata.default_config.copy()
        if config:
            merged_config.update(config)
        super().__init__(metadata, merged_config)

    def _get_api_key(self) -> Optional[str]:
        if self._api_key:
            return self._api_key
        if "api_key" in self.config:
            return self.config["api_key"]
        return os.getenv("AI21_API_KEY")

    def _get_base_url(self) -> str:
        if self._base_url:
            return self._base_url
        return self.config.get("base_url") or "https://api.ai21.com/v2"

    async def initialize(self) -> None:
        await super().initialize()
        if not self._api_key and "api_key" in self.config:
            self._api_key = self.config["api_key"]
            self.status = PluginStatus.ACTIVE
        if not self._base_url:
            self._base_url = self._get_base_url()

    async def _execute(
        self, capability: str, input_data: Dict[str, Any], options: Dict[str, Any]
    ) -> Dict[str, Any]:
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError("AI21 API key is not configured")

        base_url = self._get_base_url()
        model = options.get("model") or self.config.get("model") or "j2-ultra"
        temperature = options.get("temperature", 0.7)
        max_tokens = options.get("max_tokens", self.metadata.max_output_tokens)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        raw_messages = input_data.get("messages")
        if not raw_messages:
            text = input_data.get("prompt") or input_data.get("text", "")
            raw_messages = [{"role": "user", "content": text}]

        # Try standard chat completions format first, or j2-ultra route
        payload = {
            "model": model,
            "messages": raw_messages,
            "temperature": temperature,
            "maxTokens": max_tokens,
        }
        url = f"{base_url.rstrip('/')}/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 404:
                    # Fall back to j2-ultra model endpoint if chat completions not found
                    fallback_url = f"{base_url.rstrip('/')}/{model}/chat"
                    fallback_payload = {
                        "messages": [
                            {"role": m.get("role", "user"), "text": m.get("content", "")}
                            for m in raw_messages
                        ],
                        "temperature": temperature,
                        "maxTokens": max_tokens,
                    }
                    resp = await client.post(fallback_url, headers=headers, json=fallback_payload)

                resp.raise_for_status()
                data = resp.json()

                content = ""
                tokens = 0

                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0].get("message", {}).get("content", "")
                    tokens = data.get("usage", {}).get("total_tokens", 0)
                elif "outputs" in data and len(data["outputs"]) > 0:
                    content = data["outputs"][0].get("text", "")
                    tokens = data.get("usage", {}).get("total_tokens", 0)

                return {
                    "content": content,
                    "model": model,
                    "tokens_used": tokens,
                    "provider": self.id,
                }
        except Exception as e:
            logger.error(f"Error executing {capability} for AI21: {e}")
            raise


# =========================================================================
# 8. Mistral Provider Plugin
# =========================================================================

class MistralPlugin(OpenAICompatiblePlugin):
    """Mistral AI Provider Plugin (mistral-large)."""

    def __init__(self, config: Dict[str, Any] = None):
        metadata = PluginMetadata(
            id="mistral",
            name="Mistral AI",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            description="Mistral AI provider supporting mistral-large",
            author="EvolvixOS",
            capabilities=[Capability.CHAT, Capability.COMPLETION, Capability.STREAMING],
            requires_api_key=True,
            api_key_env="MISTRAL_API_KEY",
            is_local=False,
            cost_per_1k_tokens=0.002,
            max_context_window=128000,
            max_output_tokens=4096,
            tags=["mistral", "mistral-large", "llm"],
            default_config={
                "base_url": "https://api.mistral.ai/v1",
                "model": "mistral-large",
            },
        )
        merged_config = metadata.default_config.copy()
        if config:
            merged_config.update(config)
        super().__init__(metadata, merged_config)


# =========================================================================
# 9. Ollama Provider Plugin (Local)
# =========================================================================

class OllamaPlugin(ProviderPlugin):
    """Ollama Local Provider Plugin."""

    def __init__(self, config: Dict[str, Any] = None):
        metadata = PluginMetadata(
            id="ollama",
            name="Ollama Local",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            description="Local Ollama provider running locally at http://localhost:11434/api",
            author="EvolvixOS",
            capabilities=[Capability.CHAT, Capability.COMPLETION],
            requires_api_key=False,
            api_key_env=None,
            is_local=True,
            cost_per_1k_tokens=0.0,
            max_context_window=8192,
            max_output_tokens=2048,
            tags=["ollama", "local", "llama3", "llm"],
            default_config={
                "base_url": "http://localhost:11434/api",
                "model": "llama3",
            },
        )
        merged_config = metadata.default_config.copy()
        if config:
            merged_config.update(config)
        super().__init__(metadata, merged_config)

    def _get_base_url(self) -> str:
        if self._base_url:
            return self._base_url
        return self.config.get("base_url") or "http://localhost:11434/api"

    async def initialize(self) -> None:
        await super().initialize()
        self.status = PluginStatus.ACTIVE
        if not self._base_url:
            self._base_url = self._get_base_url()

    async def _execute(
        self, capability: str, input_data: Dict[str, Any], options: Dict[str, Any]
    ) -> Dict[str, Any]:
        base_url = self._get_base_url()
        model = options.get("model") or self.config.get("model") or "llama3"
        temperature = options.get("temperature", 0.7)

        cap = capability.lower()
        if cap in (Capability.CHAT.value, "chat"):
            messages = input_data.get("messages")
            if not messages:
                text = input_data.get("prompt") or input_data.get("text", "")
                messages = [{"role": "user", "content": text}]

            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                },
            }
            url = f"{base_url.rstrip('/')}/chat"

            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    content = data.get("message", {}).get("content", "")
                    tokens = data.get("eval_count", 0) + data.get("prompt_eval_count", 0)
                    return {
                        "content": content,
                        "model": data.get("model", model),
                        "tokens_used": tokens,
                        "provider": self.id,
                    }
            except Exception as e:
                logger.error(f"Error executing chat for Ollama: {e}")
                raise

        elif cap in (Capability.COMPLETION.value, "completion"):
            prompt = input_data.get("prompt") or input_data.get("text", "")
            if not prompt and "messages" in input_data:
                prompt = "\n".join(m.get("content", "") for m in input_data["messages"])

            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                },
            }
            url = f"{base_url.rstrip('/')}/generate"

            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    content = data.get("response", "")
                    tokens = data.get("eval_count", 0) + data.get("prompt_eval_count", 0)
                    return {
                        "content": content,
                        "model": data.get("model", model),
                        "tokens_used": tokens,
                        "provider": self.id,
                    }
            except Exception as e:
                logger.error(f"Error executing completion for Ollama: {e}")
                raise
        else:
            raise ValueError(f"Capability '{capability}' is not supported by {self.id}")


# =========================================================================
# 10. vLLM Provider Plugin (Local)
# =========================================================================

class vLLMPlugin(OpenAICompatiblePlugin):
    """vLLM Local Provider Plugin."""

    def __init__(self, config: Dict[str, Any] = None):
        metadata = PluginMetadata(
            id="vllm",
            name="vLLM Local",
            version="1.0.0",
            plugin_type=PluginType.LLM_PROVIDER,
            description="Local vLLM server providing OpenAI-compatible endpoint at http://localhost:8000/v1",
            author="EvolvixOS",
            capabilities=[Capability.CHAT, Capability.COMPLETION, Capability.STREAMING],
            requires_api_key=False,
            api_key_env=None,
            is_local=True,
            cost_per_1k_tokens=0.0,
            max_context_window=16384,
            max_output_tokens=4096,
            tags=["vllm", "local", "openai-compatible", "llm"],
            default_config={
                "base_url": "http://localhost:8000/v1",
                "model": "local-model",
            },
        )
        merged_config = metadata.default_config.copy()
        if config:
            merged_config.update(config)
        super().__init__(metadata, merged_config)

    async def initialize(self) -> None:
        await super().initialize()
        self.status = PluginStatus.ACTIVE


# =========================================================================
# Registration & Factory Helpers
# =========================================================================

ALL_PROVIDERS = [
    OpenAIPlugin,
    AnthropicPlugin,
    GoogleGeminiPlugin,
    XAIGrokPlugin,
    DeepSeekPlugin,
    CoherePlugin,
    AI21Plugin,
    MistralPlugin,
    OllamaPlugin,
    vLLMPlugin,
]

_PROVIDER_MAP = {
    "openai": OpenAIPlugin,
    "anthropic": AnthropicPlugin,
    "claude": AnthropicPlugin,
    "google": GoogleGeminiPlugin,
    "gemini": GoogleGeminiPlugin,
    "xai": XAIGrokPlugin,
    "grok": XAIGrokPlugin,
    "deepseek": DeepSeekPlugin,
    "cohere": CoherePlugin,
    "ai21": AI21Plugin,
    "mistral": MistralPlugin,
    "ollama": OllamaPlugin,
    "vllm": vLLMPlugin,
}


def register_all_providers(registry: PluginRegistry) -> None:
    """Register all provider metadata into a PluginRegistry instance."""
    for provider_cls in ALL_PROVIDERS:
        instance = provider_cls()
        registry.register_metadata(instance.metadata)
    logger.info("Registered metadata for all 10 LLM providers in registry")


def create_plugin(provider_id: str, config: Optional[Dict[str, Any]] = None) -> ProviderPlugin:
    """
    Factory function that returns a plugin instance for a given provider ID.

    Args:
        provider_id: The ID or alias of the provider (e.g. 'openai', 'anthropic', 'ollama').
        config: Optional custom configuration dictionary.

    Returns:
        An instance of ProviderPlugin corresponding to the provider_id.
    """
    key = provider_id.lower().strip()
    if key not in _PROVIDER_MAP:
        raise ValueError(
            f"Unknown provider ID: '{provider_id}'. Available providers: {list(_PROVIDER_MAP.keys())}"
        )
    cls = _PROVIDER_MAP[key]
    return cls(config=config)
