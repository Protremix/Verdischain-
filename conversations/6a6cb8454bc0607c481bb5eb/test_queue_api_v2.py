"""
Tests for Queue API v2.0: PG persistence, automated recovery, DLQ alerting.
"""

import pytest
import asyncio
import os
import sys
import time
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock PG pool before importing
with patch('asyncpg.create_pool', new_callable=AsyncMock) as mock_pool:
    mock_pool.return_value = None

from queue_api import (
    app, DLQAlertConfig, send_dlq_alert,
    persist_task, get_pending_tasks, cleanup_old_queue_tasks,
)
from async_execution_queue import (
    AsyncExecutionQueue, DeadLetterQueue, QueuedTask, TaskStatus,
)

client = TestClient(app)


class TestQueueAPIV2:
    def test_health_v2(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "pg_connected" in data
        assert "queue" in data
        assert "dlq" in data

    def test_queue_stats_v2(self):
        resp = client.get("/queue/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "pg_connected" in data

    def test_submit_task(self):
        resp = client.post("/queue/submit", json={
            "agent_id": "core-test",
            "agent_name": "Test Agent",
            "capability": "code_review",
            "input_data": {"prompt": "review this"},
            "priority": 5,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "task_id" in data

    def test_get_task(self):
        submit_resp = client.post("/queue/submit", json={
            "agent_id": "core-arch", "agent_name": "Arch", "capability": "design",
        })
        task_id = submit_resp.json()["task_id"]
        resp = client.get(f"/queue/task/{task_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == task_id

    def test_get_nonexistent_task(self):
        resp = client.get("/queue/task/nonexistent-id")
        assert resp.status_code == 404

    def test_list_tasks(self):
        for i in range(3):
            client.post("/queue/submit", json={
                "agent_id": f"agent-{i}", "agent_name": f"Agent {i}", "capability": "test",
            })
        resp = client.get("/queue/tasks?limit=10")
        assert resp.status_code == 200
        assert resp.json()["count"] >= 3

    def test_cancel_task(self):
        submit_resp = client.post("/queue/submit", json={
            "agent_id": "core-cancel", "agent_name": "Cancel", "capability": "test",
        })
        task_id = submit_resp.json()["task_id"]
        resp = client.post(f"/queue/cancel/{task_id}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_cancel_nonexistent(self):
        resp = client.post("/queue/cancel/nonexistent")
        assert resp.status_code == 400

    def test_recover_endpoint(self):
        resp = client.post("/queue/recover?limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert "recovered" in data
        assert "checked" in data

    def test_retention_endpoint(self):
        resp = client.post("/queue/retention/30")
        assert resp.status_code == 200
        data = resp.json()
        assert "deleted" in data
        assert "retention_days" in data


class TestDLQAPIV2:
    def test_dlq_stats(self):
        resp = client.get("/dlq/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "max_size" in data

    def test_dlq_list(self):
        resp = client.get("/dlq/list")
        assert resp.status_code == 200
        assert "entries" in resp.json()

    def test_dlq_add_and_get(self):
        from queue_api import dead_letter_queue
        dead_letter_queue.clear()
        task = QueuedTask(id="v2-dlq-test", agent_id="a", agent_name="A", capability="c", input_data={})
        task.error = "test failure"
        dead_letter_queue.add(task)
        
        resp = client.get("/dlq/v2-dlq-test")
        assert resp.status_code == 200
        assert resp.json()["id"] == "v2-dlq-test"
        dead_letter_queue.clear()

    def test_dlq_remove(self):
        from queue_api import dead_letter_queue
        dead_letter_queue.clear()
        task = QueuedTask(id="v2-remove", agent_id="a", agent_name="A", capability="c", input_data={})
        dead_letter_queue.add(task)
        
        resp = client.delete("/dlq/v2-remove")
        assert resp.status_code == 200
        assert resp.json()["removed"] == True
        dead_letter_queue.clear()

    def test_dlq_clear(self):
        from queue_api import dead_letter_queue
        task = QueuedTask(id="v2-clear", agent_id="a", agent_name="A", capability="c", input_data={})
        dead_letter_queue.add(task)
        resp = client.post("/dlq/clear")
        assert resp.status_code == 200
        assert resp.json()["cleared"] >= 1

    def test_dlq_requeue(self):
        from queue_api import dead_letter_queue
        dead_letter_queue.clear()
        task = QueuedTask(
            id="v2-requeue", agent_id="core-arch",
            agent_name="Architecture", capability="design",
            input_data={"prompt": "test"}, priority=3,
        )
        task.error = "failed"
        dead_letter_queue.add(task)
        
        resp = client.post("/dlq/v2-requeue/requeue")
        assert resp.status_code == 200
        assert resp.json()["status"] == "re-queued"
        dead_letter_queue.clear()


class TestDLQAlerting:
    def test_get_alert_config(self):
        resp = client.get("/dlq/alerts/config")
        assert resp.status_code == 200
        data = resp.json()
        assert "min_severity" in data
        assert "rate_limit_seconds" in data

    def test_set_alert_config(self):
        resp = client.post("/dlq/alerts/config", json={
            "webhook_url": "https://example.com/webhook",
            "min_severity": "critical",
            "rate_limit_seconds": 30,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["config"]["webhook_url"] == "https://example.com/webhook"
        assert data["config"]["min_severity"] == "critical"
        assert data["config"]["rate_limit_seconds"] == 30

    def test_alert_rate_limiting(self):
        # Reset
        DLQAlertConfig._last_alert_time = 0
        assert DLQAlertConfig.should_alert() == True
        assert DLQAlertConfig.should_alert() == False  # rate limited

    @pytest.mark.asyncio
    async def test_send_dlq_alert_no_webhook(self):
        DLQAlertConfig.webhook_url = None
        DLQAlertConfig._last_alert_time = 0
        await send_dlq_alert("test-task", "test error", "test-agent")
        # Should not raise

    @pytest.mark.asyncio
    async def test_persist_task_no_pg(self):
        """Test that persist_task gracefully handles no PG pool."""
        with patch('queue_api._pg_pool', None):
            await persist_task({"id": "test", "agent_id": "a"})
            # Should not raise

    @pytest.mark.asyncio
    async def test_get_pending_tasks_no_pg(self):
        """Test that get_pending_tasks returns empty list when no PG."""
        with patch('queue_api._pg_pool', None):
            tasks = await get_pending_tasks(limit=10)
            assert tasks == []

    @pytest.mark.asyncio
    async def test_cleanup_no_pg(self):
        """Test cleanup returns 0 when no PG."""
        with patch('queue_api._pg_pool', None):
            deleted = await cleanup_old_queue_tasks(30)
            assert deleted == 0
