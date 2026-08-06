"""
EvolvixOS Agent Orchestration API
REST API for creating, executing, and managing multi-agent workflows
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import structlog

from orchestration_engine import (
    registry, executor, Workflow, WorkflowStep, WorkflowStatus,
    StepType, WorkflowTemplate
)

logger = structlog.get_logger()

app = FastAPI(
    title="EvolvixOS Agent Orchestration",
    description="Multi-agent workflow orchestration engine",
    version="1.0.0",
)


# =========================================================================
# Request Models
# =========================================================================

class StepDefinition(BaseModel):
    name: str
    step_type: str = "agent_task"
    config: Dict[str, Any] = {}
    depends_on: List[str] = []
    max_retries: int = 3


class CreateWorkflowRequest(BaseModel):
    name: str
    description: str = ""
    steps: List[StepDefinition]
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class CreateFromTemplateRequest(BaseModel):
    template_id: str
    input_data: Dict[str, Any] = {}
    tags: List[str] = []


# =========================================================================
# Endpoints
# =========================================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "executor_stats": executor.stats,
    }

@app.get("/stats")
async def stats():
    return {
        "executor": executor.stats,
        "total_workflows": len(registry._workflows),
        "total_templates": len(registry._templates),
    }

# --- Workflow CRUD ---

@app.post("/workflows")
async def create_workflow(req: CreateWorkflowRequest):
    """Create a new workflow"""
    step_defs = [s.model_dump() for s in req.steps]
    workflow = await registry.create_workflow(
        name=req.name,
        description=req.description,
        step_defs=step_defs,
        tags=req.tags,
        metadata=req.metadata,
    )
    return workflow.to_dict()

@app.get("/workflows")
async def list_workflows(status: str = None):
    """List all workflows"""
    workflows = await registry.list_workflows(status)
    return {"workflows": [w.to_dict() for w in workflows], "count": len(workflows)}

@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get a workflow by ID"""
    workflow = await registry.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow.to_dict()

@app.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete a workflow"""
    deleted = await registry.delete_workflow(workflow_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"success": True, "deleted": workflow_id}

# --- Workflow Execution ---

@app.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str):
    """Execute a workflow"""
    try:
        result = await executor.execute(workflow_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/workflows/{workflow_id}/cancel")
async def cancel_workflow(workflow_id: str):
    """Cancel a running workflow"""
    cancelled = await executor.cancel(workflow_id)
    if not cancelled:
        raise HTTPException(status_code=400, detail="Workflow not running or not found")
    return {"success": True, "cancelled": workflow_id}

# --- Templates ---

@app.get("/templates")
async def list_templates():
    """List all workflow templates"""
    templates = await registry.list_templates()
    return {"templates": [t.to_dict() for t in templates], "count": len(templates)}

@app.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a template by ID"""
    template = await registry.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template.to_dict()

@app.post("/templates/instantiate")
async def instantiate_template(req: CreateFromTemplateRequest):
    """Create a workflow from a template"""
    try:
        workflow = await registry.create_from_template(
            template_id=req.template_id,
            input_data=req.input_data,
            tags=req.tags,
        )
        return workflow.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Step inspection ---

@app.get("/workflows/{workflow_id}/steps")
async def list_steps(workflow_id: str):
    """List all steps in a workflow"""
    workflow = await registry.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"steps": [s.to_dict() for s in workflow.steps], "count": len(workflow.steps)}

@app.get("/workflows/{workflow_id}/steps/{step_id}")
async def get_step(workflow_id: str, step_id: str):
    """Get a specific step"""
    workflow = await registry.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    for step in workflow.steps:
        if step.id == step_id:
            return step.to_dict()
    raise HTTPException(status_code=404, detail="Step not found")
