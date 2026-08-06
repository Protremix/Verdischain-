"""
EvolvixOS RBAC Module v1.0
Granular Role-Based Access Control with per-organization permissions
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import structlog
import asyncio
import os
import json
import uuid

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/rbac", tags=["RBAC"])

import asyncpg

PG_DSN = os.getenv("DATABASE_URL", "postgresql://evolvixos:EvolvixOS2026Secure@localhost:5432/evolvixos")
_pg_pool: Optional[asyncpg.Pool] = None


async def init_rbac_pg():
    global _pg_pool
    if _pg_pool:
        return True
    for attempt in range(3):
        try:
            _pg_pool = await asyncpg.create_pool(PG_DSN, min_size=2, max_size=10, command_timeout=30)
            async with _pg_pool.acquire() as conn:
                # Roles table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS rbac_roles (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        org_id UUID,
                        name TEXT NOT NULL,
                        description TEXT,
                        permissions TEXT[] DEFAULT '{}',
                        is_system BOOLEAN DEFAULT false,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW(),
                        UNIQUE(org_id, name)
                    );
                """)
                # User role assignments
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS rbac_assignments (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id TEXT NOT NULL,
                        role_id UUID NOT NULL REFERENCES rbac_roles(id) ON DELETE CASCADE,
                        org_id UUID,
                        resource_type TEXT,
                        resource_id TEXT,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        UNIQUE(user_id, role_id, org_id)
                    );
                    CREATE INDEX IF NOT EXISTS idx_rbac_assign_user ON rbac_assignments(user_id);
                    CREATE INDEX IF NOT EXISTS idx_rbac_assign_role ON rbac_assignments(role_id);
                """)
                # Permission policies (fine-grained)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS rbac_policies (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        role_id UUID NOT NULL REFERENCES rbac_roles(id) ON DELETE CASCADE,
                        resource TEXT NOT NULL,
                        action TEXT NOT NULL,
                        conditions JSONB DEFAULT '{}',
                        effect TEXT DEFAULT 'allow',
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                    CREATE INDEX IF NOT EXISTS idx_rbac_policy_role ON rbac_policies(role_id);
                """)
                
                # Seed system roles
                system_roles = [
                    ("super_admin", "Full system access", ["*"], True),
                    ("org_admin", "Organization administrator", ["org:read", "org:write", "members:read", "members:write", "agents:read", "agents:write", "audit:read", "sso:read", "sso:write", "usage:read", "gdpr:read", "gdpr:write"], True),
                    ("org_member", "Organization member", ["org:read", "agents:read", "agents:execute", "usage:read:self", "gdpr:write:self"], True),
                    ("developer", "Developer access", ["agents:read", "agents:write", "agents:execute", "sdk:use", "docs:read"], True),
                    ("viewer", "Read-only access", ["org:read", "agents:read", "audit:read", "usage:read"], True),
                    ("api_only", "API-only access (no UI)", ["api:invoke", "usage:read:self"], True),
                ]
                for name, desc, perms, is_sys in system_roles:
                    await conn.execute("""
                        INSERT INTO rbac_roles (name, description, permissions, is_system)
                        SELECT $1, $2, $3, $4
                        WHERE NOT EXISTS (
                            SELECT 1 FROM rbac_roles WHERE name = $1 AND is_system = true
                        )
                    """, name, desc, perms, is_sys)
                
                # Define standard permissions catalog
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS rbac_permission_catalog (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        resource TEXT NOT NULL,
                        action TEXT NOT NULL,
                        description TEXT,
                        UNIQUE(resource, action)
                    );
                """)
                catalog = [
                    ("org", "read", "View organization details"),
                    ("org", "write", "Modify organization settings"),
                    ("org", "delete", "Delete organization"),
                    ("members", "read", "View organization members"),
                    ("members", "write", "Add/remove members"),
                    ("members", "invite", "Invite new members"),
                    ("agents", "read", "View AI agents"),
                    ("agents", "write", "Create/modify AI agents"),
                    ("agents", "execute", "Execute AI agent tasks"),
                    ("agents", "delete", "Delete AI agents"),
                    ("audit", "read", "View audit logs"),
                    ("audit", "write", "Create audit log entries"),
                    ("sso", "read", "View SSO configurations"),
                    ("sso", "write", "Create/modify SSO configurations"),
                    ("sso", "delete", "Delete SSO configurations"),
                    ("usage", "read", "View usage statistics (all)"),
                    ("usage", "read:self", "View own usage statistics"),
                    ("gdpr", "read", "View data subject requests"),
                    ("gdpr", "write", "Create data subject requests"),
                    ("gdpr", "write:self", "Create own data subject requests"),
                    ("api", "invoke", "Invoke API endpoints"),
                    ("sdk", "use", "Use developer SDK"),
                    ("docs", "read", "Access documentation"),
                    ("blockchain", "read", "View blockchain data"),
                    ("blockchain", "write", "Submit blockchain transactions"),
                    ("blockchain", "admin", "Administer blockchain (validators, params)"),
                    ("contracts", "read", "View smart contracts"),
                    ("contracts", "write", "Deploy smart contracts"),
                    ("contracts", "execute", "Execute smart contract calls"),
                    ("plugins", "read", "View plugins"),
                    ("plugins", "write", "Install/modify plugins"),
                    ("plugins", "publish", "Publish plugins to marketplace"),
                    ("*", "*", "Super admin (all permissions)"),
                ]
                for resource, action, desc in catalog:
                    await conn.execute("""
                        INSERT INTO rbac_permission_catalog (resource, action, description)
                        SELECT $1, $2, $3
                        WHERE NOT EXISTS (
                            SELECT 1 FROM rbac_permission_catalog WHERE resource = $1 AND action = $2
                        )
                    """, resource, action, desc)
                
            logger.info("RBAC PG tables initialized with system roles and permission catalog")
            return True
        except Exception as e:
            logger.warning(f"RBAC PG attempt {attempt+1}: {e}")
            await asyncio.sleep(2)
    return False


# =========================================================================
# RBAC Manager
# =========================================================================

class RBACManager:
    @staticmethod
    async def check_permission(user_id: str, resource: str, action: str, org_id: str = None) -> bool:
        """Check if a user has permission to perform an action on a resource."""
        if not _pg_pool: return True  # Open access when PG not connected
        
        try:
            async with _pg_pool.acquire() as conn:
                # Get user's role assignments
                assignments = await conn.fetch("""
                    SELECT r.permissions, r.is_system, p.effect, p.conditions
                    FROM rbac_assignments a
                    JOIN rbac_roles r ON a.role_id = r.id
                    LEFT JOIN rbac_policies p ON p.role_id = r.id AND p.resource = $1 AND p.action = $2
                    WHERE a.user_id = $3 AND (a.org_id IS NULL OR a.org_id = $4 OR a.org_id IS NULL)
                """, resource, action, user_id, uuid.UUID(org_id) if org_id else None)
                
                if not assignments:
                    return False
                
                for a in assignments:
                    perms = a["permissions"] or []
                    # Check for wildcard permission
                    if "*" in perms or f"{resource}:*" in perms or f"*:{action}" in perms or f"{resource}:{action}" in perms:
                        # Check for explicit deny policy
                        if a["effect"] == "deny":
                            return False
                        return True
                    # Check for self-scoped permission
                    if f"{resource}:{action}:self" in perms:
                        return True
                
                return False
        except Exception as e:
            logger.warning(f"RBAC check failed: {e}")
            return True  # Fail open for availability

    @staticmethod
    async def get_user_permissions(user_id: str, org_id: str = None) -> Dict[str, Any]:
        """Get all permissions for a user."""
        if not _pg_pool: return {"permissions": [], "roles": []}
        try:
            async with _pg_pool.acquire() as conn:
                assignments = await conn.fetch("""
                    SELECT r.id, r.name, r.permissions, r.is_system
                    FROM rbac_assignments a
                    JOIN rbac_roles r ON a.role_id = r.id
                    WHERE a.user_id = $1 AND (a.org_id IS NULL OR a.org_id = $2)
                """, user_id, uuid.UUID(org_id) if org_id else None)
                
                all_perms = set()
                roles = []
                for a in assignments:
                    roles.append({"id": str(a["id"]), "name": a["name"], "is_system": a["is_system"]})
                    for p in (a["permissions"] or []):
                        all_perms.add(p)
                
                return {"permissions": sorted(all_perms), "roles": roles}
        except Exception as e:
            return {"permissions": [], "roles": [], "error": str(e)}

    @staticmethod
    async def create_role(name: str, description: str = "", permissions: List[str] = None, org_id: str = None):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO rbac_roles (org_id, name, description, permissions, is_system)
                    VALUES ($1, $2, $3, $4, false)
                    RETURNING id, name, description, permissions, is_system, created_at
                """, uuid.UUID(org_id) if org_id else None, name, description, permissions or [])
                return dict(row)
        except asyncpg.UniqueViolationError:
            raise HTTPException(409, f"Role '{name}' already exists")
        except Exception as e:
            raise HTTPException(500, str(e))

    @staticmethod
    async def list_roles(org_id: str = None, include_system: bool = True):
        if not _pg_pool: return {"roles": [], "count": 0}
        try:
            async with _pg_pool.acquire() as conn:
                if org_id:
                    query = "SELECT * FROM rbac_roles WHERE org_id = $1 OR is_system = true"
                    rows = await conn.fetch(query, uuid.UUID(org_id))
                else:
                    query = "SELECT * FROM rbac_roles WHERE is_system = true" if not include_system else "SELECT * FROM rbac_roles"
                    rows = await conn.fetch(query)
                return {"roles": [dict(r) for r in rows], "count": len(rows)}
        except Exception as e:
            return {"roles": [], "count": 0, "error": str(e)}

    @staticmethod
    async def delete_role(role_id: str):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                # Prevent deleting system roles
                is_system = await conn.fetchval("SELECT is_system FROM rbac_roles WHERE id = $1", uuid.UUID(role_id))
                if is_system:
                    raise HTTPException(403, "Cannot delete system role")
                result = await conn.execute("DELETE FROM rbac_roles WHERE id = $1", uuid.UUID(role_id))
                if result == "DELETE 0": raise HTTPException(404, "Role not found")
                return {"deleted": True, "role_id": role_id}
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def assign_role(user_id: str, role_id: str, org_id: str = None, resource_type: str = None, resource_id: str = None):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO rbac_assignments (user_id, role_id, org_id, resource_type, resource_id)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id, user_id, role_id, org_id, created_at
                """, user_id, uuid.UUID(role_id), uuid.UUID(org_id) if org_id else None,
                    resource_type, resource_id)
                return dict(row)
        except asyncpg.UniqueViolationError:
            raise HTTPException(409, "Role already assigned to this user")
        except Exception as e:
            raise HTTPException(500, str(e))

    @staticmethod
    async def revoke_role(user_id: str, role_id: str, org_id: str = None):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM rbac_assignments WHERE user_id = $1 AND role_id = $2 AND (org_id = $3 OR ($3 IS NULL AND org_id IS NULL))
                """, user_id, uuid.UUID(role_id), uuid.UUID(org_id) if org_id else None)
                if result == "DELETE 0": raise HTTPException(404, "Assignment not found")
                return {"revoked": True, "user_id": user_id, "role_id": role_id}
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def get_user_roles(user_id: str):
        if not _pg_pool: return {"assignments": [], "count": 0}
        try:
            async with _pg_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT a.id, a.user_id, a.role_id, a.org_id, r.name as role_name, r.permissions, r.is_system
                    FROM rbac_assignments a
                    JOIN rbac_roles r ON a.role_id = r.id
                    WHERE a.user_id = $1
                """, user_id)
                return {"assignments": [dict(r) for r in rows], "count": len(rows)}
        except Exception as e:
            return {"assignments": [], "count": 0, "error": str(e)}

    @staticmethod
    async def add_policy(role_id: str, resource: str, action: str, conditions: Dict = None, effect: str = "allow"):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO rbac_policies (role_id, resource, action, conditions, effect)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id, role_id, resource, action, effect, created_at
                """, uuid.UUID(role_id), resource, action, json.dumps(conditions or {}), effect)
                return dict(row)
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def list_policies(role_id: str = None):
        if not _pg_pool: return {"policies": [], "count": 0}
        try:
            async with _pg_pool.acquire() as conn:
                if role_id:
                    rows = await conn.fetch("SELECT * FROM rbac_policies WHERE role_id = $1", uuid.UUID(role_id))
                else:
                    rows = await conn.fetch("SELECT * FROM rbac_policies")
                return {"policies": [dict(r) for r in rows], "count": len(rows)}
        except Exception as e:
            return {"policies": [], "count": 0, "error": str(e)}

    @staticmethod
    async def get_permission_catalog():
        if not _pg_pool: return {"permissions": [], "count": 0}
        try:
            async with _pg_pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM rbac_permission_catalog ORDER BY resource, action")
                return {"permissions": [dict(r) for r in rows], "count": len(rows)}
        except Exception as e:
            return {"permissions": [], "count": 0, "error": str(e)}


# =========================================================================
# Models
# =========================================================================

class CreateRoleRequest(BaseModel):
    name: str; description: str = ""; permissions: List[str] = []; org_id: str = None

class AssignRoleRequest(BaseModel):
    user_id: str; role_id: str; org_id: str = None
    resource_type: str = None; resource_id: str = None

class RevokeRoleRequest(BaseModel):
    user_id: str; role_id: str; org_id: str = None

class CheckPermissionRequest(BaseModel):
    user_id: str; resource: str; action: str; org_id: str = None

class AddPolicyRequest(BaseModel):
    role_id: str; resource: str; action: str
    conditions: Dict = {}; effect: str = "allow"


# =========================================================================
# Endpoints
# =========================================================================

@router.on_event("startup")
async def startup():
    await init_rbac_pg()

@router.post("/check")
async def check_permission(req: CheckPermissionRequest):
    allowed = await RBACManager.check_permission(req.user_id, req.resource, req.action, req.org_id)
    return {"allowed": allowed, "user_id": req.user_id, "resource": req.resource, "action": req.action}

@router.get("/permissions/{user_id}")
async def get_user_permissions(user_id: str, org_id: str = None):
    return await RBACManager.get_user_permissions(user_id, org_id)

@router.get("/roles")
async def list_roles(org_id: str = None, include_system: bool = True):
    return await RBACManager.list_roles(org_id, include_system)

@router.post("/roles")
async def create_role(req: CreateRoleRequest):
    return await RBACManager.create_role(req.name, req.description, req.permissions, req.org_id)

@router.delete("/roles/{role_id}")
async def delete_role(role_id: str):
    return await RBACManager.delete_role(role_id)

@router.post("/assign")
async def assign_role(req: AssignRoleRequest):
    return await RBACManager.assign_role(req.user_id, req.role_id, req.org_id, req.resource_type, req.resource_id)

@router.post("/revoke")
async def revoke_role(req: RevokeRoleRequest):
    return await RBACManager.revoke_role(req.user_id, req.role_id, req.org_id)

@router.get("/users/{user_id}/roles")
async def get_user_roles(user_id: str):
    return await RBACManager.get_user_roles(user_id)

@router.post("/policies")
async def add_policy(req: AddPolicyRequest):
    return await RBACManager.add_policy(req.role_id, req.resource, req.action, req.conditions, req.effect)

@router.get("/policies")
async def list_policies(role_id: str = None):
    return await RBACManager.list_policies(role_id)

@router.get("/catalog")
async def get_permission_catalog():
    return await RBACManager.get_permission_catalog()

@router.get("/dashboard")
async def rbac_dashboard():
    roles = await RBACManager.list_roles(include_system=True)
    catalog = await RBACManager.get_permission_catalog()
    return {
        "version": "1.0.0",
        "total_roles": roles["count"],
        "system_roles": sum(1 for r in roles.get("roles", []) if r.get("is_system")),
        "custom_roles": sum(1 for r in roles.get("roles", []) if not r.get("is_system")),
        "total_permissions_in_catalog": catalog["count"],
        "roles": [{"name": r["name"], "permissions": r["permissions"], "is_system": r["is_system"]} for r in roles.get("roles", [])],
    }
