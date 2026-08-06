"""
Tests for EvolvixOS Agent Execution Engine and Orchestrator
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core_agents import AgentRole, get_agent, CORE_AGENTS
from agent_execution import AgentExecutionEngine, AgentOrchestrator


def mock_gateway_response(json_data: Dict, status_code: int = 200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


class TestAgentExecutionEngine:
    @pytest.fixture
    def engine(self):
        return AgentExecutionEngine("http://localhost:3400")

    def test_engine_init(self, engine):
        assert engine.gateway_url == "http://localhost:3400"
        assert len(engine._execution_history) == 0

    def test_build_messages_with_prompt(self, engine):
        agent = get_agent(AgentRole.ARCHITECTURE)
        messages = engine._build_messages(agent, {"prompt": "Design a microservice"})
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == agent.system_prompt
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Design a microservice"

    def test_build_messages_with_text(self, engine):
        agent = get_agent(AgentRole.SECURITY)
        messages = engine._build_messages(agent, {"text": "Check this code"})
        assert messages[1]["content"] == "Check this code"

    def test_build_messages_with_code(self, engine):
        agent = get_agent(AgentRole.CODE_REVIEW)
        messages = engine._build_messages(agent, {"code": "print('hello')"})
        assert "Review this code" in messages[1]["content"]

    def test_build_messages_with_custom_messages(self, engine):
        agent = get_agent(AgentRole.PLANNING)
        custom = [{"role": "user", "content": "Plan a sprint"}]
        messages = engine._build_messages(agent, {"messages": custom})
        assert messages[0]["role"] == "system"
        assert messages[1]["content"] == "Plan a sprint"

    def test_build_messages_with_dict_input(self, engine):
        agent = get_agent(AgentRole.DEVOPS)
        messages = engine._build_messages(agent, {"task": "deploy", "env": "prod"})
        assert messages[1]["role"] == "user"

    @pytest.mark.asyncio
    async def test_execute_success(self, engine):
        agent = get_agent(AgentRole.ARCHITECTURE)
        mock_resp = mock_gateway_response({
            "output": {"content": "Architecture recommendation"},
            "provider": "ollama",
        })
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp
            result = await engine.execute(agent, {"prompt": "test"})
            assert result["status"] == "completed"
            assert result["agent_id"] == "core-architecture"
            assert "latency_ms" in result

    @pytest.mark.asyncio
    async def test_execute_with_preferred_provider(self, engine):
        agent = get_agent(AgentRole.SECURITY)
        agent.preferred_provider = "openai"
        mock_resp = mock_gateway_response({
            "output": {"content": "Security analysis"},
            "provider": "openai",
        })
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp
            result = await engine.execute(agent, {"prompt": "scan"})
            assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_execute_failure(self, engine):
        agent = get_agent(AgentRole.TESTING)
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Connection refused")
            result = await engine.execute(agent, {"prompt": "test"})
            assert result["status"] == "failed"
            assert "Connection refused" in result["error"]

    def test_record_execution(self, engine):
        engine._record_execution({"execution_id": "1", "status": "completed"})
        engine._record_execution({"execution_id": "2", "status": "failed"})
        assert len(engine._execution_history) == 2

    def test_get_history(self, engine):
        engine._record_execution({"execution_id": "1", "status": "completed", "agent_id": "core-security"})
        engine._record_execution({"execution_id": "2", "status": "completed", "agent_id": "core-devops"})
        history = engine.get_history(limit=10)
        assert len(history) == 2
        # Filter by agent
        sec_history = engine.get_history(agent_id="core-security")
        assert len(sec_history) == 1

    def test_stats(self, engine):
        engine._record_execution({"status": "completed", "latency_ms": 100})
        engine._record_execution({"status": "completed", "latency_ms": 200})
        engine._record_execution({"status": "failed", "latency_ms": 50})
        stats = engine.stats()
        assert stats["total_executions"] == 3
        assert stats["completed"] == 2
        assert stats["failed"] == 1
        assert stats["success_rate"] > 0

    def test_max_history_limit(self, engine):
        engine._max_history = 5
        for i in range(10):
            engine._record_execution({"execution_id": str(i), "status": "completed"})
        assert len(engine._execution_history) == 5


class TestAgentOrchestrator:
    @pytest.fixture
    def orchestrator(self):
        engine = AgentExecutionEngine("http://localhost:3400")
        return AgentOrchestrator(engine)

    @pytest.mark.asyncio
    async def test_execute_pipeline(self, orchestrator):
        mock_resp = mock_gateway_response({
            "output": {"content": "result"},
            "provider": "ollama",
        })
        steps = [
            {"role": "security", "input_data": {"prompt": "check"}},
            {"role": "code_review", "input_data": {"prompt": "review"}},
        ]
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp
            results = await orchestrator.execute_pipeline(steps)
            assert len(results) == 2

    @pytest.mark.asyncio
    async def test_execute_parallel(self, orchestrator):
        mock_resp = mock_gateway_response({
            "output": {"content": "result"},
            "provider": "ollama",
        })
        tasks = [
            {"role": "security", "input_data": {"prompt": "check1"}},
            {"role": "performance", "input_data": {"prompt": "check2"}},
        ]
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp
            results = await orchestrator.execute_parallel(tasks)
            assert len(results) == 2

    @pytest.mark.asyncio
    async def test_pipeline_with_unknown_role(self, orchestrator):
        steps = [{"role": "nonexistent", "input_data": {}}]
        results = await orchestrator.execute_pipeline(steps)
        assert "error" in results[0]

    @pytest.mark.asyncio
    async def test_code_review_pipeline(self, orchestrator):
        mock_resp = mock_gateway_response({
            "output": {"content": "review result"},
            "provider": "ollama",
        })
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp
            result = await orchestrator.code_review_pipeline("print('hello')", "python")
            assert result["pipeline"] == "code_review"
            assert len(result["steps"]) == 3
            assert result["summary"]["total"] == 3

    @pytest.mark.asyncio
    async def test_architecture_review_pipeline(self, orchestrator):
        mock_resp = mock_gateway_response({
            "output": {"content": "architecture result"},
            "provider": "ollama",
        })
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp
            result = await orchestrator.architecture_review_pipeline("Build a payment system")
            assert result["pipeline"] == "architecture_review"
            assert len(result["steps"]) == 4
            assert result["summary"]["total"] == 4

    @pytest.mark.asyncio
    async def test_pipeline_context_passing(self, orchestrator):
        mock_resp = mock_gateway_response({
            "output": {"content": "result", "context_key": "context_value"},
            "provider": "ollama",
        })
        steps = [
            {"role": "architecture", "input_data": {"prompt": "design"}},
            {"role": "planning", "input_data": {"prompt": "plan"}},
        ]
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp
            results = await orchestrator.execute_pipeline(steps)
            assert len(results) == 2
            assert all(r.get("status") == "completed" for r in results)


class TestAllAgentsExecutable:
    """Verify every core agent can be invoked through the execution engine."""

    @pytest.mark.asyncio
    async def test_all_16_agents_can_build_messages(self):
        engine = AgentExecutionEngine("http://localhost:3400")
        for agent in CORE_AGENTS:
            messages = engine._build_messages(agent, {"prompt": "test"})
            assert len(messages) >= 2  # system + user
            assert messages[0]["role"] == "system"
            assert len(messages[0]["content"]) > 100  # substantial system prompt
