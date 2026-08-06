"""
Tests for Queue API v3.2: Redis token persistence, rate limiting, secure default.
"""

import pytest
import asyncio
import os
import sys
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

with patch('asyncpg.create_pool', new_callable=AsyncMock):
    pass

# Mock Redis to use in-memory fallback
with patch('redis.from_url') as mock_redis:
    mock_redis.return_value = None  # Will trigger in-memory fallback

from queue_api import (
    app, ws_manager, DLQAlertConfig, ttl_manager,
    generate_ws_token, validate_ws_token,
    check_rate_limit, get_rate_limit_info,
    TOKEN_RATE_LIMIT, TOKEN_RATE_WINDOW, WS_TOKEN_TTL,
    _store_token, _get_token, _delete_token, _count_tokens,
    _FALLBACK_TOKENS,
)
from async_execution_queue import QueuedTask, DeadLetterQueue

client = TestClient(app)


class TestRedisTokenPersistence:
    def test_store_and_get_token(self):
        _FALLBACK_TOKENS.clear()
        _store_token("test-token-1", "agent-1")
        data = _get_token("test-token-1")
        assert data is not None
        assert data["agent_id"] == "agent-1"

    def test_get_nonexistent_token(self):
        assert _get_token("nonexistent") is None

    def test_delete_token(self):
        _store_token("delete-me", "agent")
        assert _delete_token("delete-me") == True
        assert _get_token("delete-me") is None

    def test_delete_nonexistent(self):
        assert _delete_token("nonexistent") == False

    def test_count_tokens(self):
        _FALLBACK_TOKENS.clear()
        _store_token("t1", "a")
        _store_token("t2", "b")
        assert _count_tokens() == 2

    def test_generate_token(self):
        _FALLBACK_TOKENS.clear()
        token = generate_ws_token("gen-test")
        assert token is not None
        assert validate_ws_token(token) == True

    def test_validate_invalid_token(self):
        assert validate_ws_token("invalid") == False

    def test_validate_empty_token(self):
        assert validate_ws_token("") == False

    def test_token_expiry(self):
        _store_token("expire-test", "agent", ttl=0)
        time.sleep(0.1)
        assert validate_ws_token("expire-test") == False

    def test_token_survives_in_fallback(self):
        """In-memory fallback persists tokens within the same process."""
        _FALLBACK_TOKENS.clear()
        token = generate_ws_token("persist-test")
        # Token should be retrievable
        assert _get_token(token) is not None
        assert _get_token(token)["agent_id"] == "persist-test"


class TestRateLimiting:
    def test_rate_limit_allows_under_limit(self):
        ip = "192.168.1.1"
        for _ in range(TOKEN_RATE_LIMIT):
            assert check_rate_limit(ip) == True

    def test_rate_limit_blocks_over_limit(self):
        ip = "192.168.1.2"
        for _ in range(TOKEN_RATE_LIMIT):
            check_rate_limit(ip)
        assert check_rate_limit(ip) == False

    def test_rate_limit_info(self):
        ip = "192.168.1.3"
        check_rate_limit(ip)
        info = get_rate_limit_info(ip)
        assert info["requests"] >= 1
        assert info["limit"] == TOKEN_RATE_LIMIT
        assert info["remaining"] < TOKEN_RATE_LIMIT

    def test_different_ips_independent(self):
        ip1 = "10.0.0.1"
        ip2 = "10.0.0.2"
        for _ in range(TOKEN_RATE_LIMIT):
            check_rate_limit(ip1)
        assert check_rate_limit(ip1) == False
        assert check_rate_limit(ip2) == True


class TestWSTokenEndpoints:
    def test_create_token(self):
        resp = client.post("/ws/token", json={"agent_id": "test-create"},
                          headers={"X-Forwarded-For": "1.2.3.4"})
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["expires_in"] == WS_TOKEN_TTL

    def test_list_tokens(self):
        generate_ws_token("list-test")
        resp = client.get("/ws/tokens")
        assert resp.status_code == 200
        data = resp.json()
        assert "active_tokens" in data
        assert data["active_tokens"] >= 1

    def test_revoke_token(self):
        token = generate_ws_token("revoke-test")
        resp = client.delete(f"/ws/token/{token}")
        assert resp.status_code == 200
        assert resp.json()["revoked"] == True

    def test_revoke_nonexistent(self):
        resp = client.delete("/ws/token/nonexistent")
        assert resp.status_code == 404

    def test_rate_limit_endpoint(self):
        resp = client.get("/ws/rate-limit")
        assert resp.status_code == 200
        data = resp.json()
        assert "limit" in data
        assert "remaining" in data


class TestSecureDefault:
    def test_health_v32(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "3.2.0"
        assert "redis_connected" in data

    def test_ws_endpoint_requires_token(self):
        """WebSocket without token should be rejected."""
        # Note: TestClient doesn't directly support WebSocket testing,
        # but we can verify the token validation logic
        assert validate_ws_token(None) == False
        assert validate_ws_token("") == False

    def test_agent_submit_works(self):
        resp = client.post("/agent/submit", json={
            "agent_id": "v32-test", "agent_name": "V32", "capability": "test",
        })
        assert resp.status_code == 200

    def test_non_blocking_execute(self):
        resp = client.post("/agent/execute/async", json={
            "agent_id": "v32-async", "agent_name": "Async", "capability": "test",
        })
        assert resp.status_code == 200
        assert "poll_url" in resp.json()
