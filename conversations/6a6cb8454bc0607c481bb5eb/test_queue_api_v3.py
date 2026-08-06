"""
Tests for Queue API v3.0: Agent endpoints, WebSocket, TTL config.
"""

import pytest
import asyncio
import os
import sys
import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

with patch('asyncpg.create_pool', new_callable=AsyncMock) as mock_pool:
    mock_pool.return_value = None

from queue_api import app, ws_manager, DLQAlertConfig, ttl_manager
from async_execution_queue import QueuedTask, DeadLetterQueue

client = TestClient(app)


class TestAgentEndpoints:
    def test_agent_submit(self):
        resp = client.post("/agent/submit", json={
            "agent_id": "core-arch", "agent_name": "Architecture",
            "capability": "design", "input_data": {"prompt": "test"},
            "priority": 5,
        })
        assert resp.status_code == 200
        assert "task_id" in resp.json()

    def test_agent_task_status(self):
        submit = client.post("/agent/submit", json={
            "agent_id": "core-test", "agent_name": "Test", "capability": "test",
        })
        task_id = submit.json()["task_id"]
        resp = client.get(f"/agent/task/{task_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == task_id

    def test_agent_task_not_found(self):
        resp = client.get("/agent/task/nonexistent")
        assert resp.status_code == 404

    def test_agent_list_tasks(self):
        for i in range(3):
            client.post("/agent/submit", json={
                "agent_id": f"agent-{i}", "agent_name": f"Agent {i}", "capability": "test",
            })
        resp = client.get("/agent/tasks?limit=10")
        assert resp.status_code == 200
        assert resp.json()["count"] >= 3

    def test_agent_list_tasks_filtered(self):
        client.post("/agent/submit", json={
            "agent_id": "core-arch", "agent_name": "Arch", "capability": "design",
        })
        resp = client.get("/agent/tasks?agent_id=core-arch")
        assert resp.status_code == 200
        tasks = resp.json()["tasks"]
        assert all(t["agent_id"] == "core-arch" for t in tasks)

    def test_agent_stats(self):
        resp = client.get("/agent/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "queue" in data
        assert "dlq" in data

    def test_agent_dlq_requeue_not_found(self):
        resp = client.post("/agent/dlq/nonexistent/requeue")
        assert resp.status_code == 404


class TestTTLConfig:
    def test_get_ttl_config(self):
        resp = client.get("/ttl/config")
        assert resp.status_code == 200
        assert "ttl_seconds" in resp.json()

    def test_set_ttl_config(self):
        resp = client.post("/ttl/config", json={
            "ttl_seconds": 7200, "cleanup_interval": 1800,
        })
        assert resp.status_code == 200
        assert resp.json()["ttl_seconds"] == 7200
        
        # Reset
        client.post("/ttl/config", json={"ttl_seconds": 86400, "cleanup_interval": 3600})


class TestHealthV3:
    def test_health_v3(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "3.0.0"
        assert "pg_connected" in data
        assert "ttl_seconds" in data
        assert "ws_connections" in data


class TestDLQEndpoints:
    def test_dlq_stats(self):
        resp = client.get("/dlq/stats")
        assert resp.status_code == 200

    def test_dlq_list(self):
        resp = client.get("/dlq/list")
        assert resp.status_code == 200
        assert "entries" in resp.json()

    def test_dlq_alert_config(self):
        resp = client.get("/dlq/alerts/config")
        assert resp.status_code == 200
        assert "min_severity" in resp.json()

    def test_dlq_set_alert_config(self):
        resp = client.post("/dlq/alerts/config", json={
            "webhook_url": "https://example.com/hook",
            "min_severity": "critical",
            "rate_limit_seconds": 120,
        })
        assert resp.status_code == 200
        assert resp.json()["webhook_url"] == "https://example.com/hook"


class TestWebSocket:
    def test_ws_manager_init(self):
        assert ws_manager.connection_count >= 0

    def test_ws_manager_broadcast_empty(self):
        """Broadcast with no connections should not raise."""
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(ws_manager.broadcast({"test": True}))
        finally:
            loop.close()
