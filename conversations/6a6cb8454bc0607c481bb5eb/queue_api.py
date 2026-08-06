"""
EvolvixOS Queue API v3.0
REST API + WebSocket for async execution queue, DLQ, agent integration,
TTL management, and scheduled retention.

v3.0 additions:
- Agent queue REST endpoints (submit, execute, status, list, DLQ requeue)
- WebSocket for real-time queue monitoring
- TTL manager and scheduled retention integrated into startup
- Configurable TTL cleanup interval
"""

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import structlog
import asyncio
import os
import json
import time

from async_execution_queue import (
    AsyncExecutionQueue, QueuedTask, TaskStatus,
    execution_queue, dead_letter_queue,
)
from agent_queue_integration import (
    TaskTTLManager, ScheduledRetention, AgentQueueIntegrator,
    DEFAULT_TASK_TTL_SECONDS,
    ttl_manager, scheduled_retention, agent_queue,
)

logger = structlog.get_logger()

app = FastAPI(
    title="EvolvixOS Queue API",
    description="Async execution queue, DLQ, agent integration, and real-time monitoring",
    version="3.0.0",
)

# =========================================================================
# PostgreSQL Persistence
# =========================================================================

import asyncpg

PG_DSN = os.getenv("DATABASE_URL", "postgresql://evolvixos:EvolvixOS2026Secure@localhost:5432/evolvixos")
_pg_pool = None
MAX_PG_RETRIES = 3
PG_RETRY_DELAY = 2


async def init_pg_pool():
    global _pg_pool
    for attempt in range(MAX_PG_RETRIES):
        try:
            _pg_pool = await asyncpg.create_pool(PG_DSN, min_size=2, max_size=10, command_timeout=30)
            async with _pg_pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS queue_tasks (
                        id TEXT PRIMARY KEY, agent_id TEXT NOT NULL, agent_name TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending', capability TEXT, priority INTEGER DEFAULT 0,
                        input_data JSONB DEFAULT '{}', output_data JSONB DEFAULT '{}',
                        error TEXT DEFAULT '', latency_ms REAL DEFAULT 0, retry_count INTEGER DEFAULT 0,
                        max_retries INTEGER DEFAULT 2, created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
                    );
                    CREATE INDEX IF NOT EXISTS idx_queue_tasks_status ON queue_tasks(status);
                    CREATE INDEX IF NOT EXISTS idx_queue_tasks_agent ON queue_tasks(agent_id);
                """)
            logger.info(f"Queue PG pool connected (attempt {attempt + 1})")
            return True
        except Exception as e:
            logger.warning(f"Queue PG attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(PG_RETRY_DELAY)
    logger.warning("Queue PG: in-memory only")
    return False


async def close_pg_pool():
    global _pg_pool
    if _pg_pool:
        await _pg_pool.close()
        _pg_pool = None


async def persist_task(task_dict: Dict[str, Any]):
    if not _pg_pool:
        return
    try:
        async with _pg_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO queue_tasks (id, agent_id, agent_name, status, capability, priority,
                    input_data, output_data, error, latency_ms, retry_count, max_retries, updated_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,NOW())
                ON CONFLICT (id) DO UPDATE SET status=$4, output_data=$8, error=$9,
                    latency_ms=$10, retry_count=$11, updated_at=NOW()
            """,
                task_dict.get("id",""), task_dict.get("agent_id",""), task_dict.get("agent_name",""),
                task_dict.get("status","pending"), task_dict.get("capability",""), task_dict.get("priority",0),
                json.dumps(task_dict.get("input_data",{})), json.dumps(task_dict.get("output_data",{})),
                task_dict.get("error",""), task_dict.get("latency_ms",0), task_dict.get("retry_count",0),
                task_dict.get("max_retries",2),
            )
    except Exception as e:
        logger.warning(f"Task persist failed: {e}")


async def get_pending_tasks(limit: int = 100) -> List[Dict]:
    if not _pg_pool:
        return []
    try:
        async with _pg_pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM queue_tasks WHERE status='pending' ORDER BY priority DESC, created_at ASC LIMIT $1", limit)
            return [dict(r) for r in rows]
    except Exception:
        return []


async def cleanup_old_queue_tasks(days: int = 30) -> int:
    if not _pg_pool:
        return 0
    try:
        async with _pg_pool.acquire() as conn:
            r = await conn.execute("DELETE FROM queue_tasks WHERE status IN ('completed','failed','cancelled','timeout') AND updated_at < NOW() - INTERVAL '%s days'" % days)
            return int(r.split()[-1]) if r else 0
    except Exception:
        return 0


# =========================================================================
# DLQ Alerting
# =========================================================================

class DLQAlertConfig:
    webhook_url: Optional[str] = None
    min_severity: str = "warning"
    rate_limit_seconds: int = 60
    _last_alert_time: float = 0
    
    @classmethod
    def should_alert(cls) -> bool:
        now = time.time()
        if now - cls._last_alert_time < cls.rate_limit_seconds:
            return False
        cls._last_alert_time = now
        return True


async def send_dlq_alert(task_id: str, error: str, agent_id: str):
    if not DLQAlertConfig.should_alert():
        return
    alert = {"event":"dlq_entry","task_id":task_id,"error":error,"agent_id":agent_id,
              "timestamp":datetime.now(timezone.utc).isoformat(),"severity":"warning"}
    logger.warning(f"DLQ ALERT: Task {task_id} (agent: {agent_id}) entered DLQ: {error}")
    if DLQAlertConfig.webhook_url:
        try:
            import httpx
            async with httpx.AsyncClient() as c:
                await c.post(DLQAlertConfig.webhook_url, json=alert, timeout=5)
        except Exception as e:
            logger.warning(f"DLQ webhook alert failed: {e}")


_original_dlq_add = dead_letter_queue.add
def _dlq_add_with_alert(task: QueuedTask):
    _original_dlq_add(task)
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(send_dlq_alert(task.id, task.error or "unknown", task.agent_id))
    except RuntimeError:
        logger.warning(f"DLQ ALERT: Task {task.id} (agent: {task.agent_id}) entered DLQ: {task.error}")
dead_letter_queue.add = _dlq_add_with_alert


# =========================================================================
# WebSocket Manager
# =========================================================================

class WebSocketManager:
    """Manages WebSocket connections for real-time queue monitoring."""
    
    def __init__(self):
        self._connections: List[WebSocket] = []
        self._broadcast_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._connections.append(ws)
        logger.info(f"WebSocket connected (total: {len(self._connections)})")
    
    def disconnect(self, ws: WebSocket):
        if ws in self._connections:
            self._connections.remove(ws)
        logger.info(f"WebSocket disconnected (total: {len(self._connections)})")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients."""
        if not self._connections:
            return
        text = json.dumps(message)
        dead = []
        for ws in self._connections:
            try:
                await ws.send_text(text)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)
    
    async def start_periodic_broadcast(self, interval: int = 5):
        """Start periodic broadcast of queue stats."""
        if self._running:
            return
        self._running = True
        self._broadcast_task = asyncio.create_task(self._broadcast_loop(interval))
    
    async def stop_periodic_broadcast(self):
        self._running = False
        if self._broadcast_task:
            self._broadcast_task.cancel()
            try:
                await self._broadcast_task
            except asyncio.CancelledError:
                pass
            self._broadcast_task = None
    
    async def _broadcast_loop(self, interval: int):
        """Periodically broadcast queue stats to all clients."""
        while self._running:
            await asyncio.sleep(interval)
            stats = execution_queue.stats()
            stats["dlq"] = dead_letter_queue.stats()
            stats["timestamp"] = datetime.now(timezone.utc).isoformat()
            await self.broadcast({"type": "queue_stats", "data": stats})
    
    @property
    def connection_count(self) -> int:
        return len(self._connections)


ws_manager = WebSocketManager()


# =========================================================================
# Startup / Shutdown
# =========================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize PG, persistence, TTL, retention, recovery, and WebSocket."""
    pg_ok = await init_pg_pool()
    
    if pg_ok:
        execution_queue.set_persistence_callback(persist_task)
        pending = await get_pending_tasks(limit=100)
        if pending:
            recovered = await execution_queue.recover_from_persistence(pending)
            logger.info(f"Auto-recovered {recovered} pending tasks")
    
    # Start TTL periodic cleanup
    await ttl_manager.start_periodic_cleanup(execution_queue)
    
    # Start scheduled retention (daily)
    scheduled_retention.set_cleanup_callback(cleanup_old_queue_tasks)
    await scheduled_retention.start(interval_seconds=86400)
    
    # Start WebSocket broadcast (5s interval)
    await ws_manager.start_periodic_broadcast(interval=5)
    
    logger.info("Queue API v3.0 startup complete (PG, TTL, retention, WebSocket)")


@app.on_event("shutdown")
async def shutdown_event():
    await ws_manager.stop_periodic_broadcast()
    await ttl_manager.stop_periodic_cleanup()
    await scheduled_retention.stop()
    await execution_queue.stop()
    await close_pg_pool()
    logger.info("Queue API v3.0 shutdown complete")


# =========================================================================
# Request Models
# =========================================================================

class SubmitTaskRequest(BaseModel):
    agent_id: str
    agent_name: str
    capability: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    options: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 0
    timeout: Optional[int] = None
    max_retries: int = 2


class TTLConfigRequest(BaseModel):
    ttl_seconds: int = DEFAULT_TASK_TTL_SECONDS
    cleanup_interval: int = 3600


class DLQAlertConfigRequest(BaseModel):
    webhook_url: Optional[str] = None
    min_severity: str = "warning"
    rate_limit_seconds: int = 60


# =========================================================================
# Queue Endpoints
# =========================================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy", "version": "3.0.0",
        "pg_connected": _pg_pool is not None,
        "queue": execution_queue.stats(),
        "dlq": dead_letter_queue.stats(),
        "ttl_seconds": ttl_manager.ttl_seconds,
        "ws_connections": ws_manager.connection_count,
    }

@app.get("/queue/stats")
async def queue_stats():
    s = execution_queue.stats()
    s["pg_connected"] = _pg_pool is not None
    s["dlq"] = dead_letter_queue.stats()
    return s

@app.post("/queue/submit")
async def submit_task(req: SubmitTaskRequest):
    try:
        tid = await execution_queue.submit(
            agent_id=req.agent_id, agent_name=req.agent_name, capability=req.capability,
            input_data=req.input_data, options=req.options, priority=req.priority,
            timeout=req.timeout, max_retries=req.max_retries,
        )
        return {"task_id": tid, "status": "pending"}
    except asyncio.QueueFull as e:
        raise HTTPException(status_code=429, detail=str(e))

@app.get("/queue/task/{task_id}")
async def get_task(task_id: str):
    t = execution_queue.get_task(task_id)
    if not t:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    return t

@app.get("/queue/tasks")
async def list_tasks(limit: int = 50, status: str = None, agent_id: str = None):
    tasks = execution_queue.list_tasks(limit=limit, status=status)
    if agent_id:
        tasks = [t for t in tasks if t.get("agent_id") == agent_id]
    return {"tasks": tasks, "count": len(tasks)}

@app.post("/queue/start")
async def start_queue(workers: int = 5):
    await execution_queue.start(num_workers=workers)
    return {"status": "started", "workers": workers}

@app.post("/queue/stop")
async def stop_queue():
    await execution_queue.stop()
    return {"status": "stopped"}

@app.post("/queue/cancel/{task_id}")
async def cancel_task(task_id: str):
    ok = await execution_queue.cancel_task(task_id)
    if not ok:
        raise HTTPException(status_code=400, detail=f"Cannot cancel task {task_id}")
    return {"task_id": task_id, "status": "cancelled"}

@app.post("/queue/cancel-all")
async def cancel_all():
    c = await execution_queue.cancel_all()
    return {"cancelled": c}

@app.post("/queue/recover")
async def recover_tasks(limit: int = 100):
    pending = await get_pending_tasks(limit=limit)
    recovered = await execution_queue.recover_from_persistence(pending)
    return {"recovered": recovered, "checked": len(pending)}

@app.post("/queue/retention/{days}")
async def queue_retention(days: int):
    deleted = await cleanup_old_queue_tasks(days)
    return {"deleted": deleted, "retention_days": days}


# =========================================================================
# Agent Queue Endpoints (NEW in v3.0)
# =========================================================================

@app.post("/agent/submit")
async def agent_submit(req: SubmitTaskRequest):
    """Submit an agent task via the AgentQueueIntegrator."""
    try:
        tid = await agent_queue.submit_agent_task(
            agent_id=req.agent_id, agent_name=req.agent_name, capability=req.capability,
            input_data=req.input_data, priority=req.priority,
            timeout=req.timeout or 120, max_retries=req.max_retries,
        )
        return {"task_id": tid, "status": "pending"}
    except asyncio.QueueFull as e:
        raise HTTPException(status_code=429, detail=str(e))

@app.post("/agent/execute")
async def agent_execute(req: SubmitTaskRequest):
    """Submit and wait for an agent task to complete."""
    try:
        result = await agent_queue.execute_agent_task(
            agent_id=req.agent_id, agent_name=req.agent_name, capability=req.capability,
            input_data=req.input_data, priority=req.priority,
            timeout=req.timeout or 120, max_retries=req.max_retries,
        )
        return result
    except asyncio.QueueFull as e:
        raise HTTPException(status_code=429, detail=str(e))

@app.get("/agent/task/{task_id}")
async def agent_task_status(task_id: str):
    """Get agent task status."""
    t = agent_queue.get_task_status(task_id)
    if not t:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    return t

@app.get("/agent/tasks")
async def agent_list_tasks(limit: int = 50, agent_id: str = None, status: str = None):
    """List agent tasks, filterable by agent and status."""
    tasks = agent_queue.list_agent_tasks(agent_id=agent_id, limit=limit, status=status)
    return {"tasks": tasks, "count": len(tasks)}

@app.get("/agent/stats")
async def agent_stats():
    """Get combined agent queue and DLQ stats."""
    return {
        "queue": agent_queue.get_queue_stats(),
        "dlq": agent_queue.get_dlq_stats(),
    }

@app.post("/agent/dlq/{task_id}/requeue")
async def agent_dlq_requeue(task_id: str):
    """Re-queue a failed agent task from the DLQ."""
    new_id = await agent_queue.requeue_dlq_task(task_id)
    if not new_id:
        raise HTTPException(status_code=404, detail=f"DLQ entry not found: {task_id}")
    return {"old_task_id": task_id, "new_task_id": new_id, "status": "re-queued"}


# =========================================================================
# DLQ Endpoints
# =========================================================================

@app.get("/dlq/stats")
async def dlq_stats():
    return dead_letter_queue.stats()

@app.get("/dlq/list")
async def dlq_list(limit: int = 50):
    entries = dead_letter_queue.list(limit=limit)
    return {"entries": entries, "count": len(entries)}

@app.get("/dlq/{task_id}")
async def dlq_get(task_id: str):
    e = dead_letter_queue.get(task_id)
    if not e:
        raise HTTPException(status_code=404, detail=f"DLQ entry not found: {task_id}")
    return e

@app.delete("/dlq/{task_id}")
async def dlq_remove(task_id: str):
    if not dead_letter_queue.remove(task_id):
        raise HTTPException(status_code=404, detail=f"DLQ entry not found: {task_id}")
    return {"task_id": task_id, "removed": True}

@app.post("/dlq/clear")
async def dlq_clear():
    return {"cleared": dead_letter_queue.clear()}

@app.post("/dlq/{task_id}/requeue")
async def dlq_requeue(task_id: str):
    e = dead_letter_queue.get(task_id)
    if not e:
        raise HTTPException(status_code=404, detail=f"DLQ entry not found: {task_id}")
    dead_letter_queue.remove(task_id)
    try:
        new_id = await execution_queue.submit(
            agent_id=e.get("agent_id","unknown"), agent_name=e.get("agent_name","Unknown"),
            capability=e.get("capability","unknown"), input_data=e.get("input_data",{}),
            priority=e.get("priority",0), max_retries=e.get("max_retries",2),
        )
        return {"old_task_id": task_id, "new_task_id": new_id, "status": "re-queued"}
    except asyncio.QueueFull as ex:
        raise HTTPException(status_code=429, detail=str(ex))


# =========================================================================
# TTL Configuration
# =========================================================================

@app.get("/ttl/config")
async def get_ttl_config():
    return {
        "ttl_seconds": ttl_manager.ttl_seconds,
        "cleanup_interval": 3600,
    }

@app.post("/ttl/config")
async def set_ttl_config(req: TTLConfigRequest):
    ttl_manager.set_ttl(req.ttl_seconds)
    return {
        "status": "updated",
        "ttl_seconds": ttl_manager.ttl_seconds,
        "cleanup_interval": req.cleanup_interval,
    }


# =========================================================================
# DLQ Alert Config
# =========================================================================

@app.get("/dlq/alerts/config")
async def get_alert_config():
    return {
        "webhook_url": DLQAlertConfig.webhook_url,
        "min_severity": DLQAlertConfig.min_severity,
        "rate_limit_seconds": DLQAlertConfig.rate_limit_seconds,
    }

@app.post("/dlq/alerts/config")
async def set_alert_config(req: DLQAlertConfigRequest):
    DLQAlertConfig.webhook_url = req.webhook_url
    DLQAlertConfig.min_severity = req.min_severity
    DLQAlertConfig.rate_limit_seconds = req.rate_limit_seconds
    return {"status": "updated", "webhook_url": DLQAlertConfig.webhook_url,
            "min_severity": DLQAlertConfig.min_severity,
            "rate_limit_seconds": DLQAlertConfig.rate_limit_seconds}


# =========================================================================
# WebSocket Endpoint
# =========================================================================

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket for real-time queue monitoring."""
    await ws_manager.connect(ws)
    try:
        # Send initial state
        stats = execution_queue.stats()
        stats["dlq"] = dead_letter_queue.stats()
        stats["timestamp"] = datetime.now(timezone.utc).isoformat()
        await ws.send_text(json.dumps({"type": "queue_stats", "data": stats}))
        
        # Keep connection alive, listen for messages
        while True:
            data = await ws.receive_text()
            # Echo back any client messages (ping/pong)
            if data == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
    except Exception:
        ws_manager.disconnect(ws)
