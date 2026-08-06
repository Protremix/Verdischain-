"""
EvolvixOS Agent Execution Engine
Connects the 16 Core Agents to the AI Gateway for actual execution.
Agents invoke the gateway's intelligent router to get real AI responses.
"""

import asyncio
import time
import json
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from collections import defaultdict
import structlog

from core_agents import CoreAgent, AgentRole, CORE_AGENTS, get_agent, get_agent_by_id

logger = structlog.get_logger()


# =========================================================================
# Agent Execution Engine
# =========================================================================

class AgentExecutionEngine:
    """Executes core agents by routing through the AI Gateway."""
    
    def __init__(self, gateway_url: str = "http://localhost:3400"):
        self.gateway_url = gateway_url
        self._execution_history: List[Dict] = []
        self._max_history = 1000
        self._active_executions: Dict[str, Dict] = {}
    
    async def execute(self, agent: CoreAgent, input_data: Dict[str, Any],
                      options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a core agent via the AI Gateway."""
        options = options or {}
        execution_id = f"exec_{int(time.time() * 1000)}"
        start_time = time.time()
        
        self._active_executions[execution_id] = {
            "agent_id": agent.id,
            "agent_name": agent.name,
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "input": input_data,
        }
        
        try:
            # Build the messages for the gateway
            messages = self._build_messages(agent, input_data)
            
            # Prepare gateway invoke request
            gateway_payload = {
                "capability": agent.preferred_capability,
                "input_data": {"messages": messages},
                "options": {
                    "max_tokens": options.get("max_tokens", agent.max_tokens),
                    "temperature": options.get("temperature", agent.temperature),
                    **options,
                },
                "prefer_local": options.get("prefer_local", True),
                "max_fallbacks": options.get("max_fallbacks", 3),
            }
            
            if agent.preferred_provider:
                gateway_payload["provider"] = agent.preferred_provider
            
            # Call the gateway
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{self.gateway_url}/invoke",
                    json=gateway_payload,
                )
                resp.raise_for_status()
                result = resp.json()
            
            latency = (time.time() - start_time) * 1000
            
            execution_result = {
                "execution_id": execution_id,
                "agent_id": agent.id,
                "agent_name": agent.name,
                "status": "completed",
                "capability": agent.preferred_capability,
                "provider": result.get("provider", "unknown"),
                "fallback_used": result.get("fallback_used", False),
                "output": result.get("output", {}),
                "latency_ms": latency,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            
            self._record_execution(execution_result)
            del self._active_executions[execution_id]
            return execution_result
            
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            error_result = {
                "execution_id": execution_id,
                "agent_id": agent.id,
                "agent_name": agent.name,
                "status": "failed",
                "error": str(e),
                "latency_ms": latency,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self._record_execution(error_result)
            if execution_id in self._active_executions:
                del self._active_executions[execution_id]
            return error_result
    
    def _build_messages(self, agent: CoreAgent, input_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build the message array for the gateway from agent + input."""
        messages = [{"role": "system", "content": agent.system_prompt}]
        
        # Add user input
        if "messages" in input_data:
            messages.extend(input_data["messages"])
        elif "prompt" in input_data:
            messages.append({"role": "user", "content": input_data["prompt"]})
        elif "text" in input_data:
            messages.append({"role": "user", "content": input_data["text"]})
        elif "code" in input_data:
            messages.append({"role": "user", "content": f"Review this code:\n{input_data['code']}"})
        else:
            messages.append({"role": "user", "content": json.dumps(input_data)})
        
        return messages
    
    def _record_execution(self, result: Dict):
        self._execution_history.append(result)
        if len(self._execution_history) > self._max_history:
            self._execution_history = self._execution_history[-self._max_history:]
    
    def get_history(self, limit: int = 50, agent_id: str = None) -> List[Dict]:
        """Get execution history."""
        history = self._execution_history
        if agent_id:
            history = [h for h in history if h.get("agent_id") == agent_id]
        return history[-limit:]
    
    def get_active(self) -> Dict[str, Dict]:
        """Get currently active executions."""
        return self._active_executions
    
    def stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        total = len(self._execution_history)
        completed = sum(1 for h in self._execution_history if h["status"] == "completed")
        failed = sum(1 for h in self._execution_history if h["status"] == "failed")
        avg_latency = sum(h.get("latency_ms", 0) for h in self._execution_history) / max(total, 1)
        
        by_agent = defaultdict(int)
        for h in self._execution_history:
            by_agent[h.get("agent_id", "unknown")] += 1
        
        return {
            "total_executions": total,
            "completed": completed,
            "failed": failed,
            "success_rate": (completed / max(total, 1)) * 100,
            "avg_latency_ms": avg_latency,
            "active": len(self._active_executions),
            "by_agent": dict(by_agent),
        }


# =========================================================================
# Agent Orchestrator (coordinates multiple agents)
# =========================================================================

class AgentOrchestrator:
    """Coordinates multi-agent workflows."""
    
    def __init__(self, engine: AgentExecutionEngine):
        self.engine = engine
    
    async def execute_pipeline(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a sequence of agent invocations, passing context between them."""
        results = []
        context = {}
        
        for step in steps:
            agent_role = step.get("role")
            input_data = {**step.get("input_data", {}), **context}
            options = step.get("options", {})
            
            try:
                agent = get_agent(AgentRole(agent_role)) if agent_role else None
            except ValueError:
                agent = None
            if not agent:
                results.append({"error": f"Unknown agent role: {agent_role}"})
                continue
            
            result = await self.engine.execute(agent, input_data, options)
            results.append(result)
            
            # Pass output to context for next step
            if result["status"] == "completed":
                output = result.get("output", {})
                if isinstance(output, dict):
                    context.update(output)
        
        return results
    
    async def execute_parallel(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple agent invocations in parallel."""
        async def run_task(task):
            agent_role = task.get("role")
            try:
                agent = get_agent(AgentRole(agent_role)) if agent_role else None
            except ValueError:
                agent = None
            if not agent:
                return {"error": f"Unknown agent: {agent_role}"}
            return await self.engine.execute(agent, task.get("input_data", {}), task.get("options", {}))
        
        return await asyncio.gather(*[run_task(t) for t in tasks])
    
    async def code_review_pipeline(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Full code review: Security → Code Review → Performance → Documentation."""
        steps = [
            {"role": "security", "input_data": {"code": code, "language": language}},
            {"role": "code_review", "input_data": {"code": code, "language": language}},
            {"role": "performance", "input_data": {"code": code, "language": language}},
        ]
        results = await self.execute_pipeline(steps)
        
        return {
            "pipeline": "code_review",
            "steps": ["security", "code_review", "performance"],
            "results": results,
            "summary": {
                "total": len(results),
                "completed": sum(1 for r in results if r.get("status") == "completed"),
                "failed": sum(1 for r in results if r.get("status") == "failed"),
            },
        }
    
    async def architecture_review_pipeline(self, description: str, constraints: Dict = None) -> Dict[str, Any]:
        """Full architecture review: Architecture → Planning → Security → DevOps."""
        steps = [
            {"role": "architecture", "input_data": {"prompt": description, "constraints": constraints or {}}},
            {"role": "planning", "input_data": {"prompt": f"Create implementation plan for: {description}"}},
            {"role": "security", "input_data": {"prompt": f"Security review for: {description}"}},
            {"role": "devops", "input_data": {"prompt": f"DevOps plan for: {description}"}},
        ]
        results = await self.execute_pipeline(steps)
        
        return {
            "pipeline": "architecture_review",
            "steps": ["architecture", "planning", "security", "devops"],
            "results": results,
            "summary": {
                "total": len(results),
                "completed": sum(1 for r in results if r.get("status") == "completed"),
                "failed": sum(1 for r in results if r.get("status") == "failed"),
            },
        }


# =========================================================================
# Global instance
# =========================================================================

import os
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:3400")
engine = AgentExecutionEngine(GATEWAY_URL)
orchestrator = AgentOrchestrator(engine)
