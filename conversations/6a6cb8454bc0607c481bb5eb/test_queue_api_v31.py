"""
Tests for Queue API v3.1: WebSocket auth, non-blocking execute, DLQ webhook E2E.
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

from queue_api import (
    app, ws_manager, DLQAlertConfig, ttl_manager,
    generate_ws_token, validate_ws_token, cleanup_expired_tokens,
    WS_TOKENS, WS_TOKEN_TTL,
)
from async_execution_queue import QueuedTask, DeadLetterQueue

client = TestClient(app)


class TestWebSocketAuth:
    def test_generate_ws_token(self):
        token = generate_ws_token("agent-1")
        assert token is not None
        assert len(token) > 20
        assert token in WS_TOKENS
        assert WS_TOKENS[token]["agent_id"] == "agent-1"

    def test_validate_ws_token_valid(self):
        token = generate_ws_token("test-agent")
        assert validate_ws_token(token) == True

    def test_validate_ws_token_invalid(self):
        assert validate_ws_token("invalid-token") == False

    def test_validate_ws_token_empty(self):
        assert validate_ws_token("") == False

    def test_validate_ws_token_expired(self):
        token = generate_ws_token("expired-agent")
        # Manually expire it
        WS_TOKENS[token]["expires_at"] = time.time() - 1
        assert validate_ws_token(token) == False
        assert token not in WS_TOKENS  # should be cleaned up

    def test_cleanup_expired_tokens(self):
        token1 = generate_ws_token("a")
        token2 = generate_ws_token("b")
        WS_TOKENS[token1]["expires_at"] = time.time() - 100
        WS_TOKENS[token2]["expires_at"] = time.time() - 200
        expired = cleanup_expired_tokens()
        assert expired >= 2
        assert token1 not in WS_TOKENS
        assert token2 not in WS_TOKENS

    def test_create_ws_token_endpoint(self):
        resp = client.post("/ws/token", json={"agent_id": "test-create"})
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["expires_in"] == WS_TOKEN_TTL
        assert data["agent_id"] == "test-create"

    def test_list_ws_tokens(self):
        generate_ws_token("list-test")
        resp = client.get("/ws/tokens")
        assert resp.status_code == 200
        data = resp.json()
        assert "active_tokens" in data
        assert data["active_tokens"] >= 1

    def test_revoke_ws_token(self):
        token = generate_ws_token("revoke-test")
        resp = client.delete(f"/ws/token/{token}")
        assert resp.status_code == 200
        assert resp.json()["revoked"] == True
        assert token not in WS_TOKENS

    def test_revoke_nonexistent_token(self):
        resp = client.delete("/ws/token/nonexistent")
        assert resp.status_code == 404


class TestNonBlockingExecute:
    def test_execute_async_returns_task_id(self):
        """Non-blocking execute should return task_id immediately."""
        resp = client.post("/agent/execute/async", json={
            "agent_id": "core-arch",
            "agent_name": "Architecture",
            "capability": "design",
            "input_data": {"prompt": "test"},
            "priority": 5,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "task_id" in data
        assert data["status"] == "pending"
        assert "poll_url" in data
        assert data["poll_url"].startswith("/agent/task/")

    def test_execute_async_then_poll(self):
        """Submit via async, then poll for status."""
        submit = client.post("/agent/execute/async", json={
            "agent_id": "core-poll",
            "agent_name": "PollTest",
            "capability": "test",
        })
        task_id = submit.json()["task_id"]
        
        # Poll for status
        resp = client.get(f"/agent/task/{task_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == task_id

    def test_execute_async_queue_full(self):
        """Test that QueueFull returns 429."""
        from queue_api import agent_queue
        with patch.object(agent_queue, 'submit_agent_task', side_effect=asyncio.QueueFull("Full")):
            resp = client.post("/agent/execute/async", json={
                "agent_id": "x", "agent_name": "x", "capability": "x",
            })
            assert resp.status_code == 429


class TestDLQWebhookE2E:
    def test_webhook_test_no_config(self):
        """Test webhook test endpoint when no webhook configured."""
        DLQAlertConfig.webhook_url = None
        resp = client.post("/dlq/alerts/test")
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_webhook_test_with_mock(self):
        """Test webhook test endpoint with a mock webhook URL."""
        DLQAlertConfig.webhook_url = "https://httpbin.org/post"
        with patch('httpx.AsyncClient') as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = '{"ok": true}'
            
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(return_value=mock_resp)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance
            
            resp = client.post("/dlq/alerts/test")
            assert resp.status_code == 200
            data = resp.json()
            assert data["sent"] == True
            assert data["status_code"] == 200

    def test_webhook_test_connection_error(self):
        """Test webhook test endpoint with connection error."""
        DLQAlertConfig.webhook_url = "https://nonexistent.invalid/webhook"
        resp = client.post("/dlq/alerts/test")
        assert resp.status_code == 200
        data = resp.json()
        assert data["sent"] == False
        assert "error" in data


class TestHealthV31:
    def test_health_v31(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "3.1.0"
        assert "ws_tokens" in data

    def test_agent_submit_still_works(self):
        resp = client.post("/agent/submit", json={
            "agent_id": "v31-test", "agent_name": "V31", "capability": "test",
        })
        assert resp.status_code == 200
        assert "task_id" in resp.json()

