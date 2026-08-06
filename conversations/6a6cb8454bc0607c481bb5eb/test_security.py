"""
Security Module Tests — API keys, rate limiting, input validation, graceful shutdown
"""

import pytest
import json
import os
import time
import asyncio
import hashlib
from unittest.mock import patch, MagicMock
from gateway_security import (
    APIKeyManager, APIKey, RedisState, DistributedRateLimiter,
    GracefulShutdownManager, SecurityHeaders, InputValidator,
)
from pathlib import Path

# =========================================================================
# API Key Manager Tests
# =========================================================================

class TestAPIKeyManager:
    def setup_method(self):
        self.manager = APIKeyManager()
        self.manager.keys.clear()
        self.manager._save_keys = MagicMock()  # Don't write to disk during tests
    
    def test_create_key(self):
        result = self.manager.create_key("test-key", ["chat", "completion"])
        assert "key_id" in result
        assert "api_key" in result
        assert result["api_key"].startswith("evk_")
        assert result["name"] == "test-key"
        assert "chat" in result["scopes"]
    
    def test_validate_key(self):
        result = self.manager.create_key("valid-key", ["chat"])
        validated = self.manager.validate_key(result["api_key"])
        assert validated is not None
        assert validated.name == "valid-key"
        assert validated.request_count == 1
    
    def test_validate_invalid_key(self):
        assert self.manager.validate_key("evk_invalid") is None
    
    def test_validate_nonexistent_key(self):
        assert self.manager.validate_key("evk_00000000000000000000000000000dead") is None
    
    def test_validate_revoked_key(self):
        result = self.manager.create_key("revoke-test", ["chat"])
        self.manager.revoke_key(result["key_id"])
        assert self.manager.validate_key(result["api_key"]) is None
    
    def test_revoke_nonexistent_key(self):
        assert self.manager.revoke_key("nonexistent") == False
    
    def test_check_scope_allowed(self):
        result = self.manager.create_key("scope-test", ["chat", "sentiment"])
        key = self.manager.validate_key(result["api_key"])
        assert self.manager.check_scope(key, "chat") == True
        assert self.manager.check_scope(key, "sentiment") == True
    
    def test_check_scope_denied(self):
        result = self.manager.create_key("scope-deny", ["chat"])
        key = self.manager.validate_key(result["api_key"])
        assert self.manager.check_scope(key, "embedding") == False
    
    def test_check_scope_wildcard(self):
        result = self.manager.create_key("wildcard", ["*"])
        key = self.manager.validate_key(result["api_key"])
        assert self.manager.check_scope(key, "anything") == True
        assert self.manager.check_scope(key, "chat") == True
    
    def test_list_keys_no_raw_keys(self):
        self.manager.create_key("list-test", ["chat"])
        keys = self.manager.list_keys()
        assert len(keys) == 1
        assert "api_key" not in keys[0]  # Raw key should NOT be in list
        assert "key_hash" not in keys[0]  # Hash should NOT be in list
        assert "name" in keys[0]
    
    def test_key_hash_is_sha256(self):
        result = self.manager.create_key("hash-test", ["chat"])
        expected_hash = hashlib.sha256(result["api_key"].encode()).hexdigest()
        key = self.manager.keys[result["key_id"]]
        assert key.key_hash == expected_hash
    
    def test_request_count_increments(self):
        result = self.manager.create_key("counter-test", ["chat"])
        self.manager.validate_key(result["api_key"])
        self.manager.validate_key(result["api_key"])
        self.manager.validate_key(result["api_key"])
        assert self.manager.keys[result["key_id"]].request_count == 3

# =========================================================================
# Redis State Tests (with fallback)
# =========================================================================

class TestRedisState:
    def setup_method(self):
        # Use fallback mode (no Redis in test env)
        with patch('redis.from_url', side_effect=Exception("No Redis")):
            self.state = RedisState("redis://nonexistent:6379/2")
    
    def test_fallback_set_get(self):
        self.state.set("key1", "value1")
        assert self.state.get("key1") == "value1"
    
    def test_fallback_delete(self):
        self.state.set("key2", "value2")
        assert self.state.delete("key2") == True
        assert self.state.get("key2") is None
    
    def test_fallback_incr(self):
        assert self.state.incr("counter") == 1
        assert self.state.incr("counter") == 2
        assert self.state.incr("counter") == 3
    
    def test_fallback_hset_hget(self):
        self.state.hset("hash1", "field1", "value1")
        assert self.state.hget("hash1", "field1") == "value1"
    
    def test_fallback_hgetall(self):
        self.state.hset("hash2", "a", "1")
        self.state.hset("hash2", "b", "2")
        result = self.state.hgetall("hash2")
        assert result["a"] == "1"
        assert result["b"] == "2"

# =========================================================================
# Distributed Rate Limiter Tests
# =========================================================================

class TestDistributedRateLimiter:
    def setup_method(self):
        with patch('redis.from_url', side_effect=Exception("No Redis")):
            self.state = RedisState("redis://nonexistent:6379/2")
        self.limiter = DistributedRateLimiter(self.state)
    
    def test_under_limit(self):
        for _ in range(5):
            assert self.limiter.check("client-1", limit=5) == True
    
    def test_over_limit(self):
        for _ in range(5):
            self.limiter.check("client-2", limit=5)
        assert self.limiter.check("client-2", limit=5) == False
    
    def test_different_clients_independent(self):
        for _ in range(5):
            self.limiter.check("client-a", limit=5)
        assert self.limiter.check("client-b", limit=5) == True
    
    def test_api_key_rate_limit(self):
        for _ in range(3):
            assert self.limiter.check_api_key("key-1", limit=3) == True
        assert self.limiter.check_api_key("key-1", limit=3) == False

# =========================================================================
# Graceful Shutdown Tests
# =========================================================================

class TestGracefulShutdown:
    def setup_method(self):
        self.sm = GracefulShutdownManager()
    
    def test_start_request(self):
        assert self.sm.start_request("plugin-a", "req-1") == True
        assert self.sm.active_count("plugin-a") == 1
    
    def test_end_request(self):
        self.sm.start_request("plugin-a", "req-1")
        self.sm.end_request("plugin-a", "req-1")
        assert self.sm.active_count("plugin-a") == 0
    
    def test_signal_shutdown_blocks_new(self):
        self.sm.signal_shutdown("plugin-b")
        assert self.sm.start_request("plugin-b", "req-1") == False
    
    def test_is_idle_no_requests(self):
        assert self.sm.is_idle("plugin-c") == True
    
    def test_is_idle_with_requests(self):
        self.sm.start_request("plugin-d", "req-1")
        assert self.sm.is_idle("plugin-d") == False
    
    @pytest.mark.asyncio
    async def test_wait_for_idle(self):
        self.sm.start_request("plugin-e", "req-1")
        # End request after short delay
        asyncio.get_event_loop().call_later(0.1, lambda: self.sm.end_request("plugin-e", "req-1"))
        await self.sm.wait_for_idle("plugin-e", timeout=5.0)
        assert self.sm.is_idle("plugin-e") == True

# =========================================================================
# Security Headers Tests
# =========================================================================

class TestSecurityHeaders:
    def test_headers_present(self):
        headers = SecurityHeaders.get_headers()
        assert "X-Content-Type-Options" in headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
        assert headers["X-XSS-Protection"] == "1; mode=block"
        assert "Referrer-Policy" in headers
        assert "Permissions-Policy" in headers
    
    def test_headers_count(self):
        headers = SecurityHeaders.get_headers()
        assert len(headers) >= 5

# =========================================================================
# Input Validator Tests
# =========================================================================

class TestInputValidator:
    def test_valid_input(self):
        data = {"text": "Hello world"}
        result = InputValidator.validate_input(data)
        assert result == data
    
    def test_invalid_type(self):
        with pytest.raises(ValueError, match="dictionary"):
            InputValidator.validate_input("not a dict")
    
    def test_input_too_large(self):
        large_input = {"text": "x" * (InputValidator.MAX_INPUT_SIZE + 1)}
        with pytest.raises(ValueError, match="too large"):
            InputValidator.validate_input(large_input)
    
    def test_message_too_long(self):
        data = {"messages": [{"role": "user", "content": "x" * (InputValidator.MAX_MESSAGE_LENGTH + 1)}]}
        with pytest.raises(ValueError, match="too long"):
            InputValidator.validate_input(data)
    
    def test_valid_messages(self):
        data = {"messages": [{"role": "user", "content": "Hello"}]}
        result = InputValidator.validate_input(data)
        assert result == data
    
    def test_invalid_message_type(self):
        with pytest.raises(ValueError, match="list"):
            InputValidator.validate_input({"messages": "not a list"})
    
    def test_valid_code(self):
        data = {"code": "function add(a, b) { return a + b; }"}
        result = InputValidator.validate_input(data)
        assert result == data
    
    def test_code_too_large(self):
        data = {"code": "x" * (InputValidator.MAX_INPUT_SIZE + 1)}
        with pytest.raises(ValueError, match="too large"):
            InputValidator.validate_input(data)
