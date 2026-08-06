"""
EvolvixOS Queue API v3.2
+ WebSocket tokens persisted in Redis (survive restarts)
+ Rate limiting on token generation (10 tokens/minute per IP)
+ Secure default: requires token always (no open access)
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
    description="Async execution queue with Redis-persisted WebSocket auth and rate limiting",
    version="3.2.0",
)

# =========================================================================
# Redis for WebSocket Token Persistence
# =========================================================================

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_redis_client: Optional[redis.Redis] = None
WS_TOKEN_PREFIX = "ws_token:"
WS_TOKEN_TTL = 3600  # 1 hour

# In-memory fallback
_FALLBACK_TOKENS: Dict[str, Dict] = {}


def init_redis():
    """Initialize Redis client, fall back to in-memory if unavailable."""
    global _redis_client
    try:
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        _redis_client.ping()
        logger.info("WebSocket token Redis connected")
        return True
    except Exception as e:
        logger.warning(f"Redis unavailable, using in-memory tokens: {e}")
        _redis_client = None
        return False


def _store_token(token: str, agent_id: str, ttl: int = WS_TOKEN_TTL):
    """Store a WebSocket token in Redis (or in-memory fallback)."""
    token_data = json.dumps({
        "agent_id": agent_id,
        "created_at": time.time(),
        "expires_at": time.time() + ttl,
    })
    if _redis_client:
        _redis_client.setex(f"{WS_TOKEN_PREFIX}{token}", ttl, token_data)
    else:
        _FALLBACK_TOKENS[token] = json.loads(token_data)


def _get_token(token: str) -> Optional[Dict]:
    """Get a WebSocket token from Redis (or in-memory fallback)."""
    if _redis_client:
        data = _redis_client.get(f"{WS_TOKEN_PREFIX}{token}")
        if data:
            return json.loads(data)
        return None
    else:
        return _FALLBACK_TOKENS.get(token)


def _delete_token(token: str) -> bool:
    """Delete a WebSocket token."""
    if _redis_client:
        deleted = _redis_client.delete(f"{WS_TOKEN_PREFIX}{token}")
        return deleted > 0
    else:
        if token in _FALLBACK_TOKENS:
            del _FALLBACK_TOKENS[token]
            return True
        return False


def _count_tokens() -> int:
    """Count active tokens."""
    if _redis_client:
        return len(_redis_client.keys(f"{WS_TOKEN_PREFIX}*"))
    else:
        return len(_FALLBACK_TOKENS)


def _list_tokens() -> List[Dict]:
    """List all active tokens (without token values)."""
    result = []
    if _redis_client:
        keys = _redis_client.keys(f"{WS_TOKEN_PREFIX}*")
        for key in keys:
            data = _redis_client.get(key)
            if data:
                parsed = json.loads(data)
                result.append({"agent_id": parsed["agent_id"],
                              "expires_at": datetime.fromtimestamp(parsed["expires_at"], tz=timezone.utc).isoformat()})
    else:
        for token, data in _FALLBACK_TOKENS.items():
            result.append({"agent_id": data["agent_id"],
                          "expires_at": datetime.fromtimestamp(data["expires_at"], tz=timezone.utc).isoformat()})
    return result


def generate_ws_token(agent_id: str = "default") -> str:
    token = secrets.token_urlsafe(32)
    _store_token(token, agent_id)
    return token


def validate_ws_token(token: str) -> bool:
    if not token:
        return False
    data = _get_token(token)
    if not data:
        return False
    if time.time() > data.get("expires_at", 0):
        _delete_token(token)
        return False
    return True


# =========================================================================
# Rate Limiting for Token Generation
# =========================================================================

TOKEN_RATE_LIMIT = 10  # max tokens per minute per IP
TOKEN_RATE_WINDOW = 60  # 1 minute window
_rate_limit_store: Dict[str, deque] = defaultdict(deque)


def check_rate_limit(ip: str) -> bool:
    """Check if IP is within rate limit for token generation."""
    now = time.time()
    ip_requests = _rate_limit_store[ip]
    
    # Remove old entries outside the window
    while ip_requests and ip_requests[0] < now - TOKEN_RATE_WINDOW:
        ip_requests.popleft()
    
    if len(ip_requests) >= TOKEN_RATE_LIMIT:
        return False
    
    ip_requests.append(now)
    return True


def get_rate_limit_info(ip: str) -> Dict[str, Any]:
    """Get rate limit info for an IP."""
    now = time.time()
    ip_requests = _rate_limit_store[ip]
    while ip_requests and ip_requests[0] < now - TOKEN_RATE_WINDOW:
        ip_requests.popleft()
    return {
        "requests": len(ip_requests),
        "limit": TOKEN_RATE_LIMIT,
        "window_seconds": TOKEN_RATE_WINDOW,
        "remaining": max(0, TOKEN_RATE_LIMIT - len(ip_requests)),
    }


# =========================================================================
# PostgreSQL Persistence
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
        cls._last_alert_time = now
        return True


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
    await ttl_manager.start_periodic_cleanup(execution_queue)
    scheduled_retention.set_cleanup_callback(cleanup_old_queue_tasks)
    await scheduled_retention.start(86400)
    await ws_manager.start_periodic_broadcast(5)
    logger.info("Queue API v3.2 startup complete")


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

class TTLConfigRequest(BaseModel):
    ttl_seconds: int = DEFAULT_TASK_TTL_SECONDS; cleanup_interval: int = 3600

class DLQAlertConfigRequest(BaseModel):
    webhook_url: Optional[str] = None; min_severity: str = "warning"; rate_limit_seconds: int = 60

class WSTokenRequest(BaseModel):
    agent_id: str = "default"


# =========================================================================
# Queue Endpoints
# =========================================================================

@app.get("/health")
async def health():
    return {"status":"healthy","version":"3.2.0","pg_connected":_pg_pool is not None,
            "redis_connected":_redis_client is not None,
            "queue":execution_queue.stats(),"dlq":dead_letter_queue.stats(),
            "ttl_seconds":ttl_manager.ttl_seconds,"ws_connections":ws_manager.count,
            "ws_tokens":_count_tokens()}

@app.get("/queue/stats")
async def queue_stats():
    s = execution_queue.stats()
    s["pg_connected"] = _pg_pool is not None; s["dlq"] = dead_letter_queue.stats()
    return s

@app.post("/queue/submit")
async def submit_task(req: SubmitTaskRequest):
    try:
        tid = await execution_queue.submit(req.agent_id, req.agent_name, req.capability,
            req.input_data, req.options, req.priority, req.timeout, req.max_retries)
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
# WebSocket Token Endpoints (with rate limiting)
# =========================================================================

@app.post("/ws/token")
async def create_ws_token(req: WSTokenRequest, request: Request):
    """Generate a WebSocket authentication token (rate limited)."""
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        info = get_rate_limit_info(client_ip)
        raise HTTPException(429, f"Rate limit exceeded. Max {TOKEN_RATE_LIMIT} tokens per {TOKEN_RATE_WINDOW}s. Retry after {TOKEN_RATE_WINDOW}s.")
    
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
    """Get rate limit info for the requesting IP."""
    client_ip = request.client.host if request.client else "unknown"
    return get_rate_limit_info(client_ip)


# =========================================================================
# WebSocket Endpoint (secure — always requires token)
# =========================================================================

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, token: str = Query(None)):
    """WebSocket — always requires valid token."""
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
            if data == "ping":
                await ws.send_text(json.dumps({"type":"pong"}))
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
    except Exception:
        ws_manager.disconnect(ws)
