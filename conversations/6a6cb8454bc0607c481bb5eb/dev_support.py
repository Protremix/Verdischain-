"""
EvolvixOS Developer Support System v1.0
Documentation, tutorials, community forum, and developer resources
Addresses GPT-4o Phase 122 recommendations: developer support system
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
import re

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/dev-support", tags=["Developer Support"])

import asyncpg

PG_DSN = os.getenv("DATABASE_URL", "postgresql://evolvixos:EvolvixOS2026Secure@localhost:5432/evolvixos")
_pg_pool: Optional[asyncpg.Pool] = None

try:
    from plugins_security import InputSanitizer
except ImportError:
    pass


# =========================================================================
# Documentation Manager
# =========================================================================

class DocumentationManager:
    """Manage developer documentation with search and versioning."""
    
    DOC_CATEGORIES = ["getting-started", "sdk", "api-reference", "guides", "tutorials", "examples", "faq", "changelog"]
    
    @staticmethod
    async def init_tables():
        pool = _pg_pool
        if not pool: return False
        try:
            async with pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS dev_docs (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        title TEXT NOT NULL,
                        slug TEXT NOT NULL UNIQUE,
                        category TEXT NOT NULL,
                        content TEXT NOT NULL,
                        excerpt TEXT,
                        author TEXT,
                        tags TEXT[] DEFAULT '{}',
                        version TEXT DEFAULT '1.0.0',
                        status TEXT DEFAULT 'published',
                        sort_order INTEGER DEFAULT 0,
                        views INTEGER DEFAULT 0,
                        helpful_count INTEGER DEFAULT 0,
                        not_helpful_count INTEGER DEFAULT 0,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS dev_tutorials (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        title TEXT NOT NULL,
                        slug TEXT NOT NULL UNIQUE,
                        description TEXT,
                        difficulty TEXT DEFAULT 'beginner',
                        duration_minutes INTEGER DEFAULT 10,
                        steps JSONB DEFAULT '[]',
                        code_examples JSONB DEFAULT '[]',
                        tags TEXT[] DEFAULT '{}',
                        status TEXT DEFAULT 'published',
                        views INTEGER DEFAULT 0,
                        completions INTEGER DEFAULT 0,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS community_posts (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        title TEXT NOT NULL,
                        body TEXT NOT NULL,
                        author_id TEXT NOT NULL,
                        author_name TEXT,
                        category TEXT DEFAULT 'general',
                        tags TEXT[] DEFAULT '{}',
                        upvotes INTEGER DEFAULT 0,
                        downvotes INTEGER DEFAULT 0,
                        views INTEGER DEFAULT 0,
                        reply_count INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'open',
                        accepted_answer UUID,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS community_replies (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        post_id UUID NOT NULL REFERENCES community_posts(id) ON DELETE CASCADE,
                        body TEXT NOT NULL,
                        author_id TEXT NOT NULL,
                        author_name TEXT,
                        upvotes INTEGER DEFAULT 0,
                        downvotes INTEGER DEFAULT 0,
                        is_accepted BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_community_replies ON community_replies(post_id)")
                
                # Seed initial documentation
                docs_seed = [
                    ("Getting Started with EvolvixOS", "getting-started", "getting-started",
                     "# Getting Started\n\nWelcome to EvolvixOS! This guide will help you get up and running.\n\n## Prerequisites\n\n- Python 3.8+\n- Node.js 18+ (for TypeScript SDK)\n- EvolvixOS account\n\n## Installation\n\n```bash\npip install evolvixos-cli\n```\n\n## Quick Start\n\n```bash\nevolvixos init my-project\nevolvixos status\n```\n\n## Next Steps\n\n- Read the [SDK Guide](/docs/sdk)\n- Explore [Tutorials](/docs/tutorials)\n- Join the [Community](/docs/community)",
                     "Get started with EvolvixOS in minutes", "EvolvixOS Team", ["intro", "setup", "beginner"], 1),
                    ("EvolvixOS SDK Guide", "sdk-guide", "sdk",
                     "# EvolvixOS SDK\n\nThe EvolvixOS SDK provides programmatic access to all platform services.\n\n## Python SDK\n\n```python\nfrom evolvixos_sdk import EvolvixOSClient\n\nclient = EvolvixOSClient(api_key='your-key')\n\n# List contracts\ncontracts = await client.contracts.list()\n\n# Create agent\nagent = await client.agents.create(name='MyAgent')\n```\n\n## TypeScript SDK\n\n```typescript\nimport { EvolvixOSClient } from '@evolvixos/sdk';\n\nconst client = new EvolvixOSClient({ apiKey: 'your-key' });\nconst contracts = await client.contracts.list();\n```\n\n## Authentication\n\nAll SDK requests require an API key passed via `X-API-Key` header.",
                     "Complete guide to the EvolvixOS Python and TypeScript SDKs", "EvolvixOS Team", ["sdk", "python", "typescript", "api"], 2),
                    ("API Reference", "api-reference", "api-reference",
                     "# API Reference\n\nAll endpoints are accessible at `https://evolvixos.com`.\n\n## AI Gateway\n- POST /ai-gateway/invoke — Invoke AI capability\n- GET /ai-gateway/plugins — List plugins\n\n## Contracts\n- GET /contracts/api/v1/contracts/ — List contracts\n- POST /contracts/api/v1/contracts/ai/generate — AI generate\n- POST /contracts/api/v1/contracts/{id}/deploy — Deploy\n\n## Agents\n- GET /agents/agents — List agents\n- POST /agents/agents — Create agent\n\n## Marketplace\n- GET /marketplace/api/v1/plugins/ — List plugins\n- POST /marketplace/api/v1/plugins/install — Install\n\n## Platform\n- GET /platform/api/v1/platform/status — Platform status\n- GET /platform/api/v1/platform/scalability/config — Scalability config",
                     "Complete API reference for all EvolvixOS endpoints", "EvolvixOS Team", ["api", "reference", "endpoints"], 3),
                    ("Frequently Asked Questions", "faq", "faq",
                     "# FAQ\n\n## General\n\n**What is EvolvixOS?**\nEvolvixOS is an autonomous AI engineering platform.\n\n**How do I get an API key?**\nUse `evolvixos login --api-key <key>` to configure your CLI.\n\n## SDK\n\n**Which languages are supported?**\nPython and TypeScript/JavaScript SDKs are available.\n\n**Is the SDK async?**\nYes, both SDKs use async/await patterns.\n\n## Marketplace\n\n**How do I publish a plugin?**\nUse POST /marketplace/api/v1/plugins/safe-publish with your plugin details.\n\n**How are plugins verified?**\nPlugins go through an 8-point verification pipeline including security scan, license check, and test coverage.",
                     "Common questions about EvolvixOS platform", "EvolvixOS Team", ["faq", "questions", "help"], 99),
                ]
                
                for title, slug, cat, content, excerpt, author, tags, order in docs_seed:
                    await conn.execute("""
                        INSERT INTO dev_docs (title, slug, category, content, excerpt, author, tags, sort_order)
                        SELECT $1, $2, $3, $4, $5, $6, $7, $8
                        WHERE NOT EXISTS (SELECT 1 FROM dev_docs WHERE slug = $2)
                    """, title, slug, cat, content, excerpt, author, tags, order)
                
                # Seed tutorials
                tutorials_seed = [
                    ("Build Your First Smart Contract", "build-first-contract", "beginner", 15,
                     "Learn how to create, test, and deploy a smart contract on the Verdis blockchain.",
                     [{"title": "Create contract", "description": "Use the CLI to create a new contract"}, {"title": "Test contract", "description": "Run tests against your contract"}, {"title": "Deploy contract", "description": "Deploy to verdis-testnet"}],
                     [{"language": "bash", "code": "evolvixos contracts create MyToken --source MyToken.sol"}, {"language": "bash", "code": "evolvixos contracts test <contract-id>"}, {"language": "bash", "code": "evolvixos contracts deploy <contract-id> --network verdis-testnet"}],
                     ["contracts", "solidity", "beginner"]),
                    ("Create an AI Agent", "create-ai-agent", "intermediate", 20,
                     "Build and deploy an autonomous AI agent using the EvolvixOS Agent Framework.",
                     [{"title": "Create agent", "description": "Create a new agent via API"}, {"title": "Configure capabilities", "description": "Set up agent capabilities and system prompt"}, {"title": "Execute task", "description": "Send a task to the agent"}],
                     [{"language": "python", "code": "import httpx\nasync with httpx.AsyncClient() as c:\n    r = await c.post('https://evolvixos.com/agents/agents', json={'name': 'MyAgent', 'role': 'developer'})"}, {"language": "python", "code": "r = await c.post(f'https://evolvixos.com/agents/agents/{agent_id}/tasks', json={'instruction': 'Review this code'})"}],
                     ["agents", "ai", "intermediate"]),
                    ("Publish a Plugin", "publish-plugin", "advanced", 25,
                     "Package, verify, and publish a plugin to the EvolvixOS Marketplace.",
                     [{"title": "Write plugin", "description": "Create your plugin code"}, {"title": "Run verification", "description": "Submit to verification pipeline"}, {"title": "Publish", "description": "Publish to marketplace"}],
                     [{"language": "bash", "code": "curl -X POST https://evolvixos.com/marketplace/api/v1/plugins/safe-publish -H 'Content-Type: application/json' -d '{\"name\": \"my-plugin\", \"display_name\": \"My Plugin\"}'"}, {"language": "bash", "code": "curl -X POST https://evolvixos.com/platform/api/v1/platform/verification/run -H 'Content-Type: application/json' -d '{\"plugin_id\": \"<id>\", \"source_code\": \"...\", \"metadata\": {\"license\": \"MIT\"}}'"}],
                     ["plugins", "marketplace", "advanced"]),
                ]
                
                for title, slug, difficulty, duration, desc, steps, examples, tags in tutorials_seed:
                    await conn.execute("""
                        INSERT INTO dev_tutorials (title, slug, description, difficulty, duration_minutes, steps, code_examples, tags)
                        SELECT $1, $2, $3, $4, $5, $6, $7, $8
                        WHERE NOT EXISTS (SELECT 1 FROM dev_tutorials WHERE slug = $2)
                    """, title, slug, desc, difficulty, duration, json.dumps(steps), json.dumps(examples), tags)
                
                logger.info("Developer support tables initialized")
                return True
        except Exception as e:
            logger.warning(f"Dev support tables: {e}")
            return True


# =========================================================================
# Models
# =========================================================================

class CreateDocRequest(BaseModel):
    title: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)
    category: str = Field("guides", max_length=50)
    content: str = Field(..., max_length=50000)
    excerpt: str = Field("", max_length=500)
    author: str = Field(None, max_length=100)
    tags: List[str] = []
    sort_order: int = 0

class CreateTutorialRequest(BaseModel):
    title: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)
    description: str = Field("", max_length=1000)
    difficulty: str = Field("beginner", pattern="^(beginner|intermediate|advanced)$")
    duration_minutes: int = Field(10, ge=1, le=480)
    steps: List[Dict] = []
    code_examples: List[Dict] = []
    tags: List[str] = []

class CreatePostRequest(BaseModel):
    title: str = Field(..., max_length=200)
    body: str = Field(..., max_length=10000)
    author_id: str = Field(..., max_length=100)
    author_name: str = Field(None, max_length=100)
    category: str = Field("general", max_length=50)
    tags: List[str] = []

class CreateReplyRequest(BaseModel):
    post_id: str
    body: str = Field(..., max_length=10000)
    author_id: str = Field(..., max_length=100)
    author_name: str = Field(None, max_length=100)

class VoteRequest(BaseModel):
    direction: str = Field(..., pattern="^(up|down)$")


# =========================================================================
# Documentation Endpoints
# =========================================================================

@router.on_event("startup")
async def startup():
    global _pg_pool
    for attempt in range(3):
        try:
            _pg_pool = await asyncpg.create_pool(PG_DSN, min_size=2, max_size=10, command_timeout=30)
            async with _pg_pool.acquire() as conn:
                await conn.execute("SELECT 1")
            await DocumentationManager.init_tables()
            logger.info("Dev support PG connected")
            return
        except Exception as e:
            logger.warning(f"Dev support PG attempt {attempt+1}: {e}")
            await asyncio.sleep(2)


@router.get("/docs")
async def list_docs(category: str = None, search: str = None, limit: int = 50, offset: int = 0):
    if not _pg_pool: return {"docs": [], "count": 0}
    try:
        query = "SELECT id, title, slug, category, excerpt, author, tags, sort_order, views, helpful_count, created_at, updated_at FROM dev_docs WHERE status = 'published'"
        params, idx = [], 1
        if category: query += f" AND category = ${idx}"; params.append(category); idx += 1
        if search: query += f" AND (title ILIKE ${idx} OR content ILIKE ${idx} OR ${idx} = ANY(tags))"; params.append(f"%{search}%"); idx += 1
        query += f" ORDER BY sort_order ASC, created_at DESC LIMIT ${idx} OFFSET ${idx+1}"
        params.extend([limit, offset])
        async with _pg_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            count = await conn.fetchval("SELECT COUNT(*) FROM dev_docs WHERE status = 'published'")
            return {"docs": [dict(r) for r in rows], "count": count}
    except Exception as e: return {"docs": [], "count": 0, "error": str(e)}

@router.get("/docs/{slug}")
async def get_doc(slug: str):
    if not _pg_pool: raise HTTPException(503, "Database not connected")
    try:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM dev_docs WHERE slug = $1 AND status = 'published'", slug)
            if not row: raise HTTPException(404, "Document not found")
            await conn.execute("UPDATE dev_docs SET views = views + 1 WHERE slug = $1", slug)
            return dict(row)
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/docs")
async def create_doc(req: CreateDocRequest):
    if not _pg_pool: raise HTTPException(503, "Database not connected")
    try:
        async with _pg_pool.acquire() as conn:
            existing = await conn.fetchrow("SELECT id FROM dev_docs WHERE slug = $1", req.slug)
            if existing: raise HTTPException(409, f"Doc with slug '{req.slug}' already exists")
            row = await conn.fetchrow("""
                INSERT INTO dev_docs (title, slug, category, content, excerpt, author, tags, sort_order)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id, title, slug, category, status
            """, req.title, req.slug, req.category, req.content, req.excerpt, req.author, req.tags, req.sort_order)
            return dict(row)
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.get("/docs/{slug}/helpful")
async def mark_helpful(slug: str, helpful: bool = True):
    if not _pg_pool: raise HTTPException(503, "Database not connected")
    try:
        async with _pg_pool.acquire() as conn:
            if helpful:
                await conn.execute("UPDATE dev_docs SET helpful_count = helpful_count + 1 WHERE slug = $1", slug)
            else:
                await conn.execute("UPDATE dev_docs SET not_helpful_count = not_helpful_count + 1 WHERE slug = $1", slug)
            return {"marked": True, "helpful": helpful}
    except Exception as e: raise HTTPException(500, str(e))


# =========================================================================
# Tutorial Endpoints
# =========================================================================

@router.get("/tutorials")
async def list_tutorials(difficulty: str = None, search: str = None, limit: int = 50, offset: int = 0):
    if not _pg_pool: return {"tutorials": [], "count": 0}
    try:
        query = "SELECT * FROM dev_tutorials WHERE status = 'published'"
        params, idx = [], 1
        if difficulty: query += f" AND difficulty = ${idx}"; params.append(difficulty); idx += 1
        if search: query += f" AND (title ILIKE ${idx} OR description ILIKE ${idx} OR ${idx} = ANY(tags))"; params.append(f"%{search}%"); idx += 1
        query += f" ORDER BY created_at DESC LIMIT ${idx} OFFSET ${idx+1}"
        params.extend([limit, offset])
        async with _pg_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            count = await conn.fetchval("SELECT COUNT(*) FROM dev_tutorials WHERE status = 'published'")
            return {"tutorials": [dict(r) for r in rows], "count": count}
    except Exception as e: return {"tutorials": [], "count": 0, "error": str(e)}

@router.get("/tutorials/{slug}")
async def get_tutorial(slug: str):
    if not _pg_pool: raise HTTPException(503, "Database not connected")
    try:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM dev_tutorials WHERE slug = $1 AND status = 'published'", slug)
            if not row: raise HTTPException(404, "Tutorial not found")
            await conn.execute("UPDATE dev_tutorials SET views = views + 1 WHERE slug = $1", slug)
            return dict(row)
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/tutorials")
async def create_tutorial(req: CreateTutorialRequest):
    if not _pg_pool: raise HTTPException(503, "Database not connected")
    try:
        async with _pg_pool.acquire() as conn:
            existing = await conn.fetchrow("SELECT id FROM dev_tutorials WHERE slug = $1", req.slug)
            if existing: raise HTTPException(409, f"Tutorial with slug '{req.slug}' already exists")
            row = await conn.fetchrow("""
                INSERT INTO dev_tutorials (title, slug, description, difficulty, duration_minutes, steps, code_examples, tags)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id, title, slug, difficulty, status
            """, req.title, req.slug, req.description, req.difficulty, req.duration_minutes,
                json.dumps(req.steps), json.dumps(req.code_examples), req.tags)
            return dict(row)
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/tutorials/{slug}/complete")
async def complete_tutorial(slug: str):
    if not _pg_pool: raise HTTPException(503, "Database not connected")
    try:
        async with _pg_pool.acquire() as conn:
            await conn.execute("UPDATE dev_tutorials SET completions = completions + 1 WHERE slug = $1", slug)
            return {"completed": True, "tutorial": slug}
    except Exception as e: raise HTTPException(500, str(e))


# =========================================================================
# Community Forum Endpoints
# =========================================================================

@router.get("/community/posts")
async def list_posts(category: str = None, search: str = None, sort: str = "newest", limit: int = 50, offset: int = 0):
    if not _pg_pool: return {"posts": [], "count": 0}
    try:
        query = "SELECT * FROM community_posts WHERE status != 'deleted'"
        params, idx = [], 1
        if category: query += f" AND category = ${idx}"; params.append(category); idx += 1
        if search: query += f" AND (title ILIKE ${idx} OR body ILIKE ${idx} OR ${idx} = ANY(tags))"; params.append(f"%{search}%"); idx += 1
        sort_map = {"newest": "created_at DESC", "votes": "(upvotes - downvotes) DESC", "replies": "reply_count DESC", "views": "views DESC"}
        query += f" ORDER BY {sort_map.get(sort, 'created_at DESC')}"
        query += f" LIMIT ${idx} OFFSET ${idx+1}"
        params.extend([limit, offset])
        async with _pg_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            count = await conn.fetchval("SELECT COUNT(*) FROM community_posts WHERE status != 'deleted'")
            return {"posts": [dict(r) for r in rows], "count": count}
    except Exception as e: return {"posts": [], "count": 0, "error": str(e)}

@router.get("/community/posts/{post_id}")
async def get_post(post_id: str):
    if not _pg_pool: raise HTTPException(503, "Database not connected")
    try:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM community_posts WHERE id = $1 AND status != 'deleted'", uuid.UUID(post_id))
            if not row: raise HTTPException(404, "Post not found")
            await conn.execute("UPDATE community_posts SET views = views + 1 WHERE id = $1", uuid.UUID(post_id))
            replies = await conn.fetch("SELECT * FROM community_replies WHERE post_id = $1 ORDER BY is_accepted DESC, upvotes DESC, created_at ASC", uuid.UUID(post_id))
            post = dict(row)
            post["replies"] = [dict(r) for r in replies]
            return post
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/community/posts")
async def create_post(req: CreatePostRequest):
    if not _pg_pool: raise HTTPException(503, "Database not connected")
    # Sanitize input
    title = InputSanitizer.sanitize_text(req.title, 200) if 'InputSanitizer' in dir() else req.title
    body = InputSanitizer.sanitize_text(req.body, 10000) if 'InputSanitizer' in dir() else req.body
    try:
        async with _pg_pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO community_posts (title, body, author_id, author_name, category, tags)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id, title, category, status, created_at
            """, title, body, req.author_id, req.author_name, req.category, req.tags)
            return dict(row)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/community/replies")
async def create_reply(req: CreateReplyRequest):
    if not _pg_pool: raise HTTPException(503, "Database not connected")
    body = InputSanitizer.sanitize_text(req.body, 10000) if 'InputSanitizer' in dir() else req.body
    try:
        async with _pg_pool.acquire() as conn:
            post = await conn.fetchrow("SELECT id FROM community_posts WHERE id = $1 AND status != 'deleted'", uuid.UUID(req.post_id))
            if not post: raise HTTPException(404, "Post not found")
            row = await conn.fetchrow("""
                INSERT INTO community_replies (post_id, body, author_id, author_name)
                VALUES ($1, $2, $3, $4)
                RETURNING id, body, created_at
            """, uuid.UUID(req.post_id), body, req.author_id, req.author_name)
            await conn.execute("UPDATE community_posts SET reply_count = reply_count + 1, updated_at = NOW() WHERE id = $1", uuid.UUID(req.post_id))
            return dict(row)
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/community/posts/{post_id}/vote")
async def vote_post(post_id: str, req: VoteRequest):
    if not _pg_pool: raise HTTPException(503, "Database not connected")
    try:
        async with _pg_pool.acquire() as conn:
            if req.direction == "up":
                await conn.execute("UPDATE community_posts SET upvotes = upvotes + 1 WHERE id = $1", uuid.UUID(post_id))
            else:
                await conn.execute("UPDATE community_posts SET downvotes = downvotes + 1 WHERE id = $1", uuid.UUID(post_id))
            return {"voted": True, "direction": req.direction}
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/community/replies/{reply_id}/accept")
async def accept_reply(reply_id: str):
    if not _pg_pool: raise HTTPException(503, "Database not connected")
    try:
        async with _pg_pool.acquire() as conn:
            reply = await conn.fetchrow("SELECT post_id FROM community_replies WHERE id = $1", uuid.UUID(reply_id))
            if not reply: raise HTTPException(404, "Reply not found")
            await conn.execute("UPDATE community_replies SET is_accepted = true WHERE id = $1", uuid.UUID(reply_id))
            await conn.execute("UPDATE community_posts SET accepted_answer = $1, status = 'answered' WHERE id = $2", uuid.UUID(reply_id), reply["post_id"])
            return {"accepted": True, "reply_id": reply_id}
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))


# =========================================================================
# Developer Resources
# =========================================================================

@router.get("/resources")
async def get_resources():
    """Get all developer resources overview."""
    return {
        "documentation": {
            "categories": DocumentationManager.DOC_CATEGORIES,
            "endpoint": "/api/v1/dev-support/docs",
        },
        "tutorials": {
            "difficulties": ["beginner", "intermediate", "advanced"],
            "endpoint": "/api/v1/dev-support/tutorials",
        },
        "community": {
            "features": ["posts", "replies", "voting", "accepted_answers"],
            "endpoint": "/api/v1/dev-support/community/posts",
        },
        "cli": {
            "install": "pip install evolvixos-cli",
            "docs": "evolvixos docs",
        },
        "sdk": {
            "python": "pip install evolvixos-sdk",
            "typescript": "npm install @evolvixos/sdk",
        },
        "links": {
            "ai_gateway": "https://evolvixos.com/ai-gateway/",
            "contracts": "https://evolvixos.com/contracts/",
            "marketplace": "https://evolvixos.com/marketplace/",
            "platform": "https://evolvixos.com/platform/",
            "agents": "https://evolvixos.com/agents/",
        },
    }

@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "dev-support",
        "version": "1.0.0",
        "features": ["docs", "tutorials", "community", "resources"],
    }
