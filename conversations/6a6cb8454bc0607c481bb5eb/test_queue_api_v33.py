"""
Tests for Queue API v3.3: Redis rate limiting, WS integration test, real execution test.
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

with patch('redis.from_url') as mock_redis:
    mock_redis.return_value = None

from queue_api import (
    app, ws_manager, DLQAlertConfig, ttl_manager,
    generate_ws_token, validate_ws_token,
    check_rate_limit, get_rate_limit_info,
    TOKEN_RATE_LIMIT, TOKEN_RATE_WINDOW, WS_TOKEN_TTL,
    _store_token, _get_token, _delete_token, _count_tokens,
    _FALLBACK_TOKENS, _FALLBACK_RATE,
    execution_queue, agent_queue,
)
from async_execution_queue import QueuedTask, DeadLetterQueue

client = TestClient(app)


class TestRedisRateLimiting:
    def test_rate_limit_allows(self):
        ip = "172.16.0.1"
        for _ in range(TOKEN_RATE_LIMIT):
            assert check_rate_limit(ip) == True

    def test_rate_limit_blocks(self):
        _FALLBACK_RATE.clear()
        ip = "172.16.0.2"
        for _ in range(TOKEN_RATE_LIMIT):
            check_rate_limit(ip)
        assert check_rate_limit(ip) == False

    def test_rate_limit_info(self):
        _FALLBACK_RATE.clear()
        ip = "172.16.0.3"
        check_rate_limit(ip)
        info = get_rate_limit_info(ip)
        assert info["limit"] == TOKEN_RATE_LIMIT
        assert "remaining" in info

    def test_different_ips_independent(self):
        _FALLBACK_RATE.clear()
        ip1 = "172.16.0.10"
        ip2 = "172.16.0.11"
        for _ in range(TOKEN_RATE_LIMIT):
            check_rate_limit(ip1)
        assert check_rate_limit(ip1) == False
        assert check_rate_limit(ip2) == True


class TestWSIntegrationTest:
    def test_ws_integration_test_endpoint(self):
        """Test the WebSocket integration test endpoint."""
        _FALLBACK_TOKENS.clear()
        resp = client.post("/ws/integration-test")
        assert resp.status_code == 200
        data = resp.json()
        assert data["test"] == "websocket_integration"
        results = data["results"]
        assert results["token_generated"] == True
        assert results["token_valid"] == True
        assert results["invalid_token_rejected"] == True
        assert results["empty_token_rejected"] == True
        assert results["token_revoked"] == True
        assert results["revoked_token_rejected"] == True
        assert results["all_passed"] == True

    def test_ws_integration_test_rate_limit(self):
        """Integration test should also test rate limiting."""
        _FALLBACK_RATE.clear()
        resp = client.post("/ws/integration-test")
        data = resp.json()
        assert data["results"]["rate_limit_works"] == True
        assert "rate_limit_info" in data["results"]


class TestRealExecutionTest:
    def test_execution_test_no_executor(self):
        """Should skip when no executor is set."""
        resp = client.post("/execution/test")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "skipped"
        assert "No executor set" in data["reason"]

    def test_execution_test_with_mock_executor(self):
        """Test with a mock executor set."""
        async def mock_executor(task):
            return {"content": "test output", "tokens": 50}
        
        with patch.object(execution_queue, '_executor', mock_executor):
            with patch.object(execution_queue, '_running', True):
                with patch.object(agent_queue, '_executor_set', True):
                    with patch.object(agent_queue, 'execute_agent_task', new_callable=AsyncMock) as mock_exec:
                        mock_exec.return_value = {
                            "status": "completed", "agent_id": "exec-test-2",
                            "output": {"content": "test"}, "latency_ms": 100,
                        }
                        resp = client.post("/execution/test")
                        assert resp.status_code == 200
                        data = resp.json()
                        assert data["test"] == "real_execution"


class TestHealthV33:
    def test_health_v33(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "3.3.0"
        assert "redis_connected" in data

    def test_agent_submit(self):
        resp = client.post("/agent/submit", json={
            "agent_id": "v33-test", "agent_name": "V33", "capability": "test",
        })
        assert resp.status_code == 200

    def test_non_blocking_execute(self):
        resp = client.post("/agent/execute/async", json={
            "agent_id": "v33-async", "agent_name": "Async", "capability": "test",
        })
        assert resp.status_code == 200
        assert "poll_url" in resp.json()

    def test_create_token(self):
        _FALLBACK_RATE.clear()
        resp = client.post("/ws/token", json={"agent_id": "v33-token"},
                          headers={"X-Forwarded-For": "10.10.10.10"})
        assert resp.status_code == 200
        assert "token" in resp.json()

    def test_token_endpoint_rate_limited(self):
        """Test that token endpoint enforces rate limiting."""
        _FALLBACK_RATE.clear()
        # Make TOKEN_RATE_LIMIT requests
        for _ in range(TOKEN_RATE_LIMIT):
            resp = client.post("/ws/token", json={"agent_id": "rate-test"},
                             headers={"X-Forwarded-For": "10.10.10.20"})
            assert resp.status_code == 200
        
        # Next should be rate limited
        resp = client.post("/ws/token", json={"agent_id": "rate-test"},
                         headers={"X-Forwarded-For": "10.10.10.20"})
        assert resp.status_code == 429
