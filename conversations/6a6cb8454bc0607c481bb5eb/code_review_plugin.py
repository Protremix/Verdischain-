"""
Code Review Plugin for EvolvixOS AI Gateway
Provides: code review capability using GPT-4o for architecture and security analysis
"""

import os
import httpx
from typing import Dict, Any

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_2", os.getenv("OPENAI_API_KEY", ""))
OPENAI_BASE_URL = "https://api.openai.com/v1"

PLUGIN_METADATA = {
    "name": "code-reviewer",
    "version": "1.0.0",
    "description": "AI-powered code review — analyzes code for bugs, security issues, and best practices",
    "author": "EvolvixOS",
    "provider": "openai",
    "capabilities": ["code_review"],
    "model": "gpt-4o",
    "max_tokens": 8192,
    "cost_per_1k": 0.005,
    "avg_latency_ms": 3000,
    "reliability_score": 0.97,
    "tags": ["development", "security", "analysis"],
}

SYSTEM_PROMPT = """You are an expert code reviewer. Analyze the provided code and respond with a JSON object:
{
  "score": 1-10,
  "issues": [{"severity": "critical|high|medium|low|info", "line": int, "description": "string", "suggestion": "string"}],
  "summary": "string",
  "best_practices": ["string"],
  "security_notes": ["string"]
}"""

async def handle_request(input_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
    code = input_data.get("code", "")
    language = input_data.get("language", "unknown")
    
    if not code:
        return {"error": "No code provided", "tokens_used": 0}
    
    if not OPENAI_API_KEY:
        return {"error": "OpenAI API key not configured", "tokens_used": 0, "score": 0, "issues": [], "summary": "API unavailable"}
    
    user_prompt = f"Language: {language}\n\nCode:\n```\n{code}\n```\n\nReview this code for bugs, security issues, and best practices."
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "max_tokens": options.get("max_tokens", 8192),
            },
        )
        data = resp.json()
        if resp.status_code != 200:
            return {"error": data.get("error", {}).get("message", "Unknown error"), "tokens_used": 0}
        
        import json
        content = data["choices"][0]["message"]["content"]
        try:
            result = json.loads(content)
            result["tokens_used"] = data["usage"]["total_tokens"]
            result["model"] = data["model"]
            return result
        except:
            return {
                "score": 0,
                "issues": [],
                "summary": content,
                "best_practices": [],
                "security_notes": [],
                "tokens_used": data["usage"]["total_tokens"],
                "model": data["model"],
            }

def cleanup():
    pass
