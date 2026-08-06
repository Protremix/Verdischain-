"""
EvolvixOS Agent Framework — Test Suite
Tests agent lifecycle, task management, memory operations, and API endpoints
"""

import pytest
import json
import os
import time
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

# Set env vars before importing
os.environ["AGENT_REGISTRY_FILE"] = "/tmp/test_agent_registry.json"
os.environ["TASK_HISTORY_FILE"] = "/tmp/test_task_history.json"
os.environ["DATABASE_URL"] = "postgresql://nonexistent:nonexistent@localhost:5432/nonexistent"

from agent_framework import (
    AgentManager, MemoryManager, Agent, Task, MemoryEntry,
    AgentStatus, TaskStatus, TaskPriority, AgentCapability, MemoryType,
)
from agent_api import app, agent_manager, memory_manager

client = TestClient(app)

# =========================================================================
# Memory Manager Tests
# =========================================================================

class TestMemoryManager:
    def setup_method(self):
        self.mm = MemoryManager()
        self.mm._use_db = False
        self.mm._store.clear()
        self.mm._key_index.clear()

    def test_store_memory(self):
        entry = self.mm.store("agent-1", "key1", {"data": "value1"})
        assert entry.key == "key1"
        assert entry.value == {"data": "value1"}
        assert entry.memory_type == MemoryType.LONG_TERM

    def test_retrieve_memory(self):
        self.mm.store("agent-1", "key1", "value1")
        entry = self.mm.retrieve("agent-1", "key1")
        assert entry is not None
        assert entry.value == "value1"
        assert entry.access_count == 1

    def test_retrieve_nonexistent(self):
        assert self.mm.retrieve("agent-1", "nonexistent") is None

    def test_store_overwrite(self):
        self.mm.store("agent-1", "key1", "old_value")
        self.mm.store("agent-1", "key1", "new_value")
        entry = self.mm.retrieve("agent-1", "key1")
        assert entry.value == "new_value"

    def test_retrieve_all(self):
        self.mm.store("agent-1", "key1", "val1")
        self.mm.store("agent-1", "key2", "val2")
        entries = self.mm.retrieve_all("agent-1")
        assert len(entries) == 2

    def test_retrieve_all_by_type(self):
        self.mm.store("agent-1", "key1", "val1", memory_type=MemoryType.SHORT_TERM)
        self.mm.store("agent-1", "key2", "val2", memory_type=MemoryType.LONG_TERM)
        entries = self.mm.retrieve_all("agent-1", MemoryType.SHORT_TERM)
        assert len(entries) == 1
        assert entries[0].key == "key1"

    def test_search_memory(self):
        self.mm.store("agent-1", "project_context", {"name": "EvolvixOS"})
        self.mm.store("agent-1", "user_preference", "dark_mode")
        results = self.mm.search("agent-1", "project")
        assert len(results) == 1
        assert results[0].key == "project_context"

    def test_update_memory(self):
        self.mm.store("agent-1", "key1", "old")
        entry = self.mm.update("agent-1", "key1", "new")
        assert entry.value == "new"

    def test_update_nonexistent(self):
        assert self.mm.update("agent-1", "nonexistent", "val") is None

    def test_delete_memory(self):
        self.mm.store("agent-1", "key1", "val1")
        assert self.mm.delete("agent-1", "key1") == True
        assert self.mm.retrieve("agent-1", "key1") is None

    def test_delete_nonexistent(self):
        assert self.mm.delete("agent-1", "nonexistent") == False

    def test_clear_agent(self):
        self.mm.store("agent-1", "key1", "val1")
        self.mm.store("agent-1", "key2", "val2")
        count = self.mm.clear_agent("agent-1")
        assert count == 2
        assert self.mm.retrieve("agent-1", "key1") is None

    def test_memory_stats(self):
        self.mm.store("agent-1", "key1", "val1", importance=0.8)
        self.mm.store("agent-1", "key2", "val2", importance=0.3)
        stats = self.mm.get_stats("agent-1")
        assert stats["total_memories"] == 2
        assert "by_type" in stats
        assert "avg_importance" in stats

    def test_ttl_expiry(self):
        self.mm.store("agent-1", "temp_key", "temp_val", ttl_seconds=0)
        time.sleep(0.1)
        # Should be expired
        entry = self.mm.retrieve("agent-1", "temp_key")
        assert entry is None

    def test_different_agents_isolated(self):
        self.mm.store("agent-a", "shared_key", "value_a")
        self.mm.store("agent-b", "shared_key", "value_b")
        assert self.mm.retrieve("agent-a", "shared_key").value == "value_a"
        assert self.mm.retrieve("agent-b", "shared_key").value == "value_b"

    def test_importance_affects_ordering(self):
        self.mm.store("agent-1", "low", "val1", importance=0.1)
        self.mm.store("agent-1", "high", "val2", importance=0.9)
        entries = self.mm.retrieve_all("agent-1")
        # Higher importance should come first (sorted by importance DESC in search)
        results = self.mm.search("agent-1", "val")
        assert results[0].importance >= results[-1].importance

# =========================================================================
# Agent Manager Tests
# =========================================================================

class TestAgentManager:
    def setup_method(self):
        self.mm = MemoryManager()
        self.mm._use_db = False
        self.mm._store.clear()
        self.mm._key_index.clear()
        self.am = AgentManager(self.mm, gateway_url="http://localhost:3500")
        self.am.agents.clear()
        self.am.tasks.clear()
        self.am._task_queue.clear()
        self.am._agent_registry_file = "/tmp/test_agent_registry.json"

    def test_create_agent(self):
        agent = self.am.create_agent("Test Agent", "A test agent")
        assert agent.name == "Test Agent"
        assert agent.status == AgentStatus.CREATED
        assert agent.id in self.am.agents

    def test_get_agent(self):
        agent = self.am.create_agent("Test")
        assert self.am.get_agent(agent.id).name == "Test"

    def test_get_nonexistent_agent(self):
        assert self.am.get_agent("nonexistent") is None

    def test_list_agents(self):
        self.am.create_agent("Agent 1")
        self.am.create_agent("Agent 2")
        assert len(self.am.list_agents()) == 2

    def test_list_agents_by_status(self):
        agent = self.am.create_agent("Test")
        agent.status = AgentStatus.RUNNING
        running = self.am.list_agents(status=AgentStatus.RUNNING)
        assert len(running) == 1
        created = self.am.list_agents(status=AgentStatus.CREATED)
        assert len(created) == 0

    def test_update_agent(self):
        agent = self.am.create_agent("Test")
        updated = self.am.update_agent(agent.id, name="Updated", description="New desc")
        assert updated.name == "Updated"
        assert updated.description == "New desc"

    def test_update_nonexistent_agent(self):
        assert self.am.update_agent("nonexistent", name="Test") is None

    def test_delete_agent(self):
        agent = self.am.create_agent("Test")
        assert self.am.delete_agent(agent.id) == True
        assert agent.id not in self.am.agents

    def test_delete_agent_clears_memory(self):
        agent = self.am.create_agent("Test")
        self.mm.store(agent.id, "key1", "val1")
        self.am.delete_agent(agent.id)
        assert self.mm.retrieve(agent.id, "key1") is None

    def test_start_agent(self):
        agent = self.am.create_agent("Test")
        assert self.am.start_agent(agent.id) == True
        assert agent.status == AgentStatus.RUNNING

    def test_pause_agent(self):
        agent = self.am.create_agent("Test")
        self.am.start_agent(agent.id)
        assert self.am.pause_agent(agent.id) == True
        assert agent.status == AgentStatus.PAUSED

    def test_stop_agent(self):
        agent = self.am.create_agent("Test")
        self.am.start_agent(agent.id)
        assert self.am.stop_agent(agent.id) == True
        assert agent.status == AgentStatus.STOPPED

    def test_start_nonexistent(self):
        assert self.am.start_agent("nonexistent") == False

    def test_create_task(self):
        agent = self.am.create_agent("Test")
        self.am.start_agent(agent.id)
        task = self.am.create_task(agent.id, "chat", {"text": "hello"})
        assert task is not None
        assert task.status == TaskStatus.PENDING
        assert task.agent_id == agent.id

    def test_create_task_not_running(self):
        agent = self.am.create_agent("Test")
        task = self.am.create_task(agent.id, "chat", {"text": "hello"})
        assert task is None  # Agent not running

    def test_create_task_nonexistent_agent(self):
        task = self.am.create_task("nonexistent", "chat", {"text": "hello"})
        assert task is None

    def test_get_task(self):
        agent = self.am.create_agent("Test")
        self.am.start_agent(agent.id)
        task = self.am.create_task(agent.id, "chat", {"text": "hello"})
        assert self.am.get_task(task.id) is not None

    def test_list_tasks(self):
        agent = self.am.create_agent("Test")
        self.am.start_agent(agent.id)
        self.am.create_task(agent.id, "chat", {"text": "1"})
        self.am.create_task(agent.id, "chat", {"text": "2"})
        assert len(self.am.list_tasks()) == 2

    def test_list_tasks_by_agent(self):
        agent1 = self.am.create_agent("Agent1")
        agent2 = self.am.create_agent("Agent2")
        self.am.start_agent(agent1.id)
        self.am.start_agent(agent2.id)
        self.am.create_task(agent1.id, "chat", {"text": "1"})
        self.am.create_task(agent2.id, "chat", {"text": "2"})
        assert len(self.am.list_tasks(agent_id=agent1.id)) == 1

    def test_cancel_task(self):
        agent = self.am.create_agent("Test")
        self.am.start_agent(agent.id)
        task = self.am.create_task(agent.id, "chat", {"text": "hello"})
        assert self.am.cancel_task(task.id) == True
        assert task.status == TaskStatus.CANCELLED

    def test_cancel_completed_task(self):
        agent = self.am.create_agent("Test")
        self.am.start_agent(agent.id)
        task = self.am.create_task(agent.id, "chat", {"text": "hello"})
        task.status = TaskStatus.COMPLETED
        assert self.am.cancel_task(task.id) == False

    def test_agent_stats(self):
        agent = self.am.create_agent("Test", capabilities=["chat"])
        self.am.start_agent(agent.id)
        self.am.create_task(agent.id, "chat", {"text": "hello"})
        stats = self.am.get_agent_stats(agent.id)
        assert stats["name"] == "Test"
        assert stats["total_tasks"] == 1
        assert "memory" in stats

    def test_framework_stats(self):
        self.am.create_agent("Agent1")
        self.am.create_agent("Agent2")
        stats = self.am.get_framework_stats()
        assert stats["total_agents"] == 2
        assert "agents_by_status" in stats

    def test_task_with_priority(self):
        agent = self.am.create_agent("Test")
        self.am.start_agent(agent.id)
        task = self.am.create_task(agent.id, "chat", {"text": "urgent"}, priority=TaskPriority.CRITICAL)
        assert task.priority == TaskPriority.CRITICAL

    def test_task_with_parent(self):
        agent = self.am.create_agent("Test")
        self.am.start_agent(agent.id)
        parent = self.am.create_task(agent.id, "chat", {"text": "parent"})
        child = self.am.create_task(agent.id, "chat", {"text": "child"}, parent_task_id=parent.id)
        assert child.parent_task_id == parent.id

    def test_capabilities_preserved(self):
        agent = self.am.create_agent("Test", capabilities=["chat", "code_review"])
        assert AgentCapability.CHAT in agent.capabilities
        assert AgentCapability.CODE_REVIEW in agent.capabilities

# =========================================================================
# API Endpoint Tests
# =========================================================================

class TestAgentAPI:
    def setup_method(self):
        # Clear state
        agent_manager.agents.clear()
        agent_manager.tasks.clear()
        memory_manager._store.clear()
        memory_manager._key_index.clear()

    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"

    def test_create_agent_endpoint(self):
        resp = client.post("/agents", json={
            "name": "API Test Agent",
            "description": "Test via API",
            "capabilities": ["chat"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "API Test Agent"
        assert data["status"] == "created"

    def test_list_agents_endpoint(self):
        client.post("/agents", json={"name": "List Test", "capabilities": ["chat"]})
        resp = client.get("/agents")
        assert resp.status_code == 200
        assert resp.json()["count"] >= 1

    def test_get_agent_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Get Test"})
        agent_id = create_resp.json()["id"]
        resp = client.get(f"/agents/{agent_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Get Test"

    def test_get_nonexistent_agent(self):
        resp = client.get("/agents/nonexistent")
        assert resp.status_code == 404

    def test_update_agent_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Update Test"})
        agent_id = create_resp.json()["id"]
        resp = client.patch(f"/agents/{agent_id}", json={"name": "Updated Name"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    def test_delete_agent_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Delete Test"})
        agent_id = create_resp.json()["id"]
        resp = client.delete(f"/agents/{agent_id}")
        assert resp.status_code == 200
        assert resp.json()["success"] == True

    def test_start_agent_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Start Test"})
        agent_id = create_resp.json()["id"]
        resp = client.post(f"/agents/{agent_id}/start")
        assert resp.status_code == 200
        assert resp.json()["status"] == "running"

    def test_pause_agent_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Pause Test"})
        agent_id = create_resp.json()["id"]
        client.post(f"/agents/{agent_id}/start")
        resp = client.post(f"/agents/{agent_id}/pause")
        assert resp.status_code == 200
        assert resp.json()["status"] == "paused"

    def test_stop_agent_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Stop Test"})
        agent_id = create_resp.json()["id"]
        client.post(f"/agents/{agent_id}/start")
        resp = client.post(f"/agents/{agent_id}/stop")
        assert resp.status_code == 200
        assert resp.json()["status"] == "stopped"

    def test_agent_stats_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Stats Test"})
        agent_id = create_resp.json()["id"]
        resp = client.get(f"/agents/{agent_id}/stats")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Stats Test"

    def test_create_task_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Task Test"})
        agent_id = create_resp.json()["id"]
        client.post(f"/agents/{agent_id}/start")
        resp = client.post(f"/agents/{agent_id}/tasks", json={
            "task_type": "chat",
            "input_data": {"text": "Hello"},
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "pending"

    def test_create_task_not_running(self):
        create_resp = client.post("/agents", json={"name": "Not Running"})
        agent_id = create_resp.json()["id"]
        resp = client.post(f"/agents/{agent_id}/tasks", json={
            "task_type": "chat",
            "input_data": {"text": "Hello"},
        })
        assert resp.status_code == 400

    def test_list_tasks_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Task List"})
        agent_id = create_resp.json()["id"]
        client.post(f"/agents/{agent_id}/start")
        client.post(f"/agents/{agent_id}/tasks", json={
            "task_type": "chat",
            "input_data": {"text": "1"},
        })
        resp = client.get("/tasks")
        assert resp.status_code == 200
        assert resp.json()["count"] >= 1

    def test_get_task_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Get Task"})
        agent_id = create_resp.json()["id"]
        client.post(f"/agents/{agent_id}/start")
        task_resp = client.post(f"/agents/{agent_id}/tasks", json={
            "task_type": "chat",
            "input_data": {"text": "test"},
        })
        task_id = task_resp.json()["id"]
        resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code == 200

    def test_cancel_task_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Cancel Task"})
        agent_id = create_resp.json()["id"]
        client.post(f"/agents/{agent_id}/start")
        task_resp = client.post(f"/agents/{agent_id}/tasks", json={
            "task_type": "chat",
            "input_data": {"text": "test"},
        })
        task_id = task_resp.json()["id"]
        resp = client.post(f"/tasks/{task_id}/cancel")
        assert resp.status_code == 200

    # Memory API tests

    def test_store_memory_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Memory Test"})
        agent_id = create_resp.json()["id"]
        resp = client.post(f"/agents/{agent_id}/memory", json={
            "key": "test_key",
            "value": "test_value",
        })
        assert resp.status_code == 200
        assert resp.json()["key"] == "test_key"

    def test_get_memory_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Get Memory"})
        agent_id = create_resp.json()["id"]
        client.post(f"/agents/{agent_id}/memory", json={
            "key": "test_key",
            "value": "test_value",
        })
        resp = client.get(f"/agents/{agent_id}/memory/test_key")
        assert resp.status_code == 200
        assert resp.json()["value"] == "test_value"

    def test_get_nonexistent_memory(self):
        resp = client.get("/agents/fake_agent/memory/nonexistent")
        assert resp.status_code == 404

    def test_list_memory_endpoint(self):
        create_resp = client.post("/agents", json={"name": "List Memory"})
        agent_id = create_resp.json()["id"]
        client.post(f"/agents/{agent_id}/memory", json={"key": "k1", "value": "v1"})
        client.post(f"/agents/{agent_id}/memory", json={"key": "k2", "value": "v2"})
        resp = client.get(f"/agents/{agent_id}/memory")
        assert resp.status_code == 200
        assert resp.json()["count"] == 2

    def test_update_memory_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Update Memory"})
        agent_id = create_resp.json()["id"]
        client.post(f"/agents/{agent_id}/memory", json={"key": "k1", "value": "old"})
        resp = client.patch(f"/agents/{agent_id}/memory/k1", json={"value": "new"})
        assert resp.status_code == 200
        assert resp.json()["value"] == "new"

    def test_delete_memory_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Del Memory"})
        agent_id = create_resp.json()["id"]
        client.post(f"/agents/{agent_id}/memory", json={"key": "k1", "value": "v1"})
        resp = client.delete(f"/agents/{agent_id}/memory/k1")
        assert resp.status_code == 200

    def test_search_memory_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Search Memory"})
        agent_id = create_resp.json()["id"]
        client.post(f"/agents/{agent_id}/memory", json={"key": "project_info", "value": "EvolvixOS"})
        resp = client.get(f"/agents/{agent_id}/memory/search/project")
        assert resp.status_code == 200
        assert resp.json()["count"] >= 1

    def test_memory_stats_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Mem Stats"})
        agent_id = create_resp.json()["id"]
        client.post(f"/agents/{agent_id}/memory", json={"key": "k1", "value": "v1"})
        resp = client.get(f"/agents/{agent_id}/memory/stats")
        assert resp.status_code == 200
        assert resp.json()["total_memories"] >= 1

    def test_clear_memory_endpoint(self):
        create_resp = client.post("/agents", json={"name": "Clear Mem"})
        agent_id = create_resp.json()["id"]
        client.post(f"/agents/{agent_id}/memory", json={"key": "k1", "value": "v1"})
        resp = client.delete(f"/agents/{agent_id}/memory")
        assert resp.status_code == 200
        assert resp.json()["deleted_count"] >= 1

    def test_framework_stats_endpoint(self):
        resp = client.get("/stats")
        assert resp.status_code == 200
        assert "total_agents" in resp.json()

    def test_cleanup_expired_endpoint(self):
        resp = client.post("/memory/cleanup")
        assert resp.status_code == 200
        assert "expired_count" in resp.json()

# =========================================================================
# Integration Tests
# =========================================================================

class TestAgentMemoryIntegration:
    def setup_method(self):
        self.mm = MemoryManager()
        self.mm._use_db = False
        self.mm._store.clear()
        self.mm._key_index.clear()
        self.am = AgentManager(self.mm, gateway_url="http://localhost:3500")
        self.am.agents.clear()
        self.am.tasks.clear()

    def test_agent_with_memory_context(self):
        """Agent should have access to its memories when building gateway input"""
        agent = self.am.create_agent("Context Agent", system_prompt="You are helpful.")
        self.am.start_agent(agent.id)

        # Store some context
        self.mm.store(agent.id, "project", "EvolvixOS", importance=0.9)
        self.mm.store(agent.id, "user_name", "Rojs", importance=0.7)

        # Create a task
        task = self.am.create_task(agent.id, "chat", {"text": "What is my project?"})

        # Build gateway input (should include memory context)
        gateway_input = self.am._build_gateway_input(task, agent)

        # Check that memory context is included
        input_str = json.dumps(gateway_input)
        assert "EvolvixOS" in input_str or "project" in input_str

    def test_task_result_stored_in_memory(self):
        """Completed tasks should store results in episodic memory"""
        agent = self.am.create_agent("Result Agent")
        self.am.start_agent(agent.id)
        task = self.am.create_task(agent.id, "chat", {"text": "hello"})

        # Manually store a result (simulating completion)
        self.mm.store(
            agent_id=agent.id,
            key=f"task_result:{task.id}",
            value={"sentiment": "positive"},
            memory_type=MemoryType.EPISODIC,
        )

        # Verify it's stored
        entry = self.mm.retrieve(agent.id, f"task_result:{task.id}")
        assert entry is not None
        assert entry.value == {"sentiment": "positive"}
        assert entry.memory_type == MemoryType.EPISODIC

    def test_agent_isolation(self):
        """Agents should have isolated memory"""
        agent1 = self.am.create_agent("Agent 1")
        agent2 = self.am.create_agent("Agent 2")

        self.mm.store(agent1.id, "secret", "agent1_secret")
        self.mm.store(agent2.id, "secret", "agent2_secret")

        assert self.mm.retrieve(agent1.id, "secret").value == "agent1_secret"
        assert self.mm.retrieve(agent2.id, "secret").value == "agent2_secret"

    def test_agent_lifecycle_full(self):
        """Test full agent lifecycle: create → start → task → stop → delete"""
        # Create
        agent = self.am.create_agent("Lifecycle Agent", capabilities=["chat", "sentiment"])
        assert agent.status == AgentStatus.CREATED

        # Start
        self.am.start_agent(agent.id)
        assert agent.status == AgentStatus.RUNNING

        # Create task
        task = self.am.create_task(agent.id, "sentiment", {"text": "Great!"})
        assert task.status == TaskStatus.PENDING

        # Stop
        self.am.stop_agent(agent.id)
        assert agent.status == AgentStatus.STOPPED

        # Delete (should clear memory)
        self.mm.store(agent.id, "temp", "data")
        self.am.delete_agent(agent.id)
        assert agent.id not in self.am.agents
        assert self.mm.retrieve(agent.id, "temp") is None
