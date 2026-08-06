"""
EvolvixOS Plugin Sandbox API
REST API for sandboxed plugin execution and execution persistence.
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import asyncio
import structlog

from plugin_sandbox import (
    SandboxManager, SandboxConfig, SandboxLevel,
    ExecutionPersistence, sandbox_manager, persistence,
    get_sandbox_config, DEFAULT_SANDBOX_CONFIGS
)
from pg_persistence import PostgresExecutionPersistence

logger = structlog.get_logger()

app = FastAPI(
    title="EvolvixOS Plugin Sandbox API",
    description="Sandboxed plugin execution with resource isolation and execution persistence",
    version="2.0.0",
)

# Initialize PostgreSQL persistence with retry logic
pg_persist = PostgresExecutionPersistence()

MAX_RETRIES = 3
RETRY_DELAY = 2

async def init_pg_persistence():
    """Initialize PostgreSQL connection with retry logic."""
    for attempt in range(MAX_RETRIES):
        connected = await pg_persist.connect()
        if connected:
            logger.info(f"PostgreSQL persistence connected on attempt {attempt + 1}")
            return True
        logger.warning(f"PG connection attempt {attempt + 1} failed, retrying in {RETRY_DELAY}s...")
        await asyncio.sleep(RETRY_DELAY)
    logger.warning("PostgreSQL persistence: using in-memory fallback")
    return False

async def cleanup_old_records(retention_days: int = 30):
    """Delete execution records older than retention period."""
    if not pg_persist.is_connected or not pg_persist._pool:
        return 0
    try:
        async with pg_persist._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM agent_executions WHERE timestamp < NOW() - INTERVAL '%s days'" % retention_days
            )
            deleted = int(result.split()[-1]) if result else 0
            if deleted > 0:
                logger.info(f"Retention cleanup: deleted {deleted} records older than {retention_days} days")
            return deleted
    except Exception as e:
        logger.warning(f"Retention cleanup failed: {e}")
        return 0

@app.on_event("startup")
async def startup_event():
    await init_pg_persistence()

@app.on_event("shutdown")
async def shutdown_event():
    await pg_persist.close()


class ExecuteSandboxedRequest(BaseModel):
    plugin_module: str = Field(..., description="Python module name")
    plugin_class: str = Field(..., description="Plugin class name")
    capability: str = Field(..., description="Capability to execute")
    input_data: Dict[str, Any] = Field(default_factory=dict)
    options: Dict[str, Any] = Field(default_factory=dict)
    config_override: Optional[Dict[str, Any]] = None


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "sandbox": sandbox_manager.health_check(),
        "persistence": persistence.stats(),
        "postgres": await pg_persist.stats(),
    }

@app.get("/sandbox/stats")
async def sandbox_stats():
    return sandbox_manager.stats()

@app.get("/sandbox/configs")
async def list_sandbox_configs():
    return {ptype: cfg.to_dict() for ptype, cfg in DEFAULT_SANDBOX_CONFIGS.items()}

@app.get("/sandbox/config/{plugin_type}")
async def get_config(plugin_type: str):
    config = get_sandbox_config(plugin_type)
    return config.to_dict()

@app.post("/sandbox/execute")
async def execute_sandboxed(req: ExecuteSandboxedRequest):
    """Execute a plugin in a sandboxed environment."""
    config = get_sandbox_config("llm_provider")
    if req.config_override:
        config_dict = config.to_dict()
        config_dict.update(req.config_override)
        config = SandboxConfig(
            level=SandboxLevel(config_dict.get("level", "basic")),
            cpu_limit_seconds=config_dict.get("cpu_limit_seconds", 30),
            memory_limit_mb=config_dict.get("memory_limit_mb", 512),
            timeout_seconds=config_dict.get("timeout_seconds", 60),
            allow_network=config_dict.get("allow_network", True),
            allow_filesystem_read=config_dict.get("allow_filesystem_read", []),
            allow_filesystem_write=config_dict.get("allow_filesystem_write", []),
            max_output_size=config_dict.get("max_output_size", 1024 * 1024),
            env_whitelist=config_dict.get("env_whitelist", []),
        )
    
    result = await sandbox_manager.execute_sandboxed(
        plugin_module=req.plugin_module,
        plugin_class=req.plugin_class,
        capability=req.capability,
        input_data=req.input_data,
        options=req.options,
        config=config,
    )
    
    # Persist to both JSONL (fallback) and PostgreSQL
    persistence.record(result)
    await pg_persist.record(result)
    
    return result

@app.get("/sandbox/health")
async def sandbox_health():
    return sandbox_manager.health_check()

@app.get("/persistence/stats")
async def persistence_stats():
    """Get combined persistence stats (JSONL + PostgreSQL)."""
    return {
        "jsonl": persistence.stats(),
        "postgres": await pg_persist.stats(),
    }

@app.get("/persistence/pg/stats")
async def pg_stats():
    """Get PostgreSQL-specific persistence stats."""
    return await pg_persist.stats()

@app.get("/persistence/pg/query")
async def pg_query(limit: int = 100, agent_id: str = None, status: str = None, provider: str = None):
    """Query execution records from PostgreSQL."""
    results = await pg_persist.query(limit=limit, agent_id=agent_id, status=status, provider=provider)
    return {"executions": results, "count": len(results)}

@app.post("/persistence/retention/{days}")
async def run_retention_cleanup(days: int):
    """Delete execution records older than the specified number of days."""
    deleted = await cleanup_old_records(days)
    return {"deleted": deleted, "retention_days": days}

@app.post("/persistence/pg/init")
async def init_pg():
    """Manually initialize PostgreSQL connection."""
    result = await init_pg_persistence()
    return {"connected": result}

@app.get("/persistence/query")
async def query_executions(limit: int = 100, agent_id: str = None, status: str = None, start_date: str = None):
    """Query persisted execution records (JSONL fallback)."""
    results = persistence.query(limit=limit, agent_id=agent_id, status=status, start_date=start_date)
    return {"executions": results, "count": len(results)}

@app.post("/persistence/flush")
async def flush_persistence():
    """Flush buffered execution records to disk."""
    persistence._flush()
    return {"flushed": True, "stats": persistence.stats()}
