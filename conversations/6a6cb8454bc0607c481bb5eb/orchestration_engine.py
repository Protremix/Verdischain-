"""
EvolvixOS Agent Orchestration Engine
Multi-agent workflows, task delegation, pipeline execution, and DAG-based orchestration
"""

import asyncio
import json
import time
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from collections import defaultdict
import structlog

logger = structlog.get_logger()


# =========================================================================
# Enums
# =========================================================================

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    PENDING = "pending"
    WAITING = "waiting"       # waiting for dependencies
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class StepType(str, Enum):
    AGENT_TASK = "agent_task"       # delegate to an agent
    GATEWAY_CALL = "gateway_call"   # direct AI gateway call
    CONDITION = "condition"         # branch on condition
    PARALLEL = "parallel"           # fan-out to multiple agents
    SEQUENCE = "sequence"           # ordered steps
    LOOP = "loop"                   # iterate
    WAIT = "wait"                   # delay
    WEBHOOK = "webhook"             # call external URL
    LOG = "log"                     # log a message
    TRANSFORM = "transform"         # transform data


# =========================================================================
# Data Models
# =========================================================================

@dataclass
class WorkflowStep:
    id: str
    name: str
    step_type: StepType
    config: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)  # step IDs
    status: StepStatus = StepStatus.PENDING
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    retries: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d["step_type"] = self.step_type.value
        d["status"] = self.status.value
        return d


@dataclass
class Workflow:
    id: str
    name: str
    description: str
    steps: List[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_by: str = "system"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    global_context: Dict[str, Any] = field(default_factory=dict)  # shared between steps
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "steps": [s.to_dict() for s in self.steps],
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "created_by": self.created_by,
            "tags": self.tags,
            "metadata": self.metadata,
            "global_context": self.global_context,
        }


@dataclass
class WorkflowTemplate:
    id: str
    name: str
    description: str
    step_definitions: List[Dict[str, Any]]  # template for creating steps
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


# =========================================================================
# Workflow Registry (in-memory, persists to JSON)
# =========================================================================

class WorkflowRegistry:
    """Manages workflow definitions and templates"""
    
    def __init__(self, persist_path: str = None):
        self._workflows: Dict[str, Workflow] = {}
        self._templates: Dict[str, WorkflowTemplate] = {}
        self._persist_path = persist_path
        self._lock = asyncio.Lock()
        
        # Pre-load templates
        self._init_default_templates()
    
    def _init_default_templates(self):
        """Initialize default workflow templates"""
        templates = [
            WorkflowTemplate(
                id="code-review-pipeline",
                name="Code Review Pipeline",
                description="Sequential: review code → analyze sentiment → generate report",
                step_definitions=[
                    {"name": "Code Review", "step_type": "gateway_call", "config": {"capability": "code_review"}},
                    {"name": "Sentiment Analysis", "step_type": "gateway_call", "config": {"capability": "sentiment"}, "depends_on": ["Code Review"]},
                    {"name": "Generate Report", "step_type": "agent_task", "config": {"task_type": "chat", "system_prompt": "Summarize the code review and sentiment analysis into a report."}, "depends_on": ["Sentiment Analysis"]},
                ],
                tags=["code", "review", "analysis"],
            ),
            WorkflowTemplate(
                id="parallel-analysis",
                name="Parallel Multi-Agent Analysis",
                description="Fan-out: multiple agents analyze different aspects simultaneously",
                step_definitions=[
                    {"name": "Code Quality", "step_type": "agent_task", "config": {"task_type": "chat", "system_prompt": "Analyze code quality."}},
                    {"name": "Security Check", "step_type": "agent_task", "config": {"task_type": "chat", "system_prompt": "Check for security issues."}},
                    {"name": "Performance Review", "step_type": "agent_task", "config": {"task_type": "chat", "system_prompt": "Review performance implications."}},
                    {"name": "Aggregate", "step_type": "agent_task", "config": {"task_type": "chat", "system_prompt": "Aggregate all analyses into a final report."}, "depends_on": ["Code Quality", "Security Check", "Performance Review"]},
                ],
                tags=["parallel", "analysis", "multi-agent"],
            ),
            WorkflowTemplate(
                id="sentiment-to-action",
                name="Sentiment-Driven Action",
                description="Analyze sentiment → branch: positive (log) or negative (escalate)",
                step_definitions=[
                    {"name": "Analyze Sentiment", "step_type": "gateway_call", "config": {"capability": "sentiment"}},
                    {"name": "Check Result", "step_type": "condition", "config": {"condition": "output.sentiment == 'positive'", "depends_on_step": "Analyze Sentiment"}},
                    {"name": "Log Positive", "step_type": "log", "config": {"message": "Positive sentiment detected"}, "depends_on": ["Check Result"]},
                    {"name": "Escalate Negative", "step_type": "agent_task", "config": {"task_type": "chat", "system_prompt": "Negative sentiment detected. Generate escalation report."}, "depends_on": ["Check Result"]},
                ],
                tags=["sentiment", "conditional", "branching"],
            ),
            WorkflowTemplate(
                id="iterative-improvement",
                name="Iterative Code Improvement",
                description="Loop: review → fix → re-review until score >= 8",
                step_definitions=[
                    {"name": "Review Code", "step_type": "gateway_call", "config": {"capability": "code_review"}},
                    {"name": "Check Score", "step_type": "condition", "config": {"condition": "output.score >= 8"}},
                    {"name": "Fix Issues", "step_type": "agent_task", "config": {"task_type": "chat", "system_prompt": "Fix the issues identified in the code review."}, "depends_on": ["Check Score"]},
                ],
                tags=["loop", "improvement", "iterative"],
            ),
        ]
        for t in templates:
            self._templates[t.id] = t
    
    async def create_workflow(self, name: str, description: str,
                              step_defs: List[Dict[str, Any]],
                              tags: List[str] = None,
                              metadata: Dict = None) -> Workflow:
        """Create a new workflow from step definitions"""
        async with self._lock:
            workflow_id = f"wf_{uuid.uuid4().hex[:12]}"
            steps = []
            for sd in step_defs:
                step_id = f"step_{uuid.uuid4().hex[:8]}"
                steps.append(WorkflowStep(
                    id=step_id,
                    name=sd.get("name", step_id),
                    step_type=StepType(sd.get("step_type", "agent_task")),
                    config=sd.get("config", {}),
                    depends_on=sd.get("depends_on", []),
                    max_retries=sd.get("max_retries", 3),
                ))
            
            workflow = Workflow(
                id=workflow_id,
                name=name,
                description=description,
                steps=steps,
                tags=tags or [],
                metadata=metadata or {},
            )
            self._workflows[workflow_id] = workflow
            await self._persist()
            logger.info(f"Created workflow: {workflow_id} ({name})")
            return workflow
    
    async def create_from_template(self, template_id: str,
                                    input_data: Dict = None,
                                    tags: List[str] = None) -> Workflow:
        """Create a workflow from a template"""
        if template_id not in self._templates:
            raise ValueError(f"Template '{template_id}' not found")
        template = self._templates[template_id]
        workflow = await self.create_workflow(
            name=template.name,
            description=template.description,
            step_defs=template.step_definitions,
            tags=list(set(template.tags + (tags or []))),
            metadata={"template_id": template_id, "input_data": input_data or {}},
        )
        # Set initial input on first step
        if input_data and workflow.steps:
            workflow.steps[0].input_data.update(input_data)
        return workflow
    
    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self._workflows.get(workflow_id)
    
    async def list_workflows(self, status: str = None) -> List[Workflow]:
        if status:
            return [w for w in self._workflows.values() if w.status.value == status]
        return list(self._workflows.values())
    
    async def delete_workflow(self, workflow_id: str) -> bool:
        async with self._lock:
            if workflow_id in self._workflows:
                del self._workflows[workflow_id]
                await self._persist()
                return True
            return False
    
    async def list_templates(self) -> List[WorkflowTemplate]:
        return list(self._templates.values())
    
    async def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        return self._templates.get(template_id)
    
    async def _persist(self):
        if not self._persist_path:
            return
        try:
            data = {
                "workflows": {wid: w.to_dict() for wid, w in self._workflows.items()},
            }
            with open(self._persist_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist workflows: {e}")


# =========================================================================
# Workflow Executor
# =========================================================================

class WorkflowExecutor:
    """Executes workflows with DAG-based dependency resolution"""
    
    def __init__(self, registry: WorkflowRegistry,
                 gateway_url: str = "http://localhost:3500",
                 agent_url: str = "http://localhost:3600"):
        self.registry = registry
        self.gateway_url = gateway_url
        self.agent_url = agent_url
        self._running_workflows: Set[str] = set()
        self._execution_count = 0
        self._error_count = 0
        self._total_latency = 0.0
    
    @property
    def stats(self) -> Dict:
        return {
            "running": len(self._running_workflows),
            "total_executed": self._execution_count,
            "total_errors": self._error_count,
            "avg_latency_ms": self._total_latency / max(self._execution_count, 1),
        }
    
    async def execute(self, workflow_id: str) -> Dict:
        """Execute a workflow by ID"""
        workflow = await self.registry.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        
        if workflow.status == WorkflowStatus.RUNNING:
            raise ValueError(f"Workflow '{workflow_id}' is already running")
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now(timezone.utc).isoformat()
        self._running_workflows.add(workflow_id)
        start_time = time.time()
        
        try:
            # Build dependency graph and execute
            await self._execute_dag(workflow)
            workflow.status = WorkflowStatus.COMPLETED
        except asyncio.CancelledError:
            workflow.status = WorkflowStatus.CANCELLED
            raise
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            self._error_count += 1
            logger.error(f"Workflow {workflow_id} failed: {e}")
        finally:
            workflow.completed_at = datetime.now(timezone.utc).isoformat()
            self._running_workflows.discard(workflow_id)
            self._execution_count += 1
            self._total_latency += (time.time() - start_time) * 1000
            await self.registry._persist()
        
        return workflow.to_dict()
    
    async def cancel(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        workflow = await self.registry.get_workflow(workflow_id)
        if not workflow or workflow.status != WorkflowStatus.RUNNING:
            return False
        workflow.status = WorkflowStatus.CANCELLED
        for step in workflow.steps:
            if step.status in (StepStatus.PENDING, StepStatus.WAITING, StepStatus.RUNNING):
                step.status = StepStatus.CANCELLED
        self._running_workflows.discard(workflow_id)
        return True
    
    async def _execute_dag(self, workflow: Workflow):
        """Execute workflow steps respecting dependencies (DAG)"""
        steps_by_id = {s.id: s for s in workflow.steps}
        steps_by_name = {s.name: s for s in workflow.steps}
        
        # Resolve depends_on from names to IDs
        for step in workflow.steps:
            resolved_deps = []
            for dep in step.depends_on:
                if dep in steps_by_id:
                    resolved_deps.append(dep)
                elif dep in steps_by_name:
                    resolved_deps.append(steps_by_name[dep].id)
            step.depends_on = resolved_deps
        
        # Topological execution
        completed_steps: Set[str] = set()
        remaining = set(steps_by_id.keys())
        
        while remaining:
            # Find executable steps (all deps completed)
            executable = []
            for step_id in remaining:
                step = steps_by_id[step_id]
                if step.status == StepStatus.CANCELLED:
                    completed_steps.add(step_id)
                    continue
                deps_ok = all(d in completed_steps for d in step.depends_on)
                if deps_ok:
                    # Check if any dependency failed
                    dep_failed = any(
                        steps_by_id[d].status == StepStatus.FAILED
                        for d in step.depends_on if d in steps_by_id
                    )
                    if dep_failed:
                        step.status = StepStatus.SKIPPED
                        completed_steps.add(step_id)
                        continue
                    executable.append(step)
            
            if not executable:
                # No executable steps and still remaining — possible cycle or all waiting
                stuck = [steps_by_id[sid] for sid in remaining if steps_by_id[sid].status not in (StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED, StepStatus.CANCELLED)]
                if stuck:
                    raise ValueError(f"Deadlock: steps {[s.name for s in stuck]} have unresolvable dependencies")
                remaining = {sid for sid in remaining if steps_by_id[sid].status not in (StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED, StepStatus.CANCELLED)}
                if not remaining:
                    break
                continue
            
            # Execute all executable steps in parallel
            tasks = [self._execute_step(step, workflow) for step in executable]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for step, result in zip(executable, results):
                if isinstance(result, Exception):
                    step.status = StepStatus.FAILED
                    step.error = str(result)
                completed_steps.add(step.id)
                remaining.discard(step.id)
    
    async def _execute_step(self, step: WorkflowStep, workflow: Workflow) -> Dict:
        """Execute a single workflow step"""
        step.status = StepStatus.RUNNING
        step.started_at = datetime.now(timezone.utc).isoformat()
        
        # Merge input from dependencies' output
        input_data = {**step.input_data}
        steps_by_id = {s.id: s for s in workflow.steps}
        for dep_id in step.depends_on:
            if dep_id in steps_by_id:
                dep_output = steps_by_id[dep_id].output_data
                input_data.update(dep_output)
        
        # Also merge global context
        input_data.update(workflow.global_context)
        
        try:
            result = await self._execute_by_type(step, input_data, workflow)
            step.output_data = result
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.now(timezone.utc).isoformat()
            # Update global context with step output
            workflow.global_context[f"{step.name}_output"] = result
            return result
        except Exception as e:
            step.retries += 1
            if step.retries < step.max_retries:
                logger.warning(f"Step {step.name} failed (attempt {step.retries}), retrying: {e}")
                return await self._execute_step(step, workflow)
            step.status = StepStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.now(timezone.utc).isoformat()
            raise
    
    async def _execute_by_type(self, step: WorkflowStep, input_data: Dict,
                               workflow: Workflow) -> Dict:
        """Execute step based on its type"""
        step_type = step.step_type
        config = step.config
        
        if step_type == StepType.AGENT_TASK:
            return await self._execute_agent_task(config, input_data)
        elif step_type == StepType.GATEWAY_CALL:
            return await self._execute_gateway_call(config, input_data)
        elif step_type == StepType.CONDITION:
            return await self._execute_condition(config, input_data)
        elif step_type == StepType.LOG:
            msg = config.get("message", "Log step")
            logger.info(f"Workflow log: {msg}")
            return {"logged": msg}
        elif step_type == StepType.WAIT:
            delay = config.get("seconds", 1)
            await asyncio.sleep(delay)
            return {"waited": delay}
        elif step_type == StepType.TRANSFORM:
            return self._execute_transform(config, input_data)
        else:
            raise ValueError(f"Unsupported step type: {step_type}")
    
    async def _execute_agent_task(self, config: Dict, input_data: Dict) -> Dict:
        """Execute a task via the Agent Framework"""
        import httpx
        task_type = config.get("task_type", "chat")
        system_prompt = config.get("system_prompt", "")
        
        # Create a temporary agent if agent_id not provided
        agent_id = config.get("agent_id")
        
        async with httpx.AsyncClient(timeout=180) as client:
            if not agent_id:
                # Create a temporary agent
                resp = await client.post(f"{self.agent_url}/agents", json={
                    "name": f"orchestrator_{task_type}",
                    "capabilities": [task_type],
                    "system_prompt": system_prompt,
                })
                agent = resp.json()
                agent_id = agent["id"]
                # Start it
                await client.post(f"{self.agent_url}/agents/{agent_id}/start")
            
            # Create and execute task
            task_input = {**input_data}
            if system_prompt and "system" not in task_input:
                task_input["system"] = system_prompt
            
            resp = await client.post(f"{self.agent_url}/agents/{agent_id}/tasks", json={
                "task_type": task_type,
                "input_data": task_input,
            })
            task = resp.json()
            
            resp = await client.post(f"{self.agent_url}/agents/{agent_id}/tasks/{task['id']}/execute")
            result = resp.json()
            
            # Cleanup temporary agent
            if not config.get("agent_id"):
                await client.delete(f"{self.agent_url}/agents/{agent_id}")
            
            return result.get("output_data", result)
    
    async def _execute_gateway_call(self, config: Dict, input_data: Dict) -> Dict:
        """Execute a direct AI Gateway call"""
        import httpx
        capability = config.get("capability", "chat")
        plugin = config.get("plugin")
        
        payload = {
            "capability": capability,
            "input": input_data,
            "options": {"capability": capability},
        }
        if plugin:
            payload["plugin"] = plugin
        
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.gateway_url}/gateway/invoke",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("output", data)
    
    async def _execute_condition(self, config: Dict, input_data: Dict) -> Dict:
        """Evaluate a condition"""
        condition = config.get("condition", "true")
        
        # Simple condition evaluation
        # Support: output.sentiment == 'positive', output.score >= 8, etc.
        result = self._eval_condition(condition, input_data)
        
        return {"condition_met": result, "condition": condition}
    
    def _eval_condition(self, condition: str, data: Dict) -> bool:
        """Evaluate a simple condition against data"""
        try:
            # Create a safe namespace
            namespace = {"output": data, "input": data, "result": data, "true": True, "false": False}
            # Evaluate safely
            return bool(eval(condition, {"__builtins__": {}}, namespace))
        except Exception:
            return False
    
    def _execute_transform(self, config: Dict, input_data: Dict) -> Dict:
        """Transform data using a mapping"""
        transform_map = config.get("map", {})
        output = {}
        for key, value_path in transform_map.items():
            # Simple dot-notation: output.content → input_data["content"]
            parts = value_path.split(".")
            val = input_data
            for part in parts:
                if isinstance(val, dict):
                    val = val.get(part, None)
                else:
                    val = None
                    break
            output[key] = val
        return output


# =========================================================================
# Global instances
# =========================================================================

import os

registry = WorkflowRegistry(persist_path=os.getenv("WORKFLOW_PERSIST_PATH", "/tmp/workflows.json"))
executor = WorkflowExecutor(registry)
