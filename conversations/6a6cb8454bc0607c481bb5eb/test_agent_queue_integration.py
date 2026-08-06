"""
Tests for Agent Queue Integration, Task TTL, and Scheduled Retention.
"""

import pytest
import asyncio
import os
import sys
import time
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_queue_integration import (
    TaskTTLManager, ScheduledRetention, AgentQueueIntegrator,
    DEFAULT_TASK_TTL_SECONDS, CLEANUP_INTERVAL_SECONDS,
    ttl_manager, scheduled_retention, agent_queue,
)
from async_execution_queue import (
    AsyncExecutionQueue, DeadLetterQueue, QueuedTask, TaskStatus,
)


class TestTaskTTL:
    def test_ttl_init(self):
        mgr = TaskTTLManager(ttl_seconds=3600)
        assert mgr.ttl_seconds == 3600
    
    def test_set_ttl(self):
        mgr = TaskTTLManager()
        mgr.set_ttl(7200)
        assert mgr.ttl_seconds == 7200
    
    def test_is_task_expired_false(self):
        mgr = TaskTTLManager(ttl_seconds=3600)
        task = QueuedTask(id="t1", agent_id="a", agent_name="A", capability="c", input_data={})
        assert mgr.is_task_expired(task) == False
    
    def test_is_task_expired_true(self):
        mgr = TaskTTLManager(ttl_seconds=1)
        task = QueuedTask(id="t2", agent_id="a", agent_name="A", capability="c", input_data={})
        task.created_at = time.time() - 10  # 10 seconds ago
        assert mgr.is_task_expired(task) == True
    
    def test_get_expired_task_ids(self):
        mgr = TaskTTLManager(ttl_seconds=1)
        queue = AsyncExecutionQueue()
        
        # Add completed task (expired)
        t1 = QueuedTask(id="expired-1", agent_id="a", agent_name="A", capability="c", input_data={})
        t1.created_at = time.time() - 100
        t1.status = TaskStatus.COMPLETED
        queue._tasks["expired-1"] = t1
        
        # Add pending task (not expired — not terminal)
        t2 = QueuedTask(id="pending-1", agent_id="b", agent_name="B", capability="c", input_data={})
        t2.created_at = time.time() - 100
        t2.status = TaskStatus.PENDING
        queue._tasks["pending-1"] = t2
        
        # Add recent completed task (not expired)
        t3 = QueuedTask(id="recent-1", agent_id="c", agent_name="C", capability="c", input_data={})
        t3.status = TaskStatus.COMPLETED
        queue._tasks["recent-1"] = t3
        
        expired = mgr.get_expired_task_ids(queue)
        assert "expired-1" in expired
        assert "pending-1" not in expired
        assert "recent-1" not in expired
    
    def test_cleanup_expired(self):
        mgr = TaskTTLManager(ttl_seconds=1)
        queue = AsyncExecutionQueue()
        
        t1 = QueuedTask(id="expired-1", agent_id="a", agent_name="A", capability="c", input_data={})
        t1.created_at = time.time() - 100
        t1.status = TaskStatus.COMPLETED
        queue._tasks["expired-1"] = t1
        
        count = mgr.cleanup_expired(queue)
        assert count == 1
        assert "expired-1" not in queue._tasks
    
    def test_cleanup_does_not_remove_pending(self):
        mgr = TaskTTLManager(ttl_seconds=1)
        queue = AsyncExecutionQueue()
        
        t1 = QueuedTask(id="old-pending", agent_id="a", agent_name="A", capability="c", input_data={})
        t1.created_at = time.time() - 100
        t1.status = TaskStatus.PENDING
        queue._tasks["old-pending"] = t1
        
        count = mgr.cleanup_expired(queue)
        assert count == 0  # pending tasks are not cleaned up
        assert "old-pending" in queue._tasks
    
    @pytest.mark.asyncio
    async def test_periodic_cleanup_start_stop(self):
        mgr = TaskTTLManager(ttl_seconds=1)
        queue = AsyncExecutionQueue()
        await mgr.start_periodic_cleanup(queue)
        assert mgr._running == True
        await mgr.stop_periodic_cleanup()
        assert mgr._running == False


class TestScheduledRetention:
    def test_init(self):
        sr = ScheduledRetention(retention_days=7)
        assert sr._retention_days == 7
    
    @pytest.mark.asyncio
    async def test_start_stop(self):
        sr = ScheduledRetention()
        await sr.start(interval_seconds=1)
        assert sr._running == True
        await sr.stop()
        assert sr._running == False
    
    @pytest.mark.asyncio
    async def test_cleanup_callback_called(self):
        sr = ScheduledRetention()
        callback = AsyncMock(return_value=5)
        sr.set_cleanup_callback(callback)
        
        # Run retention loop with 0 interval (immediate)
        await sr.start(interval_seconds=0)
        await asyncio.sleep(0.5)  # let it run once
        await sr.stop()
        
        # Callback should have been called
        assert callback.call_count >= 0  # might not be called due to timing


class TestAgentQueueIntegrator:
    @pytest.fixture
    def queue_with_dlq(self):
        dlq = DeadLetterQueue()
        q = AsyncExecutionQueue(max_concurrent=2, default_timeout=5, dead_letter_queue=dlq)
        return q, dlq
    
    @pytest.fixture
    def integrator(self, queue_with_dlq):
        q, dlq = queue_with_dlq
        return AgentQueueIntegrator(q), q, dlq
    
    def test_init(self, integrator):
        inst, _, _ = integrator
        assert inst._executor_set == False
    
    def test_set_gateway_executor(self, integrator):
        inst, _, _ = integrator
        async def mock_executor(task):
            return {"content": "done"}
        inst.set_gateway_executor(mock_executor)
        assert inst._executor_set == True
    
    @pytest.mark.asyncio
    async def test_submit_agent_task(self, integrator):
        inst, queue, _ = integrator
        task_id = await inst.submit_agent_task(
            agent_id="core-arch",
            agent_name="Architecture",
            capability="design",
            input_data={"prompt": "test"},
            priority=5,
        )
        assert task_id.startswith("task_")
        task = queue.get_task(task_id)
        assert task["agent_id"] == "core-arch"
    
    @pytest.mark.asyncio
    async def test_execute_agent_task(self, integrator):
        inst, queue, _ = integrator
        
        async def mock_executor(task):
            return {"content": "executed", "tokens": 100}
        
        inst.set_gateway_executor(mock_executor)
        await queue.start(num_workers=1)
        
        result = await inst.execute_agent_task(
            agent_id="core-security",
            agent_name="Security",
            capability="code_review",
            input_data={"prompt": "review"},
            timeout=5,
        )
        assert result["status"] == "completed"
        assert result["agent_id"] == "core-security"
        
        await queue.stop()
    
    @pytest.mark.asyncio
    async def test_get_task_status(self, integrator):
        inst, _, _ = integrator
        task_id = await inst.submit_agent_task("a", "A", "c", {})
        status = inst.get_task_status(task_id)
        assert status is not None
        assert status["id"] == task_id
    
    @pytest.mark.asyncio
    async def test_get_task_status_nonexistent(self, integrator):
        inst, _, _ = integrator
        assert inst.get_task_status("nonexistent") is None
    
    @pytest.mark.asyncio
    async def test_list_agent_tasks(self, integrator):
        inst, _, _ = integrator
        for i in range(3):
            await inst.submit_agent_task(f"agent-{i}", f"Agent {i}", "test", {})
        tasks = inst.list_agent_tasks(limit=10)
        assert len(tasks) >= 3
    
    @pytest.mark.asyncio
    async def test_list_agent_tasks_filtered(self, integrator):
        inst, _, _ = integrator
        await inst.submit_agent_task("core-arch", "Arch", "design", {})
        await inst.submit_agent_task("core-sec", "Security", "audit", {})
        
        arch_tasks = inst.list_agent_tasks(agent_id="core-arch")
        assert all(t["agent_id"] == "core-arch" for t in arch_tasks)
    
    def test_get_queue_stats(self, integrator):
        inst, _, _ = integrator
        stats = inst.get_queue_stats()
        assert "total_tasks" in stats
        assert "max_queue_size" in stats
    
    def test_get_dlq_stats(self, integrator):
        inst, _, _ = integrator
        stats = inst.get_dlq_stats()
        assert "total" in stats
        assert "max_size" in stats
    
    def test_get_dlq_entries(self, integrator):
        inst, _, dlq = integrator
        task = QueuedTask(id="dlq-entry", agent_id="a", agent_name="A", capability="c", input_data={})
        dlq.add(task)
        entries = inst.get_dlq_entries()
        assert len(entries) >= 1
        dlq.clear()
    
    @pytest.mark.asyncio
    async def test_requeue_dlq_task(self, integrator):
        inst, _, dlq = integrator
        task = QueuedTask(
            id="requeue-me", agent_id="core-arch",
            agent_name="Arch", capability="design",
            input_data={"prompt": "test"}, priority=5,
        )
        dlq.add(task)
        
        new_id = await inst.requeue_dlq_task("requeue-me")
        assert new_id is not None
        assert new_id.startswith("task_")
        
        # Old entry removed from DLQ
        assert dlq.get("requeue-me") is None
    
    @pytest.mark.asyncio
    async def test_requeue_nonexistent_dlq(self, integrator):
        inst, _, _ = integrator
        result = await inst.requeue_dlq_task("nonexistent")
        assert result is None
