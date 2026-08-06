"""
EvolvixOS Queue API v3.4
+ AI Gateway wired as execution queue executor (real execution)
+ Per-task TTL override
+ WebSocket client library (Python + TypeScript SDK)
"""

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect, Request
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import structlog
import asyncio
import os
import json
import time
import hashlib
import secrets
from collections import defaultdict, deque

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
    description="Async execution queue with AI Gateway executor, per-task TTL, and WebSocket client library",
    version="3.5.0",
)

# =========================================================================
# Redis Setup
# =========================================================================

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_redis_client: Optional[redis.Redis] = None
WS_TOKEN_PREFIX = "ws_token:"
WS_TOKEN_TTL = 3600
RATE_LIMIT_PREFIX = "rl:"
TOKEN_RATE_LIMIT = 10
TOKEN_RATE_WINDOW = 60

_FALLBACK_TOKENS: Dict[str, Dict] = {}
_FALLBACK_RATE: Dict[str, deque] = defaultdict(deque)


def init_redis():
    global _redis_client
    try:
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        _redis_client.ping()
        logger.info("Redis connected (tokens + rate limiting)")
        return True
    except Exception as e:
        logger.warning(f"Redis unavailable, in-memory fallback: {e}")
        _redis_client = None
        return False


# =========================================================================
# Token Management (Redis)
# =========================================================================

def _store_token(token, agent_id, ttl=WS_TOKEN_TTL):
    data = json.dumps({"agent_id": agent_id, "created_at": time.time(), "expires_at": time.time() + ttl})
    if _redis_client:
        _redis_client.setex(f"{WS_TOKEN_PREFIX}{token}", ttl, data)
    else:
        _FALLBACK_TOKENS[token] = json.loads(data)

def _get_token(token):
    if _redis_client:
        d = _redis_client.get(f"{WS_TOKEN_PREFIX}{token}")
        return json.loads(d) if d else None
    return _FALLBACK_TOKENS.get(token)

def _delete_token(token):
    if _redis_client:
        return _redis_client.delete(f"{WS_TOKEN_PREFIX}{token}") > 0
    if token in _FALLBACK_TOKENS:
        del _FALLBACK_TOKENS[token]; return True
    return False

def _count_tokens():
    if _redis_client:
        return len(_redis_client.keys(f"{WS_TOKEN_PREFIX}*"))
    return len(_FALLBACK_TOKENS)

def _list_tokens():
    result = []
    if _redis_client:
        for key in _redis_client.keys(f"{WS_TOKEN_PREFIX}*"):
            d = _redis_client.get(key)
            if d:
                p = json.loads(d)
                result.append({"agent_id": p["agent_id"], "expires_at": datetime.fromtimestamp(p["expires_at"], tz=timezone.utc).isoformat()})
    else:
        for _, d in _FALLBACK_TOKENS.items():
            result.append({"agent_id": d["agent_id"], "expires_at": datetime.fromtimestamp(d["expires_at"], tz=timezone.utc).isoformat()})
    return result

def generate_ws_token(agent_id="default"):
    token = secrets.token_urlsafe(32)
    _store_token(token, agent_id)
    return token

def validate_ws_token(token):
    if not token: return False
    data = _get_token(token)
    if not data: return False
    if time.time() > data.get("expires_at", 0):
        _delete_token(token); return False
    return True


# =========================================================================
# Redis-Backed Rate Limiting (pipeline-optimized)
# =========================================================================

def check_rate_limit(ip):
    now = time.time()
    key = f"{RATE_LIMIT_PREFIX}{ip}"
    if _redis_client:
        pipe = _redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, now - TOKEN_RATE_WINDOW)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, TOKEN_RATE_WINDOW)
        results = pipe.execute()
        return results[1] < TOKEN_RATE_LIMIT
    else:
        ip_reqs = _FALLBACK_RATE[ip]
        while ip_reqs and ip_reqs[0] < now - TOKEN_RATE_WINDOW:
            ip_reqs.popleft()
        if len(ip_reqs) >= TOKEN_RATE_LIMIT: return False
        ip_reqs.append(now); return True

def get_rate_limit_info(ip):
    now = time.time()
    key = f"{RATE_LIMIT_PREFIX}{ip}"
    if _redis_client:
        pipe = _redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, now - TOKEN_RATE_WINDOW)
        pipe.zcard(key)
        pipe.execute()
        count = _redis_client.zcard(key)  # Use pipeline result
        # Actually use the pipeline results properly
        pipe2 = _redis_client.pipeline()
        pipe2.zremrangebyscore(key, 0, now - TOKEN_RATE_WINDOW)
        pipe2.zcard(key)
        results = pipe2.execute()
        count = results[1]
    else:
        ip_reqs = _FALLBACK_RATE[ip]
        while ip_reqs and ip_reqs[0] < now - TOKEN_RATE_WINDOW:
            ip_reqs.popleft()
        count = len(ip_reqs)
    return {"requests": count, "limit": TOKEN_RATE_LIMIT,
            "window_seconds": TOKEN_RATE_WINDOW, "remaining": max(0, TOKEN_RATE_LIMIT - count)}


# =========================================================================
# AI Gateway Executor
# =========================================================================

GATEWAY_URL = os.getenv("AI_GATEWAY_URL", "http://localhost:3500")
GATEWAY_API_KEY = os.getenv("AI_GATEWAY_API_KEY", "")

async def gateway_executor(task: QueuedTask) -> Dict[str, Any]:
    """Execute a task via the AI Gateway.
    
    Routes the task to the appropriate gateway endpoint based on capability.
    """
    import httpx
    
    capability = task.capability or "chat"
    input_data = task.input_data or {}
    
    # Determine gateway endpoint based on capability
    if "code_review" in capability or "review" in capability:
        endpoint = f"{GATEWAY_URL}/invoke"
        payload = {"provider": "code-reviewer", "input": input_data}
    elif "sentiment" in capability:
        endpoint = f"{GATEWAY_URL}/invoke"
        payload = {"provider": "sentiment-analyzer", "input": input_data}
    elif "embedding" in capability:
        endpoint = f"{GATEWAY_URL}/invoke"
        payload = {"provider": "openai-gpt4o", "capability": "embedding", "input": input_data}
    else:
        # Default: chat/completion
        endpoint = f"{GATEWAY_URL}/invoke"
        payload = {"provider": "openai-gpt4o", "capability": "chat", "input": input_data}
    
    headers = {"Content-Type": "application/json"}
    if GATEWAY_API_KEY:
        headers["Authorization"] = f"Bearer {GATEWAY_API_KEY}"
    
    try:
        async with httpx.AsyncClient(timeout=getattr(task, "timeout", None) or 120) as client:
            resp = await client.post(endpoint, json=payload, headers=headers)
            resp.raise_for_status()
            result = resp.json()
            
            return {
                "content": result.get("content", result.get("response", str(result))),
                "tokens": result.get("tokens", 0),
                "provider": result.get("provider", "gateway"),
                "model": result.get("model", "gpt-4o"),
                "latency_ms": result.get("latency_ms", 0),
            }
    except httpx.TimeoutException:
        raise TimeoutError(f"Gateway timed out for capability: {capability}")
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Gateway HTTP error: {e.response.status_code}")
    except Exception as e:
        raise RuntimeError(f"Gateway error: {e}")


# =========================================================================
# Per-Task TTL
# =========================================================================

class TaskTTLRegistry:
    """Registry for per-task TTL overrides (Redis-backed)."""
    TTL_PREFIX = "ttl_override:"
    
    def set_task_ttl(self, task_id: str, ttl_seconds: int):
        if _redis_client:
            _redis_client.set(f"{self.TTL_PREFIX}{task_id}", str(ttl_seconds))
        else:
            _FALLBACK_TOKENS[f"{self.TTL_PREFIX}{task_id}"] = ttl_seconds
    
    def get_task_ttl(self, task_id: str, default: int = DEFAULT_TASK_TTL_SECONDS) -> int:
        if _redis_client:
            val = _redis_client.get(f"{self.TTL_PREFIX}{task_id}")
            return int(val) if val else default
        return _FALLBACK_TOKENS.get(f"{self.TTL_PREFIX}{task_id}", default)
    
    def remove_task_ttl(self, task_id: str):
        if _redis_client:
            _redis_client.delete(f"{self.TTL_PREFIX}{task_id}")
        else:
            _FALLBACK_TOKENS.pop(f"{self.TTL_PREFIX}{task_id}", None)
    
    def count_overrides(self) -> int:
        if _redis_client:
            return len(_redis_client.keys(f"{self.TTL_PREFIX}*"))
        return sum(1 for k in _FALLBACK_TOKENS if k.startswith(self.TTL_PREFIX))
    
    def is_override(self, task_id: str) -> bool:
        if _redis_client:
            return _redis_client.exists(f"{self.TTL_PREFIX}{task_id}") > 0
        return f"{self.TTL_PREFIX}{task_id}" in _FALLBACK_TOKENS

ttl_registry = TaskTTLRegistry()


# =========================================================================
# PostgreSQL
# =========================================================================

import asyncpg

PG_DSN = os.getenv("DATABASE_URL", "postgresql://evolvixos:EvolvixOS2026Secure@localhost:5432/evolvixos")
_pg_pool = None

async def init_pg_pool():
    global _pg_pool
    for attempt in range(3):
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
            logger.info(f"Queue PG connected (attempt {attempt+1})")
            return True
        except Exception as e:
            logger.warning(f"Queue PG attempt {attempt+1}: {e}")
            await asyncio.sleep(2)
    return False

async def close_pg_pool():
    global _pg_pool
    if _pg_pool: await _pg_pool.close(); _pg_pool = None

async def persist_task(task_dict):
    if not _pg_pool: return
    try:
        async with _pg_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO queue_tasks (id, agent_id, agent_name, status, capability, priority,
                    input_data, output_data, error, latency_ms, retry_count, max_retries, updated_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,NOW())
                ON CONFLICT (id) DO UPDATE SET status=$4, output_data=$8, error=$9,
                    latency_ms=$10, retry_count=$11, updated_at=NOW()
            """, task_dict.get("id",""), task_dict.get("agent_id",""), task_dict.get("agent_name",""),
                task_dict.get("status","pending"), task_dict.get("capability",""), task_dict.get("priority",0),
                json.dumps(task_dict.get("input_data",{})), json.dumps(task_dict.get("output_data",{})),
                task_dict.get("error",""), task_dict.get("latency_ms",0), task_dict.get("retry_count",0),
                task_dict.get("max_retries",2))
    except Exception as e:
        logger.warning(f"Persist failed: {e}")

async def get_pending_tasks(limit=100):
    if not _pg_pool: return []
    try:
        async with _pg_pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM queue_tasks WHERE status='pending' ORDER BY priority DESC, created_at ASC LIMIT $1", limit)
            return [dict(r) for r in rows]
    except: return []

async def cleanup_old_queue_tasks(days=30):
    if not _pg_pool: return 0
    try:
        async with _pg_pool.acquire() as conn:
            r = await conn.execute("DELETE FROM queue_tasks WHERE status IN ('completed','failed','cancelled','timeout') AND updated_at < NOW() - INTERVAL '%s days'" % days)
            return int(r.split()[-1]) if r else 0
    except: return 0


# =========================================================================
# DLQ Alerting
# =========================================================================

class DLQAlertConfig:
    webhook_url: Optional[str] = None
    min_severity: str = "warning"
    rate_limit_seconds: int = 60
    _last_alert_time: float = 0
    
    @classmethod
    def should_alert(cls):
        now = time.time()
        if now - cls._last_alert_time < cls.rate_limit_seconds: return False
        cls._last_alert_time = now; return True

async def send_dlq_alert(task_id, error, agent_id):
    if not DLQAlertConfig.should_alert(): return
    alert = {"event":"dlq_entry","task_id":task_id,"error":error,"agent_id":agent_id,
              "timestamp":datetime.now(timezone.utc).isoformat(),"severity":"warning"}
    logger.warning(f"DLQ ALERT: {task_id} ({agent_id}): {error}")
    if DLQAlertConfig.webhook_url:
        try:
            import httpx
            async with httpx.AsyncClient() as c:
                await c.post(DLQAlertConfig.webhook_url, json=alert, timeout=5)
        except Exception as e:
            logger.warning(f"DLQ webhook failed: {e}")

_original_dlq_add = dead_letter_queue.add
def _dlq_add_with_alert(task):
    _original_dlq_add(task)
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(send_dlq_alert(task.id, task.error or "unknown", task.agent_id))
    except RuntimeError:
        logger.warning(f"DLQ ALERT: {task.id} ({task.agent_id}): {task.error}")
dead_letter_queue.add = _dlq_add_with_alert


# =========================================================================
# WebSocket Manager
# =========================================================================

class WebSocketManager:
    def __init__(self):
        self._connections: List[WebSocket] = []
        self._broadcast_task = None
        self._running = False
    
    async def connect(self, ws): await ws.accept(); self._connections.append(ws)
    def disconnect(self, ws):
        if ws in self._connections: self._connections.remove(ws)
    
    async def broadcast(self, msg):
        if not self._connections: return
        text = json.dumps(msg)
        dead = []
        for ws in self._connections:
            try: await ws.send_text(text)
            except: dead.append(ws)
        for ws in dead: self.disconnect(ws)
    
    async def start_periodic_broadcast(self, interval=5):
        if self._running: return
        self._running = True
        self._broadcast_task = asyncio.create_task(self._loop(interval))
    
    async def stop_periodic_broadcast(self):
        self._running = False
        if self._broadcast_task:
            self._broadcast_task.cancel()
            try: await self._broadcast_task
            except asyncio.CancelledError: pass
            self._broadcast_task = None
    
    async def _loop(self, interval):
        while self._running:
            await asyncio.sleep(interval)
            stats = execution_queue.stats()
            stats["dlq"] = dead_letter_queue.stats()
            stats["timestamp"] = datetime.now(timezone.utc).isoformat()
            await self.broadcast({"type":"queue_stats","data":stats})
    
    @property
    def count(self): return len(self._connections)

ws_manager = WebSocketManager()


# =========================================================================
# Startup / Shutdown
# =========================================================================

@app.on_event("startup")
async def startup_event():
    init_redis()
    pg_ok = await init_pg_pool()
    if pg_ok:
        execution_queue.set_persistence_callback(persist_task)
        pending = await get_pending_tasks(100)
        if pending:
            recovered = await execution_queue.recover_from_persistence(pending)
            logger.info(f"Auto-recovered {recovered} tasks")
    
    # Wire AI Gateway as executor
    agent_queue.set_gateway_executor(gateway_executor)
    logger.info(f"AI Gateway executor wired: {GATEWAY_URL}")
    
    # Start queue workers
    await execution_queue.start(num_workers=3)
    
    await ttl_manager.start_periodic_cleanup(execution_queue)
    scheduled_retention.set_cleanup_callback(cleanup_old_queue_tasks)
    await scheduled_retention.start(86400)
    await ws_manager.start_periodic_broadcast(5)
    logger.info("Queue API v3.4 startup complete (Gateway executor + workers)")

@app.on_event("shutdown")
async def shutdown_event():
    await ws_manager.stop_periodic_broadcast()
    await ttl_manager.stop_periodic_cleanup()
    await scheduled_retention.stop()
    await execution_queue.stop()
    await close_pg_pool()


# =========================================================================
# Models
# =========================================================================

class SubmitTaskRequest(BaseModel):
    agent_id: str; agent_name: str; capability: str
    input_data: Dict[str, Any] = {}; options: Dict[str, Any] = {}
    priority: int = 0; timeout: Optional[int] = None; max_retries: int = 2
    ttl_seconds: Optional[int] = None  # Per-task TTL override

class TTLConfigRequest(BaseModel):
    ttl_seconds: int = DEFAULT_TASK_TTL_SECONDS; cleanup_interval: int = 3600

class DLQAlertConfigRequest(BaseModel):
    webhook_url: Optional[str] = None; min_severity: str = "warning"; rate_limit_seconds: int = 60

class WSTokenRequest(BaseModel):
    agent_id: str = "default"

class TaskTTLRequest(BaseModel):
    ttl_seconds: int


# =========================================================================
# Queue Endpoints
# =========================================================================

@app.get("/health")
async def health():
    return {"status":"healthy","version":"3.5.0","pg_connected":_pg_pool is not None,
            "redis_connected":_redis_client is not None,
            "gateway_wired":execution_queue._executor is not None,
            "queue":execution_queue.stats(),"dlq":dead_letter_queue.stats(),
            "ttl_seconds":ttl_manager.ttl_seconds,"ws_connections":ws_manager.count,
            "ws_tokens":_count_tokens(),"ttl_overrides":ttl_registry.count_overrides()}

@app.get("/queue/stats")
async def queue_stats():
    s = execution_queue.stats(); s["pg_connected"] = _pg_pool is not None
    s["dlq"] = dead_letter_queue.stats(); return s

@app.post("/queue/submit")
async def submit_task(req: SubmitTaskRequest):
    try:
        tid = await execution_queue.submit(req.agent_id, req.agent_name, req.capability,
            req.input_data, req.options, req.priority, req.timeout, req.max_retries)
        if req.ttl_seconds:
            ttl_registry.set_task_ttl(tid, req.ttl_seconds)
        return {"task_id":tid,"status":"pending"}
    except asyncio.QueueFull as e: raise HTTPException(429, str(e))

@app.get("/queue/task/{task_id}")
async def get_task(task_id: str):
    t = execution_queue.get_task(task_id)
    if not t: raise HTTPException(404, f"Task not found: {task_id}")
    return t

@app.get("/queue/tasks")
async def list_tasks(limit: int = 50, status: str = None, agent_id: str = None):
    tasks = execution_queue.list_tasks(limit=limit, status=status)
    if agent_id: tasks = [t for t in tasks if t.get("agent_id") == agent_id]
    return {"tasks":tasks,"count":len(tasks)}

@app.post("/queue/start")
async def start_queue(workers: int = 5):
    await execution_queue.start(num_workers=workers); return {"status":"started","workers":workers}

@app.post("/queue/stop")
async def stop_queue():
    await execution_queue.stop(); return {"status":"stopped"}

@app.post("/queue/cancel/{task_id}")
async def cancel_task(task_id: str):
    ok = await execution_queue.cancel_task(task_id)
    if not ok: raise HTTPException(400, f"Cannot cancel {task_id}")
    return {"task_id":task_id,"status":"cancelled"}

@app.post("/queue/cancel-all")
async def cancel_all(): return {"cancelled": await execution_queue.cancel_all()}

@app.post("/queue/recover")
async def recover_tasks(limit: int = 100):
    pending = await get_pending_tasks(limit)
    return {"recovered": await execution_queue.recover_from_persistence(pending), "checked": len(pending)}

@app.post("/queue/retention/{days}")
async def queue_retention(days: int):
    return {"deleted": await cleanup_old_queue_tasks(days), "retention_days": days}


# =========================================================================
# Agent Queue Endpoints
# =========================================================================

@app.post("/agent/submit")
async def agent_submit(req: SubmitTaskRequest):
    try:
        tid = await agent_queue.submit_agent_task(
            req.agent_id, req.agent_name, req.capability, req.input_data,
            req.priority, req.timeout or 120, req.max_retries)
        if req.ttl_seconds:
            ttl_registry.set_task_ttl(tid, req.ttl_seconds)
        return {"task_id":tid,"status":"pending"}
    except asyncio.QueueFull as e: raise HTTPException(429, str(e))

@app.post("/agent/execute")
async def agent_execute(req: SubmitTaskRequest):
    try:
        result = await agent_queue.execute_agent_task(
            req.agent_id, req.agent_name, req.capability, req.input_data,
            req.priority, req.timeout or 120, req.max_retries)
        return result
    except asyncio.QueueFull as e: raise HTTPException(429, str(e))

@app.post("/agent/execute/async")
async def agent_execute_async(req: SubmitTaskRequest):
    try:
        tid = await agent_queue.submit_agent_task(
            req.agent_id, req.agent_name, req.capability, req.input_data,
            req.priority, req.timeout or 120, req.max_retries)
        if req.ttl_seconds:
            ttl_registry.set_task_ttl(tid, req.ttl_seconds)
        return {"task_id":tid,"status":"pending","poll_url":f"/agent/task/{tid}"}
    except asyncio.QueueFull as e: raise HTTPException(429, str(e))

@app.get("/agent/task/{task_id}")
async def agent_task_status(task_id: str):
    t = agent_queue.get_task_status(task_id)
    if not t: raise HTTPException(404, f"Task not found: {task_id}")
    return t

@app.get("/agent/tasks")
async def agent_list_tasks(limit: int = 50, agent_id: str = None, status: str = None):
    tasks = agent_queue.list_agent_tasks(agent_id=agent_id, limit=limit, status=status)
    return {"tasks":tasks,"count":len(tasks)}

@app.get("/agent/stats")
async def agent_stats():
    return {"queue":agent_queue.get_queue_stats(),"dlq":agent_queue.get_dlq_stats()}

@app.post("/agent/dlq/{task_id}/requeue")
async def agent_dlq_requeue(task_id: str):
    new_id = await agent_queue.requeue_dlq_task(task_id)
    if not new_id: raise HTTPException(404, f"DLQ entry not found: {task_id}")
    return {"old_task_id":task_id,"new_task_id":new_id,"status":"re-queued"}


# =========================================================================
# Per-Task TTL Endpoints
# =========================================================================

@app.get("/task/{task_id}/ttl")
async def get_task_ttl(task_id: str):
    return {"task_id": task_id, "ttl_seconds": ttl_registry.get_task_ttl(task_id),
            "is_override": ttl_registry.is_override(task_id)}

@app.post("/task/{task_id}/ttl")
async def set_task_ttl(task_id: str, req: TaskTTLRequest):
    ttl_registry.set_task_ttl(task_id, req.ttl_seconds)
    return {"task_id": task_id, "ttl_seconds": req.ttl_seconds, "status": "set"}

@app.delete("/task/{task_id}/ttl")
async def remove_task_ttl(task_id: str):
    ttl_registry.remove_task_ttl(task_id)
    return {"task_id": task_id, "status": "removed"}


# =========================================================================
# DLQ Endpoints
# =========================================================================

@app.get("/dlq/stats")
async def dlq_stats(): return dead_letter_queue.stats()

@app.get("/dlq/list")
async def dlq_list(limit: int = 50):
    entries = dead_letter_queue.list(limit=limit); return {"entries":entries,"count":len(entries)}

@app.get("/dlq/{task_id}")
async def dlq_get(task_id: str):
    e = dead_letter_queue.get(task_id)
    if not e: raise HTTPException(404, f"Not found: {task_id}")
    return e

@app.delete("/dlq/{task_id}")
async def dlq_remove(task_id: str):
    if not dead_letter_queue.remove(task_id): raise HTTPException(404, f"Not found: {task_id}")
    return {"task_id":task_id,"removed":True}

@app.post("/dlq/clear")
async def dlq_clear(): return {"cleared": dead_letter_queue.clear()}

@app.post("/dlq/{task_id}/requeue")
async def dlq_requeue(task_id: str):
    e = dead_letter_queue.get(task_id)
    if not e: raise HTTPException(404, f"Not found: {task_id}")
    dead_letter_queue.remove(task_id)
    try:
        new_id = await execution_queue.submit(
            e.get("agent_id","unknown"), e.get("agent_name","Unknown"),
            e.get("capability","unknown"), e.get("input_data",{}),
            e.get("priority",0), max_retries=e.get("max_retries",2))
        return {"old_task_id":task_id,"new_task_id":new_id,"status":"re-queued"}
    except asyncio.QueueFull as ex: raise HTTPException(429, str(ex))

@app.get("/dlq/alerts/config")
async def get_alert_config():
    return {"webhook_url":DLQAlertConfig.webhook_url,"min_severity":DLQAlertConfig.min_severity,
            "rate_limit_seconds":DLQAlertConfig.rate_limit_seconds}

@app.post("/dlq/alerts/config")
async def set_alert_config(req: DLQAlertConfigRequest):
    DLQAlertConfig.webhook_url = req.webhook_url
    DLQAlertConfig.min_severity = req.min_severity
    DLQAlertConfig.rate_limit_seconds = req.rate_limit_seconds
    return {"status":"updated","webhook_url":DLQAlertConfig.webhook_url,
            "min_severity":DLQAlertConfig.min_severity,"rate_limit_seconds":DLQAlertConfig.rate_limit_seconds}

@app.post("/dlq/alerts/test")
async def test_dlq_webhook():
    if not DLQAlertConfig.webhook_url:
        raise HTTPException(400, "No webhook URL configured")
    test_alert = {"event":"dlq_test","task_id":"test-alert","error":"E2E test",
                  "agent_id":"test","timestamp":datetime.now(timezone.utc).isoformat(),"severity":"info"}
    try:
        import httpx
        async with httpx.AsyncClient() as c:
            resp = await c.post(DLQAlertConfig.webhook_url, json=test_alert, timeout=10)
            return {"sent":True,"status_code":resp.status_code,"response":resp.text[:200]}
    except Exception as e:
        return {"sent":False,"error":str(e)}


# =========================================================================
# TTL Config
# =========================================================================

@app.get("/ttl/config")
async def get_ttl_config(): return {"ttl_seconds":ttl_manager.ttl_seconds,"cleanup_interval":3600}

@app.post("/ttl/config")
async def set_ttl_config(req: TTLConfigRequest):
    ttl_manager.set_ttl(req.ttl_seconds)
    return {"status":"updated","ttl_seconds":ttl_manager.ttl_seconds,"cleanup_interval":req.cleanup_interval}


# =========================================================================
# WebSocket Token Endpoints
# =========================================================================

@app.post("/ws/token")
async def create_ws_token(req: WSTokenRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        raise HTTPException(429, f"Rate limit exceeded. Max {TOKEN_RATE_LIMIT} tokens per {TOKEN_RATE_WINDOW}s.")
    token = generate_ws_token(req.agent_id)
    return {"token":token,"expires_in":WS_TOKEN_TTL,"agent_id":req.agent_id}

@app.get("/ws/tokens")
async def list_ws_tokens():
    return {"active_tokens": _count_tokens(), "tokens": _list_tokens()}

@app.delete("/ws/token/{token}")
async def revoke_ws_token(token: str):
    if not _delete_token(token): raise HTTPException(404, "Token not found")
    return {"revoked": True}

@app.get("/ws/rate-limit")
async def ws_rate_limit_info(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    return get_rate_limit_info(client_ip)


# =========================================================================
# Integration Test Endpoints
# =========================================================================

@app.post("/ws/integration-test")
async def ws_integration_test():
    results = {}
    token = generate_ws_token("integration-test")
    results["token_generated"] = token is not None
    results["token_valid"] = validate_ws_token(token)
    results["invalid_token_rejected"] = not validate_ws_token("invalid-token-12345")
    results["empty_token_rejected"] = not validate_ws_token("")
    results["token_revoked"] = _delete_token(token)
    results["revoked_token_rejected"] = not validate_ws_token(token)
    results["rate_limit_works"] = check_rate_limit("test-ip-integration")
    results["rate_limit_info"] = get_rate_limit_info("test-ip-integration")
    all_passed = all(v for k, v in results.items() if k != "rate_limit_info" and isinstance(v, bool))
    results["all_passed"] = all_passed
    return {"test": "websocket_integration", "results": results, "passed": all_passed}

@app.post("/execution/test")
async def execution_test():
    """Test real execution pipeline via AI Gateway."""
    if not execution_queue._executor:
        return {"test": "real_execution", "status": "skipped", "reason": "No executor set"}
    try:
        result = await agent_queue.execute_agent_task(
            agent_id="exec-test", agent_name="Execution Test",
            capability="chat", input_data={"prompt": "Hello, this is a test."},
            timeout=30, max_retries=0)
        return {"test": "real_execution", "status": "completed" if result.get("status") == "completed" else "failed", "result": result}
    except Exception as e:
        return {"test": "real_execution", "status": "error", "error": str(e)}

@app.post("/execution/e2e-test")
async def e2e_execution_test():
    """End-to-end execution test: submit → queue → gateway_executor → AI Gateway → result."""
    if not execution_queue._executor:
        return {"test": "e2e_execution", "status": "skipped", "reason": "No executor set"}
    
    results = {}
    
    # 1. Verify queue is running
    results["queue_running"] = execution_queue._running
    
    # 2. Verify gateway is reachable
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5) as c:
            gw_resp = await c.get(f"{GATEWAY_URL}/health")
            results["gateway_reachable"] = gw_resp.status_code == 200
            results["gateway_status"] = gw_resp.json() if results["gateway_reachable"] else None
    except Exception as e:
        results["gateway_reachable"] = False
        results["gateway_error"] = str(e)
    
    # 3. Submit a test task and wait for result
    try:
        result = await agent_queue.execute_agent_task(
            agent_id="e2e-test", agent_name="E2E Test",
            capability="chat", input_data={"prompt": "Say 'E2E test successful' in exactly 3 words."},
            timeout=30, max_retries=0)
        results["task_result"] = result
        results["task_status"] = result.get("status", "unknown")
        results["task_completed"] = result.get("status") == "completed"
        if result.get("output"):
            results["task_output"] = result["output"]
    except Exception as e:
        results["task_error"] = str(e)
        results["task_completed"] = False
    
    # 4. Check DLQ for any failures
    results["dlq_count"] = dead_letter_queue.stats()["total"]
    
    all_passed = (
        results.get("queue_running", False) and
        results.get("gateway_reachable", False) and
        results.get("task_completed", False) and
        results.get("dlq_count", 1) == 0
    )
    results["all_passed"] = all_passed
    
    return {"test": "e2e_execution", "results": results, "passed": all_passed}


# =========================================================================
# WebSocket Client Library Info Endpoint
# =========================================================================

@app.get("/ws/client-library")
async def ws_client_library():
    """Return WebSocket client library code snippets for easy integration."""
    return {
        "python": '''
import asyncio
import json
import websockets

class EvolvixOSWSClient:
    def __init__(self, base_url, token):
        self.url = f"{base_url}/ws?token={token}"
        self.ws = None
    
    async def connect(self):
        self.ws = await websockets.connect(self.url)
        # Receive initial state
        msg = await self.ws.recv()
        return json.loads(msg)
    
    async def listen(self):
        while True:
            msg = await self.ws.recv()
            data = json.loads(msg)
            if data.get("type") == "queue_stats":
                yield data["data"]
    
    async def ping(self):
        await self.ws.send("ping")
        msg = await self.ws.recv()
        return json.loads(msg)
    
    async def close(self):
        if self.ws:
            await self.ws.close()

# Usage:
# client = EvolvixOSWSClient("ws://localhost:4300", "your-token")
# await client.connect()
# async for stats in client.listen():
#     print(stats)
''',
        "typescript": '''
import WebSocket from 'ws';

class EvolvixOSWSClient {
  private ws: WebSocket | null = null;
  
  constructor(private baseUrl: string, private token: string) {}
  
  async connect(): Promise<any> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(`${this.baseUrl}/ws?token=${this.token}`);
      this.ws.on('open', () => {});
      this.ws.on('message', (data: string) => {
        const msg = JSON.parse(data);
        if (msg.type === 'queue_stats') resolve(msg.data);
      });
      this.ws.on('error', reject);
    });
  }
  
  onStats(callback: (stats: any) => void) {
    if (this.ws) {
      this.ws.on('message', (data: string) => {
        const msg = JSON.parse(data);
        if (msg.type === 'queue_stats') callback(msg.data);
      });
    }
  }
  
  ping() {
    this.ws?.send('ping');
  }
  
  close() {
    this.ws?.close();
  }
}

// Usage:
// const client = new EvolvixOSWSClient('ws://localhost:4300', 'your-token');
// await client.connect();
// client.onStats((stats) => console.log(stats));
''',
        "curl": 'curl -N -H "Connection: Upgrade" -H "Upgrade: websocket" "http://localhost:4300/ws?token=YOUR_TOKEN"',
    }


# =========================================================================
# WebSocket Endpoint (secure)
# =========================================================================

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, token: str = Query(None)):
    if not validate_ws_token(token or ""):
        await ws.close(code=4001, reason="Invalid or missing token")
        return
    await ws_manager.connect(ws)
    try:
        stats = execution_queue.stats()
        stats["dlq"] = dead_letter_queue.stats()
        stats["timestamp"] = datetime.now(timezone.utc).isoformat()
        await ws.send_text(json.dumps({"type":"queue_stats","data":stats}))
        while True:
            data = await ws.receive_text()
            # Message-level auth: validate token on each message
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping" or data == "ping":
                    await ws.send_text(json.dumps({"type":"pong"}))
                    continue
                # For authenticated messages, validate token
                if "token" in msg:
                    if not validate_ws_token(msg["token"]):
                        await ws.send_text(json.dumps({"type":"error","code":4003,"message":"Invalid token"}))
                        await ws.close(code=4003, reason="Invalid message token")
                        ws_manager.disconnect(ws)
                        return
                # Process authenticated message
                if msg.get("type") == "subscribe":
                    await ws.send_text(json.dumps({"type":"subscribed","channel":msg.get("channel","all")}))
                elif msg.get("type") == "get_stats":
                    stats = execution_queue.stats()
                    stats["dlq"] = dead_letter_queue.stats()
                    stats["timestamp"] = datetime.now(timezone.utc).isoformat()
                    await ws.send_text(json.dumps({"type":"queue_stats","data":stats}))
            except json.JSONDecodeError:
                # Non-JSON message, treat as ping
                if data == "ping":
                    await ws.send_text(json.dumps({"type":"pong"}))
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
    except Exception:
        ws_manager.disconnect(ws)
