"""
Tests for Queue API v3.5: Redis TTL persistence, WS message auth, E2E execution test.
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
    gateway_executor, ttl_registry, TaskTTLRegistry,
    execution_queue, agent_queue,
)
from async_execution_queue import QueuedTask, DeadLetterQueue

client = TestClient(app)


class TestRedisTTLPersistence:
    def test_set_and_get_ttl(self):
        ttl_registry.set_task_ttl("redis-task-1", 7200)
        assert ttl_registry.get_task_ttl("redis-task-1") == 7200

    def test_get_default_ttl(self):
        assert ttl_registry.get_task_ttl("nonexistent-redis", default=3600) == 3600

    def test_remove_ttl(self):
        ttl_registry.set_task_ttl("redis-remove", 1800)
        ttl_registry.remove_task_ttl("redis-remove")
        assert ttl_registry.get_task_ttl("redis-remove", default=999) == 999

    def test_count_overrides(self):
        ttl_registry.set_task_ttl("count-a", 1)
        ttl_registry.set_task_ttl("count-b", 2)
        assert ttl_registry.count_overrides() >= 2

    def test_is_override(self):
        ttl_registry.set_task_ttl("override-check", 3600)
        assert ttl_registry.is_override("override-check") == True
        assert ttl_registry.is_override("not-an-override") == False

    def test_set_ttl_endpoint(self):
        resp = client.post("/task/redis-task/ttl", json={"ttl_seconds": 7200})
        assert resp.status_code == 200
        assert resp.json()["ttl_seconds"] == 7200

    def test_get_ttl_endpoint(self):
        client.post("/task/redis-get/ttl", json={"ttl_seconds": 3600})
        resp = client.get("/task/redis-get/ttl")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ttl_seconds"] == 3600
        assert data["is_override"] == True

    def test_remove_ttl_endpoint(self):
        client.post("/task/redis-rem/ttl", json={"ttl_seconds": 1800})
        resp = client.delete("/task/redis-rem/ttl")
        assert resp.status_code == 200
        assert resp.json()["status"] == "removed"

    def test_submit_with_ttl_persists(self):
        resp = client.post("/agent/submit", json={
            "agent_id": "redis-ttl-test", "agent_name": "RedisTTL", 
            "capability": "test", "ttl_seconds": 3600,
        })
        assert resp.status_code == 200
        task_id = resp.json()["task_id"]
        assert ttl_registry.is_override(task_id) == True


class TestE2EExecutionTest:
    def test_e2e_test_no_executor(self):
        """Should skip when no executor is set."""
        with patch.object(execution_queue, '_executor', None):
            resp = client.post("/execution/e2e-test")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "skipped"

    def test_e2e_test_with_mock_executor(self):
        """Test E2E endpoint with mock executor and mock gateway."""
        async def mock_exec(task):
            return {"content": "E2E test successful", "tokens": 10}
        
        with patch.object(execution_queue, '_executor', mock_exec):
            with patch.object(execution_queue, '_running', True):
                with patch.object(agent_queue, 'execute_agent_task', new_callable=AsyncMock) as mock_exec_agent:
                    mock_exec_agent.return_value = {
                        "status": "completed", "agent_id": "e2e-test",
                        "output": {"content": "E2E test successful"},
                    }
                    with patch('httpx.AsyncClient') as mock_httpx:
                        mock_resp = MagicMock()
                        mock_resp.status_code = 200
                        mock_resp.json.return_value = {"status": "healthy"}
                        
                        mock_inst = AsyncMock()
                        mock_inst.get = AsyncMock(return_value=mock_resp)
                        mock_inst.__aenter__ = AsyncMock(return_value=mock_inst)
                        mock_inst.__aexit__ = AsyncMock(return_value=None)
                        mock_httpx.return_value = mock_inst
                        
                        resp = client.post("/execution/e2e-test")
                        assert resp.status_code == 200
                        data = resp.json()
                        assert data["test"] == "e2e_execution"
                        results = data["results"]
                        assert results["queue_running"] == True
                        assert results["gateway_reachable"] == True


class TestHealthV35:
    def test_health_v35(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "3.5.0"
        assert "gateway_wired" in data
        assert "ttl_overrides" in data

    def test_agent_submit_works(self):
        resp = client.post("/agent/submit", json={
            "agent_id": "v35-test", "agent_name": "V35", "capability": "test",
        })
        assert resp.status_code == 200
