"""
OpenAI Plugin for EvolvixOS AI Gateway
Provides: chat, completion, embedding capabilities via OpenAI API
"""

import os
import httpx
import asyncio
from typing import Dict, Any

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_2", os.getenv("OPENAI_API_KEY", ""))
OPENAI_BASE_URL = "https://api.openai.com/v1"

PLUGIN_METADATA = {
    "name": "openai-gpt4o",
    "version": "1.0.0",
    "description": "OpenAI GPT-4o multi-capability plugin (chat, completion, embedding)",
    "author": "EvolvixOS",
    "provider": "openai",
    "capabilities": ["chat", "completion", "embedding"],
    "model": "gpt-4o",
    "max_tokens": 16384,
    "cost_per_1k": 0.005,
    "avg_latency_ms": 1500,
    "reliability_score": 0.99,
    "tags": ["default", "premium", "multimodal"],
}

async def handle_request(input_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
    capability = options.get("capability", "chat")
    if not OPENAI_API_KEY:
        return {"error": "OpenAI API key not configured", "tokens_used": 0}
    async with httpx.AsyncClient(timeout=30.0) as client:
        if capability == "chat":
            return await _handle_chat(input_data, options, client)
        elif capability == "completion":
            return await _handle_completion(input_data, options, client)
        elif capability == "embedding":
            return await _handle_embedding(input_data, options, client)
        else:
            return {"error": f"Unknown capability: {capability}", "tokens_used": 0}

async def _handle_chat(input_data: Dict, options: Dict, client: httpx.AsyncClient) -> Dict:
    messages = input_data.get("messages", [])
    model = options.get("model", "gpt-4o")
    temperature = options.get("temperature", 0.7)
    max_tokens = options.get("max_tokens", 4096)
    resp = await client.post(
        f"{OPENAI_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens},
    )
    data = resp.json()
    if resp.status_code != 200:
        return {"error": data.get("error", {}).get("message", "Unknown error"), "tokens_used": 0}
    return {
        "content": data["choices"][0]["message"]["content"],
        "role": data["choices"][0]["message"]["role"],
        "finish_reason": data["choices"][0]["finish_reason"],
        "tokens_used": data["usage"]["total_tokens"],
        "model": data["model"],
    }

async def _handle_completion(input_data: Dict, options: Dict, client: httpx.AsyncClient) -> Dict:
    prompt = input_data.get("prompt", "")
    model = options.get("model", "gpt-4o")
    resp = await client.post(
        f"{OPENAI_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": options.get("temperature", 0.7), "max_tokens": options.get("max_tokens", 2048)},
    )
    data = resp.json()
    if resp.status_code != 200:
        return {"error": data.get("error", {}).get("message", "Unknown error"), "tokens_used": 0}
    return {"content": data["choices"][0]["message"]["content"], "finish_reason": data["choices"][0]["finish_reason"], "tokens_used": data["usage"]["total_tokens"], "model": data["model"]}

async def _handle_embedding(input_data: Dict, options: Dict, client: httpx.AsyncClient) -> Dict:
    text = input_data.get("text", "")
    model = options.get("model", "text-embedding-3-small")
    resp = await client.post(
        f"{OPENAI_BASE_URL}/embeddings",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={"input": text, "model": model},
    )
    data = resp.json()
    if resp.status_code != 200:
        return {"error": data.get("error", {}).get("message", "Unknown error"), "tokens_used": 0}
    return {"embedding": data["data"][0]["embedding"], "tokens_used": data["usage"]["total_tokens"], "model": data["model"]}

def cleanup():
    pass
