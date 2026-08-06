"""
Tests for Async Execution Queue v2.0: Retry, Backpressure, Persistence.
"""

import pytest
import asyncio
import os
import sys
import time
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from async_execution_queue import (
    AsyncExecutionQueue, QueuedTask, TaskStatus, DEFAULT_MAX_QUEUE_SIZE,
)


class TestRetryMechanism:
    @pytest.fixture
    def queue(self):
        return AsyncExecutionQueue(max_concurrent=1, default_timeout=5, max_queue_size=100)

    @pytest.mark.asyncio
    async def test_retry_on_failure(self, queue):
        call_count = 0
        async def flaky_executor(task):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RuntimeError("Transient failure")
            return {"content": "succeeded on retry"}

        queue.set_executor(flaky_executor)
        await queue.start(num_workers=1)

        task_id = await queue.submit(
            "core-test", "Test", "flaky", {}, max_retries=2, timeout=5,
        )
        result = await queue.wait_for_task(task_id, timeout=15)
        assert result["status"] == "completed"
        assert call_count == 2
        assert queue._total_retried == 1

        await queue.stop()

    @pytest.mark.asyncio
    async def test_max_retries_exhausted(self, queue):
        async def always_fail(task):
            raise RuntimeError("Permanent failure")

        queue.set_executor(always_fail)
        await queue.start(num_workers=1)

        task_id = await queue.submit(
            "core-test", "Test", "fail", {}, max_retries=2, timeout=5,
        )
        result = await queue.wait_for_task(task_id, timeout=15)
        assert result["status"] == "failed"
        assert result["retry_count"] == 2

        await queue.stop()

    @pytest.mark.asyncio
    async def test_no_retries_by_default(self, queue):
        async def always_fail(task):
            raise RuntimeError("Immediate fail")

        queue.set_executor(always_fail)
        await queue.start(num_workers=1)

        task_id = await queue.submit(
            "core-test", "Test", "fail", {}, max_retries=0, timeout=5,
        )
        result = await queue.wait_for_task(task_id, timeout=10)
        assert result["status"] == "failed"
        assert result["retry_count"] == 0

        await queue.stop()

    @pytest.mark.asyncio
    async def test_timeout_no_retry(self, queue):
        async def slow_executor(task):
            await asyncio.sleep(10)
            return {}

        queue.set_executor(slow_executor)
        await queue.start(num_workers=1)

        task_id = await queue.submit(
            "core-test", "Test", "slow", {}, max_retries=3, timeout=1,
        )
        result = await queue.wait_for_task(task_id, timeout=10)
        assert result["status"] == "timeout"
        assert result["retry_count"] == 0  # timeouts don't retry

        await queue.stop()

    @pytest.mark.asyncio
    async def test_retry_count_in_to_dict(self, queue):
        async def always_fail(task):
            raise RuntimeError("fail")

        queue.set_executor(always_fail)
        await queue.start(num_workers=1)

        task_id = await queue.submit("a", "A", "c", {}, max_retries=1, timeout=5)
        result = await queue.wait_for_task(task_id, timeout=10)
        assert "retry_count" in result
        assert "max_retries" in result

        await queue.stop()


class TestBackpressure:
    @pytest.fixture
    def queue(self):
        return AsyncExecutionQueue(max_concurrent=1, default_timeout=5, max_queue_size=3)

    @pytest.mark.asyncio
    async def test_queue_full_rejects(self, queue):
        async def slow_executor(task):
            await asyncio.sleep(5)
            return {}

        queue.set_executor(slow_executor)
        await queue.start(num_workers=1)

        # Fill the queue
        ids = []
        for i in range(3):
            tid = await queue.submit(f"a{i}", f"A{i}", "c", {})
            ids.append(tid)

        # Next submit should be rejected
        with pytest.raises(asyncio.QueueFull):
            await queue.submit("rejected", "R", "c", {})

        assert queue._total_rejected == 1
        await queue.stop()

    @pytest.mark.asyncio
    async def test_backpressure_in_stats(self, queue):
        async def slow_executor(task):
            await asyncio.sleep(5)
            return {}

        queue.set_executor(slow_executor)
        await queue.start(num_workers=1)

        for i in range(3):
            await queue.submit(f"a{i}", f"A{i}", "c", {})

        try:
            await queue.submit("reject", "R", "c", {})
        except asyncio.QueueFull:
            pass

        stats = queue.stats()
        assert "max_queue_size" in stats
        assert stats["max_queue_size"] == 3
        assert stats["rejected"] == 1

        await queue.stop()

    def test_max_queue_size_default(self):
        q = AsyncExecutionQueue()
        assert q._max_queue_size == DEFAULT_MAX_QUEUE_SIZE


class TestPersistence:
    @pytest.fixture
    def queue(self):
        return AsyncExecutionQueue(max_concurrent=1, default_timeout=5)

    @pytest.mark.asyncio
    async def test_persistence_callback_on_submit(self, queue):
        callback = AsyncMock()
        queue.set_persistence_callback(callback)

        async def mock_executor(task):
            return {"content": "done"}

        queue.set_executor(mock_executor)
        await queue.start(num_workers=1)

        task_id = await queue.submit("a", "A", "c", {})
        await queue.wait_for_task(task_id, timeout=5)

        # Should be called at least twice: on submit and on completion
        assert callback.call_count >= 2

        await queue.stop()

    @pytest.mark.asyncio
    async def test_persistence_callback_failure_handled(self, queue):
        callback = AsyncMock(side_effect=Exception("DB down"))
        queue.set_persistence_callback(callback)

        async def mock_executor(task):
            return {"content": "done"}

        queue.set_executor(mock_executor)
        await queue.start(num_workers=1)

        # Should not raise even if persistence fails
        task_id = await queue.submit("a", "A", "c", {})
        result = await queue.wait_for_task(task_id, timeout=5)
        assert result["status"] == "completed"

        await queue.stop()

    @pytest.mark.asyncio
    async def test_to_persist_dict(self, queue):
        async def mock_executor(task):
            return {"content": "result"}

        queue.set_executor(mock_executor)
        await queue.start(num_workers=1)

        task_id = await queue.submit("core-arch", "Architecture Agent", "design", {"prompt": "test"})
        await queue.wait_for_task(task_id, timeout=5)

        task = queue._tasks[task_id]
        persist_dict = task.to_persist_dict()
        assert persist_dict["agent_id"] == "core-arch"
        assert persist_dict["status"] == "completed"
        assert persist_dict["output_data"] == {"content": "result"}
        assert "latency_ms" in persist_dict

        await queue.stop()

    @pytest.mark.asyncio
    async def test_no_persistence_callback(self, queue):
        async def mock_executor(task):
            return {"content": "done"}

        queue.set_executor(mock_executor)
        await queue.start(num_workers=1)

        task_id = await queue.submit("a", "A", "c", {})
        result = await queue.wait_for_task(task_id, timeout=5)
        assert result["status"] == "completed"

        await queue.stop()
