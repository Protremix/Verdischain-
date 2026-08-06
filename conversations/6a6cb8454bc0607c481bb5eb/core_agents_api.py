"""
EvolvixOS Core Agents API + RBAC + Audit Logging
REST API for managing and invoking the 15 core agents.
"""

from fastapi import FastAPI, HTTPException, Query, Request, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from collections import defaultdict
import structlog
import os
import json
import hashlib
import time

from core_agents import (
    CoreAgent, AgentRole, CORE_AGENTS, get_agent, get_agent_by_id,
    list_agents, list_auto_run_agents, agents_summary
)

logger = structlog.get_logger()

app = FastAPI(
    title="EvolvixOS Core Agents API",
    description="15 specialized AI agents for autonomous engineering",
    version="1.0.0",
)


# =========================================================================
# RBAC (Role-Based Access Control)
# =========================================================================

class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"
    DEPLOY = "deploy"
    MANAGE_AGENTS = "manage_agents"
    MANAGE_PLUGINS = "manage_plugins"
    MANAGE_SECRETS = "manage_secrets"
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT = "view_audit"

from enum import Enum

class Role(str, Enum):
    VIEWER = "viewer"
    DEVELOPER = "developer"
    ENGINEER = "engineer"
    ADMIN = "admin"
    OWNER = "owner"

ROLE_PERMISSIONS = {
    Role.VIEWER: [Permission.READ, Permission.VIEW_AUDIT],
    Role.DEVELOPER: [Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.VIEW_AUDIT],
    Role.ENGINEER: [Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.DEPLOY, Permission.VIEW_AUDIT],
    Role.ADMIN: [Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.DEPLOY,
                Permission.MANAGE_AGENTS, Permission.MANAGE_PLUGINS, Permission.ADMIN, Permission.VIEW_AUDIT],
    Role.OWNER: [p for p in Permission],  # all permissions
}


class RBACManager:
    """Role-based access control for EvolvixOS."""
    
    def __init__(self):
        self._users: Dict[str, Dict] = {}  # user_id -> {role, permissions}
        self._api_keys: Dict[str, Dict] = {}  # hashed_key -> {user_id, role, scopes}
    
    def create_user(self, user_id: str, role: Role = Role.DEVELOPER) -> Dict:
        """Create a new user with a role."""
        if user_id in self._users:
            raise ValueError(f"User '{user_id}' already exists")
        perms = ROLE_PERMISSIONS.get(role, [Permission.READ])
        self._users[user_id] = {
            "user_id": user_id,
            "role": role,
            "permissions": [p.value for p in perms],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(f"Created user: {user_id} ({role.value})")
        return self._users[user_id]
    
    def assign_role(self, user_id: str, role: Role) -> bool:
        """Change a user's role."""
        if user_id not in self._users:
            return False
        perms = ROLE_PERMISSIONS.get(role, [Permission.READ])
        self._users[user_id]["role"] = role
        self._users[user_id]["permissions"] = [p.value for p in perms]
        return True
    
    def create_api_key(self, user_id: str, scopes: List[str] = None) -> str:
        """Create an API key for a user."""
        if user_id not in self._users:
            raise ValueError(f"User '{user_id}' not found")
        raw_key = f"evx_{hashlib.sha256(f'{user_id}:{time.time()}'.encode()).hexdigest()[:32]}"
        hashed = hashlib.sha256(raw_key.encode()).hexdigest()
        self._api_keys[hashed] = {
            "user_id": user_id,
            "role": self._users[user_id]["role"],
            "scopes": scopes or ["read", "execute"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return raw_key  # return raw key only once
    
    def authenticate(self, raw_key: str) -> Optional[Dict]:
        """Authenticate an API key."""
        hashed = hashlib.sha256(raw_key.encode()).hexdigest()
        return self._api_keys.get(hashed)
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if a user has a permission."""
        user = self._users.get(user_id)
        if not user:
            return False
        return permission.value in user["permissions"]
    
    def list_users(self) -> List[Dict]:
        return list(self._users.values())
    
    def list_api_keys(self) -> List[Dict]:
        return [{**v, "key_id": k[:8] + "..."} for k, v in self._api_keys.items()]
    
    def stats(self) -> Dict:
        return {
            "total_users": len(self._users),
            "total_api_keys": len(self._api_keys),
            "roles": {r.value: sum(1 for u in self._users.values() if u["role"] == r) for r in Role},
        }


# =========================================================================
# Audit Logging
# =========================================================================

class AuditLogger:
    """Audit logging for all security-relevant actions."""
    
    def __init__(self, persist_path: str = None):
        self._persist_path = persist_path
        self._entries: List[Dict] = []
        self._max_entries = 10000
    
    def log(self, action: str, user_id: str = "system", resource: str = "",
            details: Dict = None, severity: str = "info"):
        """Log an audit entry."""
        entry = {
            "id": hashlib.sha256(f"{action}:{time.time()}".encode()).hexdigest()[:16],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "user_id": user_id,
            "resource": resource,
            "details": details or {},
            "severity": severity,
        }
        self._entries.append(entry)
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]
        
        if severity == "warning":
            logger.warning(f"AUDIT: {action} by {user_id} on {resource}")
        elif severity == "critical":
            logger.error(f"AUDIT CRITICAL: {action} by {user_id} on {resource}")
        else:
            logger.info(f"AUDIT: {action} by {user_id} on {resource}")
        
        return entry
    
    def list(self, limit: int = 100, action: str = None, user_id: str = None,
             severity: str = None) -> List[Dict]:
        """Query audit log entries."""
        entries = self._entries
        if action:
            entries = [e for e in entries if e["action"] == action]
        if user_id:
            entries = [e for e in entries if e["user_id"] == user_id]
        if severity:
            entries = [e for e in entries if e["severity"] == severity]
        return entries[-limit:]
    
    def stats(self) -> Dict:
        severity_counts = defaultdict(int)
        action_counts = defaultdict(int)
        for e in self._entries:
            severity_counts[e["severity"]] += 1
            action_counts[e["action"]] += 1
        return {
            "total_entries": len(self._entries),
            "by_severity": dict(severity_counts),
            "by_action": dict(action_counts),
        }


# =========================================================================
# Global instances
# =========================================================================

rbac = RBACManager()
audit = AuditLogger()

# Create default admin user
rbac.create_user("admin", Role.ADMIN)
rbac.create_user("owner", Role.OWNER)

# Log startup
audit.log("system.startup", "system", "core_agents_api", {"agents": len(CORE_AGENTS)})


# =========================================================================
# Request Models
# =========================================================================

class InvokeAgentRequest(BaseModel):
    role: str = Field(..., description="Agent role to invoke")
    input_data: Dict[str, Any] = Field(default_factory=dict)
    options: Dict[str, Any] = Field(default_factory=dict)
    provider: Optional[str] = None

class CreateUserRequest(BaseModel):
    user_id: str
    role: str = "developer"

class AssignRoleRequest(BaseModel):
    user_id: str
    role: str

class CreateApiKeyRequest(BaseModel):
    user_id: str
    scopes: List[str] = ["read", "execute"]


# =========================================================================
# Agent Endpoints
# =========================================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "agents": agents_summary()["total"],
        "auto_run_agents": agents_summary()["auto_run"],
        "rbac": rbac.stats(),
        "audit": audit.stats(),
    }

@app.get("/agents")
async def list_all_agents():
    """List all 15 core agents."""
    return agents_summary()

@app.get("/agents/{role}")
async def get_agent_by_role(role: str):
    """Get a specific agent by role."""
    try:
        agent_role = AgentRole(role)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Unknown role: {role}")
    agent = get_agent(agent_role)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.to_dict()

@app.get("/agents/auto-run/list")
async def list_auto_run():
    """List agents that run proactively."""
    agents = list_auto_run_agents()
    return {"agents": [a.to_dict() for a in agents], "count": len(agents)}

@app.post("/agents/invoke")
async def invoke_agent(req: InvokeAgentRequest):
    """Invoke a core agent."""
    agent = get_agent_by_id(f"core-{req.role}")
    if not agent:
        try:
            agent = get_agent(AgentRole(req.role))
        except ValueError:
            raise HTTPException(status_code=404, detail=f"Unknown agent role: {req.role}")
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    audit.log("agent.invoke", "system", agent.id, {"capability": agent.preferred_capability})
    
    return {
        "agent": agent.to_dict(),
        "system_prompt": agent.system_prompt[:200] + "...",
        "input_data": req.input_data,
        "status": "queued",
        "message": f"Agent '{agent.name}' queued for execution via {agent.preferred_capability}",
    }

# =========================================================================
# RBAC Endpoints
# =========================================================================

@app.get("/rbac/stats")
async def rbac_stats():
    """Get RBAC statistics."""
    return rbac.stats()

@app.get("/rbac/users")
async def list_users():
    """List all users."""
    return {"users": rbac.list_users()}

@app.post("/rbac/users")
async def create_user(req: CreateUserRequest):
    """Create a new user."""
    try:
        role = Role(req.role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {req.role}")
    try:
        user = rbac.create_user(req.user_id, role)
        audit.log("user.create", "system", req.user_id, {"role": req.role})
        return user
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.put("/rbac/users/{user_id}/role")
async def assign_role(user_id: str, req: AssignRoleRequest):
    """Assign a role to a user."""
    try:
        role = Role(req.role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {req.role}")
    result = rbac.assign_role(user_id, role)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    audit.log("user.role_change", "system", user_id, {"new_role": req.role})
    return {"success": True, "user_id": user_id, "role": req.role}

@app.post("/rbac/api-keys")
async def create_api_key(req: CreateApiKeyRequest):
    """Create an API key for a user."""
    try:
        raw_key = rbac.create_api_key(req.user_id, req.scopes)
        audit.log("api_key.create", "system", req.user_id, {"scopes": req.scopes}, "warning")
        return {"api_key": raw_key, "message": "Save this key — it won't be shown again"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/rbac/api-keys")
async def list_api_keys():
    """List all API keys (masked)."""
    return {"api_keys": rbac.list_api_keys()}

@app.get("/rbac/permissions")
async def list_permissions():
    """List all permissions and role mappings."""
    return {
        "permissions": [p.value for p in Permission],
        "roles": {r.value: [p.value for p in perms] for r, perms in ROLE_PERMISSIONS.items()},
    }

@app.get("/rbac/users/{user_id}/permissions")
async def check_permissions(user_id: str):
    """Check a user's permissions."""
    user = rbac._users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# =========================================================================
# Audit Log Endpoints
# =========================================================================

@app.get("/audit")
async def list_audit(limit: int = 100, action: str = None, user_id: str = None, severity: str = None):
    """Query audit log entries."""
    entries = audit.list(limit=limit, action=action, user_id=user_id, severity=severity)
    return {"entries": entries, "count": len(entries)}

@app.get("/audit/stats")
async def audit_stats():
    """Get audit log statistics."""
    return audit.stats()

@app.get("/audit/recent")
async def recent_audit(limit: int = 20):
    """Get recent audit entries."""
    entries = audit.list(limit=limit)
    return {"entries": entries, "count": len(entries)}
