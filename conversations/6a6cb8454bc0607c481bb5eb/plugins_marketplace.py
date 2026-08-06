"""
EvolvixOS Plugin Marketplace v1.0
Plugin discovery, installation, publishing, reviews, and management
"""

from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import structlog
import asyncio
import os
import json
import uuid
import hashlib

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/plugins", tags=["Plugin Marketplace"])

import asyncpg

PG_DSN = os.getenv("DATABASE_URL", "postgresql://evolvixos:EvolvixOS2026Secure@localhost:5432/evolvixos")
_pg_pool: Optional[asyncpg.Pool] = None


async def init_plugins_pg():
    global _pg_pool
    if _pg_pool:
        try:
            async with _pg_pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS marketplace_plugins (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name TEXT NOT NULL UNIQUE,
                        display_name TEXT NOT NULL,
                        description TEXT,
                        category TEXT NOT NULL DEFAULT 'general',
                        plugin_type TEXT NOT NULL DEFAULT 'llm_provider',
                        version TEXT NOT NULL DEFAULT '1.0.0',
                        author TEXT,
                        author_email TEXT,
                        homepage TEXT,
                        repository TEXT,
                        license TEXT DEFAULT 'MIT',
                        tags TEXT[] DEFAULT '{}',
                        source_url TEXT,
                        documentation TEXT,
                        config_schema JSONB DEFAULT '{}',
                        default_config JSONB DEFAULT '{}',
                        download_count INTEGER DEFAULT 0,
                        rating_sum REAL DEFAULT 0,
                        rating_count INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'published',
                        verified BOOLEAN DEFAULT FALSE,
                        featured BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS plugin_installs (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        plugin_id UUID NOT NULL REFERENCES marketplace_plugins(id) ON DELETE CASCADE,
                        org_id UUID,
                        installed_by TEXT,
                        config JSONB DEFAULT '{}',
                        status TEXT DEFAULT 'installed',
                        version TEXT,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW()
                    );
                    CREATE INDEX IF NOT EXISTS idx_plugin_installs ON plugin_installs(plugin_id);
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS plugin_reviews (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        plugin_id UUID NOT NULL REFERENCES marketplace_plugins(id) ON DELETE CASCADE,
                        user_id TEXT NOT NULL,
                        rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                        review_text TEXT,
                        helpful_count INTEGER DEFAULT 0,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        UNIQUE(plugin_id, user_id)
                    );
                    CREATE INDEX IF NOT EXISTS idx_plugin_reviews ON plugin_reviews(plugin_id);
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS plugin_versions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        plugin_id UUID NOT NULL REFERENCES marketplace_plugins(id) ON DELETE CASCADE,
                        version TEXT NOT NULL,
                        changelog TEXT,
                        source_url TEXT,
                        checksum TEXT,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        UNIQUE(plugin_id, version)
                    );
                    CREATE INDEX IF NOT EXISTS idx_plugin_versions ON plugin_versions(plugin_id);
                """)
                
                # Seed initial marketplace plugins
                seed_plugins = [
                    ("openai-gpt4o", "OpenAI GPT-4o", "GPT-4o chat, completion, and embedding provider", "llm_provider", "openai", "1.2.0", "EvolvixOS", "https://openai.com", "https://github.com/evolvixos/openai-plugin", ["openai", "gpt4o", "chat", "completion", "embedding"]),
                    ("anthropic-claude", "Anthropic Claude", "Claude 3.5 Sonnet chat and analysis provider", "llm_provider", "anthropic", "1.1.0", "EvolvixOS", "https://anthropic.com", "https://github.com/evolvixos/anthropic-plugin", ["anthropic", "claude", "chat", "analysis"]),
                    ("sentiment-analyzer", "Sentiment Analyzer", "AI-powered sentiment analysis with GPT-4o-mini fallback", "analyzer", "ai_tool", "1.0.0", "EvolvixOS", None, "https://github.com/evolvixos/sentiment-plugin", ["sentiment", "nlp", "analysis", "emotion"]),
                    ("code-reviewer", "Code Reviewer", "AI-powered code review with structured JSON output", "analyzer", "ai_tool", "1.0.0", "EvolvixOS", None, "https://github.com/evolvixos/code-reviewer-plugin", ["code", "review", "quality", "security"]),
                    ("verdis-blockchain", "Verdis Blockchain", "Verdis blockchain integration — RPC, wallet, transactions, DEX", "blockchain", "integration", "2.0.0", "Verdis Chain", "https://verdischain.com", "https://github.com/verdischain/verdis-plugin", ["blockchain", "verdis", "rpc", "wallet", "dex"]),
                    ("redis-cache", "Redis Cache", "Redis-backed caching and shared state for plugins", "infrastructure", "utility", "1.0.0", "EvolvixOS", "https://redis.io", "https://github.com/evolvixos/redis-plugin", ["redis", "cache", "state", "performance"]),
                    ("prometheus-monitor", "Prometheus Monitor", "Prometheus metrics exporter for plugin performance tracking", "monitoring", "utility", "1.0.0", "EvolvixOS", "https://prometheus.io", "https://github.com/evolvixos/prometheus-plugin", ["prometheus", "metrics", "monitoring", "observability"]),
                    ("email-notifier", "Email Notifier", "Email notification plugin for alerts and reports", "notification", "utility", "1.0.0", "EvolvixOS", None, "https://github.com/evolvixos/email-plugin", ["email", "notification", "alert", "smtp"]),
                    ("webhook-dispatcher", "Webhook Dispatcher", "HTTP webhook delivery with retry and DLQ support", "integration", "utility", "1.0.0", "EvolvixOS", None, "https://github.com/evolvixos/webhook-plugin", ["webhook", "http", "integration", "retry"]),
                    ("file-storage", "File Storage", "S3-compatible file storage plugin for uploads and downloads", "storage", "utility", "1.0.0", "EvolvixOS", "https://aws.amazon.com/s3", "https://github.com/evolvixos/storage-plugin", ["storage", "s3", "files", "uploads"]),
                    ("erc20-token", "ERC20 Token", "ERC20 token contract template and interaction plugin", "blockchain", "smart_contract", "1.0.0", "Verdis Chain", "https://verdischain.com", "https://github.com/verdischain/erc20-plugin", ["erc20", "token", "contract", "blockchain"]),
                    ("carbon-credit", "Carbon Credit", "Carbon credit tracking and verification for eco-blockchain", "blockchain", "smart_contract", "1.0.0", "Verdis Chain", "https://verdischain.com", "https://github.com/verdischain/carbon-plugin", ["carbon", "eco", "green", "sustainability"]),
                ]
                
                for name, display, desc, ptype, cat, ver, author, homepage, repo, tags in seed_plugins:
                    await conn.execute("""
                        INSERT INTO marketplace_plugins (name, display_name, description, category, plugin_type, version, author, homepage, repository, tags, verified, featured)
                        SELECT $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, true, false
                        WHERE NOT EXISTS (SELECT 1 FROM marketplace_plugins WHERE name = $1)
                    """, name, display, desc, cat, ptype, ver, author, homepage, repo, tags)
                
                # Mark some as featured
                await conn.execute("UPDATE marketplace_plugins SET featured = true WHERE name IN ('openai-gpt4o', 'verdis-blockchain', 'code-reviewer')")
                
                logger.info("Plugin marketplace initialized with 12 plugins")
            return True
        except Exception as e:
            logger.warning(f"Plugins PG error: {e}")
            return True
    
    for attempt in range(3):
        try:
            _pg_pool = await asyncpg.create_pool(PG_DSN, min_size=2, max_size=10, command_timeout=30)
            async with _pg_pool.acquire() as conn:
                await conn.execute("SELECT 1")
            return await init_plugins_pg()
        except Exception as e:
            logger.warning(f"Plugins PG attempt {attempt+1}: {e}")
            await asyncio.sleep(2)
    return False


# =========================================================================
# Models
# =========================================================================

class PublishPluginRequest(BaseModel):
    name: str
    display_name: str
    description: str = ""
    category: str = "general"
    plugin_type: str = "utility"
    version: str = "1.0.0"
    author: str = None
    author_email: str = None
    homepage: str = None
    repository: str = None
    license: str = "MIT"
    tags: List[str] = []
    source_url: str = None
    documentation: str = ""
    config_schema: Dict = {}
    default_config: Dict = {}

class InstallPluginRequest(BaseModel):
    plugin_name: str
    org_id: str = None
    installed_by: str = None
    config: Dict = {}
    version: str = None

class ReviewPluginRequest(BaseModel):
    user_id: str
    rating: int = Field(ge=1, le=5)
    review_text: str = ""

class UpdatePluginRequest(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    documentation: Optional[str] = None
    featured: Optional[bool] = None
    status: Optional[str] = None


# =========================================================================
# Plugin Manager
# =========================================================================

class PluginMarketplace:
    @staticmethod
    async def list_plugins(limit=50, offset=0, category=None, plugin_type=None, search=None, sort="downloads"):
        if not _pg_pool: return {"plugins": [], "count": 0}
        query = "SELECT * FROM marketplace_plugins WHERE status = 'published'"
        params, idx = [], 1
        if category: query += f" AND category = ${idx}"; params.append(category); idx += 1
        if plugin_type: query += f" AND plugin_type = ${idx}"; params.append(plugin_type); idx += 1
        if search: query += f" AND (name ILIKE ${idx} OR display_name ILIKE ${idx} OR description ILIKE ${idx} OR $${idx} = ANY(tags))"; params.append(f"%{search}%"); idx += 1
        
        sort_map = {"downloads": "download_count DESC", "rating": "rating_sum NULLIF(rating_sum,0)/NULLIF(rating_count,0) DESC", "newest": "created_at DESC", "name": "name ASC"}
        query += f" ORDER BY {sort_map.get(sort, 'download_count DESC')}"
        query += f" LIMIT ${idx} OFFSET ${idx+1}"
        params.extend([limit, offset])
        
        try:
            async with _pg_pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                count = await conn.fetchval("SELECT COUNT(*) FROM marketplace_plugins WHERE status = 'published'")
                plugins = []
                for r in rows:
                    p = dict(r)
                    p["avg_rating"] = round(p["rating_sum"] / p["rating_count"], 1) if p["rating_count"] > 0 else 0.0
                    plugins.append(p)
                return {"plugins": plugins, "count": count}
        except Exception as e: return {"plugins": [], "count": 0, "error": str(e)}

    @staticmethod
    async def get_plugin(plugin_id: str):
        if not _pg_pool: return None
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM marketplace_plugins WHERE id = $1", uuid.UUID(plugin_id))
                if not row: return None
                p = dict(row)
                p["avg_rating"] = round(p["rating_sum"] / p["rating_count"], 1) if p["rating_count"] > 0 else 0.0
                return p
        except: return None

    @staticmethod
    async def get_by_name(name: str):
        if not _pg_pool: return None
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM marketplace_plugins WHERE name = $1", name)
                return dict(row) if row else None
        except: return None

    @staticmethod
    async def publish_plugin(req: PublishPluginRequest):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                existing = await conn.fetchrow("SELECT id FROM marketplace_plugins WHERE name = $1", req.name)
                if existing: raise HTTPException(409, f"Plugin '{req.name}' already exists")
                row = await conn.fetchrow("""
                    INSERT INTO marketplace_plugins (name, display_name, description, category, plugin_type, version, author, author_email, homepage, repository, license, tags, source_url, documentation, config_schema, default_config)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    RETURNING id, name, version, status
                """, req.name, req.display_name, req.description, req.category, req.plugin_type, req.version,
                    req.author, req.author_email, req.homepage, req.repository, req.license, req.tags,
                    req.source_url, req.documentation, json.dumps(req.config_schema), json.dumps(req.default_config))
                return dict(row)
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def install_plugin(req: InstallPluginRequest):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                plugin = await conn.fetchrow("SELECT * FROM marketplace_plugins WHERE name = $1 AND status = 'published'", req.plugin_name)
                if not plugin: raise HTTPException(404, f"Plugin '{req.plugin_name}' not found")
                
                # Increment download count
                await conn.execute("UPDATE marketplace_plugins SET download_count = download_count + 1 WHERE name = $1", req.plugin_name)
                
                # Create install record
                row = await conn.fetchrow("""
                    INSERT INTO plugin_installs (plugin_id, org_id, installed_by, config, status, version)
                    VALUES ($1, $2, $3, $4, 'installed', $5)
                    ON CONFLICT DO NOTHING
                    RETURNING id, status, created_at
                """, plugin["id"], uuid.UUID(req.org_id) if req.org_id else None, req.installed_by,
                    json.dumps(req.config), req.version or plugin["version"])
                
                return {
                    "installed": True,
                    "plugin": req.plugin_name,
                    "version": req.version or plugin["version"],
                    "install_id": str(row["id"]) if row else None,
                    "plugin_type": plugin["plugin_type"],
                    "config_schema": plugin["config_schema"],
                }
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def uninstall_plugin(plugin_name: str, org_id: str = None):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                plugin = await conn.fetchrow("SELECT id FROM marketplace_plugins WHERE name = $1", plugin_name)
                if not plugin: raise HTTPException(404, "Plugin not found")
                result = await conn.execute("DELETE FROM plugin_installs WHERE plugin_id = $1 AND org_id = $2",
                    plugin["id"], uuid.UUID(org_id) if org_id else None)
                return {"uninstalled": True, "plugin": plugin_name, "deleted": result}
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def review_plugin(plugin_id: str, req: ReviewPluginRequest):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                # Insert or update review
                row = await conn.fetchrow("""
                    INSERT INTO plugin_reviews (plugin_id, user_id, rating, review_text)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (plugin_id, user_id) DO UPDATE
                    SET rating = $3, review_text = $4
                    RETURNING id, rating
                """, uuid.UUID(plugin_id), req.user_id, req.rating, req.review_text)
                
                # Update plugin rating aggregate
                await conn.execute("""
                    UPDATE marketplace_plugins SET
                        rating_sum = (SELECT COALESCE(SUM(rating), 0) FROM plugin_reviews WHERE plugin_id = $1),
                        rating_count = (SELECT COUNT(*) FROM plugin_reviews WHERE plugin_id = $1)
                    WHERE id = $1
                """, uuid.UUID(plugin_id))
                
                return {"reviewed": True, "rating": req.rating, "review_id": str(row["id"])}
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def get_reviews(plugin_id: str, limit=20, offset=0):
        if not _pg_pool: return {"reviews": [], "count": 0}
        try:
            async with _pg_pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM plugin_reviews WHERE plugin_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3",
                    uuid.UUID(plugin_id), limit, offset)
                count = await conn.fetchval("SELECT COUNT(*) FROM plugin_reviews WHERE plugin_id = $1", uuid.UUID(plugin_id))
                return {"reviews": [dict(r) for r in rows], "count": count}
        except Exception as e: return {"reviews": [], "count": 0, "error": str(e)}

    @staticmethod
    async def get_featured():
        if not _pg_pool: return {"plugins": [], "count": 0}
        try:
            async with _pg_pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM marketplace_plugins WHERE featured = true AND status = 'published' ORDER BY download_count DESC")
                return {"plugins": [dict(r) for r in rows], "count": len(rows)}
        except Exception as e: return {"plugins": [], "count": 0}

    @staticmethod
    async def get_categories():
        if not _pg_pool: return {"categories": []}
        try:
            async with _pg_pool.acquire() as conn:
                rows = await conn.fetch("SELECT category, COUNT(*) as count FROM marketplace_plugins WHERE status = 'published' GROUP BY category ORDER BY count DESC")
                return {"categories": [{"name": r["category"], "count": r["count"]} for r in rows]}
        except Exception as e: return {"categories": []}

    @staticmethod
    async def get_installed(org_id: str = None, installed_by: str = None):
        if not _pg_pool: return {"installed": [], "count": 0}
        try:
            query = "SELECT pi.*, mp.name, mp.display_name, mp.plugin_type, mp.category FROM plugin_installs pi JOIN marketplace_plugins mp ON pi.plugin_id = mp.id WHERE 1=1"
            params, idx = [], 1
            if org_id: query += f" AND pi.org_id = ${idx}"; params.append(uuid.UUID(org_id)); idx += 1
            if installed_by: query += f" AND pi.installed_by = ${idx}"; params.append(installed_by); idx += 1
            async with _pg_pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                return {"installed": [dict(r) for r in rows], "count": len(rows)}
        except Exception as e: return {"installed": [], "count": 0, "error": str(e)}

    @staticmethod
    async def update_plugin(plugin_id: str, updates: Dict):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        allowed = {"display_name", "description", "tags", "documentation", "featured", "status"}
        fields = {k: v for k, v in updates.items() if k in allowed and v is not None}
        if not fields: raise HTTPException(400, "No valid fields")
        set_parts, params, idx = [], [], 1
        for k, v in fields.items():
            set_parts.append(f"{k} = ${idx}"); params.append(v); idx += 1
        set_parts.append("updated_at = NOW()"); params.append(uuid.UUID(plugin_id))
        try:
            async with _pg_pool.acquire() as conn:
                row = await conn.fetchrow(f"UPDATE marketplace_plugins SET {', '.join(set_parts)} WHERE id = ${idx} RETURNING *", *params)
                if not row: raise HTTPException(404, "Plugin not found")
                return dict(row)
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))

    @staticmethod
    async def delete_plugin(plugin_id: str):
        if not _pg_pool: raise HTTPException(503, "Database not connected")
        try:
            async with _pg_pool.acquire() as conn:
                result = await conn.execute("DELETE FROM marketplace_plugins WHERE id = $1", uuid.UUID(plugin_id))
                if result == "DELETE 0": raise HTTPException(404, "Plugin not found")
                return {"deleted": True, "plugin_id": plugin_id}
        except HTTPException: raise
        except Exception as e: raise HTTPException(500, str(e))


# =========================================================================
# Endpoints
# =========================================================================

@router.on_event("startup")
async def startup():
    await init_plugins_pg()

@router.get("/dashboard")
async def marketplace_dashboard():
    if not _pg_pool:
        return {"version": "1.0.0", "total_plugins": 0, "categories": [], "featured": [], "message": "Connecting to database..."}
    plugins = await PluginMarketplace.list_plugins(limit=1000)
    featured = await PluginMarketplace.get_featured()
    categories = await PluginMarketplace.get_categories()
    total_downloads = sum(p.get("download_count", 0) for p in plugins.get("plugins", []))
    total_ratings = sum(p.get("rating_count", 0) for p in plugins.get("plugins", []))
    return {
        "version": "1.0.0",
        "total_plugins": plugins["count"],
        "total_downloads": total_downloads,
        "total_ratings": total_ratings,
        "featured_count": featured["count"],
        "categories": categories["categories"],
        "featured": featured["plugins"][:3],
    }

@router.get("/")
async def list_plugins(limit: int = 50, offset: int = 0, category: str = None, plugin_type: str = None, search: str = None, sort: str = "downloads"):
    return await PluginMarketplace.list_plugins(limit, offset, category, plugin_type, search, sort)

@router.get("/featured")
async def get_featured():
    return await PluginMarketplace.get_featured()

@router.get("/categories")
async def get_categories():
    return await PluginMarketplace.get_categories()

@router.get("/installed")
async def get_installed(org_id: str = None, installed_by: str = None):
    return await PluginMarketplace.get_installed(org_id, installed_by)

@router.get("/{plugin_id}")
async def get_plugin(plugin_id: str):
    plugin = await PluginMarketplace.get_plugin(plugin_id)
    if not plugin: raise HTTPException(404, "Plugin not found")
    return plugin

@router.post("/")
async def publish_plugin(req: PublishPluginRequest):
    return await PluginMarketplace.publish_plugin(req)

@router.post("/install")
async def install_plugin(req: InstallPluginRequest):
    return await PluginMarketplace.install_plugin(req)

@router.delete("/uninstall/{plugin_name}")
async def uninstall_plugin(plugin_name: str, org_id: str = None):
    return await PluginMarketplace.uninstall_plugin(plugin_name, org_id)

@router.post("/{plugin_id}/review")
async def review_plugin(plugin_id: str, req: ReviewPluginRequest):
    return await PluginMarketplace.review_plugin(plugin_id, req)

@router.get("/{plugin_id}/reviews")
async def get_reviews(plugin_id: str, limit: int = 20, offset: int = 0):
    return await PluginMarketplace.get_reviews(plugin_id, limit, offset)

@router.patch("/{plugin_id}")
async def update_plugin(plugin_id: str, req: UpdatePluginRequest):
    return await PluginMarketplace.update_plugin(plugin_id, req.dict())

@router.delete("/{plugin_id}")
async def delete_plugin(plugin_id: str):
    return await PluginMarketplace.delete_plugin(plugin_id)
