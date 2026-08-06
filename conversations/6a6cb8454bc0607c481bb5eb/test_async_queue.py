"""
Tests for Async Execution Queue and JSONL Migration.
"""

import pytest
import asyncio
import os
import sys
import json
import time
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from async_execution_queue import (
    AsyncExecutionQueue, QueuedTask, TaskStatus, execution_queue
)


# =========================================================================
# QueuedTask Tests
# =========================================================================

class TestQueuedTask:
    def test_task_creation(self):
        task = QueuedTask(
            id="test-1",
            agent_id="core-security",
            agent_name="Security Agent",
            capability="code_review",
            input_data={"prompt": "test"},
        )
        assert task.id == "test-1"
        assert task.status == TaskStatus.PENDING
        assert task.priority == 0
    
    def test_task_to_dict(self):
        task = QueuedTask(
            id="test-2",
            agent_id="core-arch",
            agent_name="Architecture Agent",
            capability="architecture",
            input_data={"prompt": "design"},
            priority=5,
        )
        d = task.to_dict()
        assert d["id"] == "test-2"
        assert d["agent_id"] == "core-arch"
        assert d["status"] == "pending"
        assert d["priority"] == 5
    
    def test_task_latency(self):
        task = QueuedTask(
            id="test-3", agent_id="a", agent_name="A", capability="c", input_data={},
        )
        assert task.latency_ms == 0
        task.started_at = time.time()
        task.completed_at = task.started_at + 0.5
        assert task.latency_ms > 400  # ~500ms


# =========================================================================
# Async Execution Queue Tests
# =========================================================================

class TestAsyncExecutionQueue:
    @pytest.fixture
    def queue(self):
        return AsyncExecutionQueue(max_concurrent=3, default_timeout=5)
    
    def test_init(self, queue):
        assert queue._max_concurrent == 3
        assert queue._default_timeout == 5
        assert queue._running == False
    
    @pytest.mark.asyncio
    async def test_submit_task(self, queue):
        task_id = await queue.submit(
            agent_id="core-security",
            agent_name="Security",
            capability="code_review",
            input_data={"prompt": "test"},
        )
        assert task_id.startswith("task_")
        assert task_id in queue._tasks
    
    @pytest.mark.asyncio
    async def test_submit_with_priority(self, queue):
        task_id = await queue.submit(
            agent_id="core-arch", agent_name="Arch", capability="design",
            input_data={}, priority=10,
        )
        task = queue._tasks[task_id]
        assert task.priority == 10
    
    @pytest.mark.asyncio
    async def test_start_stop(self, queue):
        await queue.start(num_workers=2)
        assert queue._running == True
        assert len(queue._workers) == 2
        await queue.stop()
        assert queue._running == False
    
    @pytest.mark.asyncio
    async def test_task_execution(self, queue):
        async def mock_executor(task):
            return {"content": "executed", "provider": "mock"}
        
        queue.set_executor(mock_executor)
        await queue.start(num_workers=2)
        
        task_id = await queue.submit(
            agent_id="core-testing", agent_name="Testing", capability="test_gen",
            input_data={"prompt": "write test"},
        )
        
        result = await queue.wait_for_task(task_id, timeout=10)
        assert result["status"] == "completed"
        
        await queue.stop()
    
    @pytest.mark.asyncio
    async def test_task_timeout(self, queue):
        async def slow_executor(task):
            await asyncio.sleep(10)
            return {}
        
        queue.set_executor(slow_executor)
        await queue.start(num_workers=1)
        
        task_id = await queue.submit(
            agent_id="core-arch", agent_name="Arch", capability="design",
            input_data={}, timeout=1,  # 1 second timeout
        )
        
        result = await queue.wait_for_task(task_id, timeout=5)
        assert result["status"] == "timeout"
        
        await queue.stop()
    
    @pytest.mark.asyncio
    async def test_task_failure(self, queue):
        async def failing_executor(task):
            raise RuntimeError("Execution failed")
        
        queue.set_executor(failing_executor)
        await queue.start(num_workers=1)
        
        task_id = await queue.submit(
            agent_id="core-devops", agent_name="DevOps", capability="deploy",
            input_data={},
        )
        
        result = await queue.wait_for_task(task_id, timeout=5)
        assert result["status"] == "failed"
        assert "Execution failed" in result.get("error", "")
        
        await queue.stop()
    
    @pytest.mark.asyncio
    async def test_submit_and_wait(self, queue):
        async def mock_executor(task):
            return {"content": "result"}
        
        queue.set_executor(mock_executor)
        await queue.start(num_workers=1)
        
        result = await queue.submit_and_wait(
            agent_id="core-docs", agent_name="Docs", capability="documentation",
            input_data={"prompt": "document"},
        )
        assert result["status"] == "completed"
        
        await queue.stop()
    
    @pytest.mark.asyncio
    async def test_cancel_pending_task(self, queue):
        task_id = await queue.submit(
            agent_id="core-planning", agent_name="Planning", capability="plan",
            input_data={},
        )
        cancelled = await queue.cancel_task(task_id)
        assert cancelled == True
        assert queue._tasks[task_id].status == TaskStatus.CANCELLED
    
    @pytest.mark.asyncio
    async def test_cancel_running_task_fails(self, queue):
        async def mock_executor(task):
            await asyncio.sleep(5)
            return {}
        
        queue.set_executor(mock_executor)
        await queue.start(num_workers=1)
        
        task_id = await queue.submit(
            agent_id="core-perf", agent_name="Perf", capability="optimize",
            input_data={},
        )
        await asyncio.sleep(0.5)  # let task start
        cancelled = await queue.cancel_task(task_id)
        assert cancelled == False  # can't cancel running task
        
        await queue.stop()
    
    @pytest.mark.asyncio
    async def test_get_task(self, queue):
        task_id = await queue.submit(
            agent_id="core-api", agent_name="API", capability="api_design",
            input_data={},
        )
        task = queue.get_task(task_id)
        assert task is not None
        assert task["id"] == task_id
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_task(self, queue):
        assert queue.get_task("nonexistent") is None
    
    @pytest.mark.asyncio
    async def test_list_tasks(self, queue):
        for i in range(5):
            await queue.submit(
                agent_id=f"agent-{i}", agent_name=f"Agent {i}",
                capability="test", input_data={},
            )
        tasks = queue.list_tasks(limit=10)
        assert len(tasks) == 5
    
    @pytest.mark.asyncio
    async def test_list_tasks_by_status(self, queue):
        async def mock_executor(task):
            return {"content": "done"}
        
        queue.set_executor(mock_executor)
        await queue.start(num_workers=1)
        
        t1 = await queue.submit("a1", "A1", "c", {})
        t2 = await queue.submit("a2", "A2", "c", {})
        await queue.wait_for_task(t1, timeout=5)
        await queue.wait_for_task(t2, timeout=5)
        
        completed = queue.list_tasks(status="completed")
        assert len(completed) >= 2
        
        pending = queue.list_tasks(status="pending")
        assert len(pending) == 0
        
        await queue.stop()
    
    @pytest.mark.asyncio
    async def test_stats(self, queue):
        async def mock_executor(task):
            return {"content": "done"}
        
        queue.set_executor(mock_executor)
        await queue.start(num_workers=1)
        
        for i in range(3):
            await queue.submit(f"agent-{i}", f"Agent {i}", "test", {})
        
        await asyncio.sleep(1)
        stats = queue.stats()
        assert stats["total_tasks"] >= 3
        assert stats["max_concurrent"] == 3
        
        await queue.stop()
    
    @pytest.mark.asyncio
    async def test_cancel_all(self, queue):
        for i in range(5):
            await queue.submit(f"a{i}", f"A{i}", "c", {})
        cancelled = await queue.cancel_all()
        assert cancelled == 5
    
    @pytest.mark.asyncio
    async def test_priority_ordering(self, queue):
        async def mock_executor(task):
            return {"content": task.id}
        
        queue.set_executor(mock_executor)
        await queue.start(num_workers=1)
        
        # Submit low priority first, then high priority
        low_id = await queue.submit("a1", "A1", "c", {}, priority=1)
        high_id = await queue.submit("a2", "A2", "c", {}, priority=10)
        
        await asyncio.sleep(2)
        
        # High priority should complete first
        high_task = queue._tasks[high_id]
        low_task = queue._tasks[low_id]
        
        # Both should be completed
        assert high_task.status == TaskStatus.COMPLETED
        
        await queue.stop()
    
    @pytest.mark.asyncio
    async def test_no_executor_raises(self, queue):
        await queue.start(num_workers=1)
        task_id = await queue.submit("a", "A", "c", {})
        result = await queue.wait_for_task(task_id, timeout=5)
        assert result["status"] == "failed"
        await queue.stop()


# =========================================================================
# Migration Script Tests
# =========================================================================

class TestJSONLMigration:
    @pytest.mark.asyncio
    async def test_migrate_empty_file(self, tmp_path):
        from migrate_jsonl_to_pg import migrate_jsonl_to_postgres
        path = str(tmp_path / "empty.jsonl")
        with open(path, 'w') as f:
            pass  # empty file
        
        mock_pg = AsyncMock()
        mock_pg.is_connected = True
        mock_pg.record = AsyncMock(return_value=True)
        
        stats = await migrate_jsonl_to_postgres(path, mock_pg)
        assert stats["migrated"] == 0
        assert stats["total_read"] == 0
    
    @pytest.mark.asyncio
    async def test_migrate_nonexistent_file(self):
        from migrate_jsonl_to_pg import migrate_jsonl_to_postgres
        mock_pg = AsyncMock()
        mock_pg.is_connected = True
        
        stats = await migrate_jsonl_to_postgres("/nonexistent/path.jsonl", mock_pg)
        assert stats["migrated"] == 0
    
    @pytest.mark.asyncio
    async def test_migrate_valid_records(self, tmp_path):
        from migrate_jsonl_to_pg import migrate_jsonl_to_postgres
        path = str(tmp_path / "test.jsonl")
        with open(path, 'w') as f:
            for i in range(5):
                f.write(json.dumps({
                    "execution_id": f"exec-{i}",
                    "status": "completed",
                    "agent_id": f"core-{i}",
                }) + "\n")
        
        mock_pg = AsyncMock()
        mock_pg.is_connected = True
        mock_pg.record = AsyncMock(return_value=True)
        
        stats = await migrate_jsonl_to_postgres(path, mock_pg)
        assert stats["migrated"] == 5
        assert stats["errors"] == 0
    
    @pytest.mark.asyncio
    async def test_migrate_with_errors(self, tmp_path):
        from migrate_jsonl_to_pg import migrate_jsonl_to_postgres
        path = str(tmp_path / "mixed.jsonl")
        with open(path, 'w') as f:
            f.write(json.dumps({"execution_id": "1", "status": "completed"}) + "\n")
            f.write("INVALID JSON\n")
            f.write(json.dumps({"execution_id": "2", "status": "failed"}) + "\n")
        
        mock_pg = AsyncMock()
        mock_pg.is_connected = True
        mock_pg.record = AsyncMock(return_value=True)
        
        stats = await migrate_jsonl_to_postgres(path, mock_pg)
        assert stats["migrated"] == 2
        assert stats["errors"] == 1
    
    @pytest.mark.asyncio
    async def test_migrate_pg_not_connected(self, tmp_path):
        from migrate_jsonl_to_pg import migrate_jsonl_to_postgres
        path = str(tmp_path / "test.jsonl")
        with open(path, 'w') as f:
            f.write(json.dumps({"execution_id": "1", "status": "completed"}) + "\n")
        
        mock_pg = AsyncMock()
        mock_pg.is_connected = False
        mock_pg.connect = AsyncMock(return_value=False)
        
        stats = await migrate_jsonl_to_postgres(path, mock_pg)
        assert "error" in stats
