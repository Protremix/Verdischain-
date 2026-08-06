"""
Tests for Queue API (DLQ endpoints + queue management).
"""

import pytest
import asyncio
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from queue_api import app
from async_execution_queue import (
    AsyncExecutionQueue, DeadLetterQueue, QueuedTask, TaskStatus,
)

client = TestClient(app)


class TestQueueAPI:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "queue" in data
        assert "dlq" in data

    def test_queue_stats(self):
        resp = client.get("/queue/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_tasks" in data
        assert "max_queue_size" in data

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
        assert data["status"] == "pending"

    def test_get_task(self):
        # Submit first
        submit_resp = client.post("/queue/submit", json={
            "agent_id": "core-arch",
            "agent_name": "Arch",
            "capability": "design",
        })
        task_id = submit_resp.json()["task_id"]
        
        resp = client.get(f"/queue/task/{task_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == task_id

    def test_get_nonexistent_task(self):
        resp = client.get("/queue/task/nonexistent-id")
        assert resp.status_code == 404

    def test_list_tasks(self):
        for i in range(3):
            client.post("/queue/submit", json={
                "agent_id": f"agent-{i}",
                "agent_name": f"Agent {i}",
                "capability": "test",
            })
        resp = client.get("/queue/tasks?limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 3

    def test_cancel_task(self):
        submit_resp = client.post("/queue/submit", json={
            "agent_id": "core-cancel",
            "agent_name": "Cancel",
            "capability": "test",
        })
        task_id = submit_resp.json()["task_id"]
        
        resp = client.post(f"/queue/cancel/{task_id}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_cancel_nonexistent(self):
        resp = client.post("/queue/cancel/nonexistent")
        assert resp.status_code == 400


class TestDLQAPI:
    def test_dlq_stats(self):
        resp = client.get("/dlq/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "max_size" in data

    def test_dlq_list_empty(self):
        resp = client.get("/dlq/list")
        assert resp.status_code == 200
        data = resp.json()
        assert "entries" in data
        assert "count" in data

    def test_dlq_add_and_list(self):
        from queue_api import dead_letter_queue
        # Clear first to ensure clean state
        dead_letter_queue.clear()
        
        task = QueuedTask(id="dlq-test-1", agent_id="a", agent_name="A", capability="c", input_data={})
        task.error = "test failure"
        dead_letter_queue.add(task)
        
        resp = client.get("/dlq/list")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1
        assert data["entries"][0]["id"] == "dlq-test-1"
        
        # Cleanup
        dead_letter_queue.clear()

    def test_dlq_get_entry(self):
        from queue_api import dead_letter_queue
        dead_letter_queue.clear()
        
        task = QueuedTask(id="dlq-get-test", agent_id="a", agent_name="A", capability="c", input_data={})
        dead_letter_queue.add(task)
        
        resp = client.get("/dlq/dlq-get-test")
        assert resp.status_code == 200
        assert resp.json()["id"] == "dlq-get-test"
        
        dead_letter_queue.clear()

    def test_dlq_get_nonexistent(self):
        resp = client.get("/dlq/nonexistent-entry")
        assert resp.status_code == 404

    def test_dlq_remove(self):
        from queue_api import dead_letter_queue
        dead_letter_queue.clear()
        
        task = QueuedTask(id="dlq-remove-me", agent_id="a", agent_name="A", capability="c", input_data={})
        dead_letter_queue.add(task)
        
        resp = client.delete("/dlq/dlq-remove-me")
        assert resp.status_code == 200
        assert resp.json()["removed"] == True
        
        # Verify it's gone
        resp2 = client.get("/dlq/dlq-remove-me")
        assert resp2.status_code == 404

    def test_dlq_remove_nonexistent(self):
        resp = client.delete("/dlq/nonexistent")
        assert resp.status_code == 404

    def test_dlq_clear(self):
        from queue_api import dead_letter_queue
        task = QueuedTask(id="dlq-clear-1", agent_id="a", agent_name="A", capability="c", input_data={})
        dead_letter_queue.add(task)
        task2 = QueuedTask(id="dlq-clear-2", agent_id="b", agent_name="B", capability="c", input_data={})
        dead_letter_queue.add(task2)
        
        resp = client.post("/dlq/clear")
        assert resp.status_code == 200
        assert resp.json()["cleared"] >= 2

    def test_dlq_requeue(self):
        from queue_api import dead_letter_queue, execution_queue
        dead_letter_queue.clear()
        
        task = QueuedTask(
            id="dlq-requeue-test", agent_id="core-arch",
            agent_name="Architecture", capability="design",
            input_data={"prompt": "test"}, priority=3,
        )
        task.error = "failed permanently"
        dead_letter_queue.add(task)
        
        resp = client.post("/dlq/dlq-requeue-test/requeue")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "re-queued"
        assert "new_task_id" in data
        
        # Verify old entry is gone from DLQ
        resp2 = client.get("/dlq/dlq-requeue-test")
        assert resp2.status_code == 404
        
        # Cleanup
        dead_letter_queue.clear()
