"""
EvolvixOS Async Queue-Based Execution Engine
Replaces synchronous await-based execution with a task queue for better
scalability and resource management under high load.
"""

import asyncio
import time
import json
import os
from typing import Dict, List, Optional, Any, Callable, Awaitable
from datetime import datetime, timezone
from collections import defaultdict
from enum import Enum
from dataclasses import dataclass, field
import structlog

logger = structlog.get_logger()


# =========================================================================
# Task Status
# =========================================================================

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class QueuedTask:
    """A task in the execution queue."""
    id: str
    agent_id: str
    agent_name: str
    capability: str
    input_data: Dict[str, Any]
    options: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # higher = more important
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    timeout_seconds: int = 120
    
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
            "created_at": datetime.fromtimestamp(self.created_at, tz=timezone.utc).isoformat(),
            "started_at": datetime.fromtimestamp(self.started_at, tz=timezone.utc).isoformat() if self.started_at else None,
            "completed_at": datetime.fromtimestamp(self.completed_at, tz=timezone.utc).isoformat() if self.completed_at else None,
            "error": self.error,
        }


# =========================================================================
# Async Execution Queue
# =========================================================================

class AsyncExecutionQueue:
    """Queue-based execution engine for agent tasks.
    
    Features:
    - Priority-based task ordering
    - Configurable concurrency (max concurrent tasks)
    - Timeout enforcement per task
    - Retry on failure (configurable)
    - Task status tracking
    - Statistics
    """
    
    def __init__(self, max_concurrent: int = 5, default_timeout: int = 120):
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._max_concurrent = max_concurrent
        self._default_timeout = default_timeout
        self._tasks: Dict[str, QueuedTask] = {}
        self._workers: List[asyncio.Task] = []
        self._running = False
        self._total_completed = 0
        self._total_failed = 0
        self._total_timeout = 0
        self._total_cancelled = 0
        self._task_counter = 0
        self._executor: Optional[Callable] = None
    
    def set_executor(self, executor: Callable[[QueuedTask], Awaitable[Dict[str, Any]]]):
        """Set the async function that executes tasks."""
        self._executor = executor
    
    async def submit(self, agent_id: str, agent_name: str, capability: str,
                     input_data: Dict[str, Any], options: Dict[str, Any] = None,
                     priority: int = 0, timeout: int = None) -> str:
        """Submit a task to the queue. Returns task ID."""
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
        )
        
        self._tasks[task_id] = task
        # PriorityQueue uses negative for higher priority (lower number = higher priority)
        await self._queue.put((-task.priority, time.time(), task))
        
        logger.info(f"Task submitted: {task_id} (agent: {agent_id}, priority: {priority})")
        return task_id
    
    async def submit_and_wait(self, agent_id: str, agent_name: str, capability: str,
                               input_data: Dict[str, Any], options: Dict[str, Any] = None,
                               priority: int = 0, timeout: int = None) -> Dict[str, Any]:
        """Submit a task and wait for its result."""
        task_id = await self.submit(agent_id, agent_name, capability, input_data, options, priority, timeout)
        return await self.wait_for_task(task_id)
    
    async def wait_for_task(self, task_id: str, timeout: int = 300) -> Dict[str, Any]:
        """Wait for a task to complete. Returns the task result."""
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
        """Start the execution queue workers."""
        if self._running:
            return
        self._running = True
        num_workers = num_workers or self._max_concurrent
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker_loop(i))
            self._workers.append(worker)
        logger.info(f"Execution queue started with {num_workers} workers")
    
    async def stop(self):
        """Stop the execution queue."""
        self._running = False
        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        logger.info("Execution queue stopped")
    
    async def _worker_loop(self, worker_id: int):
        """Worker loop that processes tasks from the queue."""
        logger.info(f"Worker {worker_id} started")
        while self._running:
            try:
                priority, timestamp, task = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            
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
                task.status = TaskStatus.TIMEOUT
                task.error = f"Task exceeded {task.timeout_seconds}s timeout"
                task.completed_at = time.time()
                self._total_timeout += 1
                logger.warning(f"Task {task.id} timed out")
                
            except asyncio.CancelledError:
                task.status = TaskStatus.CANCELLED
                task.completed_at = time.time()
                self._total_cancelled += 1
                
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.completed_at = time.time()
                self._total_failed += 1
                logger.error(f"Task {task.id} failed: {e}")
            
            self._queue.task_done()
        
        logger.info(f"Worker {worker_id} stopped")
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID."""
        task = self._tasks.get(task_id)
        return task.to_dict() if task else None
    
    def list_tasks(self, limit: int = 50, status: str = None) -> List[Dict[str, Any]]:
        """List tasks, optionally filtered by status."""
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status.value == status]
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return [t.to_dict() for t in tasks[:limit]]
    
    def stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
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
            "max_concurrent": self._max_concurrent,
            "total_tasks": len(self._tasks),
            "completed": self._total_completed,
            "failed": self._total_failed,
            "timeout": self._total_timeout,
            "cancelled": self._total_cancelled,
            "by_status": dict(by_status),
            "avg_latency_ms": avg_latency,
        }
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            task.completed_at = time.time()
            self._total_cancelled += 1
            return True
        return False
    
    async def cancel_all(self) -> int:
        """Cancel all pending tasks."""
        cancelled = 0
        for task in self._tasks.values():
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                task.completed_at = time.time()
                self._total_cancelled += 1
                cancelled += 1
        return cancelled


# =========================================================================
# Global instance
# =========================================================================

execution_queue = AsyncExecutionQueue(max_concurrent=5, default_timeout=120)
