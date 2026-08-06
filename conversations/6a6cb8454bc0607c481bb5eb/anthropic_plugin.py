"""
EvolvixOS AI Gateway Plugin — Anthropic Claude
Provides chat and completion capabilities via Anthropic's Claude API
"""

import os
import time
import httpx
import structlog
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

logger = structlog.get_logger()

# Plugin metadata
PLUGIN_NAME = "anthropic-claude"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Anthropic Claude AI plugin for EvolvixOS Gateway"
PLUGIN_AUTHOR = "EvolvixOS"
PLUGIN_PROVIDER = "anthropic"
PLUGIN_CAPABILITIES = ["chat", "completion"]
PLUGIN_MODEL = "claude-sonnet-4-20250514"
PLUGIN_MAX_TOKENS = 8192
PLUGIN_COST_PER_1K = 0.003
PLUGIN_AVG_LATENCY = 1200
PLUGIN_RELIABILITY = 0.99
PLUGIN_TAGS = ["default", "anthropic", "claude"]


class AnthropicPlugin:
    """Anthropic Claude AI Plugin"""
    
    name = PLUGIN_NAME
    version = PLUGIN_VERSION
    description = PLUGIN_DESCRIPTION
    author = PLUGIN_AUTHOR
    provider = PLUGIN_PROVIDER
    capabilities = PLUGIN_CAPABILITIES
    model = PLUGIN_MODEL
    max_tokens = PLUGIN_MAX_TOKENS
    cost_per_1k = PLUGIN_COST_PER_1K
    avg_latency_ms = PLUGIN_AVG_LATENCY
    reliability_score = PLUGIN_RELIABILITY
    tags = PLUGIN_TAGS
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model or PLUGIN_MODEL
        self.base_url = "https://api.anthropic.com/v1"
        self._request_count = 0
        self._error_count = 0
        self._total_latency = 0.0
        self._total_tokens = 0
        
        if not self.api_key:
            logger.warning("AnthropicPlugin initialized without API key")
    
    @property
    def metrics(self) -> Dict[str, Any]:
        return {
            "request_count": self._request_count,
            "error_count": self._error_count,
            "avg_latency_ms": self._total_latency / max(self._request_count, 1),
            "total_tokens": self._total_tokens,
            "error_rate": self._error_count / max(self._request_count, 1),
        }
    
    def health_check(self) -> bool:
        """Check if the plugin is healthy"""
        return bool(self.api_key)
    
    async def chat(self, messages: List[Dict[str, str]], max_tokens: int = 4096,
                   temperature: float = 0.7, system: str = None) -> Dict[str, Any]:
        """Chat completion via Claude"""
        if not self.api_key:
            raise ValueError("Anthropic API key not configured")
        
        start = time.time()
        self._request_count += 1
        
        # Extract system message if present in messages
        system_prompt = system or ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = system_prompt or msg["content"]
            else:
                chat_messages.append({"role": msg["role"], "content": msg["content"]})
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        
        body = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": chat_messages,
        }
        if system_prompt:
            body["system"] = system_prompt
        
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(f"{self.base_url}/messages", headers=headers, json=body)
                resp.raise_for_status()
                data = resp.json()
                
                latency = (time.time() - start) * 1000
                self._total_latency += latency
                tokens_used = data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)
                self._total_tokens += tokens_used
                
                return {
                    "content": data["content"][0]["text"] if data.get("content") else "",
                    "model": data.get("model", self.model),
                    "role": "assistant",
                    "tokens_used": tokens_used,
                    "latency_ms": latency,
                    "raw": data,
                }
        except Exception as e:
            self._error_count += 1
            logger.error(f"Anthropic chat error: {e}")
            raise
    
    async def completion(self, prompt: str, max_tokens: int = 100,
                         temperature: float = 0.7) -> Dict[str, Any]:
        """Text completion via Claude"""
        return await self.chat(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
    
    async def execute(self, capability: str, input_data: Dict[str, Any],
                      options: Dict = None) -> Dict[str, Any]:
        """Execute a capability"""
        options = options or {}
        
        if capability == "chat":
            messages = input_data.get("messages", [])
            if not messages and "text" in input_data:
                messages = [{"role": "user", "content": input_data["text"]}]
            
            return await self.chat(
                messages=messages,
                max_tokens=options.get("max_tokens", 4096),
                temperature=options.get("temperature", 0.7),
                system=input_data.get("system"),
            )
        
        elif capability == "completion":
            return await self.completion(
                prompt=input_data.get("prompt", input_data.get("text", "")),
                max_tokens=options.get("max_tokens", 100),
                temperature=options.get("temperature", 0.7),
            )
        
        else:
            raise ValueError(f"Unsupported capability: {capability}")
