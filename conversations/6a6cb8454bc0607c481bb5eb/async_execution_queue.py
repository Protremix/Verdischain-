"""
EvolvixOS Async Queue-Based Execution Engine v2.0
Replaces synchronous await-based execution with a task queue for better
scalability and resource management under high load.

v2.0 additions:
- Task persistence (callback-based for PostgreSQL or other durable storage)
- Retry with exponential backoff (configurable max_retries per task)
- Backpressure (max queue size, rejects when full)
"""

import asyncio
import time
import json
import os
import hashlib
from typing import Dict, List, Optional, Any, Callable, Awaitable
from datetime import datetime, timezone
from collections import defaultdict
from enum import Enum
from dataclasses import dataclass, field
import structlog

logger = structlog.get_logger()

DEFAULT_MAX_QUEUE_SIZE = 1000


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class QueuedTask:
    id: str
    agent_id: str
    agent_name: str
    capability: str
    input_data: Dict[str, Any]
    options: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    timeout_seconds: int = 120
    max_retries: int = 2
    retry_count: int = 0
    retry_delay: float = 1.0

    @property
    def latency_ms(self) -> float:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at) * 1000
        return 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "capability": self.capability,
            "status": self.status.value,
            "priority": self.priority,
            "latency_ms": self.latency_ms,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "created_at": datetime.fromtimestamp(self.created_at, tz=timezone.utc).isoformat(),
            "started_at": datetime.fromtimestamp(self.started_at, tz=timezone.utc).isoformat() if self.started_at else None,
            "completed_at": datetime.fromtimestamp(self.completed_at, tz=timezone.utc).isoformat() if self.completed_at else None,
            "error": self.error,
        }

    def to_persist_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "capability": self.capability,
            "input_data": self.input_data,
            "output_data": self.result or {},
            "error": self.error or "",
            "latency_ms": self.latency_ms,
            "retry_count": self.retry_count,
            "created_at": datetime.fromtimestamp(self.created_at, tz=timezone.utc).isoformat(),
        }


class AsyncExecutionQueue:
    def __init__(self, max_concurrent: int = 5, default_timeout: int = 120,
                 max_queue_size: int = DEFAULT_MAX_QUEUE_SIZE,
                 dead_letter_queue: 'DeadLetterQueue' = None):
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=max_queue_size)
        self._max_concurrent = max_concurrent
        self._default_timeout = default_timeout
        self._max_queue_size = max_queue_size
        self._tasks: Dict[str, QueuedTask] = {}
        self._workers: List[asyncio.Task] = []
        self._running = False
        self._total_completed = 0
        self._total_failed = 0
        self._total_timeout = 0
        self._total_cancelled = 0
        self._total_retried = 0
        self._total_rejected = 0
        self._task_counter = 0
        self._executor: Optional[Callable] = None
        self._persistence_callback: Optional[Callable] = None
        self._dlq = dead_letter_queue

    def set_executor(self, executor: Callable[[QueuedTask], Awaitable[Dict[str, Any]]]):
        self._executor = executor

    def set_persistence_callback(self, callback: Callable[[Dict], Awaitable[None]]):
        self._persistence_callback = callback

    async def submit(self, agent_id: str, agent_name: str, capability: str,
                     input_data: Dict[str, Any], options: Dict[str, Any] = None,
                     priority: int = 0, timeout: int = None,
                     max_retries: int = 2) -> str:
        if self._queue.qsize() >= self._max_queue_size:
            self._total_rejected += 1
            raise asyncio.QueueFull(f"Queue is full ({self._max_queue_size}). Backpressure active.")

        self._task_counter += 1
        task_id = f"task_{int(time.time() * 1000)}_{self._task_counter}"

        task = QueuedTask(
            id=task_id,
            agent_id=agent_id,
            agent_name=agent_name,
            capability=capability,
            input_data=input_data,
            options=options or {},
            priority=priority,
            timeout_seconds=timeout or self._default_timeout,
            max_retries=max_retries,
        )

        self._tasks[task_id] = task
        await self._queue.put((-task.priority, time.time(), task))

        if self._persistence_callback:
            try:
                await self._persistence_callback(task.to_persist_dict())
            except Exception as e:
                logger.warning(f"Task persistence failed for {task_id}: {e}")

        logger.info(f"Task submitted: {task_id} (agent: {agent_id}, priority: {priority}, queue: {self._queue.qsize()}/{self._max_queue_size})")
        return task_id

    async def submit_and_wait(self, agent_id: str, agent_name: str, capability: str,
                               input_data: Dict[str, Any], options: Dict[str, Any] = None,
                               priority: int = 0, timeout: int = None,
                               max_retries: int = 2) -> Dict[str, Any]:
        task_id = await self.submit(agent_id, agent_name, capability, input_data, options, priority, timeout, max_retries)
        return await self.wait_for_task(task_id)

    async def wait_for_task(self, task_id: str, timeout: int = 300) -> Dict[str, Any]:
        deadline = time.time() + timeout
        while time.time() < deadline:
            task = self._tasks.get(task_id)
            if not task:
                return {"error": f"Task not found: {task_id}"}
            if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.TIMEOUT, TaskStatus.CANCELLED):
                return task.to_dict()
            await asyncio.sleep(0.1)
        return {"error": f"Task {task_id} did not complete within {timeout}s"}

    async def start(self, num_workers: int = None):
        if self._running:
            return
        self._running = True
        num_workers = num_workers or self._max_concurrent
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker_loop(i))
            self._workers.append(worker)
        logger.info(f"Execution queue started with {num_workers} workers (max_queue: {self._max_queue_size})")

    async def stop(self):
        self._running = False
        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        logger.info("Execution queue stopped")

    async def _worker_loop(self, worker_id: int):
        logger.info(f"Worker {worker_id} started")
        while self._running:
            try:
                priority, timestamp, task = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            await self._execute_task(task)
            self._queue.task_done()
        logger.info(f"Worker {worker_id} stopped")

    async def _execute_task(self, task: QueuedTask):
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()

        try:
            if not self._executor:
                raise RuntimeError("No executor set")

            result = await asyncio.wait_for(
                self._executor(task),
                timeout=task.timeout_seconds,
            )
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            self._total_completed += 1
            logger.info(f"Task {task.id} completed in {task.latency_ms:.0f}ms")

        except asyncio.TimeoutError:
            task.error = f"Task exceeded {task.timeout_seconds}s timeout"
            await self._handle_failure(task, is_timeout=True)

        except asyncio.CancelledError:
            task.status = TaskStatus.CANCELLED
            task.completed_at = time.time()
            self._total_cancelled += 1

        except Exception as e:
            task.error = str(e)
            await self._handle_failure(task, is_timeout=False)

        if self._persistence_callback:
            try:
                await self._persistence_callback(task.to_persist_dict())
            except Exception as e:
                logger.warning(f"Task persistence failed for {task.id}: {e}")

    async def _handle_failure(self, task: QueuedTask, is_timeout: bool):
        if task.retry_count < task.max_retries and not is_timeout:
            task.retry_count += 1
            backoff_delay = task.retry_delay * (2 ** (task.retry_count - 1))
            self._total_retried += 1
            logger.info(f"Task {task.id} retrying ({task.retry_count}/{task.max_retries}) after {backoff_delay:.1f}s backoff")

            await asyncio.sleep(backoff_delay)
            task.status = TaskStatus.PENDING
            task.started_at = None
            task.error = None
            await self._queue.put((-task.priority, time.time(), task))
        else:
            if is_timeout:
                task.status = TaskStatus.TIMEOUT
                self._total_timeout += 1
                logger.warning(f"Task {task.id} timed out (retries: {task.retry_count})")
            else:
                task.status = TaskStatus.FAILED
                self._total_failed += 1
                logger.error(f"Task {task.id} failed after {task.retry_count} retries: {task.error}")
            task.completed_at = time.time()
            # Move permanently failed tasks to dead letter queue
            if self._dlq:
                self._dlq.add(task)

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        task = self._tasks.get(task_id)
        return task.to_dict() if task else None

    def list_tasks(self, limit: int = 50, status: str = None) -> List[Dict[str, Any]]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status.value == status]
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return [t.to_dict() for t in tasks[:limit]]

    def stats(self) -> Dict[str, Any]:
        by_status = defaultdict(int)
        for task in self._tasks.values():
            by_status[task.status.value] += 1

        avg_latency = 0
        completed = [t for t in self._tasks.values() if t.status == TaskStatus.COMPLETED]
        if completed:
            avg_latency = sum(t.latency_ms for t in completed) / len(completed)

        return {
            "running": self._running,
            "queue_size": self._queue.qsize(),
            "max_queue_size": self._max_queue_size,
            "max_concurrent": self._max_concurrent,
            "total_tasks": len(self._tasks),
            "completed": self._total_completed,
            "failed": self._total_failed,
            "timeout": self._total_timeout,
            "cancelled": self._total_cancelled,
            "retried": self._total_retried,
            "rejected": self._total_rejected,
            "by_status": dict(by_status),
            "avg_latency_ms": avg_latency,
        }

    async def cancel_task(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            task.completed_at = time.time()
            self._total_cancelled += 1
            return True
        return False

    async def cancel_all(self) -> int:
        cancelled = 0
        for task in self._tasks.values():
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                task.completed_at = time.time()
                self._total_cancelled += 1
                cancelled += 1
        return cancelled
    
    async def recover_from_persistence(self, persisted_tasks: List[Dict[str, Any]]) -> int:
        """Re-queue pending tasks from persistent storage on startup.
        
        Args:
            persisted_tasks: List of task dicts from PG with status='pending'
        
        Returns:
            Number of tasks recovered
        """
        recovered = 0
        for pt in persisted_tasks:
            if pt.get("status") != "pending":
                continue
            
            task_id = pt.get("id", f"recovered_{int(time.time()*1000)}_{recovered}")
            
            task = QueuedTask(
                id=task_id,
                agent_id=pt.get("agent_id", "unknown"),
                agent_name=pt.get("agent_name", "Unknown"),
                capability=pt.get("capability", "unknown"),
                input_data=pt.get("input_data", {}) if isinstance(pt.get("input_data"), dict) else {},
                priority=pt.get("priority", 0),
                timeout_seconds=self._default_timeout,
                max_retries=pt.get("max_retries", 2),
                retry_count=pt.get("retry_count", 0),
            )
            
            self._tasks[task_id] = task
            try:
                self._queue.put_nowait((-task.priority, time.time(), task))
                recovered += 1
            except asyncio.QueueFull:
                logger.warning(f"Queue full, cannot recover task {task_id}")
                break
        
        logger.info(f"Recovered {recovered} pending tasks from persistence")
        return recovered
    
    def get_dlq(self) -> Optional['DeadLetterQueue']:
        """Get the dead letter queue instance."""
        return self._dlq


class DeadLetterQueue:
    """Stores tasks that failed permanently (all retries exhausted)."""
    
    def __init__(self, max_size: int = 500):
        self._tasks: List[Dict[str, Any]] = []
        self._max_size = max_size
    
    def add(self, task: QueuedTask):
        """Add a permanently failed task to the DLQ."""
        entry = task.to_dict()
        entry["error"] = task.error
        entry["dlq_timestamp"] = datetime.now(timezone.utc).isoformat()
        self._tasks.append(entry)
        # Enforce max size (ring buffer)
        if len(self._tasks) > self._max_size:
            self._tasks = self._tasks[-self._max_size:]
        logger.warning(f"Task {task.id} moved to DLQ (retries: {task.retry_count})")
    
    def list(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List DLQ entries."""
        return list(reversed(self._tasks))[:limit]
    
    def get(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific DLQ entry."""
        for entry in self._tasks:
            if entry.get("id") == task_id:
                return entry
        return None
    
    def remove(self, task_id: str) -> bool:
        """Remove an entry from the DLQ."""
        for i, entry in enumerate(self._tasks):
            if entry.get("id") == task_id:
                self._tasks.pop(i)
                return True
        return False
    
    def clear(self) -> int:
        """Clear all DLQ entries. Returns count cleared."""
        count = len(self._tasks)
        self._tasks.clear()
        return count
    
    def stats(self) -> Dict[str, Any]:
        return {
            "total": len(self._tasks),
            "max_size": self._max_size,
        }


dead_letter_queue = DeadLetterQueue()
execution_queue = AsyncExecutionQueue(max_concurrent=5, default_timeout=120, dead_letter_queue=dead_letter_queue)
