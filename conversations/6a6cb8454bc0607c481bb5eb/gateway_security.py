"""
EvolvixOS AI Gateway — Security & Scalability Enhancement
Adds: JWT authentication, API key management, Redis shared state, graceful plugin shutdowns
"""

import os
import json
import time
import uuid
import hashlib
import hmac
import redis
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from collections import defaultdict
import asyncio

# =========================================================================
# JWT Authentication
# =========================================================================

JWT_SECRET = os.getenv("AI_GATEWAY_JWT_SECRET", "evolvixos-ai-gateway-secret-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24
API_KEYS_FILE = os.getenv("API_KEYS_FILE", "/app/api_keys.json")

@dataclass
class APIKey:
    key_id: str
    key_hash: str  # SHA-256 hash of the API key
    name: str
    scopes: List[str]  # e.g., ["chat", "completion", "embedding", "sentiment", "code_review"]
    rate_limit_per_min: int
    created_at: str
    last_used: str = ""
    request_count: int = 0
    active: bool = True

class APIKeyManager:
    """Manages API keys for gateway authentication"""
    
    def __init__(self):
        self.keys: Dict[str, APIKey] = {}  # key_id -> APIKey
        self.key_prefix = "evk_"  # EvolvixOS key prefix
        self._load_keys()
    
    def _load_keys(self):
        """Load API keys from file"""
        path = API_KEYS_FILE
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            for key_data in data.get("keys", []):
                key = APIKey(**key_data)
                self.keys[key.key_id] = key
    
    def _save_keys(self):
        """Save API keys to file"""
        data = {
            "version": "1.0.0",
            "keys": []
        }
        for key in self.keys.values():
            data["keys"].append({
                "key_id": key.key_id,
                "key_hash": key.key_hash,
                "name": key.name,
                "scopes": key.scopes,
                "rate_limit_per_min": key.rate_limit_per_min,
                "created_at": key.created_at,
                "last_used": key.last_used,
                "request_count": key.request_count,
                "active": key.active,
            })
        with open(API_KEYS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_key(self, name: str, scopes: List[str], rate_limit: int = 60) -> Dict:
        """Create a new API key. Returns the full key (shown once)."""
        key_id = str(uuid.uuid4())[:8]
        raw_key = f"{self.key_prefix}{uuid.uuid4().hex}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            scopes=scopes,
            rate_limit_per_min=rate_limit,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self.keys[key_id] = api_key
        self._save_keys()
        
        return {
            "key_id": key_id,
            "api_key": raw_key,
            "name": name,
            "scopes": scopes,
            "rate_limit_per_min": rate_limit,
        }
    
    def validate_key(self, raw_key: str) -> Optional[APIKey]:
        """Validate an API key. Returns the key if valid, None if invalid."""
        if not raw_key.startswith(self.key_prefix):
            return None
        
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        for key in self.keys.values():
            if key.key_hash == key_hash and key.active:
                key.last_used = datetime.now(timezone.utc).isoformat()
                key.request_count += 1
                self._save_keys()
                return key
        return None
    
    def revoke_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        if key_id in self.keys:
            self.keys[key_id].active = False
            self._save_keys()
            return True
        return False
    
    def list_keys(self) -> List[Dict]:
        """List all API keys (without revealing the actual key)"""
        return [
            {
                "key_id": k.key_id,
                "name": k.name,
                "scopes": k.scopes,
                "rate_limit_per_min": k.rate_limit_per_min,
                "created_at": k.created_at,
                "last_used": k.last_used,
                "request_count": k.request_count,
                "active": k.active,
            }
            for k in self.keys.values()
        ]
    
    def check_scope(self, key: APIKey, capability: str) -> bool:
        """Check if a key has access to a capability"""
        if "*" in key.scopes:
            return True
        return capability in key.scopes

# =========================================================================
# Redis Shared State
# =========================================================================

class RedisState:
    """Redis-backed shared state for multi-worker plugin registry and rate limiting"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/2"):
        try:
            self.redis = redis.from_url(redis_url, decode_responses=True)
            self.redis.ping()
            self.available = True
        except Exception as e:
            print(f"Redis not available, using in-memory fallback: {e}")
            self.available = False
            self._fallback_store = {}
    
    def get(self, key: str) -> Optional[str]:
        if self.available:
            return self.redis.get(key)
        return self._fallback_store.get(key)
    
    def set(self, key: str, value: str, ttl: int = 0) -> bool:
        if self.available:
            if ttl > 0:
                self.redis.setex(key, ttl, value)
            else:
                self.redis.set(key, value)
            return True
        self._fallback_store[key] = value
        return True
    
    def delete(self, key: str) -> bool:
        if self.available:
            return self.redis.delete(key) > 0
        if key in self._fallback_store:
            del self._fallback_store[key]
            return True
        return False
    
    def incr(self, key: str) -> int:
        if self.available:
            return self.redis.incr(key)
        val = int(self._fallback_store.get(key, 0)) + 1
        self._fallback_store[key] = str(val)
        return val
    
    def expire(self, key: str, ttl: int) -> bool:
        if self.available:
            return self.redis.expire(key, ttl)
        return True  # no-op in fallback
    
    def hset(self, name: str, key: str, value: str) -> bool:
        if self.available:
            self.redis.hset(name, key, value)
            return True
        if name not in self._fallback_store:
            self._fallback_store[name] = {}
        self._fallback_store[name][key] = value
        return True
    
    def hget(self, name: str, key: str) -> Optional[str]:
        if self.available:
            return self.redis.hget(name, key)
        return self._fallback_store.get(name, {}).get(key)
    
    def hgetall(self, name: str) -> Dict:
        if self.available:
            return self.redis.hgetall(name)
        return self._fallback_store.get(name, {})
    
    def hdel(self, name: str, key: str) -> bool:
        if self.available:
            return self.redis.hdel(name, key) > 0
        if name in self._fallback_store and key in self._fallback_store[name]:
            del self._fallback_store[name][key]
            return True
        return False
    
    def keys(self, pattern: str = "*") -> List[str]:
        if self.available:
            return self.redis.keys(pattern)
        return list(self._fallback_store.keys())

# =========================================================================
# Distributed Rate Limiter (Redis-backed)
# =========================================================================

class DistributedRateLimiter:
    """Rate limiter using Redis for multi-worker support"""
    
    def __init__(self, redis_state: RedisState):
        self.redis = redis_state
    
    def check(self, client_id: str, limit: int = 60, window: int = 60) -> bool:
        """Check rate limit. Returns True if allowed."""
        key = f"rate_limit:{client_id}"
        count = self.redis.incr(key)
        if count == 1:
            self.redis.expire(key, window)
        return count <= limit
    
    def check_api_key(self, key_id: str, limit: int, window: int = 60) -> bool:
        """Rate limit per API key"""
        key = f"rate_limit_key:{key_id}"
        count = self.redis.incr(key)
        if count == 1:
            self.redis.expire(key, window)
        return count <= limit

# =========================================================================
# Graceful Plugin Shutdown Manager
# =========================================================================

class GracefulShutdownManager:
    """Tracks in-flight requests per plugin and ensures graceful shutdown"""
    
    def __init__(self):
        self.active_requests: Dict[str, Set[str]] = defaultdict(set)  # plugin -> set of request_ids
        self.shutdown_signals: Set[str] = set()  # plugins marked for shutdown
    
    def start_request(self, plugin: str, request_id: str) -> bool:
        """Track a new request. Returns False if plugin is shutting down."""
        if plugin in self.shutdown_signals:
            return False
        self.active_requests[plugin].add(request_id)
        return True
    
    def end_request(self, plugin: str, request_id: str):
        """Mark a request as complete"""
        self.active_requests[plugin].discard(request_id)
    
    def signal_shutdown(self, plugin: str):
        """Signal that a plugin should not accept new requests"""
        self.shutdown_signals.add(plugin)
    
    def is_idle(self, plugin: str) -> bool:
        """Check if all in-flight requests have completed"""
        return len(self.active_requests[plugin]) == 0
    
    async def wait_for_idle(self, plugin: str, timeout: float = 30.0):
        """Wait for all in-flight requests to complete"""
        start = time.time()
        while not self.is_idle(plugin):
            if time.time() - start > timeout:
                break
            await asyncio.sleep(0.1)
        self.shutdown_signals.discard(plugin)
    
    def active_count(self, plugin: str) -> int:
        return len(self.active_requests[plugin])

# =========================================================================
# Security Middleware
# =========================================================================

class SecurityHeaders:
    """Security headers for HTTP responses"""
    
    @staticmethod
    def get_headers() -> Dict[str, str]:
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }

class InputValidator:
    """Validates and sanitizes input to prevent injection attacks"""
    
    MAX_INPUT_SIZE = 100_000  # 100KB max input
    MAX_MESSAGE_LENGTH = 32_000  # 32K chars per message
    
    @classmethod
    def validate_input(cls, input_data: Dict) -> Dict:
        """Validate and sanitize input data"""
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary")
        
        # Check total size
        input_str = json.dumps(input_data)
        if len(input_str) > cls.MAX_INPUT_SIZE:
            raise ValueError(f"Input too large (max {cls.MAX_INPUT_SIZE} bytes)")
        
        # Validate messages if present
        messages = input_data.get("messages", [])
        if messages:
            if not isinstance(messages, list):
                raise ValueError("Messages must be a list")
            for msg in messages:
                if not isinstance(msg, dict):
                    raise ValueError("Each message must be a dictionary")
                content = msg.get("content", "")
                if len(str(content)) > cls.MAX_MESSAGE_LENGTH:
                    raise ValueError(f"Message content too long (max {cls.MAX_MESSAGE_LENGTH} chars)")
        
        # Validate text if present
        text = input_data.get("text", "")
        if text and len(str(text)) > cls.MAX_MESSAGE_LENGTH:
            raise ValueError(f"Text too long (max {cls.MAX_MESSAGE_LENGTH} chars)")
        
        # Validate code if present
        code = input_data.get("code", "")
        if code and len(str(code)) > cls.MAX_INPUT_SIZE:
            raise ValueError(f"Code too large (max {cls.MAX_INPUT_SIZE} bytes)")
        
        return input_data
