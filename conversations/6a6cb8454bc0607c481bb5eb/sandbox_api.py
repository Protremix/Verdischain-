"""
EvolvixOS Plugin Sandbox API
REST API for sandboxed plugin execution and execution persistence.
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import structlog

from plugin_sandbox import (
    SandboxManager, SandboxConfig, SandboxLevel,
    ExecutionPersistence, sandbox_manager, persistence,
    get_sandbox_config, DEFAULT_SANDBOX_CONFIGS
)

logger = structlog.get_logger()

app = FastAPI(
    title="EvolvixOS Plugin Sandbox API",
    description="Sandboxed plugin execution with resource isolation and execution persistence",
    version="1.0.0",
)


class ExecuteSandboxedRequest(BaseModel):
    plugin_module: str = Field(..., description="Python module name")
    plugin_class: str = Field(..., description="Plugin class name")
    capability: str = Field(..., description="Capability to execute")
    input_data: Dict[str, Any] = Field(default_factory=dict)
    options: Dict[str, Any] = Field(default_factory=dict)
    config_override: Optional[Dict[str, Any]] = None


class ExecutionQueryRequest(BaseModel):
    limit: int = 100
    agent_id: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[str] = None


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "sandbox": sandbox_manager.health_check(),
        "persistence": persistence.stats(),
    }

@app.get("/sandbox/stats")
async def sandbox_stats():
    return sandbox_manager.stats()

@app.get("/sandbox/configs")
async def list_sandbox_configs():
    """List default sandbox configurations by plugin type."""
    return {
        ptype: cfg.to_dict()
        for ptype, cfg in DEFAULT_SANDBOX_CONFIGS.items()
    }

@app.get("/sandbox/config/{plugin_type}")
async def get_config(plugin_type: str):
    """Get sandbox config for a specific plugin type."""
    config = get_sandbox_config(plugin_type)
    return config.to_dict()

@app.post("/sandbox/execute")
async def execute_sandboxed(req: ExecuteSandboxedRequest):
    """Execute a plugin in a sandboxed environment."""
    config = get_sandbox_config(req.plugin_type if hasattr(req, 'plugin_type') else "llm_provider")
    
    if req.config_override:
        # Apply overrides
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
    
    # Persist result
    persistence.record(result)
    
    return result

@app.get("/sandbox/health")
async def sandbox_health():
    return sandbox_manager.health_check()

@app.get("/persistence/stats")
async def persistence_stats():
    return persistence.stats()

@app.get("/persistence/query")
async def query_executions(
    limit: int = 100,
    agent_id: str = None,
    status: str = None,
    start_date: str = None,
):
    """Query persisted execution records."""
    results = persistence.query(
        limit=limit,
        agent_id=agent_id,
        status=status,
        start_date=start_date,
    )
    return {"executions": results, "count": len(results)}

@app.post("/persistence/flush")
async def flush_persistence():
    """Flush buffered execution records to disk."""
    persistence._flush()
    return {"flushed": True, "stats": persistence.stats()}
