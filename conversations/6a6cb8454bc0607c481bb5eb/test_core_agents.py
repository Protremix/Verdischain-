"""
Tests for EvolvixOS Core Agents, RBAC, and Audit Logging
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core_agents import (
    CoreAgent, AgentRole, CORE_AGENTS, get_agent, get_agent_by_id,
    list_agents, list_auto_run_agents, agents_summary
)


# =========================================================================
# Core Agents Tests
# =========================================================================

class TestCoreAgents:
    def test_agent_count(self):
        assert len(CORE_AGENTS) == 16  # 15 listed + release = 16 total

    def test_all_roles_unique(self):
        roles = [a.role for a in CORE_AGENTS]
        assert len(roles) == len(set(roles))

    def test_all_have_system_prompts(self):
        for agent in CORE_AGENTS:
            assert len(agent.system_prompt) > 100, f"Agent {agent.name} has short prompt"

    def test_get_agent_by_role(self):
        agent = get_agent(AgentRole.ARCHITECTURE)
        assert agent is not None
        assert agent.name == "Architecture Agent"

    def test_get_agent_by_id(self):
        agent = get_agent_by_id("core-architecture")
        assert agent is not None
        assert agent.role == AgentRole.ARCHITECTURE

    def test_get_nonexistent_agent(self):
        assert get_agent_by_id("nonexistent") is None

    def test_list_agents(self):
        agents = list_agents()
        assert len(agents) >= 15

    def test_list_auto_run_agents(self):
        agents = list_auto_run_agents()
        assert len(agents) > 0
        for a in agents:
            assert a.auto_run == True

    def test_agents_summary(self):
        summary = agents_summary()
        assert "total" in summary
        assert "auto_run" in summary
        assert "agents" in summary
        assert summary["total"] >= 15

    def test_agent_to_dict(self):
        agent = get_agent(AgentRole.SECURITY)
        d = agent.to_dict()
        assert d["id"] == "core-security"
        assert d["role"] == "security"
        assert "chat" in d["capabilities"]

    def test_agent_has_tools(self):
        arch = get_agent(AgentRole.ARCHITECTURE)
        assert len(arch.tools) > 0

    def test_agent_ids(self):
        for agent in CORE_AGENTS:
            assert agent.id.startswith("core-")
            assert agent.role.value in agent.id


class TestAgentRoles:
    def test_role_values(self):
        assert AgentRole.ARCHITECTURE.value == "architecture"
        assert AgentRole.PLANNING.value == "planning"
        assert AgentRole.SECURITY.value == "security"
        assert AgentRole.RELEASE.value == "release"

    def test_role_count(self):
        assert len(AgentRole) >= 15


# =========================================================================
# RBAC Tests (tested via API)
# =========================================================================

class TestRBAC:
    def test_create_user(self):
        from core_agents_api import rbac, Role, Permission
        user = rbac.create_user("test-user-1", Role.DEVELOPER)
        assert user["user_id"] == "test-user-1"
        assert user["role"] == Role.DEVELOPER
        assert Permission.READ.value in user["permissions"]

    def test_create_duplicate_user(self):
        from core_agents_api import rbac, Role
        rbac.create_user("dup-user", Role.DEVELOPER)
        with pytest.raises(ValueError):
            rbac.create_user("dup-user", Role.DEVELOPER)

    def test_assign_role(self):
        from core_agents_api import rbac, Role
        rbac.create_user("role-test", Role.VIEWER)
        result = rbac.assign_role("role-test", Role.ENGINEER)
        assert result == True
        user = rbac._users["role-test"]
        assert user["role"] == Role.ENGINEER

    def test_create_api_key(self):
        from core_agents_api import rbac, Role
        rbac.create_user("key-test", Role.ENGINEER)
        raw_key = rbac.create_api_key("key-test", ["read", "execute"])
        assert raw_key.startswith("evx_")

    def test_authenticate_api_key(self):
        from core_agents_api import rbac, Role
        rbac.create_user("auth-test", Role.DEVELOPER)
        raw_key = rbac.create_api_key("auth-test")
        auth = rbac.authenticate(raw_key)
        assert auth is not None
        assert auth["user_id"] == "auth-test"

    def test_authenticate_invalid_key(self):
        from core_agents_api import rbac
        result = rbac.authenticate("invalid-key")
        assert result is None

    def test_has_permission(self):
        from core_agents_api import rbac, Role, Permission
        rbac.create_user("perm-test", Role.ENGINEER)
        assert rbac.has_permission("perm-test", Permission.DEPLOY) == True
        assert rbac.has_permission("perm-test", Permission.MANAGE_SECRETS) == False

    def test_admin_has_all_permissions(self):
        from core_agents_api import rbac, Role, Permission
        rbac.create_user("admin-test", Role.ADMIN)
        for perm in Permission:
            assert rbac.has_permission("admin-test", perm) == True

    def test_viewer_permissions(self):
        from core_agents_api import rbac, Role, Permission
        rbac.create_user("viewer-test", Role.VIEWER)
        assert rbac.has_permission("viewer-test", Permission.READ) == True
        assert rbac.has_permission("viewer-test", Permission.WRITE) == False

    def test_owner_has_all(self):
        from core_agents_api import rbac, Role, Permission
        rbac.create_user("owner-test", Role.OWNER)
        for perm in Permission:
            assert rbac.has_permission("owner-test", perm) == True

    def test_rbac_stats(self):
        from core_agents_api import rbac
        stats = rbac.stats()
        assert "total_users" in stats
        assert "total_api_keys" in stats


# =========================================================================
# Audit Logger Tests
# =========================================================================

class TestAuditLogger:
    def test_log_entry(self):
        from core_agents_api import audit
        entry = audit.log("test.action", "test-user", "test-resource")
        assert entry["action"] == "test.action"
        assert entry["user_id"] == "test-user"
        assert entry["resource"] == "test-resource"
        assert "timestamp" in entry
        assert "id" in entry

    def test_log_with_details(self):
        from core_agents_api import audit
        entry = audit.log("test.detail", "user", "res", {"key": "value"}, "warning")
        assert entry["details"] == {"key": "value"}
        assert entry["severity"] == "warning"

    def test_list_entries(self):
        from core_agents_api import audit
        audit.log("list.test.1", "user1")
        audit.log("list.test.2", "user2")
        entries = audit.list(limit=10)
        assert len(entries) >= 2

    def test_list_by_action(self):
        from core_agents_api import audit
        audit.log("filter.action", "user1")
        entries = audit.list(action="filter.action")
        assert all(e["action"] == "filter.action" for e in entries)

    def test_list_by_user(self):
        from core_agents_api import audit
        audit.log("user.filter", "specific-user")
        entries = audit.list(user_id="specific-user")
        assert all(e["user_id"] == "specific-user" for e in entries)

    def test_list_by_severity(self):
        from core_agents_api import audit
        audit.log("sev.test", "user", "res", severity="warning")
        entries = audit.list(severity="warning")
        assert all(e["severity"] == "warning" for e in entries)

    def test_audit_stats(self):
        from core_agents_api import audit
        audit.log("stats.test", "user")
        stats = audit.stats()
        assert "total_entries" in stats
        assert "by_severity" in stats
        assert "by_action" in stats
