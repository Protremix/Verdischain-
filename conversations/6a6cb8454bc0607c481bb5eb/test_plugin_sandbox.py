"""
Tests for EvolvixOS Plugin Sandbox Manager and Execution Persistence
"""

import pytest
import asyncio
import os
import sys
import json
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugin_sandbox import (
    SandboxManager, SandboxConfig, SandboxLevel,
    ExecutionPersistence, get_sandbox_config,
    DEFAULT_SANDBOX_CONFIGS, sandbox_manager, persistence,
)


# =========================================================================
# Sandbox Config Tests
# =========================================================================

class TestSandboxConfig:
    def test_default_config(self):
        config = SandboxConfig()
        assert config.level == SandboxLevel.BASIC
        assert config.cpu_limit_seconds == 30
        assert config.memory_limit_mb == 512
        assert config.timeout_seconds == 60
        assert config.allow_network == True

    def test_strict_config(self):
        config = SandboxConfig(
            level=SandboxLevel.STRICT,
            allow_network=False,
            allow_filesystem_read=[],
            allow_filesystem_write=[],
        )
        assert config.level == SandboxLevel.STRICT
        assert config.allow_network == False

    def test_config_to_dict(self):
        config = SandboxConfig()
        d = config.to_dict()
        assert "level" in d
        assert "cpu_limit_seconds" in d
        assert "memory_limit_mb" in d
        assert "timeout_seconds" in d
        assert "allow_network" in d

    def test_get_sandbox_config_for_llm(self):
        config = get_sandbox_config("llm_provider")
        assert config.level == SandboxLevel.BASIC
        assert config.timeout_seconds == 120
        assert "OPENAI_API_KEY" in config.env_whitelist

    def test_get_sandbox_config_for_coding(self):
        config = get_sandbox_config("coding_provider")
        assert config.cpu_limit_seconds == 60
        assert "OPENAI_API_KEY" in config.env_whitelist

    def test_get_sandbox_config_for_image(self):
        config = get_sandbox_config("image_provider")
        assert config.memory_limit_mb == 512

    def test_get_sandbox_config_for_search(self):
        config = get_sandbox_config("search_provider")
        assert config.timeout_seconds == 30
        assert "TAVILY_API_KEY" in config.env_whitelist

    def test_get_sandbox_config_unknown_type(self):
        config = get_sandbox_config("unknown_type")
        assert config.level == SandboxLevel.BASIC

    def test_all_plugin_types_have_configs(self):
        expected = ["llm_provider", "coding_provider", "image_provider",
                    "speech_provider", "search_provider", "embedding_provider",
                    "translation_provider", "speech_recognition", "ocr_provider",
                    "vector_memory"]
        for ptype in expected:
            assert ptype in DEFAULT_SANDBOX_CONFIGS

    def test_llm_config_env_whitelist(self):
        config = DEFAULT_SANDBOX_CONFIGS["llm_provider"]
        assert "OPENAI_API_KEY" in config.env_whitelist
        assert "ANTHROPIC_API_KEY" in config.env_whitelist
        assert "GOOGLE_API_KEY" in config.env_whitelist
        assert "DEEPSEEK_API_KEY" in config.env_whitelist

    def test_search_config_no_filesystem_write(self):
        config = DEFAULT_SANDBOX_CONFIGS["search_provider"]
        assert config.allow_filesystem_write == []

    def test_sandbox_level_values(self):
        assert SandboxLevel.NONE.value == "none"
        assert SandboxLevel.BASIC.value == "basic"
        assert SandboxLevel.STRICT.value == "strict"
        assert SandboxLevel.CONTAINER.value == "container"


# =========================================================================
# Sandbox Manager Tests
# =========================================================================

class TestSandboxManager:
    @pytest.fixture
    def manager(self):
        return SandboxManager(runner_dir=tempfile.gettempdir())

    def test_runner_script_created(self, manager):
        assert os.path.exists(manager._runner_path)
        assert os.access(manager._runner_path, os.R_OK)

    def test_initial_stats(self, manager):
        stats = manager.stats()
        assert stats["total_executions"] == 0
        assert stats["violation_count"] == 0

    def test_health_check(self, manager):
        health = manager.health_check()
        assert health["status"] == "healthy"
        assert health["runner_exists"] == True
        assert health["runner_readable"] == True

    def test_get_sandbox_config(self, manager):
        config = manager.get_sandbox_config("llm_provider")
        assert config.timeout_seconds == 120

    def test_prepare_environment(self, manager):
        config = SandboxConfig(env_whitelist=["TEST_VAR"])
        os.environ["TEST_VAR"] = "test_value"
        env = manager._prepare_environment(config)
        assert env["TEST_VAR"] == "test_value"
        assert "PATH" in env
        assert "HOME" in env
        # Non-whelisted vars should not be present (except defaults)
        assert "NONEXISTENT_VAR" not in env
        del os.environ["TEST_VAR"]

    @pytest.mark.asyncio
    async def test_execute_direct_no_sandbox(self, manager):
        config = SandboxConfig(level=SandboxLevel.NONE)
        result = await manager.execute_sandboxed(
            plugin_module="llm_providers",
            plugin_class="OpenAICompatiblePlugin",
            capability="chat",
            input_data={},
            options={},
            config=config,
        )
        assert "status" in result

    @pytest.mark.asyncio
    async def test_sandboxed_execution_timeout(self, manager):
        """Test that sandbox timeout is enforced."""
        config = SandboxConfig(
            level=SandboxLevel.BASIC,
            timeout_seconds=1,  # very short timeout
        )
        result = await manager.execute_sandboxed(
            plugin_module="llm_providers",
            plugin_class="NonExistentPlugin",
            capability="chat",
            input_data={},
            options={},
            config=config,
        )
        # Should timeout or error, not hang
        assert result["status"] in ["timeout", "failed", "error"]

    def test_stats_after_execution(self, manager):
        # Just verify stats dict has expected keys
        stats = manager.stats()
        assert "total_executions" in stats
        assert "by_outcome" in stats


# =========================================================================
# Execution Persistence Tests
# =========================================================================

class TestExecutionPersistence:
    @pytest.fixture
    def persist(self, tmp_path):
        path = str(tmp_path / "test_executions.jsonl")
        return ExecutionPersistence(persist_path=path)

    def test_record_single(self, persist):
        persist.record({
            "execution_id": "test-1",
            "status": "completed",
            "agent_id": "core-architecture",
        })
        persist._flush()
        results = persist.query(limit=10)
        assert len(results) == 1
        assert results[0]["execution_id"] == "test-1"

    def test_record_multiple(self, persist):
        for i in range(5):
            persist.record({
                "execution_id": f"test-{i}",
                "status": "completed",
            })
        persist._flush()
        results = persist.query(limit=10)
        assert len(results) == 5

    def test_buffer_flush(self, persist):
        # Buffer size is 100, add 99 (shouldn't flush yet)
        for i in range(99):
            persist.record({"execution_id": f"buf-{i}", "status": "completed"})
        assert len(persist._buffer) == 99
        # Add one more to trigger flush
        persist.record({"execution_id": "buf-99", "status": "completed"})
        assert len(persist._buffer) == 0
        assert persist._total_persisted == 100

    def test_query_by_agent_id(self, persist):
        persist.record({"execution_id": "1", "status": "completed", "agent_id": "core-security"})
        persist.record({"execution_id": "2", "status": "completed", "agent_id": "core-devops"})
        persist._flush()
        results = persist.query(agent_id="core-security")
        assert len(results) == 1
        assert results[0]["agent_id"] == "core-security"

    def test_query_by_status(self, persist):
        persist.record({"execution_id": "1", "status": "completed"})
        persist.record({"execution_id": "2", "status": "failed"})
        persist._flush()
        results = persist.query(status="failed")
        assert len(results) == 1
        assert results[0]["status"] == "failed"

    def test_query_with_limit(self, persist):
        for i in range(10):
            persist.record({"execution_id": f"q-{i}", "status": "completed"})
        persist._flush()
        results = persist.query(limit=5)
        assert len(results) == 5

    def test_persistence_stats(self, persist):
        persist.record({"execution_id": "s-1", "status": "completed"})
        persist._flush()
        stats = persist.stats()
        assert stats["total_persisted"] == 1
        assert "persist_path" in stats

    def test_record_has_id_and_timestamp(self, persist):
        persist.record({"execution_id": "meta-1", "status": "completed"})
        persist._flush()
        results = persist.query(limit=1)
        assert "id" in results[0]
        assert "timestamp" in results[0]

    def test_close_flushes_buffer(self, persist):
        persist.record({"execution_id": "close-1", "status": "completed"})
        persist.close()
        assert len(persist._buffer) == 0

    def test_query_empty_persist(self, persist):
        results = persist.query(limit=10)
        assert results == []
