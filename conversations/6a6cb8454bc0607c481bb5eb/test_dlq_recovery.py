"""
Tests for Dead Letter Queue and Task Recovery.
"""

import pytest
import asyncio
import os
import sys
import time
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from async_execution_queue import (
    AsyncExecutionQueue, QueuedTask, TaskStatus, DeadLetterQueue,
    dead_letter_queue, execution_queue,
)


class TestDeadLetterQueue:
    @pytest.fixture
    def dlq(self):
        return DeadLetterQueue(max_size=10)
    
    @pytest.fixture
    def queue(self, dlq):
        return AsyncExecutionQueue(max_concurrent=1, default_timeout=5, dead_letter_queue=dlq)
    
    def test_dlq_init(self, dlq):
        assert dlq._max_size == 10
        assert len(dlq._tasks) == 0
    
    def test_dlq_add(self, dlq):
        task = QueuedTask(id="t1", agent_id="a", agent_name="A", capability="c", input_data={})
        task.error = "permanent failure"
        dlq.add(task)
        assert len(dlq._tasks) == 1
        assert dlq._tasks[0]["id"] == "t1"
        assert dlq._tasks[0]["error"] == "permanent failure"
    
    def test_dlq_list(self, dlq):
        for i in range(5):
            task = QueuedTask(id=f"t{i}", agent_id="a", agent_name="A", capability="c", input_data={})
            dlq.add(task)
        entries = dlq.list(limit=3)
        assert len(entries) == 3
        # Most recent first
        assert entries[0]["id"] == "t4"
    
    def test_dlq_get(self, dlq):
        task = QueuedTask(id="get-me", agent_id="a", agent_name="A", capability="c", input_data={})
        dlq.add(task)
        entry = dlq.get("get-me")
        assert entry is not None
        assert entry["id"] == "get-me"
        assert dlq.get("nonexistent") is None
    
    def test_dlq_remove(self, dlq):
        task = QueuedTask(id="remove-me", agent_id="a", agent_name="A", capability="c", input_data={})
        dlq.add(task)
        assert dlq.remove("remove-me") == True
        assert len(dlq._tasks) == 0
        assert dlq.remove("nonexistent") == False
    
    def test_dlq_clear(self, dlq):
        for i in range(3):
            task = QueuedTask(id=f"t{i}", agent_id="a", agent_name="A", capability="c", input_data={})
            dlq.add(task)
        cleared = dlq.clear()
        assert cleared == 3
        assert len(dlq._tasks) == 0
    
    def test_dlq_max_size(self, dlq):
        for i in range(15):
            task = QueuedTask(id=f"t{i}", agent_id="a", agent_name="A", capability="c", input_data={})
            dlq.add(task)
        # Should keep last 10 (ring buffer)
        assert len(dlq._tasks) == 10
        assert dlq._tasks[0]["id"] == "t5"
    
    def test_dlq_stats(self, dlq):
        task = QueuedTask(id="t1", agent_id="a", agent_name="A", capability="c", input_data={})
        dlq.add(task)
        stats = dlq.stats()
        assert stats["total"] == 1
        assert stats["max_size"] == 10
    
    @pytest.mark.asyncio
    async def test_failed_task_goes_to_dlq(self, queue, dlq):
        async def always_fail(task):
            raise RuntimeError("Permanent error")
        
        queue.set_executor(always_fail)
        await queue.start(num_workers=1)
        
        task_id = await queue.submit("a", "A", "c", {}, max_retries=1, timeout=5)
        result = await queue.wait_for_task(task_id, timeout=15)
        
        assert result["status"] == "failed"
        assert len(dlq._tasks) == 1
        assert dlq._tasks[0]["id"] == task_id
        
        await queue.stop()
    
    @pytest.mark.asyncio
    async def test_completed_task_not_in_dlq(self, queue, dlq):
        async def success(task):
            return {"content": "done"}
        
        queue.set_executor(success)
        await queue.start(num_workers=1)
        
        task_id = await queue.submit("a", "A", "c", {})
        await queue.wait_for_task(task_id, timeout=5)
        
        assert len(dlq._tasks) == 0
        
        await queue.stop()


class TestTaskRecovery:
    @pytest.fixture
    def queue(self):
        dlq = DeadLetterQueue()
        return AsyncExecutionQueue(max_concurrent=2, default_timeout=10, dead_letter_queue=dlq)
    
    @pytest.mark.asyncio
    async def test_recover_pending_tasks(self, queue):
        async def mock_executor(task):
            return {"content": "recovered"}
        
        queue.set_executor(mock_executor)
        
        # Simulate persisted pending tasks
        persisted = [
            {"id": "rec-1", "agent_id": "core-arch", "agent_name": "Architecture", "capability": "design",
             "input_data": {"prompt": "test"}, "status": "pending", "priority": 0},
            {"id": "rec-2", "agent_id": "core-security", "agent_name": "Security", "capability": "audit",
             "input_data": {"prompt": "scan"}, "status": "pending", "priority": 5},
        ]
        
        recovered = await queue.recover_from_persistence(persisted)
        assert recovered == 2
        
        await queue.start(num_workers=2)
        
        r1 = await queue.wait_for_task("rec-1", timeout=10)
        r2 = await queue.wait_for_task("rec-2", timeout=10)
        
        assert r1["status"] == "completed"
        assert r2["status"] == "completed"
        
        await queue.stop()
    
    @pytest.mark.asyncio
    async def test_recover_skips_non_pending(self, queue):
        persisted = [
            {"id": "skip-1", "agent_id": "a", "agent_name": "A", "capability": "c",
             "input_data": {}, "status": "completed"},
            {"id": "skip-2", "agent_id": "b", "agent_name": "B", "capability": "c",
             "input_data": {}, "status": "failed"},
            {"id": "skip-3", "agent_id": "c", "agent_name": "C", "capability": "c",
             "input_data": {}, "status": "pending"},
        ]
        
        recovered = await queue.recover_from_persistence(persisted)
        assert recovered == 1  # only the pending one
    
    @pytest.mark.asyncio
    async def test_recover_empty_list(self, queue):
        recovered = await queue.recover_from_persistence([])
        assert recovered == 0
    
    @pytest.mark.asyncio
    async def test_recover_queue_full(self):
        dlq = DeadLetterQueue()
        q = AsyncExecutionQueue(max_concurrent=1, default_timeout=5, max_queue_size=2, dead_letter_queue=dlq)
        
        # Fill queue with pending tasks
        persisted = [
            {"id": f"r{i}", "agent_id": "a", "agent_name": "A", "capability": "c",
             "input_data": {}, "status": "pending"}
            for i in range(5)
        ]
        
        recovered = await q.recover_from_persistence(persisted)
        assert recovered == 2  # only 2 fit (max_queue_size=2)
    
    @pytest.mark.asyncio
    async def test_recover_preserves_retry_count(self, queue):
        persisted = [
            {"id": "rec-retry", "agent_id": "a", "agent_name": "A", "capability": "c",
             "input_data": {}, "status": "pending", "retry_count": 1, "max_retries": 3},
        ]
        
        recovered = await queue.recover_from_persistence(persisted)
        assert recovered == 1
        task = queue._tasks["rec-retry"]
        assert task.retry_count == 1
    
    def test_get_dlq(self, queue):
        dlq = queue.get_dlq()
        assert dlq is not None
        assert isinstance(dlq, DeadLetterQueue)
