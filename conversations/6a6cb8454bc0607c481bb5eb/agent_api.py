"""
EvolvixOS Agent Framework — FastAPI Endpoints
Exposes agent lifecycle, task management, and memory operations as REST API
"""

from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid
import structlog

from agent_framework import (
    AgentManager, MemoryManager, Agent, Task, MemoryEntry,
    AgentStatus, TaskStatus, TaskPriority, AgentCapability, MemoryType,
)

logger = structlog.get_logger()

# Initialize
memory_manager = MemoryManager()
agent_manager = AgentManager(memory_manager, gateway_url="http://localhost:3500")

app = FastAPI(
    title="EvolvixOS Agent Framework",
    description="Autonomous AI agent lifecycle, task execution, and persistent memory",
    version="1.0.0",
)

# =========================================================================
# Request/Response Models
# =========================================================================

class CreateAgentRequest(BaseModel):
    name: str
    description: str = ""
    capabilities: List[str] = ["chat"]
    system_prompt: str = ""
    model: str = "gpt-4o"
    config: Dict[str, Any] = {}
    tags: List[str] = []

class UpdateAgentRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    max_concurrent_tasks: Optional[int] = None

class CreateTaskRequest(BaseModel):
    task_type: str
    input_data: Dict[str, Any]
    priority: int = 2
    timeout: int = 120
    parent_task_id: Optional[str] = None

class StoreMemoryRequest(BaseModel):
    key: str
    value: Any
    memory_type: str = "long_term"
    context: Dict[str, Any] = {}
    importance: float = 0.5
    ttl_seconds: Optional[int] = None

class UpdateMemoryRequest(BaseModel):
    value: Any
    importance: Optional[float] = None

# =========================================================================
# Agent Endpoints
# =========================================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "agents": agent_manager.get_framework_stats(),
    }

@app.post("/agents")
async def create_agent(req: CreateAgentRequest):
    """Create a new AI agent"""
    capabilities = [AgentCapability(c) for c in req.capabilities]
    agent = agent_manager.create_agent(
        name=req.name,
        description=req.description,
        capabilities=capabilities,
        system_prompt=req.system_prompt,
        model=req.model,
        config=req.config,
        tags=req.tags,
    )
    return agent.to_dict()

@app.get("/agents")
async def list_agents(status: Optional[str] = None):
    """List all agents, optionally filtered by status"""
    agent_status = AgentStatus(status) if status else None
    agents = agent_manager.list_agents(status=agent_status)
    return {"agents": [a.to_dict() for a in agents], "count": len(agents)}

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get a specific agent"""
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.to_dict()

@app.patch("/agents/{agent_id}")
async def update_agent(agent_id: str, req: UpdateAgentRequest):
    """Update agent properties"""
    updates = {k: v for k, v in req.dict().items() if v is not None}
    agent = agent_manager.update_agent(agent_id, **updates)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.to_dict()

@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent and its memories"""
    success = agent_manager.delete_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"success": True, "agent_id": agent_id}

@app.post("/agents/{agent_id}/start")
async def start_agent(agent_id: str):
    """Start an agent"""
    success = agent_manager.start_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"success": True, "agent_id": agent_id, "status": "running"}

@app.post("/agents/{agent_id}/pause")
async def pause_agent(agent_id: str):
    """Pause an agent"""
    success = agent_manager.pause_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"success": True, "agent_id": agent_id, "status": "paused"}

@app.post("/agents/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """Stop an agent"""
    success = agent_manager.stop_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"success": True, "agent_id": agent_id, "status": "stopped"}

@app.get("/agents/{agent_id}/stats")
async def agent_stats(agent_id: str):
    """Get agent statistics"""
    stats = agent_manager.get_agent_stats(agent_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Agent not found")
    return stats

# =========================================================================
# Task Endpoints
# =========================================================================

@app.post("/agents/{agent_id}/tasks")
async def create_task(agent_id: str, req: CreateTaskRequest):
    """Create a task for an agent"""
    task = agent_manager.create_task(
        agent_id=agent_id,
        task_type=req.task_type,
        input_data=req.input_data,
        priority=TaskPriority(req.priority),
        timeout=req.timeout,
        parent_task_id=req.parent_task_id,
    )
    if not task:
        raise HTTPException(status_code=400, detail="Agent not found or not running")
    return task.to_dict()

@app.post("/agents/{agent_id}/tasks/{task_id}/execute")
async def execute_task(agent_id: str, task_id: str):
    """Execute a task (calls the AI Gateway)"""
    task = agent_manager.get_task(task_id)
    if not task or task.agent_id != agent_id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    result = await agent_manager.execute_task(task_id)
    if not result:
        raise HTTPException(status_code=500, detail="Task execution failed")
    return result.to_dict()

@app.get("/tasks")
async def list_tasks(
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, le=200),
):
    """List tasks, optionally filtered"""
    task_status = TaskStatus(status) if status else None
    tasks = agent_manager.list_tasks(agent_id=agent_id, status=task_status, limit=limit)
    return {"tasks": [t.to_dict() for t in tasks], "count": len(tasks)}

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a specific task"""
    task = agent_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()

@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel a task"""
    success = agent_manager.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or already completed")
    return {"success": True, "task_id": task_id, "status": "cancelled"}

# =========================================================================
# Memory Endpoints
# =========================================================================

@app.post("/agents/{agent_id}/memory")
async def store_memory(agent_id: str, req: StoreMemoryRequest):
    """Store a memory entry for an agent"""
    entry = memory_manager.store(
        agent_id=agent_id,
        key=req.key,
        value=req.value,
        memory_type=MemoryType(req.memory_type),
        context=req.context,
        importance=req.importance,
        ttl_seconds=req.ttl_seconds,
    )
    return entry.to_dict()

@app.get("/agents/{agent_id}/memory/{key}")
async def get_memory(agent_id: str, key: str):
    """Retrieve a memory entry by key"""
    entry = memory_manager.retrieve(agent_id, key)
    if not entry:
        raise HTTPException(status_code=404, detail="Memory not found")
    return entry.to_dict()

@app.get("/agents/{agent_id}/memory")
async def list_memory(agent_id: str, memory_type: Optional[str] = None):
    """List all memories for an agent"""
    mem_type = MemoryType(memory_type) if memory_type else None
    entries = memory_manager.retrieve_all(agent_id, mem_type)
    return {"memories": [e.to_dict() for e in entries], "count": len(entries)}

@app.patch("/agents/{agent_id}/memory/{key}")
async def update_memory(agent_id: str, key: str, req: UpdateMemoryRequest):
    """Update a memory entry"""
    entry = memory_manager.update(agent_id, key, req.value, req.importance)
    if not entry:
        raise HTTPException(status_code=404, detail="Memory not found")
    return entry.to_dict()

@app.delete("/agents/{agent_id}/memory/{key}")
async def delete_memory(agent_id: str, key: str):
    """Delete a memory entry"""
    success = memory_manager.delete(agent_id, key)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"success": True, "key": key}

@app.get("/agents/{agent_id}/memory/search/{query}")
async def search_memory(agent_id: str, query: str, limit: int = Query(10, le=50)):
    """Search agent memories"""
    entries = memory_manager.search(agent_id, query, limit)
    return {"results": [e.to_dict() for e in entries], "count": len(entries)}

@app.get("/agents/{agent_id}/memory/stats")
async def memory_stats(agent_id: str):
    """Get memory statistics for an agent"""
    return memory_manager.get_stats(agent_id)

@app.delete("/agents/{agent_id}/memory")
async def clear_memory(agent_id: str):
    """Clear all memories for an agent"""
    count = memory_manager.clear_agent(agent_id)
    return {"success": True, "deleted_count": count}

@app.post("/memory/cleanup")
async def cleanup_memory(agent_id: Optional[str] = None):
    """Clean up expired memories"""
    count = memory_manager.cleanup_expired(agent_id)
    return {"success": True, "expired_count": count}

# =========================================================================
# Framework Stats
# =========================================================================

@app.get("/stats")
async def framework_stats():
    """Get overall framework statistics"""
    return agent_manager.get_framework_stats()
