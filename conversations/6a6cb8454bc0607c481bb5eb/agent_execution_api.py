"""
EvolvixOS Agent Execution API
REST API for executing core agents and multi-agent pipelines via the AI Gateway.
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import structlog

from core_agents import AgentRole, get_agent, agents_summary
from agent_execution import engine, orchestrator

logger = structlog.get_logger()

app = FastAPI(
    title="EvolvixOS Agent Execution API",
    description="Execute core agents and multi-agent pipelines via AI Gateway",
    version="1.0.0",
)


# =========================================================================
# Request Models
# =========================================================================

class ExecuteRequest(BaseModel):
    role: str = Field(..., description="Agent role to execute")
    input_data: Dict[str, Any] = Field(default_factory=dict)
    options: Dict[str, Any] = Field(default_factory=dict)

class PipelineRequest(BaseModel):
    steps: List[Dict[str, Any]] = Field(..., description="List of pipeline steps")

class ParallelRequest(BaseModel):
    tasks: List[Dict[str, Any]] = Field(..., description="List of parallel tasks")

class CodeReviewPipelineRequest(BaseModel):
    code: str
    language: str = "python"

class ArchitectureReviewRequest(BaseModel):
    description: str
    constraints: Dict[str, Any] = {}


class RouteAgentRequest(BaseModel):
    role: str
    input_data: Dict[str, Any] = {}


# =========================================================================
# Endpoints
# =========================================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "gateway_url": engine.gateway_url,
        "stats": engine.stats(),
    }

@app.post("/execute")
async def execute_agent(req: ExecuteRequest):
    """Execute a single core agent via the AI Gateway."""
    try:
        agent_role = AgentRole(req.role)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Unknown role: {req.role}")
    
    agent = get_agent(agent_role)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    result = await engine.execute(agent, req.input_data, req.options)
    return result

@app.post("/pipeline")
async def execute_pipeline(req: PipelineRequest):
    """Execute a sequence of agent invocations with context passing."""
    results = await orchestrator.execute_pipeline(req.steps)
    return {"results": results, "count": len(results)}

@app.post("/parallel")
async def execute_parallel(req: ParallelRequest):
    """Execute multiple agent invocations in parallel."""
    results = await orchestrator.execute_parallel(req.tasks)
    return {"results": results, "count": len(results)}

@app.post("/pipeline/code-review")
async def code_review_pipeline(req: CodeReviewPipelineRequest):
    """Full code review pipeline: Security → Code Review → Performance."""
    return await orchestrator.code_review_pipeline(req.code, req.language)

@app.post("/pipeline/architecture-review")
async def architecture_review_pipeline(req: ArchitectureReviewRequest):
    """Full architecture review: Architecture → Planning → Security → DevOps."""
    return await orchestrator.architecture_review_pipeline(req.description, req.constraints)

@app.get("/executions")
async def list_executions(limit: int = 50, agent_id: str = None):
    """Get execution history."""
    return {"executions": engine.get_history(limit=limit, agent_id=agent_id)}

@app.get("/executions/active")
async def active_executions():
    """Get currently active executions."""
    return {"active": engine.get_active()}

@app.get("/stats")
async def execution_stats():
    """Get execution statistics."""
    return engine.stats()

@app.get("/agents")
async def list_executable_agents():
    """List all agents available for execution."""
    summary = agents_summary()
    return {
        "total": summary["total"],
        "agents": [
            {"id": a["id"], "role": a["role"], "name": a["name"], "capability": a["preferred_capability"]}
            for a in summary["agents"]
        ],
    }
