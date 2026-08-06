"""
Tests for network isolation and PG integration in sandbox.
"""

import pytest
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugin_sandbox import NetworkIsolation, SandboxConfig, SandboxLevel


class TestNetworkIsolation:
    def test_is_network_allowed_openai(self):
        assert NetworkIsolation.is_network_allowed("https://api.openai.com/v1/chat", True) == True
    
    def test_is_network_allowed_anthropic(self):
        assert NetworkIsolation.is_network_allowed("https://api.anthropic.com/v1/messages", True) == True
    
    def test_is_network_allowed_blocked_when_network_off(self):
        assert NetworkIsolation.is_network_allowed("https://api.openai.com", False) == False
    
    def test_is_network_allowed_unknown_domain(self):
        assert NetworkIsolation.is_network_allowed("https://malicious-site.com", True) == False
    
    def test_validate_url_blocks_aws_metadata(self):
        assert NetworkIsolation.validate_url("http://169.254.169.254/latest/meta-data/") == False
    
    def test_validate_url_blocks_gcp_metadata(self):
        assert NetworkIsolation.validate_url("http://metadata.google.internal/computeMetadata/") == False
    
    def test_validate_url_allows_openai(self):
        assert NetworkIsolation.validate_url("https://api.openai.com/v1/chat") == True
    
    def test_get_blocked_domains(self):
        blocked = NetworkIsolation.get_blocked_domains()
        assert "169.254.169.254" in blocked
        assert "metadata.google.internal" in blocked
        assert "169.254.169.253" in blocked
    
    def test_ollama_localhost_allowed(self):
        assert NetworkIsolation.is_network_allowed("http://localhost:11434/api/chat", True) == True
    
    def test_qdrant_localhost_allowed(self):
        assert NetworkIsolation.is_network_allowed("http://localhost:6333/collections", True) == True
    
    def test_deepseek_allowed(self):
        assert NetworkIsolation.is_network_allowed("https://api.deepseek.com/v1/chat", True) == True
    
    def test_whitelist_size(self):
        assert len(NetworkIsolation.NETWORK_WHITELIST) >= 15


class TestPGIntegration:
    """Test that sandbox_api correctly uses PG persistence."""
    
    @pytest.mark.asyncio
    async def test_pg_persistence_record_fallback(self):
        from pg_persistence import PostgresExecutionPersistence
        persist = PostgresExecutionPersistence("invalid://url")
        result = await persist.record({"execution_id": "test", "status": "completed"})
        assert result == False  # Falls back to buffer
    
    @pytest.mark.asyncio
    async def test_pg_persistence_query_fallback(self):
        from pg_persistence import PostgresExecutionPersistence
        persist = PostgresExecutionPersistence("invalid://url")
        await persist.record({"execution_id": "test", "status": "completed", "agent_id": "a1"})
        results = await persist.query(limit=10)
        assert len(results) == 1
    
    @pytest.mark.asyncio
    async def test_pg_persistence_stats_offline(self):
        from pg_persistence import PostgresExecutionPersistence
        persist = PostgresExecutionPersistence("invalid://url")
        await persist.record({"execution_id": "test", "status": "completed"})
        stats = await persist.stats()
        assert stats["connected"] == False
        assert stats["fallback_buffer"] == 1
    
    def test_retention_cleanup_function_exists(self):
        """Verify that retention cleanup is importable from sandbox_api."""
        try:
            import sandbox_api
            assert hasattr(sandbox_api, 'cleanup_old_records')
        except ImportError:
            pytest.skip("sandbox_api not importable in test env")
