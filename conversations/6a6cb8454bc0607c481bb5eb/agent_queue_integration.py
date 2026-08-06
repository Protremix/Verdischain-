"""
EvolvixOS Agent Execution Integration with Async Queue
Integrates the async execution queue into the agent execution API,
replacing synchronous execution with queue-based execution.
Also adds task TTL and scheduled retention cleanup.
"""

import asyncio
import time
import os
import json
import structlog
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass

from async_execution_queue import (
    AsyncExecutionQueue, QueuedTask, TaskStatus,
    execution_queue, dead_letter_queue,
)

logger = structlog.get_logger()

# =========================================================================
# Task TTL Configuration
# =========================================================================

DEFAULT_TASK_TTL_SECONDS = 86400  # 24 hours
CLEANUP_INTERVAL_SECONDS = 3600   # Run cleanup every hour


class TaskTTLManager:
    """Manages task TTL (time-to-live) and automatic cleanup of stale tasks."""
    
    def __init__(self, ttl_seconds: int = DEFAULT_TASK_TTL_SECONDS):
        self._ttl_seconds = ttl_seconds
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
    
    @property
    def ttl_seconds(self) -> int:
        return self._ttl_seconds
    
    def set_ttl(self, seconds: int):
        self._ttl_seconds = seconds
    
    def is_task_expired(self, task: QueuedTask) -> bool:
        """Check if a task has exceeded its TTL."""
        age = time.time() - task.created_at
        return age > self._ttl_seconds
    
    def get_expired_task_ids(self, queue: AsyncExecutionQueue) -> List[str]:
        """Get IDs of expired tasks (completed/failed/cancelled/timeout only)."""
        expired = []
        for task_id, task in queue._tasks.items():
            if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, 
                              TaskStatus.CANCELLED, TaskStatus.TIMEOUT):
                if self.is_task_expired(task):
                    expired.append(task_id)
        return expired
    
    def cleanup_expired(self, queue: AsyncExecutionQueue) -> int:
        """Remove expired terminal tasks from the queue's in-memory store."""
        expired_ids = self.get_expired_task_ids(queue)
        for task_id in expired_ids:
            queue._tasks.pop(task_id, None)
        if expired_ids:
            logger.info(f"TTL cleanup: removed {len(expired_ids)} expired tasks")
        return len(expired_ids)
    
    async def start_periodic_cleanup(self, queue: AsyncExecutionQueue):
        """Start periodic cleanup of expired tasks."""
        if self._running:
            return
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop(queue))
        logger.info(f"TTL cleanup started (interval: {CLEANUP_INTERVAL_SECONDS}s, TTL: {self._ttl_seconds}s)")
    
    async def stop_periodic_cleanup(self):
        """Stop periodic cleanup."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
    
    async def _cleanup_loop(self, queue: AsyncExecutionQueue):
        """Background cleanup loop."""
        while self._running:
            await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
            self.cleanup_expired(queue)


# =========================================================================
# Scheduled Retention (PG cleanup)
# =========================================================================

class ScheduledRetention:
    """Scheduled retention cleanup for PostgreSQL task records."""
    
    def __init__(self, retention_days: int = 30):
        self._retention_days = retention_days
        self._retention_task: Optional[asyncio.Task] = None
        self._running = False
        self._cleanup_callback: Optional[Any] = None
    
    def set_cleanup_callback(self, callback):
        """Set the async callback for PG cleanup."""
        self._cleanup_callback = callback
    
    async def start(self, interval_seconds: int = 86400):
        """Start scheduled retention cleanup (default: daily)."""
        if self._running:
            return
        self._running = True
        self._retention_task = asyncio.create_task(self._retention_loop(interval_seconds))
        logger.info(f"Scheduled retention started (interval: {interval_seconds}s, retention: {self._retention_days} days)")
    
    async def stop(self):
        """Stop scheduled retention."""
        self._running = False
        if self._retention_task:
            self._retention_task.cancel()
            try:
                await self._retention_task
            except asyncio.CancelledError:
                pass
            self._retention_task = None
    
    async def _retention_loop(self, interval_seconds: int):
        """Background retention cleanup loop."""
        while self._running:
            await asyncio.sleep(interval_seconds)
            if self._cleanup_callback:
                try:
                    deleted = await self._cleanup_callback(self._retention_days)
                    if deleted > 0:
                        logger.info(f"Scheduled retention: deleted {deleted} old records")
                except Exception as e:
                    logger.warning(f"Scheduled retention failed: {e}")


# =========================================================================
# Agent Queue Integration
# =========================================================================

class AgentQueueIntegrator:
    """Integrates the async execution queue with the agent execution API.
    
    This replaces the synchronous execution model with queue-based execution,
    allowing tasks to be submitted, tracked, and managed through the queue API.
    """
    
    def __init__(self, queue: AsyncExecutionQueue):
        self._queue = queue
        self._executor_set = False
    
    def set_gateway_executor(self, gateway_call_fn):
        """Set the AI Gateway call function as the executor.
        
        Args:
            gateway_call_fn: async function that takes a QueuedTask and returns Dict
        """
        self._queue.set_executor(gateway_call_fn)
        self._executor_set = True
        logger.info("Agent queue executor set (AI Gateway)")
    
    async def submit_agent_task(
        self,
        agent_id: str,
        agent_name: str,
        capability: str,
        input_data: Dict[str, Any],
        priority: int = 0,
        timeout: int = 120,
        max_retries: int = 2,
    ) -> str:
        """Submit an agent task to the execution queue.
        
        Returns:
            task_id: The queue task ID for tracking
        """
        return await self._queue.submit(
            agent_id=agent_id,
            agent_name=agent_name,
            capability=capability,
            input_data=input_data,
            priority=priority,
            timeout=timeout,
            max_retries=max_retries,
        )
    
    async def execute_agent_task(
        self,
        agent_id: str,
        agent_name: str,
        capability: str,
        input_data: Dict[str, Any],
        priority: int = 0,
        timeout: int = 120,
        max_retries: int = 2,
    ) -> Dict[str, Any]:
        """Submit and wait for an agent task to complete.
        
        Returns:
            Task result dict with status, latency, output
        """
        return await self._queue.submit_and_wait(
            agent_id=agent_id,
            agent_name=agent_name,
            capability=capability,
            input_data=input_data,
            priority=priority,
            timeout=timeout,
            max_retries=max_retries,
        )
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a submitted task."""
        return self._queue.get_task(task_id)
    
    def list_agent_tasks(self, agent_id: str = None, limit: int = 50, status: str = None) -> List[Dict]:
        """List tasks, optionally filtered by agent and status."""
        tasks = self._queue.list_tasks(limit=limit, status=status)
        if agent_id:
            tasks = [t for t in tasks if t.get("agent_id") == agent_id]
        return tasks
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return self._queue.stats()
    
    def get_dlq_stats(self) -> Dict[str, Any]:
        """Get dead letter queue statistics."""
        if self._queue._dlq:
            return self._queue._dlq.stats()
        return {"total": 0, "max_size": 0}
    
    def get_dlq_entries(self, limit: int = 50) -> List[Dict]:
        """Get dead letter queue entries."""
        if self._queue._dlq:
            return self._queue._dlq.list(limit=limit)
        return []
    
    async def requeue_dlq_task(self, task_id: str) -> Optional[str]:
        """Re-queue a failed task from the DLQ."""
        if not self._queue._dlq:
            return None
        entry = self._queue._dlq.get(task_id)
        if not entry:
            return None
        self._queue._dlq.remove(task_id)
        return await self._queue.submit(
            agent_id=entry.get("agent_id", "unknown"),
            agent_name=entry.get("agent_name", "Unknown"),
            capability=entry.get("capability", "unknown"),
            input_data=entry.get("input_data", {}),
            priority=entry.get("priority", 0),
            max_retries=entry.get("max_retries", 2),
        )


# =========================================================================
# Global instances
# =========================================================================

ttl_manager = TaskTTLManager(ttl_seconds=DEFAULT_TASK_TTL_SECONDS)
scheduled_retention = ScheduledRetention(retention_days=30)
agent_queue = AgentQueueIntegrator(execution_queue)
