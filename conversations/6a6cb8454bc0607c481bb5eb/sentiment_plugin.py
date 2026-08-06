"""
Sentiment Analysis Plugin for EvolvixOS AI Gateway
Provides: sentiment analysis using OpenAI for text classification
"""

import os
import httpx
from typing import Dict, Any

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_2", os.getenv("OPENAI_API_KEY", ""))
OPENAI_BASE_URL = "https://api.openai.com/v1"

PLUGIN_METADATA = {
    "name": "sentiment-analyzer",
    "version": "1.0.0",
    "description": "Sentiment analysis plugin — classifies text as positive, negative, or neutral",
    "author": "EvolvixOS",
    "provider": "openai",
    "capabilities": ["sentiment"],
    "model": "gpt-4o-mini",
    "max_tokens": 100,
    "cost_per_1k": 0.00015,
    "avg_latency_ms": 500,
    "reliability_score": 0.95,
    "tags": ["analysis", "fast", "lightweight"],
}

SYSTEM_PROMPT = """You are a sentiment analysis engine. Analyze the given text and respond with ONLY a JSON object:
{"sentiment": "positive|negative|neutral", "confidence": 0.0-1.0, "key_phrases": ["phrase1", "phrase2"]}"""

async def handle_request(input_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
    text = input_data.get("text", "")
    if not text:
        return {"error": "No text provided", "tokens_used": 0}
    
    if not OPENAI_API_KEY:
        # Fallback: simple keyword-based sentiment
        return _fallback_sentiment(text)
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                "temperature": 0.3,
                "max_tokens": 100,
            },
        )
        data = resp.json()
        if resp.status_code != 200:
            return _fallback_sentiment(text)
        
        import json
        content = data["choices"][0]["message"]["content"]
        try:
            result = json.loads(content)
            result["tokens_used"] = data["usage"]["total_tokens"]
            result["model"] = data["model"]
            return result
        except:
            return _fallback_sentiment(text)

def _fallback_sentiment(text: str) -> Dict:
    """Simple keyword-based fallback when API is unavailable"""
    positive_words = ["good", "great", "excellent", "happy", "love", "wonderful", "amazing", "fantastic", "positive", "best"]
    negative_words = ["bad", "terrible", "awful", "hate", "horrible", "worst", "negative", "sad", "angry", "disappointed"]
    
    text_lower = text.lower()
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)
    
    if pos_count > neg_count:
        sentiment = "positive"
        confidence = min(0.5 + (pos_count - neg_count) * 0.1, 0.9)
    elif neg_count > pos_count:
        sentiment = "negative"
        confidence = min(0.5 + (neg_count - pos_count) * 0.1, 0.9)
    else:
        sentiment = "neutral"
        confidence = 0.5
    
    return {"sentiment": sentiment, "confidence": confidence, "key_phrases": [], "tokens_used": 0, "model": "fallback"}

def cleanup():
    pass
