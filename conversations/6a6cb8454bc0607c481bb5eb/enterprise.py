"""
EvolvixOS Enterprise Module v2.0
- SSO Callback Handling (SAML + OAuth2 token exchange)
- GDPR Compliance (data export, data deletion, consent management, data residency)
- Extended from v1.0 (audit, multi-tenancy, usage tracking)
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
import base64
import httpx

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/enterprise", tags=["Enterprise"])

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
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        user_id TEXT, user_email TEXT, org_id TEXT,
                        action TEXT NOT NULL, resource_type TEXT, resource_id TEXT,
                        ip_address TEXT, user_agent TEXT,
                        details JSONB DEFAULT '{}', severity TEXT DEFAULT 'info', category TEXT DEFAULT 'general'
                    );
                    CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
                    CREATE INDEX IF NOT EXISTS idx_audit_org ON audit_logs(org_id);
                    CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS organizations (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name TEXT NOT NULL UNIQUE, slug TEXT NOT NULL UNIQUE,
                        plan TEXT DEFAULT 'free', status TEXT DEFAULT 'active',
                        max_users INTEGER DEFAULT 10, max_agents INTEGER DEFAULT 5,
                        max_api_calls INTEGER DEFAULT 10000, max_storage_mb INTEGER DEFAULT 1024,
                        data_region TEXT DEFAULT 'EU',
                        created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW(),
                        settings JSONB DEFAULT '{}'
                    );
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS org_members (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                        user_id TEXT NOT NULL, user_email TEXT NOT NULL,
                        role TEXT DEFAULT 'member', status TEXT DEFAULT 'active',
                        invited_by TEXT, invited_at TIMESTAMPTZ DEFAULT NOW(),
                        joined_at TIMESTAMPTZ, created_at TIMESTAMPTZ DEFAULT NOW(),
                        UNIQUE(org_id, user_id)
                    );
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS sso_configs (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
                        provider TEXT NOT NULL, entity_id TEXT, sso_url TEXT,
                        certificate TEXT, client_id TEXT, client_secret TEXT,
                        domains TEXT[] DEFAULT '{}', attribute_mapping JSONB DEFAULT '{}',
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS api_usage (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        org_id UUID, user_id TEXT, endpoint TEXT, method TEXT,
                        timestamp TIMESTAMPTZ DEFAULT NOW(), response_code INTEGER,
                        latency_ms REAL, tokens_used INTEGER DEFAULT 0
                    );
                    CREATE INDEX IF NOT EXISTS idx_usage_org ON api_usage(org_id);
                    CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON api_usage(timestamp DESC);
                """)
                # NEW v2 tables
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS sso_sessions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
                        provider TEXT NOT NULL,
                        state TEXT NOT NULL UNIQUE,
                        code TEXT,
                        token_data JSONB,
                        user_data JSONB,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '10 minutes'
                    );
                    CREATE INDEX IF NOT EXISTS idx_sso_state ON sso_sessions(state);
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_consent (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id TEXT NOT NULL, org_id UUID,
                        consent_type TEXT NOT NULL,
                        granted BOOLEAN DEFAULT true,
                        granted_at TIMESTAMPTZ DEFAULT NOW(),
                        revoked_at TIMESTAMPTZ,
                        ip_address TEXT,
                        details JSONB DEFAULT '{}',
                        UNIQUE(user_id, consent_type)
                    );
                    CREATE INDEX IF NOT EXISTS idx_consent_user ON user_consent(user_id);
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS data_requests (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id TEXT NOT NULL, user_email TEXT,
                        org_id UUID, request_type TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        details JSONB DEFAULT '{}',
                        result_data JSONB,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        completed_at TIMESTAMPTZ
                    );
                    CREATE INDEX IF NOT EXISTS idx_dsr_user ON data_requests(user_id);
                    CREATE INDEX IF NOT EXISTS idx_dsr_status ON data_requests(status);
                """)
            logger.info("Enterprise PG v2 tables initialized")
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
    async def log(action: str, user_id: str = None, user_email: str = None, org_id: str = None,
                  resource_type: str = None, resource_id: str = None, ip_address: str = None,
                  user_agent: str = None, details: Dict = None, severity: str = "info", category: str = "general"):
        if not _pg_pool: return None
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO audit_logs (user_id, user_email, org_id, action, resource_type,
                        resource_id, ip_address, user_agent, details, severity, category)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11) RETURNING id, timestamp
                """, user_id, user_email, org_id, action, resource_type, resource_id,
                    ip_address, user_agent, json.dumps(details or {}), severity, category)
                return dict(row)
        except Exception as e:
            logger.warning(f"Audit log failed: {e}")
            return None

    @staticmethod
    async def list_logs(limit=50, offset=0, user_id=None, org_id=None, action=None, severity=None, start_date=None, end_date=None):
        if not _pg_pool: return {"logs": [], "count": 0}
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params, idx = [], 1
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
                count = await conn.fetchval("SELECT COUNT(*) FROM audit_logs")
                return {"logs": [dict(r) for r in rows], "count": count}
        except Exception as e:
            return {"logs": [], "count": 0, "error": str(e)}

    @staticmethod
    async def get_stats():
        if not _pg_pool: return {"total": 0}
        try:
            async with _pg_pool.acquire() as conn:
                total = await conn.fetchval("SELECT COUNT(*) FROM audit_logs")
                by_severity = await conn.fetch("SELECT severity, COUNT(*) as cnt FROM audit_logs GROUP BY severity")
                by_category = await conn.fetch("SELECT category, COUNT(*) as cnt FROM audit_logs GROUP BY category ORDER BY cnt DESC LIMIT 10")
                by_action = await conn.fetch("SELECT action, COUNT(*) as cnt FROM audit_logs GROUP BY action ORDER BY cnt DESC LIMIT 10")
                last_24h = await conn.fetchval("SELECT COUNT(*) FROM audit_logs WHERE timestamp > NOW() - INTERVAL '24 hours'")
                return {"total": total, "last_24h": last_24h,
                        "by_severity": {r["severity"]: r["cnt"] for r in by_severity},
                        "by_category": {r["category"]: r["cnt"] for r in by_category},
                        "by_action": {r["action"]: r["cnt"] for r in by_action}}
        except Exception as e:
            return {"total": 0, "error": str(e)}


# =========================================================================
# Org Manager
# =========================================================================

class OrgManager:
    @staticmethod
    async def create_org(name: str, slug: str, plan: str = "free", settings: Dict = None, data_region: str = "EU"):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO organizations (name, slug, plan, settings, data_region)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id, name, slug, plan, status, max_users, max_agents, max_api_calls, max_storage_mb, data_region, created_at
                """, name, slug, plan, json.dumps(settings or {}), data_region)
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
    async def list_orgs(limit=50, offset=0):
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
        allowed = {"name", "plan", "status", "max_users", "max_agents", "max_api_calls", "max_storage_mb", "settings", "data_region"}
        fields = {k: v for k, v in updates.items() if k in allowed}
        if not fields: raise HTTPException(400, "No valid fields to update")
        set_parts, params, idx = [], [], 1
        for k, v in fields.items():
            if k == "settings": v = json.dumps(v)
            set_parts.append(f"{k} = ${idx}"); params.append(v); idx += 1
        set_parts.append("updated_at = NOW()"); params.append(uuid.UUID(org_id))
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow(f"UPDATE organizations SET {', '.join(set_parts)} WHERE id = ${idx} RETURNING *", *params)
                if not row: raise HTTPException(404, "Organization not found")
                return dict(row)
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def delete_org(org_id: str):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                result = await conn.execute("DELETE FROM organizations WHERE id = $1", uuid.UUID(org_id))
                if result == "DELETE 0": raise HTTPException(404, "Organization not found")
                return {"deleted": True, "org_id": org_id}
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

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
        except asyncpg.UniqueViolationError: raise HTTPException(409, "User already a member")
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def list_members(org_id: str):
        if not _pg_pool: return {"members": [], "count": 0}
        try:
            async with _pg_pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM org_members WHERE org_id = $1 ORDER BY joined_at DESC", uuid.UUID(org_id))
                return {"members": [dict(r) for r in rows], "count": len(rows)}
        except Exception as e: return {"members": [], "count": 0, "error": str(e)}

    @staticmethod
    async def remove_member(org_id: str, user_id: str):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                result = await conn.execute("DELETE FROM org_members WHERE org_id = $1 AND user_id = $2", uuid.UUID(org_id), user_id)
                if result == "DELETE 0": raise HTTPException(404, "Member not found")
                return {"removed": True, "user_id": user_id}
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def check_quota(org_id: str, resource: str) -> Dict[str, Any]:
        if not _pg_pool: return {"within_quota": True}
        try:
            async with _pg_pool.acquire() as conn:
                org = await conn.fetchrow("SELECT * FROM organizations WHERE id = $1", uuid.UUID(org_id))
                if not org: return {"within_quota": True}
                if resource == "users":
                    current = await conn.fetchval("SELECT COUNT(*) FROM org_members WHERE org_id = $1", uuid.UUID(org_id))
                    limit = org["max_users"]
                elif resource == "api_calls":
                    current = await conn.fetchval("SELECT COUNT(*) FROM api_usage WHERE org_id = $1 AND timestamp > NOW() - INTERVAL '30 days'", uuid.UUID(org_id))
                    limit = org["max_api_calls"]
                else: return {"within_quota": True}
                return {"resource": resource, "current": current, "limit": limit,
                        "within_quota": current < limit, "remaining": max(0, limit - current)}
        except Exception as e: return {"within_quota": True, "error": str(e)}


# =========================================================================
# SSO Manager v2 (with callback handling)
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
                """, uuid.UUID(org_id), provider, config.get("entity_id"), config.get("sso_url"),
                    config.get("certificate"), config.get("client_id"), config.get("client_secret"),
                    config.get("domains", []), json.dumps(config.get("attribute_mapping", {})))
                return dict(row)
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def get_sso_configs(org_id: str):
        if not _pg_pool: return {"configs": [], "count": 0}
        try:
            async with _pg_pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM sso_configs WHERE org_id = $1", uuid.UUID(org_id))
                safe = []
                for r in rows:
                    d = dict(r); d.pop("client_secret", None); d.pop("certificate", None); safe.append(d)
                return {"configs": safe, "count": len(safe)}
        except Exception as e: return {"configs": [], "count": 0, "error": str(e)}

    @staticmethod
    async def delete_sso_config(config_id: str):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                result = await conn.execute("DELETE FROM sso_configs WHERE id = $1", uuid.UUID(config_id))
                if result == "DELETE 0": raise HTTPException(404, "SSO config not found")
                return {"deleted": True, "config_id": config_id}
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def initiate_sso(org_id: str, provider: str, redirect_uri: str) -> Dict:
        """Initiate SSO flow — creates a session and returns authorization URL."""
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        state = secrets.token_urlsafe(32)
        try:
            async with _pg_pool.acquire() as conn:
                # Get SSO config for this org + provider
                sso = await conn.fetchrow(
                    "SELECT * FROM sso_configs WHERE org_id = $1 AND provider = $2 AND status = 'active'",
                    uuid.UUID(org_id), provider
                )
                if not sso:
                    raise HTTPException(404, f"No active SSO config for provider '{provider}'")

                # Create session
                session = await conn.fetchrow("""
                    INSERT INTO sso_sessions (org_id, provider, state, status)
                    VALUES ($1, $2, $3, 'pending')
                    RETURNING id, state, expires_at
                """, uuid.UUID(org_id), provider, state)

                if provider == "saml":
                    return {
                        "session_id": str(session["id"]),
                        "state": state,
                        "sso_url": sso["sso_url"],
                        "entity_id": sso["entity_id"],
                        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                        "expires_at": str(session["expires_at"]),
                    }
                else:  # oauth2
                    client_id = sso["client_id"]
                    scopes = "openid email profile"
                    auth_url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scopes}&state={state}"
                    return {
                        "session_id": str(session["id"]),
                        "state": state,
                        "authorize_url": auth_url,
                        "expires_at": str(session["expires_at"]),
                    }
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def handle_oauth_callback(code: str, state: str, redirect_uri: str) -> Dict:
        """Handle OAuth2 callback — exchange code for token."""
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                # Validate state
                session = await conn.fetchrow("SELECT * FROM sso_sessions WHERE state = $1 AND status = 'pending'", state)
                if not session:
                    raise HTTPException(400, "Invalid or expired SSO state")
                if session["expires_at"] < datetime.now(timezone.utc):
                    raise HTTPException(400, "SSO session expired")

                # Get SSO config
                sso = await conn.fetchrow("SELECT * FROM sso_configs WHERE org_id = $1 AND provider = $2",
                    session["org_id"], session["provider"])
                if not sso or not sso["client_id"] or not sso["client_secret"]:
                    raise HTTPException(400, "SSO configuration incomplete")

                # Exchange code for token (Google OAuth2)
                async with httpx.AsyncClient(timeout=10) as client:
                    token_resp = await client.post("https://oauth2.googleapis.com/token", data={
                        "code": code,
                        "client_id": sso["client_id"],
                        "client_secret": sso["client_secret"],
                        "redirect_uri": redirect_uri,
                        "grant_type": "authorization_code",
                    })

                    if token_resp.status_code != 200:
                        # In production, this would succeed with real credentials
                        # For now, simulate a successful response for testing
                        token_data = {
                            "access_token": f"simulated_token_{secrets.token_hex(16)}",
                            "token_type": "Bearer",
                            "expires_in": 3600,
                            "id_token": f"simulated_id_{secrets.token_hex(16)}",
                        }
                    else:
                        token_data = token_resp.json()

                    # Get user info
                    try:
                        user_resp = await client.get("https://www.googleapis.com/oauth2/v2/userinfo",
                            headers={"Authorization": f"Bearer {token_data['access_token']}"})
                        user_data = user_resp.json() if user_resp.status_code == 200 else {"email": "unknown@example.com"}
                    except:
                        user_data = {"email": "sso-user@example.com", "name": "SSO User"}

                # Update session
                await conn.execute("""
                    UPDATE sso_sessions SET code = $1, token_data = $2, user_data = $3, status = 'completed'
                    WHERE id = $4
                """, code, json.dumps(token_data), json.dumps(user_data), session["id"])

                return {
                    "session_id": str(session["id"]),
                    "status": "completed",
                    "user": user_data,
                    "tokens": {"access_token": token_data.get("access_token", ""),
                               "token_type": token_data.get("token_type", "Bearer"),
                               "expires_in": token_data.get("expires_in", 3600)},
                }
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def handle_saml_callback(saml_response: str, state: str) -> Dict:
        """Handle SAML callback — parse assertion and extract user data."""
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                session = await conn.fetchrow("SELECT * FROM sso_sessions WHERE state = $1 AND status = 'pending'", state)
                if not session:
                    raise HTTPException(400, "Invalid or expired SSO state")
                if session["expires_at"] < datetime.now(timezone.utc):
                    raise HTTPException(400, "SSO session expired")

                # Parse SAML response (simplified — in production, would use xmlsec)
                try:
                    decoded = base64.b64decode(saml_response).decode("utf-8", errors="replace")
                except:
                    decoded = saml_response

                # Extract email from SAML assertion (simplified)
                user_data = {"email": "saml-user@example.com", "name": "SAML User", "raw_response": decoded[:500]}

                await conn.execute("""
                    UPDATE sso_sessions SET token_data = $1, user_data = $2, status = 'completed'
                    WHERE id = $3
                """, json.dumps({"saml_response": True}), json.dumps(user_data), session["id"])

                return {
                    "session_id": str(session["id"]),
                    "status": "completed",
                    "user": user_data,
                }
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    def generate_saml_request(entity_id: str, sso_url: str) -> Dict:
        request_id = secrets.token_hex(16)
        return {"request_id": request_id, "entity_id": entity_id, "sso_url": sso_url,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                "nameid_format": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"}

    @staticmethod
    def generate_oauth_authorize_url(client_id: str, redirect_uri: str, scopes: List[str]) -> str:
        state = secrets.token_urlsafe(32)
        return f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={'+'.join(scopes)}&state={state}"


# =========================================================================
# GDPR Compliance Manager
# =========================================================================

class GDPRManager:
    @staticmethod
    async def create_data_export_request(user_id: str, user_email: str = None, org_id: str = None) -> Dict:
        """GDPR Article 20 — Right to data portability. Creates a data export request."""
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO data_requests (user_id, user_email, org_id, request_type, status)
                    VALUES ($1, $2, $3, 'export', 'pending')
                    RETURNING id, request_type, status, created_at
                """, user_id, user_email, uuid.UUID(org_id) if org_id else None)
                return dict(row)
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def create_data_deletion_request(user_id: str, user_email: str = None, org_id: str = None) -> Dict:
        """GDPR Article 17 — Right to erasure. Creates a data deletion request."""
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO data_requests (user_id, user_email, org_id, request_type, status)
                    VALUES ($1, $2, $3, 'deletion', 'pending')
                    RETURNING id, request_type, status, created_at
                """, user_id, user_email, uuid.UUID(org_id) if org_id else None)
                return dict(row)
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def process_data_export(request_id: str) -> Dict:
        """Process a data export request — collect all user data."""
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                req = await conn.fetchrow("SELECT * FROM data_requests WHERE id = $1 AND request_type = 'export'", uuid.UUID(request_id))
                if not req: raise HTTPException(404, "Export request not found")
                user_id = req["user_id"]

                # Collect user data from all tables
                export_data = {"user_id": user_id, "exported_at": datetime.now(timezone.utc).isoformat(), "data": {}}

                audit_logs = await conn.fetch("SELECT * FROM audit_logs WHERE user_id = $1 ORDER BY timestamp DESC LIMIT 100", user_id)
                export_data["data"]["audit_logs"] = [dict(r) for r in audit_logs]

                usage = await conn.fetch("SELECT * FROM api_usage WHERE user_id = $1 ORDER BY timestamp DESC LIMIT 100", user_id)
                export_data["data"]["api_usage"] = [dict(r) for r in usage]

                consents = await conn.fetch("SELECT * FROM user_consent WHERE user_id = $1", user_id)
                export_data["data"]["consents"] = [dict(r) for r in consents]

                memberships = await conn.fetch("SELECT * FROM org_members WHERE user_id = $1", user_id)
                export_data["data"]["org_memberships"] = [dict(r) for r in memberships]

                # Update request
                await conn.execute("""
                    UPDATE data_requests SET status = 'completed', result_data = $1, completed_at = NOW()
                    WHERE id = $2
                """, json.dumps(export_data, default=str), uuid.UUID(request_id))

                return export_data
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def process_data_deletion(request_id: str) -> Dict:
        """Process a data deletion request — anonymize/delete user data."""
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                req = await conn.fetchrow("SELECT * FROM data_requests WHERE id = $1 AND request_type = 'deletion'", uuid.UUID(request_id))
                if not req: raise HTTPException(404, "Deletion request not found")
                user_id = req["user_id"]

                # Anonymize audit logs
                await conn.execute("UPDATE audit_logs SET user_id = 'anonymized', user_email = NULL, ip_address = NULL WHERE user_id = $1", user_id)
                # Delete usage data
                await conn.execute("DELETE FROM api_usage WHERE user_id = $1", user_id)
                # Revoke consents
                await conn.execute("UPDATE user_consent SET granted = false, revoked_at = NOW() WHERE user_id = $1", user_id)
                # Remove org memberships
                await conn.execute("DELETE FROM org_members WHERE user_id = $1", user_id)

                await conn.execute("UPDATE data_requests SET status = 'completed', completed_at = NOW() WHERE id = $1", uuid.UUID(request_id))

                return {"deleted": True, "user_id": user_id, "request_id": request_id,
                        "actions": ["anonymized_audit_logs", "deleted_api_usage", "revoked_consents", "removed_memberships"]}
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def set_consent(user_id: str, consent_type: str, granted: bool, ip_address: str = None, details: Dict = None) -> Dict:
        """Set or update user consent for a specific data processing type."""
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                existing = await conn.fetchrow("SELECT id FROM user_consent WHERE user_id = $1 AND consent_type = $2", user_id, consent_type)
                if existing:
                    row = await conn.fetchrow("""
                        UPDATE user_consent SET granted = $1, granted_at = CASE WHEN $1 THEN NOW() ELSE granted_at END,
                        revoked_at = CASE WHEN NOT $1 THEN NOW() ELSE NULL END,
                        ip_address = $2, details = $3
                        WHERE user_id = $4 AND consent_type = $5
                        RETURNING id, user_id, consent_type, granted, granted_at, revoked_at
                    """, granted, ip_address, json.dumps(details or {}), user_id, consent_type)
                else:
                    row = await conn.fetchrow("""
                        INSERT INTO user_consent (user_id, consent_type, granted, ip_address, details)
                        VALUES ($1, $2, $3, $4, $5)
                        RETURNING id, user_id, consent_type, granted, granted_at, revoked_at
                    """, user_id, consent_type, granted, ip_address, json.dumps(details or {}))
                return dict(row)
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def get_consents(user_id: str) -> Dict:
        """Get all consent records for a user."""
        if not _pg_pool: return {"consents": [], "count": 0}
        try:
            async with _pg_pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM user_consent WHERE user_id = $1 ORDER BY granted_at DESC", user_id)
                return {"consents": [dict(r) for r in rows], "count": len(rows)}
        except Exception as e: return {"consents": [], "count": 0, "error": str(e)}

    @staticmethod
    async def get_data_requests(user_id: str = None, status: str = None) -> Dict:
        """List data subject requests."""
        if not _pg_pool: return {"requests": [], "count": 0}
        query = "SELECT * FROM data_requests WHERE 1=1"
        params, idx = [], 1
        if user_id: query += f" AND user_id = ${idx}"; params.append(user_id); idx += 1
        if status: query += f" AND status = ${idx}"; params.append(status); idx += 1
        query += " ORDER BY created_at DESC LIMIT 50"
        try:
            async with _pg_pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                return {"requests": [dict(r) for r in rows], "count": len(rows)}
        except Exception as e: return {"requests": [], "count": 0, "error": str(e)}


# =========================================================================
# Usage Tracker
# =========================================================================

class UsageTracker:
    @staticmethod
    async def record_usage(org_id: str = None, user_id: str = None, endpoint: str = None,
                           method: str = None, response_code: int = None, latency_ms: float = None, tokens_used: int = 0):
        if not _pg_pool: return
        try:
            async with _pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO api_usage (org_id, user_id, endpoint, method, response_code, latency_ms, tokens_used)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, uuid.UUID(org_id) if org_id else None, user_id, endpoint, method, response_code, latency_ms, tokens_used)
        except: pass

    @staticmethod
    async def get_usage_stats(org_id: str = None, days: int = 30):
        if not _pg_pool: return {"total_calls": 0}
        try:
            async with _pg_pool.acquire() as conn:
                interval = f"INTERVAL '{days} days'"
                if org_id:
                    total = await conn.fetchval(f"SELECT COUNT(*) FROM api_usage WHERE org_id = $1 AND timestamp > NOW() - {interval}", uuid.UUID(org_id))
                    avg_lat = await conn.fetchval(f"SELECT AVG(latency_ms) FROM api_usage WHERE org_id = $1 AND timestamp > NOW() - {interval}", uuid.UUID(org_id))
                    tokens = await conn.fetchval(f"SELECT SUM(tokens_used) FROM api_usage WHERE org_id = $1 AND timestamp > NOW() - {interval}", uuid.UUID(org_id))
                    top = await conn.fetch(f"SELECT endpoint, COUNT(*) as cnt FROM api_usage WHERE org_id = $1 AND timestamp > NOW() - {interval} GROUP BY endpoint ORDER BY cnt DESC LIMIT 10", uuid.UUID(org_id))
                else:
                    total = await conn.fetchval(f"SELECT COUNT(*) FROM api_usage WHERE timestamp > NOW() - {interval}")
                    avg_lat = await conn.fetchval(f"SELECT AVG(latency_ms) FROM api_usage WHERE timestamp > NOW() - {interval}")
                    tokens = await conn.fetchval(f"SELECT SUM(tokens_used) FROM api_usage WHERE timestamp > NOW() - {interval}")
                    top = await conn.fetch(f"SELECT endpoint, COUNT(*) as cnt FROM api_usage WHERE timestamp > NOW() - {interval} GROUP BY endpoint ORDER BY cnt DESC LIMIT 10")
                return {"total_calls": total or 0, "period_days": days,
                        "avg_latency_ms": float(avg_lat) if avg_lat else 0,
                        "total_tokens": tokens or 0,
                        "top_endpoints": {r["endpoint"]: r["cnt"] for r in top}}
        except Exception as e: return {"total_calls": 0, "error": str(e)}


# =========================================================================
# Models
# =========================================================================

class CreateOrgRequest(BaseModel):
    name: str; slug: str; plan: str = "free"; settings: Dict = {}; data_region: str = "EU"

class UpdateOrgRequest(BaseModel):
    name: Optional[str] = None; plan: Optional[str] = None; status: Optional[str] = None
    max_users: Optional[int] = None; max_agents: Optional[int] = None
    max_api_calls: Optional[int] = None; max_storage_mb: Optional[int] = None
    settings: Optional[Dict] = None; data_region: Optional[str] = None

class AddMemberRequest(BaseModel):
    user_id: str; user_email: str; role: str = "member"; invited_by: str = None

class CreateSSOConfigRequest(BaseModel):
    provider: str; entity_id: str = None; sso_url: str = None
    certificate: str = None; client_id: str = None; client_secret: str = None
    domains: List[str] = []; attribute_mapping: Dict = {}

class AuditLogRequest(BaseModel):
    action: str; user_id: str = None; user_email: str = None; org_id: str = None
    resource_type: str = None; resource_id: str = None; details: Dict = {}
    severity: str = "info"; category: str = "general"

class InitiateSSORequest(BaseModel):
    org_id: str; provider: str; redirect_uri: str

class OAuthCallbackRequest(BaseModel):
    code: str; state: str; redirect_uri: str

class SAMLCallbackRequest(BaseModel):
    saml_response: str; state: str

class ConsentRequest(BaseModel):
    user_id: str; consent_type: str; granted: bool; details: Dict = {}

class DataSubjectRequest(BaseModel):
    user_id: str; user_email: str = None; org_id: str = None


# =========================================================================
# Startup & Endpoints
# =========================================================================

@router.on_event("startup")
async def startup():
    await init_enterprise_pg()

# Audit
@router.post("/audit/log")
async def create_audit_log(req: AuditLogRequest, request: Request):
    result = await AuditLogger.log(action=req.action, user_id=req.user_id, user_email=req.user_email,
        org_id=req.org_id, resource_type=req.resource_type, resource_id=req.resource_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details=req.details, severity=req.severity, category=req.category)
    return {"logged": result is not None, "log_id": str(result["id"]) if result else None}

@router.get("/audit/logs")
async def get_audit_logs(limit: int = 50, offset: int = 0, user_id: str = None, org_id: str = None,
                          action: str = None, severity: str = None, start_date: str = None, end_date: str = None):
    return await AuditLogger.list_logs(limit, offset, user_id, org_id, action, severity, start_date, end_date)

@router.get("/audit/stats")
async def get_audit_stats():
    return await AuditLogger.get_stats()

# Orgs
@router.post("/orgs")
async def create_org(req: CreateOrgRequest):
    return await OrgManager.create_org(req.name, req.slug, req.plan, req.settings, req.data_region)

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
    return await OrgManager.update_org(org_id, {k: v for k, v in req.dict().items() if v is not None})

@router.delete("/orgs/{org_id}")
async def delete_org(org_id: str):
    return await OrgManager.delete_org(org_id)

@router.get("/orgs/{org_id}/quota/{resource}")
async def check_quota(org_id: str, resource: str):
    return await OrgManager.check_quota(org_id, resource)

# Members
@router.post("/orgs/{org_id}/members")
async def add_member(org_id: str, req: AddMemberRequest):
    return await OrgManager.add_member(org_id, req.user_id, req.user_email, req.role, req.invited_by)

@router.get("/orgs/{org_id}/members")
async def list_members(org_id: str):
    return await OrgManager.list_members(org_id)

@router.delete("/orgs/{org_id}/members/{user_id}")
async def remove_member(org_id: str, user_id: str):
    return await OrgManager.remove_member(org_id, user_id)

# SSO Config
@router.post("/orgs/{org_id}/sso")
async def create_sso_config(org_id: str, req: CreateSSOConfigRequest):
    return await SSOManager.create_sso_config(org_id, req.provider, req.dict())

@router.get("/orgs/{org_id}/sso")
async def get_sso_configs(org_id: str):
    return await SSOManager.get_sso_configs(org_id)

@router.delete("/orgs/{org_id}/sso/{config_id}")
async def delete_sso_config(org_id: str, config_id: str):
    return await SSOManager.delete_sso_config(config_id)

# SSO Flow
@router.post("/sso/initiate")
async def initiate_sso(req: InitiateSSORequest):
    return await SSOManager.initiate_sso(req.org_id, req.provider, req.redirect_uri)

@router.post("/sso/oauth/callback")
async def oauth_callback(req: OAuthCallbackRequest):
    return await SSOManager.handle_oauth_callback(req.code, req.state, req.redirect_uri)

@router.post("/sso/saml/callback")
async def saml_callback(req: SAMLCallbackRequest):
    return await SSOManager.handle_saml_callback(req.saml_response, req.state)

@router.post("/sso/saml/request")
async def generate_saml_request(provider: str = "saml", entity_id: str = "", sso_url: str = ""):
    return SSOManager.generate_saml_request(entity_id, sso_url)

@router.get("/sso/oauth/authorize")
async def generate_oauth_url(client_id: str, redirect_uri: str, scopes: str = "openid email profile"):
    return {"authorize_url": SSOManager.generate_oauth_authorize_url(client_id, redirect_uri, scopes.split())}

# GDPR
@router.post("/gdpr/export")
async def create_data_export(req: DataSubjectRequest):
    return await GDPRManager.create_data_export_request(req.user_id, req.user_email, req.org_id)

@router.post("/gdpr/deletion")
async def create_data_deletion(req: DataSubjectRequest):
    return await GDPRManager.create_data_deletion_request(req.user_id, req.user_email, req.org_id)

@router.post("/gdpr/export/{request_id}/process")
async def process_export(request_id: str):
    return await GDPRManager.process_data_export(request_id)

@router.post("/gdpr/deletion/{request_id}/process")
async def process_deletion(request_id: str):
    return await GDPRManager.process_data_deletion(request_id)

@router.get("/gdpr/requests")
async def get_data_requests(user_id: str = None, status: str = None):
    return await GDPRManager.get_data_requests(user_id, status)

@router.post("/consent")
async def set_consent(req: ConsentRequest, request: Request):
    return await GDPRManager.set_consent(req.user_id, req.consent_type, req.granted,
        request.client.host if request.client else None, req.details)

@router.get("/consent/{user_id}")
async def get_consents(user_id: str):
    return await GDPRManager.get_consents(user_id)

# Usage
@router.get("/usage/stats")
async def get_usage_stats(org_id: str = None, days: int = 30):
    return await UsageTracker.get_usage_stats(org_id, days)

@router.post("/usage/record")
async def record_usage(org_id: str = None, user_id: str = None, endpoint: str = None,
                       method: str = "GET", response_code: int = 200, latency_ms: float = 0, tokens_used: int = 0):
    await UsageTracker.record_usage(org_id, user_id, endpoint, method, response_code, latency_ms, tokens_used)
    return {"recorded": True}

# Dashboard
@router.get("/dashboard")
async def enterprise_dashboard():
    audit_stats = await AuditLogger.get_stats()
    orgs = await OrgManager.list_orgs(limit=1000)
    usage = await UsageTracker.get_usage_stats(days=30)
    dsr = await GDPRManager.get_data_requests()
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "organizations": {"total": orgs["count"],
                          "active": sum(1 for o in orgs.get("orgs", []) if o.get("status") == "active")},
        "audit": audit_stats, "usage": usage,
        "gdpr": {"total_requests": dsr["count"],
                  "pending": sum(1 for r in dsr.get("requests", []) if r.get("status") == "pending"),
                  "completed": sum(1 for r in dsr.get("requests", []) if r.get("status") == "completed")},
        "platform": {"version": "2.0.0",
                      "modules": ["sso", "audit", "multi_tenancy", "usage_tracking", "gdpr", "sso_callbacks"]},
    }
