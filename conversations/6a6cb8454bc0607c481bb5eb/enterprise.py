"""
EvolvixOS Enterprise Module v1.0
- SSO (SAML 2.0 + OAuth2)
- Audit Logging (comprehensive, PostgreSQL-backed)
- Multi-Tenancy (organization isolation, resource quotas)
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
import structlog
import asyncio
import os
import json
import hashlib
import secrets
import uuid

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/enterprise", tags=["Enterprise"])

# =========================================================================
# Audit Logging (PostgreSQL-backed)
# =========================================================================

import asyncpg

PG_DSN = os.getenv("DATABASE_URL", "postgresql://evolvixos:EvolvixOS2026Secure@localhost:5432/evolvixos")
_pg_pool: Optional[asyncpg.Pool] = None

async def init_enterprise_pg():
    global _pg_pool
    if _pg_pool:
        return True
    for attempt in range(3):
        try:
            _pg_pool = await asyncpg.create_pool(PG_DSN, min_size=2, max_size=10, command_timeout=30)
            async with _pg_pool.acquire() as conn:
                # Audit logs table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        user_id TEXT,
                        user_email TEXT,
                        org_id TEXT,
                        action TEXT NOT NULL,
                        resource_type TEXT,
                        resource_id TEXT,
                        ip_address TEXT,
                        user_agent TEXT,
                        details JSONB DEFAULT '{}',
                        severity TEXT DEFAULT 'info',
                        category TEXT DEFAULT 'general'
                    );
                    CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
                    CREATE INDEX IF NOT EXISTS idx_audit_org ON audit_logs(org_id);
                    CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
                    CREATE INDEX IF NOT EXISTS idx_audit_severity ON audit_logs(severity);
                """)
                
                # Organizations table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS organizations (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name TEXT NOT NULL UNIQUE,
                        slug TEXT NOT NULL UNIQUE,
                        plan TEXT DEFAULT 'free',
                        status TEXT DEFAULT 'active',
                        max_users INTEGER DEFAULT 10,
                        max_agents INTEGER DEFAULT 5,
                        max_api_calls INTEGER DEFAULT 10000,
                        max_storage_mb INTEGER DEFAULT 1024,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW(),
                        settings JSONB DEFAULT '{}'
                    );
                """)
                
                # Organization members
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS org_members (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                        user_id TEXT NOT NULL,
                        user_email TEXT NOT NULL,
                        role TEXT DEFAULT 'member',
                        status TEXT DEFAULT 'active',
                        invited_by TEXT,
                        invited_at TIMESTAMPTZ DEFAULT NOW(),
                        joined_at TIMESTAMPTZ,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        UNIQUE(org_id, user_id)
                    );
                    CREATE INDEX IF NOT EXISTS idx_org_members_org ON org_members(org_id);
                    CREATE INDEX IF NOT EXISTS idx_org_members_user ON org_members(user_id);
                """)
                
                # SSO configurations
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS sso_configs (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                        provider TEXT NOT NULL,
                        entity_id TEXT,
                        sso_url TEXT,
                        certificate TEXT,
                        client_id TEXT,
                        client_secret TEXT,
                        domains TEXT[] DEFAULT '{}',
                        attribute_mapping JSONB DEFAULT '{}',
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW()
                    );
                    CREATE INDEX IF NOT EXISTS idx_sso_org ON sso_configs(org_id);
                """)
                
                # API usage tracking
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS api_usage (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        org_id UUID,
                        user_id TEXT,
                        endpoint TEXT,
                        method TEXT,
                        timestamp TIMESTAMPTZ DEFAULT NOW(),
                        response_code INTEGER,
                        latency_ms REAL,
                        tokens_used INTEGER DEFAULT 0
                    );
                    CREATE INDEX IF NOT EXISTS idx_usage_org ON api_usage(org_id);
                    CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON api_usage(timestamp DESC);
                """)
            
            logger.info("Enterprise PG tables initialized")
            return True
        except Exception as e:
            logger.warning(f"Enterprise PG attempt {attempt+1}: {e}")
            await asyncio.sleep(2)
    return False


# =========================================================================
# Audit Logger
# =========================================================================

class AuditLogger:
    @staticmethod
    async def log(
        action: str,
        user_id: str = None,
        user_email: str = None,
        org_id: str = None,
        resource_type: str = None,
        resource_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        details: Dict = None,
        severity: str = "info",
        category: str = "general",
    ):
        if not _pg_pool:
            logger.warning("Audit log skipped — PG not connected")
            return None
        
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO audit_logs (user_id, user_email, org_id, action, resource_type,
                        resource_id, ip_address, user_agent, details, severity, category)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
                    RETURNING id, timestamp
                """, user_id, user_email, org_id, action, resource_type, resource_id,
                    ip_address, user_agent, json.dumps(details or {}), severity, category)
                return dict(row)
        except Exception as e:
            logger.warning(f"Audit log failed: {e}")
            return None
    
    @staticmethod
    async def list_logs(
        limit: int = 50, offset: int = 0,
        user_id: str = None, org_id: str = None,
        action: str = None, severity: str = None,
        start_date: str = None, end_date: str = None,
    ):
        if not _pg_pool:
            return {"logs": [], "count": 0}
        
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        idx = 1
        
        if user_id: query += f" AND user_id = ${idx}"; params.append(user_id); idx += 1
        if org_id: query += f" AND org_id = ${idx}"; params.append(org_id); idx += 1
        if action: query += f" AND action = ${idx}"; params.append(action); idx += 1
        if severity: query += f" AND severity = ${idx}"; params.append(severity); idx += 1
        if start_date: query += f" AND timestamp >= ${idx}"; params.append(start_date); idx += 1
        if end_date: query += f" AND timestamp <= ${idx}"; params.append(end_date); idx += 1
        
        query += f" ORDER BY timestamp DESC LIMIT ${idx} OFFSET ${idx+1}"
        params.extend([limit, offset])
        
        try:
            async with _pg_pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                count_row = await conn.fetchrow("SELECT COUNT(*) as cnt FROM audit_logs")
                return {"logs": [dict(r) for r in rows], "count": count_row["cnt"]}
        except Exception as e:
            logger.warning(f"Audit list failed: {e}")
            return {"logs": [], "count": 0, "error": str(e)}
    
    @staticmethod
    async def get_stats():
        if not _pg_pool:
            return {"total": 0}
        try:
            async with _pg_pool.acquire() as conn:
                total = await conn.fetchval("SELECT COUNT(*) FROM audit_logs")
                by_severity = await conn.fetch("SELECT severity, COUNT(*) as cnt FROM audit_logs GROUP BY severity")
                by_category = await conn.fetch("SELECT category, COUNT(*) as cnt FROM audit_logs GROUP BY category ORDER BY cnt DESC LIMIT 10")
                by_action = await conn.fetch("SELECT action, COUNT(*) as cnt FROM audit_logs GROUP BY action ORDER BY cnt DESC LIMIT 10")
                last_24h = await conn.fetchval("SELECT COUNT(*) FROM audit_logs WHERE timestamp > NOW() - INTERVAL '24 hours'")
                
                return {
                    "total": total,
                    "last_24h": last_24h,
                    "by_severity": {r["severity"]: r["cnt"] for r in by_severity},
                    "by_category": {r["category"]: r["cnt"] for r in by_category},
                    "by_action": {r["action"]: r["cnt"] for r in by_action},
                }
        except Exception as e:
            return {"total": 0, "error": str(e)}


# =========================================================================
# Organization Manager (Multi-Tenancy)
# =========================================================================

class OrgManager:
    @staticmethod
    async def create_org(name: str, slug: str, plan: str = "free", settings: Dict = None):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO organizations (name, slug, plan, settings)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id, name, slug, plan, status, max_users, max_agents, max_api_calls, max_storage_mb, created_at
                """, name, slug, plan, json.dumps(settings or {}))
                return dict(row)
        except asyncpg.UniqueViolationError:
            raise HTTPException(409, f"Organization '{name}' already exists")
        except Exception as e:
            raise HTTPException(500, str(e))
    
    @staticmethod
    async def get_org(org_id: str):
        if not _pg_pool: return None
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM organizations WHERE id = $1", uuid.UUID(org_id))
                return dict(row) if row else None
        except: return None
    
    @staticmethod
    async def list_orgs(limit: int = 50, offset: int = 0):
        if not _pg_pool: return {"orgs": [], "count": 0}
        try:
            async with _pg_pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM organizations ORDER BY created_at DESC LIMIT $1 OFFSET $2", limit, offset)
                count = await conn.fetchval("SELECT COUNT(*) FROM organizations")
                return {"orgs": [dict(r) for r in rows], "count": count}
        except Exception as e:
            return {"orgs": [], "count": 0, "error": str(e)}
    
    @staticmethod
    async def update_org(org_id: str, updates: Dict):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        allowed = {"name", "plan", "status", "max_users", "max_agents", "max_api_calls", "max_storage_mb", "settings"}
        fields = {k: v for k, v in updates.items() if k in allowed}
        if not fields: raise HTTPException(400, "No valid fields to update")
        
        set_parts = []
        params = []
        idx = 1
        for k, v in fields.items():
            if k == "settings": v = json.dumps(v)
            set_parts.append(f"{k} = ${idx}")
            params.append(v)
            idx += 1
        set_parts.append(f"updated_at = NOW()")
        params.append(uuid.UUID(org_id))
        
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow(
                    f"UPDATE organizations SET {', '.join(set_parts)} WHERE id = ${idx} RETURNING *",
                    *params
                )
                if not row: raise HTTPException(404, "Organization not found")
                return dict(row)
        except HTTPException: raise
        except Exception as e:
            raise HTTPException(500, str(e))
    
    @staticmethod
    async def delete_org(org_id: str):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                result = await conn.execute("DELETE FROM organizations WHERE id = $1", uuid.UUID(org_id))
                if result == "DELETE 0": raise HTTPException(404, "Organization not found")
                return {"deleted": True, "org_id": org_id}
        except HTTPException: raise
        except Exception as e:
            raise HTTPException(500, str(e))
    
    @staticmethod
    async def add_member(org_id: str, user_id: str, user_email: str, role: str = "member", invited_by: str = None):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO org_members (org_id, user_id, user_email, role, invited_by, joined_at)
                    VALUES ($1, $2, $3, $4, $5, NOW())
                    RETURNING id, org_id, user_id, user_email, role, status, joined_at
                """, uuid.UUID(org_id), user_id, user_email, role, invited_by)
                return dict(row)
        except asyncpg.UniqueViolationError:
            raise HTTPException(409, "User already a member")
        except Exception as e:
            raise HTTPException(500, str(e))
    
    @staticmethod
    async def list_members(org_id: str):
        if not _pg_pool: return {"members": [], "count": 0}
        try:
            async with _pg_pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM org_members WHERE org_id = $1 ORDER BY joined_at DESC", uuid.UUID(org_id))
                return {"members": [dict(r) for r in rows], "count": len(rows)}
        except Exception as e:
            return {"members": [], "count": 0, "error": str(e)}
    
    @staticmethod
    async def remove_member(org_id: str, user_id: str):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM org_members WHERE org_id = $1 AND user_id = $2",
                    uuid.UUID(org_id), user_id
                )
                if result == "DELETE 0": raise HTTPException(404, "Member not found")
                return {"removed": True, "user_id": user_id}
        except HTTPException: raise
        except Exception as e:
            raise HTTPException(500, str(e))
    
    @staticmethod
    async def check_quota(org_id: str, resource: str) -> Dict[str, Any]:
        """Check if organization is within quota for a resource."""
        if not _pg_pool: return {"within_quota": True}
        try:
            async with _pg_pool.acquire() as conn:
                org = await conn.fetchrow("SELECT * FROM organizations WHERE id = $1", uuid.UUID(org_id))
                if not org: return {"within_quota": True}
                
                if resource == "users":
                    current = await conn.fetchval("SELECT COUNT(*) FROM org_members WHERE org_id = $1", uuid.UUID(org_id))
                    limit = org["max_users"]
                elif resource == "agents":
                    current = 0  # Would query agents table
                    limit = org["max_agents"]
                elif resource == "api_calls":
                    current = await conn.fetchval("SELECT COUNT(*) FROM api_usage WHERE org_id = $1 AND timestamp > NOW() - INTERVAL '30 days'", uuid.UUID(org_id))
                    limit = org["max_api_calls"]
                else:
                    return {"within_quota": True}
                
                return {
                    "resource": resource,
                    "current": current,
                    "limit": limit,
                    "within_quota": current < limit,
                    "remaining": max(0, limit - current),
                }
        except Exception as e:
            return {"within_quota": True, "error": str(e)}


# =========================================================================
# SSO Manager (SAML 2.0 + OAuth2)
# =========================================================================

class SSOManager:
    @staticmethod
    async def create_sso_config(org_id: str, provider: str, config: Dict):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO sso_configs (org_id, provider, entity_id, sso_url, certificate,
                        client_id, client_secret, domains, attribute_mapping, status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'active')
                    RETURNING id, org_id, provider, entity_id, sso_url, client_id, domains, status, created_at
                """, uuid.UUID(org_id), provider,
                    config.get("entity_id"), config.get("sso_url"), config.get("certificate"),
                    config.get("client_id"), config.get("client_secret"),
                    config.get("domains", []), json.dumps(config.get("attribute_mapping", {})))
                return dict(row)
        except Exception as e:
            raise HTTPException(500, str(e))
    
    @staticmethod
    async def get_sso_configs(org_id: str):
        if not _pg_pool: return {"configs": [], "count": 0}
        try:
            async with _pg_pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM sso_configs WHERE org_id = $1", uuid.UUID(org_id))
                # Don't return secrets
                safe = []
                for r in rows:
                    d = dict(r)
                    d.pop("client_secret", None)
                    d.pop("certificate", None)
                    safe.append(d)
                return {"configs": safe, "count": len(safe)}
        except Exception as e:
            return {"configs": [], "count": 0, "error": str(e)}
    
    @staticmethod
    async def delete_sso_config(config_id: str):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                result = await conn.execute("DELETE FROM sso_configs WHERE id = $1", uuid.UUID(config_id))
                if result == "DELETE 0": raise HTTPException(404, "SSO config not found")
                return {"deleted": True, "config_id": config_id}
        except HTTPException: raise
        except Exception as e:
            raise HTTPException(500, str(e))
    
    @staticmethod
    def generate_saml_request(entity_id: str, sso_url: str) -> Dict:
        """Generate a SAML authentication request."""
        request_id = secrets.token_hex(16)
        timestamp = datetime.now(timezone.utc).isoformat()
        return {
            "request_id": request_id,
            "entity_id": entity_id,
            "sso_url": sso_url,
            "timestamp": timestamp,
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            "nameid_format": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        }
    
    @staticmethod
    def generate_oauth_authorize_url(client_id: str, redirect_uri: str, scopes: List[str]) -> str:
        """Generate OAuth2 authorization URL."""
        state = secrets.token_urlsafe(32)
        scope_str = " ".join(scopes)
        return f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope_str}&state={state}"


# =========================================================================
# API Usage Tracker
# =========================================================================

class UsageTracker:
    @staticmethod
    async def record_usage(org_id: str = None, user_id: str = None, endpoint: str = None,
                           method: str = None, response_code: int = None,
                           latency_ms: float = None, tokens_used: int = 0):
        if not _pg_pool: return
        try:
            async with _pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO api_usage (org_id, user_id, endpoint, method, response_code, latency_ms, tokens_used)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, uuid.UUID(org_id) if org_id else None, user_id, endpoint, method,
                    response_code, latency_ms, tokens_used)
        except: pass
    
    @staticmethod
    async def get_usage_stats(org_id: str = None, days: int = 30):
        if not _pg_pool: return {"total": 0}
        try:
            async with _pg_pool.acquire() as conn:
                if org_id:
                    total = await conn.fetchval("SELECT COUNT(*) FROM api_usage WHERE org_id = $1 AND timestamp > NOW() - INTERVAL '%s days'" % days, uuid.UUID(org_id))
                    by_endpoint = await conn.fetch("SELECT endpoint, COUNT(*) as cnt FROM api_usage WHERE org_id = $1 AND timestamp > NOW() - INTERVAL '%s days' GROUP BY endpoint ORDER BY cnt DESC LIMIT 10" % days, uuid.UUID(org_id))
                    avg_latency = await conn.fetchval("SELECT AVG(latency_ms) FROM api_usage WHERE org_id = $1 AND timestamp > NOW() - INTERVAL '%s days'" % days, uuid.UUID(org_id))
                    total_tokens = await conn.fetchval("SELECT SUM(tokens_used) FROM api_usage WHERE org_id = $1 AND timestamp > NOW() - INTERVAL '%s days'" % days, uuid.UUID(org_id))
                else:
                    total = await conn.fetchval("SELECT COUNT(*) FROM api_usage WHERE timestamp > NOW() - INTERVAL '%s days'" % days)
                    by_endpoint = await conn.fetch("SELECT endpoint, COUNT(*) as cnt FROM api_usage WHERE timestamp > NOW() - INTERVAL '%s days' GROUP BY endpoint ORDER BY cnt DESC LIMIT 10" % days)
                    avg_latency = await conn.fetchval("SELECT AVG(latency_ms) FROM api_usage WHERE timestamp > NOW() - INTERVAL '%s days'" % days)
                    total_tokens = await conn.fetchval("SELECT SUM(tokens_used) FROM api_usage WHERE timestamp > NOW() - INTERVAL '%s days'" % days)
                
                return {
                    "total_calls": total,
                    "period_days": days,
                    "avg_latency_ms": float(avg_latency) if avg_latency else 0,
                    "total_tokens": total_tokens or 0,
                    "top_endpoints": {r["endpoint"]: r["cnt"] for r in by_endpoint},
                }
        except Exception as e:
            return {"total": 0, "error": str(e)}


# =========================================================================
# Models
# =========================================================================

class CreateOrgRequest(BaseModel):
    name: str; slug: str; plan: str = "free"; settings: Dict = {}

class UpdateOrgRequest(BaseModel):
    name: Optional[str] = None; plan: Optional[str] = None
    status: Optional[str] = None; max_users: Optional[int] = None
    max_agents: Optional[int] = None; max_api_calls: Optional[int] = None
    max_storage_mb: Optional[int] = None; settings: Optional[Dict] = None

class AddMemberRequest(BaseModel):
    user_id: str; user_email: str; role: str = "member"; invited_by: str = None

class CreateSSOConfigRequest(BaseModel):
    provider: str; entity_id: str = None; sso_url: str = None
    certificate: str = None; client_id: str = None; client_secret: str = None
    domains: List[str] = []; attribute_mapping: Dict = {}

class AuditLogRequest(BaseModel):
    action: str; user_id: str = None; user_email: str = None
    org_id: str = None; resource_type: str = None; resource_id: str = None
    details: Dict = {}; severity: str = "info"; category: str = "general"


# =========================================================================
# Audit Log Endpoints
# =========================================================================

@router.on_event("startup")
async def startup():
    await init_enterprise_pg()

@router.post("/audit/log")
async def create_audit_log(req: AuditLogRequest, request: Request):
    result = await AuditLogger.log(
        action=req.action, user_id=req.user_id, user_email=req.user_email,
        org_id=req.org_id, resource_type=req.resource_type, resource_id=req.resource_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details=req.details, severity=req.severity, category=req.category,
    )
    return {"logged": result is not None, "log_id": str(result["id"]) if result else None}

@router.get("/audit/logs")
async def get_audit_logs(
    limit: int = 50, offset: int = 0,
    user_id: str = None, org_id: str = None,
    action: str = None, severity: str = None,
    start_date: str = None, end_date: str = None,
):
    return await AuditLogger.list_logs(limit, offset, user_id, org_id, action, severity, start_date, end_date)

@router.get("/audit/stats")
async def get_audit_stats():
    return await AuditLogger.get_stats()


# =========================================================================
# Organization Endpoints
# =========================================================================

@router.post("/orgs")
async def create_org(req: CreateOrgRequest):
    return await OrgManager.create_org(req.name, req.slug, req.plan, req.settings)

@router.get("/orgs")
async def list_orgs(limit: int = 50, offset: int = 0):
    return await OrgManager.list_orgs(limit, offset)

@router.get("/orgs/{org_id}")
async def get_org(org_id: str):
    org = await OrgManager.get_org(org_id)
    if not org: raise HTTPException(404, "Organization not found")
    return org

@router.patch("/orgs/{org_id}")
async def update_org(org_id: str, req: UpdateOrgRequest):
    updates = {k: v for k, v in req.dict().items() if v is not None}
    return await OrgManager.update_org(org_id, updates)

@router.delete("/orgs/{org_id}")
async def delete_org(org_id: str):
    return await OrgManager.delete_org(org_id)

@router.get("/orgs/{org_id}/quota/{resource}")
async def check_quota(org_id: str, resource: str):
    return await OrgManager.check_quota(org_id, resource)


# =========================================================================
# Organization Members
# =========================================================================

@router.post("/orgs/{org_id}/members")
async def add_member(org_id: str, req: AddMemberRequest):
    return await OrgManager.add_member(org_id, req.user_id, req.user_email, req.role, req.invited_by)

@router.get("/orgs/{org_id}/members")
async def list_members(org_id: str):
    return await OrgManager.list_members(org_id)

@router.delete("/orgs/{org_id}/members/{user_id}")
async def remove_member(org_id: str, user_id: str):
    return await OrgManager.remove_member(org_id, user_id)


# =========================================================================
# SSO Endpoints
# =========================================================================

@router.post("/orgs/{org_id}/sso")
async def create_sso_config(org_id: str, req: CreateSSOConfigRequest):
    return await SSOManager.create_sso_config(org_id, req.provider, req.dict())

@router.get("/orgs/{org_id}/sso")
async def get_sso_configs(org_id: str):
    return await SSOManager.get_sso_configs(org_id)

@router.delete("/orgs/{org_id}/sso/{config_id}")
async def delete_sso_config(org_id: str, config_id: str):
    return await SSOManager.delete_sso_config(config_id)

@router.post("/sso/saml/request")
async def generate_saml_request(provider: str = "saml", entity_id: str = "", sso_url: str = ""):
    return SSOManager.generate_saml_request(entity_id, sso_url)

@router.get("/sso/oauth/authorize")
async def generate_oauth_url(client_id: str, redirect_uri: str, scopes: str = "openid email profile"):
    url = SSOManager.generate_oauth_authorize_url(client_id, redirect_uri, scopes.split())
    return {"authorize_url": url}


# =========================================================================
# API Usage Endpoints
# =========================================================================

@router.get("/usage/stats")
async def get_usage_stats(org_id: str = None, days: int = 30):
    return await UsageTracker.get_usage_stats(org_id, days)

@router.post("/usage/record")
async def record_usage(org_id: str = None, user_id: str = None, endpoint: str = None,
                       method: str = "GET", response_code: int = 200,
                       latency_ms: float = 0, tokens_used: int = 0):
    await UsageTracker.record_usage(org_id, user_id, endpoint, method, response_code, latency_ms, tokens_used)
    return {"recorded": True}


# =========================================================================
# Enterprise Dashboard
# =========================================================================

@router.get("/dashboard")
async def enterprise_dashboard():
    """Comprehensive enterprise dashboard with all metrics."""
    audit_stats = await AuditLogger.get_stats()
    orgs = await OrgManager.list_orgs(limit=1000)
    usage = await UsageTracker.get_usage_stats(days=30)
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "organizations": {
            "total": orgs["count"],
            "active": sum(1 for o in orgs.get("orgs", []) if o.get("status") == "active"),
        },
        "audit": audit_stats,
        "usage": usage,
        "platform": {
            "version": "1.0.0",
            "modules": ["sso", "audit", "multi_tenancy", "usage_tracking"],
        },
    }
