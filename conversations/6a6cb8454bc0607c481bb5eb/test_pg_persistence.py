"""
Tests for PostgreSQL Execution Persistence and Real Execution.
"""

import pytest
import asyncio
import os
import sys
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pg_persistence import PostgresExecutionPersistence, HAS_ASYNCPG


# =========================================================================
# PostgreSQL Persistence Tests (with mock)
# =========================================================================

class TestPostgresPersistenceUnit:
    """Unit tests for PostgreSQL persistence with mocked asyncpg."""
    
    @pytest.fixture
    def persist(self):
        return PostgresExecutionPersistence("postgresql://test:test@localhost/test")
    
    def test_init(self, persist):
        assert persist._database_url == "postgresql://test:test@localhost/test"
        assert persist._connected == False
        assert persist._total_persisted == 0
    
    @pytest.mark.asyncio
    async def test_record_without_connection(self, persist):
        """Records go to fallback buffer when not connected."""
        result = await persist.record({
            "execution_id": "test-1",
            "status": "completed",
            "agent_id": "core-architecture",
        })
        assert result == False
        assert len(persist._fallback_buffer) == 1
        assert persist._fallback_buffer[0]["execution_id"] == "test-1"
        assert "id" in persist._fallback_buffer[0]
    
    @pytest.mark.asyncio
    async def test_record_multiple_without_connection(self, persist):
        for i in range(5):
            await persist.record({"execution_id": f"test-{i}", "status": "completed"})
        assert len(persist._fallback_buffer) == 5
    
    @pytest.mark.asyncio
    async def test_query_without_connection(self, persist):
        await persist.record({"execution_id": "q-1", "status": "completed"})
        results = await persist.query(limit=10)
        assert len(results) == 1
    
    @pytest.mark.asyncio
    async def test_stats_without_connection(self, persist):
        await persist.record({"execution_id": "s-1", "status": "completed"})
        stats = await persist.stats()
        assert stats["connected"] == False
        assert stats["fallback_buffer"] == 1
    
    @pytest.mark.asyncio
    async def test_connect_with_mock(self, persist):
        mock_conn = AsyncMock()
        mock_pool = MagicMock()
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=mock_conn)
        cm.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = cm
        
        with patch("asyncpg.create_pool", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_pool
            result = await persist.connect()
            assert result == True
            assert persist._connected == True
            mock_conn.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, persist):
        with patch("asyncpg.create_pool", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("Connection refused")
            result = await persist.connect()
            assert result == False
            assert persist._connected == False
    
    @pytest.mark.asyncio
    async def test_record_with_mock_connection(self, persist):
        mock_conn = AsyncMock()
        mock_pool = MagicMock()
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=mock_conn)
        cm.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = cm
        
        persist._pool = mock_pool
        persist._connected = True
        
        result = await persist.record({
            "execution_id": "mock-1",
            "status": "completed",
            "agent_id": "core-security",
            "agent_name": "Security Agent",
            "capability": "code_review",
            "provider": "openai",
            "latency_ms": 1500,
        })
        
        assert result == True
        assert persist._total_persisted == 1
        mock_conn.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query_with_mock_connection(self, persist):
        mock_conn = AsyncMock()
        mock_pool = MagicMock()
        
        # Mock fetch to return rows
        mock_conn.fetch.return_value = [
            {"id": "abc123", "timestamp": MagicMock(isoformat=lambda: "2026-01-01T00:00:00"),
             "execution_id": "q-1", "agent_id": "core-devops", "agent_name": "DevOps",
             "status": "completed", "capability": "devops", "provider": "ollama",
             "fallback_used": False, "latency_ms": 200, "input_data": None,
             "output_data": None, "error": None, "sandboxed": True, "metadata": None},
        ]
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=mock_conn)
        cm.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = cm
        
        persist._pool = mock_pool
        persist._connected = True
        
        results = await persist.query(limit=10)
        assert len(results) == 1
        assert results[0]["agent_id"] == "core-devops"
        assert results[0]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_stats_with_mock_connection(self, persist):
        mock_conn = AsyncMock()
        mock_pool = MagicMock()
        
        mock_conn.fetchval.return_value = 5
        mock_conn.fetch.side_effect = [
            [{"status": "completed", "count": 3}, {"status": "failed", "count": 2}],
            [{"agent_id": "core-arch", "count": 3}],
        ]
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=mock_conn)
        cm.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = cm
        
        persist._pool = mock_pool
        persist._connected = True
        
        stats = await persist.stats()
        assert stats["connected"] == True
        assert stats["total_persisted"] == 5
        assert stats["by_status"]["completed"] == 3
        assert stats["by_status"]["failed"] == 2
    
    @pytest.mark.asyncio
    async def test_close(self, persist):
        mock_pool = MagicMock()
        mock_pool.close = AsyncMock()
        persist._pool = mock_pool
        persist._connected = True
        
        await persist.close()
        assert persist._connected == False
        mock_pool.close.assert_called_once()
    
    def test_is_connected_property(self, persist):
        assert persist.is_connected == False
        persist._connected = True
        assert persist.is_connected == True


# =========================================================================
# Real Execution Tests (with OpenAI API)
# =========================================================================

class TestRealExecution:
    """Real execution tests that actually call the AI Gateway.
    
    These tests require a running gateway and API keys.
    Skip if no OPENAI_API_KEY is available.
    """
    
    OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
    
    @pytest.fixture
    def engine(self):
        from agent_execution import AgentExecutionEngine
        return AgentExecutionEngine("http://localhost:3400")
    
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY", ""), reason="No OPENAI_API_KEY")
    def test_has_openai_key(self):
        """Verify OpenAI API key is available."""
        assert self.OPENAI_KEY, "OPENAI_API_KEY not set"
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_KEY, reason="No OPENAI_API_KEY")
    async def test_real_security_agent(self, engine):
        """Execute the Security Agent with a real prompt."""
        from core_agents import get_agent, AgentRole
        agent = get_agent(AgentRole.SECURITY)
        result = await engine.execute(agent, {
            "prompt": "Analyze this code for security issues: print('hello')"
        })
        assert result["status"] in ["completed", "failed"]
        if result["status"] == "completed":
            assert "output" in result
            assert "latency_ms" in result
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_KEY, reason="No OPENAI_API_KEY")
    async def test_real_code_review_agent(self, engine):
        """Execute the Code Review Agent with a real code sample."""
        from core_agents import get_agent, AgentRole
        agent = get_agent(AgentRole.CODE_REVIEW)
        result = await engine.execute(agent, {
            "code": "def add(a, b):\n    return a + b",
            "language": "python",
        })
        assert result["status"] in ["completed", "failed"]
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_KEY, reason="No OPENAI_API_KEY")
    async def test_real_architecture_agent(self, engine):
        """Execute the Architecture Agent with a real design question."""
        from core_agents import get_agent, AgentRole
        agent = get_agent(AgentRole.ARCHITECTURE)
        result = await engine.execute(agent, {
            "prompt": "Should we use microservices or monolith for a small team?"
        })
        assert result["status"] in ["completed", "failed"]
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_KEY, reason="No OPENAI_API_KEY")
    async def test_real_pipeline_execution(self, engine):
        """Execute a real code review pipeline."""
        from agent_execution import AgentOrchestrator
        orchestrator = AgentOrchestrator(engine)
        result = await orchestrator.code_review_pipeline(
            "def hello():\n    print('world')",
            "python",
        )
        assert result["pipeline"] == "code_review"
        assert result["summary"]["total"] == 3
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_KEY, reason="No OPENAI_API_KEY")
    async def test_real_execution_tracked(self, engine):
        """Verify execution is tracked in history."""
        from core_agents import get_agent, AgentRole
        agent = get_agent(AgentRole.TESTING)
        await engine.execute(agent, {"prompt": "Write a test for addition"})
        history = engine.get_history(limit=5)
        assert len(history) > 0
        assert any(h.get("agent_id") == "core-testing" for h in history)
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPENAI_KEY, reason="No OPENAI_API_KEY")
    async def test_real_execution_stats(self, engine):
        """Verify execution stats are updated."""
        from core_agents import get_agent, AgentRole
        agent = get_agent(AgentRole.DOCS)
        await engine.execute(agent, {"prompt": "Document this function: def add(a,b): return a+b"})
        stats = engine.stats()
        assert stats["total_executions"] > 0
