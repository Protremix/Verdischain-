"""
Tests for Queue API v3.4: AI Gateway executor, per-task TTL, WS client library.
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
    gateway_executor, TaskTTLRegistry, ttl_registry,
    execution_queue, agent_queue,
)
from async_execution_queue import QueuedTask, DeadLetterQueue

client = TestClient(app)


class TestGatewayExecutor:
    @pytest.mark.asyncio
    async def test_gateway_executor_function_exists(self):
        """Verify gateway_executor is an async function."""
        assert callable(gateway_executor)
        assert asyncio.iscoroutinefunction(gateway_executor)

    @pytest.mark.asyncio
    async def test_gateway_executor_calls_httpx(self):
        """Test that gateway_executor makes HTTP request."""
        task = QueuedTask(
            id="test-gw", agent_id="test", agent_name="Test",
            capability="chat", input_data={"prompt": "hello"},
        )
        task.timeout = 10
        
        with patch('httpx.AsyncClient') as mock_client_cls:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"content": "test response", "tokens": 50}
            mock_resp.raise_for_status = MagicMock()
            
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(return_value=mock_resp)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_instance
            
            result = await gateway_executor(task)
            assert result["content"] == "test response"
            assert result["tokens"] == 50

    @pytest.mark.asyncio
    async def test_gateway_executor_timeout(self):
        """Test gateway executor handles timeout."""
        import httpx
        task = QueuedTask(
            id="test-timeout", agent_id="test", agent_name="Test",
            capability="chat", input_data={"prompt": "hello"},
        )
        task.timeout = 1
        
        with patch('httpx.AsyncClient') as mock_client_cls:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_instance
            
            with pytest.raises(TimeoutError):
                await gateway_executor(task)

    @pytest.mark.asyncio
    async def test_gateway_executor_routes_capability(self):
        """Test that different capabilities route to different payloads."""
        task_review = QueuedTask(
            id="review-task", agent_id="test", agent_name="Test",
            capability="code_review", input_data={"code": "test"},
        )
        task_review.timeout = 10
        
        with patch('httpx.AsyncClient') as mock_client_cls:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"content": "review done"}
            mock_resp.raise_for_status = MagicMock()
            
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(return_value=mock_resp)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_instance
            
            await gateway_executor(task_review)
            call_args = mock_instance.post.call_args
            payload = call_args[1]["json"]
            assert payload["provider"] == "code-reviewer"


class TestPerTaskTTL:
    def test_ttl_registry_init(self):
        reg = TaskTTLRegistry()
        assert reg.count_overrides() == 0

    def test_set_and_get_ttl(self):
        reg = TaskTTLRegistry()
        reg.set_task_ttl("task-1", 7200)
        assert reg.get_task_ttl("task-1") == 7200

    def test_get_default_ttl(self):
        reg = TaskTTLRegistry()
        assert reg.get_task_ttl("nonexistent", default=3600) == 3600

    def test_remove_ttl(self):
        reg = TaskTTLRegistry()
        reg.set_task_ttl("task-2", 1800)
        reg.remove_task_ttl("task-2")
        assert reg.get_task_ttl("task-2", default=999) == 999

    def test_count_overrides(self):
        reg = TaskTTLRegistry()
        reg.set_task_ttl("a", 1)
        reg.set_task_ttl("b", 2)
        assert reg.count_overrides() == 2

    def test_set_task_ttl_endpoint(self):
        resp = client.post("/task/test-task/ttl", json={"ttl_seconds": 7200})
        assert resp.status_code == 200
        assert resp.json()["ttl_seconds"] == 7200

    def test_get_task_ttl_endpoint(self):
        client.post("/task/get-test/ttl", json={"ttl_seconds": 3600})
        resp = client.get("/task/get-test/ttl")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ttl_seconds"] == 3600
        assert data["is_override"] == True

    def test_remove_task_ttl_endpoint(self):
        client.post("/task/remove-test/ttl", json={"ttl_seconds": 1800})
        resp = client.delete("/task/remove-test/ttl")
        assert resp.status_code == 200
        assert resp.json()["status"] == "removed"

    def test_submit_with_ttl(self):
        """Test that submit accepts ttl_seconds in request."""
        resp = client.post("/agent/submit", json={
            "agent_id": "ttl-test", "agent_name": "TTL", "capability": "test",
            "ttl_seconds": 3600,
        })
        assert resp.status_code == 200
        task_id = resp.json()["task_id"]
        assert ttl_registry.get_task_ttl(task_id) == 3600


class TestWSClientLibrary:
    def test_ws_client_library_endpoint(self):
        resp = client.get("/ws/client-library")
        assert resp.status_code == 200
        data = resp.json()
        assert "python" in data
        assert "typescript" in data
        assert "curl" in data
        assert "EvolvixOSWSClient" in data["python"]
        assert "EvolvixOSWSClient" in data["typescript"]


class TestHealthV34:
    def test_health_v34(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "3.4.0"
        assert "gateway_wired" in data
        assert "ttl_overrides" in data

    def test_execution_test_with_executor(self):
        """Test execution endpoint when executor is set."""
        with patch.object(execution_queue, '_executor', AsyncMock()):
            with patch.object(agent_queue, 'execute_agent_task', new_callable=AsyncMock) as mock_exec:
                mock_exec.return_value = {"status": "completed", "agent_id": "exec-test"}
                resp = client.post("/execution/test")
                assert resp.status_code == 200
                data = resp.json()
                assert data["status"] in ("completed", "failed")
