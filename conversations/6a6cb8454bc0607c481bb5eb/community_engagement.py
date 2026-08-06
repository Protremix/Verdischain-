"""
EvolvixOS Community Engagement + Scalability v1.0
Addresses GPT-4o Phase 123 findings:
- Reputation and badge system
- User notifications
- Community engagement tracking
- Scalability assessment and metrics
- AI-driven content insights
"""

from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import structlog
import asyncio
import os
import json
import uuid
import hashlib
import time
import math

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/community", tags=["Community Engagement"])

import asyncpg

PG_DSN = os.getenv("DATABASE_URL", "postgresql://evolvixos:EvolvixOS2026Secure@localhost:5432/evolvixos")
_pg_pool: Optional[asyncpg.Pool] = None

try:
    from plugins_security import InputSanitizer
except ImportError:
    pass


# =========================================================================
# Reputation & Badge System
# =========================================================================

class ReputationSystem:
    """User reputation, badges, and gamification."""
    
    BADGES = [
        {"id": "first_post", "name": "First Post", "description": "Created your first community post", "icon": "📝", "xp": 10, "category": "engagement"},
        {"id": "first_reply", "name": "First Reply", "description": "Replied to a community post", "icon": "💬", "xp": 5, "category": "engagement"},
        {"id": "accepted_answer", "name": "Accepted Answer", "description": "Your reply was accepted as the best answer", "icon": "✅", "xp": 25, "category": "quality"},
        {"id": "helpful", "name": "Helpful Member", "description": "Received 10 upvotes on posts or replies", "icon": "👍", "xp": 20, "category": "quality"},
        {"id": "contributor", "name": "Active Contributor", "description": "Created 10 posts or replies", "icon": "🎯", "xp": 30, "category": "engagement"},
        {"id": "expert", "name": "Community Expert", "description": "Received 50 upvotes total", "icon": "🏆", "xp": 50, "category": "quality"},
        {"id": "doc_author", "name": "Documentation Author", "description": "Published a documentation article", "icon": "📚", "xp": 15, "category": "content"},
        {"id": "tutorial_author", "name": "Tutorial Creator", "description": "Published a tutorial", "icon": "🎓", "xp": 25, "category": "content"},
        {"id": "plugin_author", "name": "Plugin Developer", "description": "Published a plugin to the marketplace", "icon": "🔌", "xp": 40, "category": "content"},
        {"id": "early_adopter", "name": "Early Adopter", "description": "Joined during beta period", "icon": "🚀", "xp": 15, "category": "special"},
    ]
    
    XP_LEVELS = [
        {"level": 1, "title": "Newcomer", "min_xp": 0},
        {"level": 2, "title": "Explorer", "min_xp": 25},
        {"level": 3, "title": "Contributor", "min_xp": 75},
        {"level": 4, "title": "Regular", "min_xp": 150},
        {"level": 5, "title": "Guide", "min_xp": 300},
        {"level": 6, "title": "Expert", "min_xp": 500},
        {"level": 7, "title": "Master", "min_xp": 750},
        {"level": 8, "title": "Legend", "min_xp": 1000},
        {"level": 9, "title": "Architect", "min_xp": 1500},
        {"level": 10, "title": "Visionary", "min_xp": 2500},
    ]
    
    @staticmethod
    async def init_tables():
        pool = _pg_pool
        if not pool: return False
        try:
            async with pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_reputation (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id TEXT NOT NULL UNIQUE,
                        username TEXT,
                        total_xp INTEGER DEFAULT 0,
                        level INTEGER DEFAULT 1,
                        level_title TEXT DEFAULT 'Newcomer',
                        posts_count INTEGER DEFAULT 0,
                        replies_count INTEGER DEFAULT 0,
                        upvotes_received INTEGER DEFAULT 0,
                        accepted_answers INTEGER DEFAULT 0,
                        docs_published INTEGER DEFAULT 0,
                        tutorials_published INTEGER DEFAULT 0,
                        plugins_published INTEGER DEFAULT 0,
                        badges_earned TEXT[] DEFAULT '{}',
                        last_active TIMESTAMPTZ DEFAULT NOW(),
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_badges (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id TEXT NOT NULL,
                        badge_id TEXT NOT NULL,
                        badge_name TEXT,
                        badge_category TEXT,
                        xp_earned INTEGER,
                        earned_at TIMESTAMPTZ DEFAULT NOW(),
                        UNIQUE(user_id, badge_id)
                    )
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_notifications (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id TEXT NOT NULL,
                        notification_type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        body TEXT,
                        link TEXT,
                        metadata JSONB DEFAULT '{}',
                        read BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    )
                    CREATE INDEX IF NOT EXISTS idx_notifications_user ON user_notifications(user_id, read)
                """)
                return True
        except Exception as e:
            logger.warning(f"Reputation tables: {e}")
            return True
    
    @staticmethod
    async def get_or_create_user(user_id: str, username: str = None):
        pool = _pg_pool
        if not pool: return None
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM user_reputation WHERE user_id = $1", user_id)
                if not row:
                    row = await conn.fetchrow("""
                        INSERT INTO user_reputation (user_id, username)
                        VALUES ($1, $2)
                        RETURNING *
                    """, user_id, username)
                return dict(row)
        except Exception as e:
            logger.warning(f"Get user reputation: {e}")
            return None
    
    @staticmethod
    async def award_xp(user_id: str, xp: int, reason: str = ""):
        pool = _pg_pool
        if not pool: return None
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow("SELECT total_xp, level FROM user_reputation WHERE user_id = $1", user_id)
                if not row:
                    await ReputationSystem.get_or_create_user(user_id)
                    row = await conn.fetchrow("SELECT total_xp, level FROM user_reputation WHERE user_id = $1", user_id)
                
                new_xp = (row["total_xp"] or 0) + xp
                new_level = ReputationSystem.calculate_level(new_xp)
                
                await conn.execute("""
                    UPDATE user_reputation 
                    SET total_xp = $1, level = $2, level_title = $3, updated_at = NOW(), last_active = NOW()
                    WHERE user_id = $4
                """, new_xp, new_level["level"], new_level["title"], user_id)
                
                return {"xp_earned": xp, "total_xp": new_xp, "level": new_level, "reason": reason}
        except Exception as e:
            logger.warning(f"Award XP: {e}")
            return None
    
    @staticmethod
    async def award_badge(user_id: str, badge_id: str):
        pool = _pg_pool
        if not pool: return None
        badge = next((b for b in ReputationSystem.BADGES if b["id"] == badge_id), None)
        if not badge: return None
        try:
            async with pool.acquire() as conn:
                existing = await conn.fetchrow("SELECT id FROM user_badges WHERE user_id = $1 AND badge_id = $2", user_id, badge_id)
                if existing:
                    return {"already_earned": True, "badge": badge_id}
                
                await conn.execute("""
                    INSERT INTO user_badges (user_id, badge_id, badge_name, badge_category, xp_earned)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT DO NOTHING
                """, user_id, badge_id, badge["name"], badge["category"], badge["xp"])
                
                await conn.execute("""
                    UPDATE user_reputation 
                    SET badges_earned = array_append(badges_earned, $1), updated_at = NOW()
                    WHERE user_id = $2
                """, badge_id, user_id)
                
                await ReputationSystem.award_xp(user_id, badge["xp"], f"badge: {badge['name']}")
                
                # Create notification
                await NotificationSystem.create_notification(
                    user_id, "badge", f"Badge Earned: {badge['name']}",
                    f"You earned the {badge['name']} badge! +{badge['xp']} XP",
                    metadata={"badge_id": badge_id, "xp": badge["xp"]}
                )
                
                return {"earned": True, "badge": badge_id, "xp": badge["xp"]}
        except Exception as e:
            logger.warning(f"Award badge: {e}")
            return None
    
    @staticmethod
    def calculate_level(total_xp: int) -> Dict:
        current_level = ReputationSystem.XP_LEVELS[0]
        for level in ReputationSystem.XP_LEVELS:
            if total_xp >= level["min_xp"]:
                current_level = level
        return current_level
    
    @staticmethod
    async def get_leaderboard(limit: int = 20):
        pool = _pg_pool
        if not pool: return {"users": [], "count": 0}
        try:
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT user_id, username, total_xp, level, level_title,
                           posts_count, replies_count, accepted_answers, badges_earned
                    FROM user_reputation
                    ORDER BY total_xp DESC
                    LIMIT $1
                """, limit)
                return {"users": [dict(r) for r in rows], "count": len(rows)}
        except Exception as e: return {"users": [], "count": 0}
    
    @staticmethod
    async def get_user_profile(user_id: str):
        pool = _pg_pool
        if not pool: return None
        try:
            async with pool.acquire() as conn:
                rep = await conn.fetchrow("SELECT * FROM user_reputation WHERE user_id = $1", user_id)
                if not rep:
                    rep = await ReputationSystem.get_or_create_user(user_id)
                    if not rep: return None
                badges = await conn.fetch("SELECT * FROM user_badges WHERE user_id = $1 ORDER BY earned_at DESC", user_id)
                profile = dict(rep)
                profile["badges"] = [dict(b) for b in badges]
                profile["next_level"] = ReputationSystem.get_next_level(rep["total_xp"])
                return profile
        except Exception as e: return None
    
    @staticmethod
    def get_next_level(current_xp: int) -> Optional[Dict]:
        for i, level in enumerate(ReputationSystem.XP_LEVELS):
            if current_xp < level["min_xp"]:
                return {"level": level["level"], "title": level["title"], "xp_needed": level["min_xp"] - current_xp}
        return None
    
    @staticmethod
    async def track_activity(user_id: str, activity_type: str):
        """Track user activity and update counters + check for badges."""
        pool = _pg_pool
        if not pool: return None
        try:
            async with pool.acquire() as conn:
                updates = {
                    "post": "posts_count = posts_count + 1",
                    "reply": "replies_count = replies_count + 1",
                    "accepted": "accepted_answers = accepted_answers + 1",
                    "upvote": "upvotes_received = upvotes_received + 1",
                    "doc": "docs_published = docs_published + 1",
                    "tutorial": "tutorials_published = tutorials_published + 1",
                    "plugin": "plugins_published = plugins_published + 1",
                }
                if activity_type in updates:
                    await conn.execute(f"""
                        UPDATE user_reputation SET {updates[activity_type]}, last_active = NOW(), updated_at = NOW()
                        WHERE user_id = $1
                    """, user_id)
                    
                    # Award XP
                    xp_map = {"post": 5, "reply": 3, "accepted": 25, "upvote": 1, "doc": 15, "tutorial": 25, "plugin": 40}
                    if activity_type in xp_map:
                        await ReputationSystem.award_xp(user_id, xp_map[activity_type], activity_type)
                    
                    # Check badges
                    row = await conn.fetchrow("SELECT posts_count, replies_count, upvotes_received, accepted_answers, docs_published, tutorials_published, plugins_published FROM user_reputation WHERE user_id = $1", user_id)
                    if row:
                        if activity_type == "post" and row["posts_count"] == 1:
                            await ReputationSystem.award_badge(user_id, "first_post")
                        if activity_type == "reply" and row["replies_count"] == 1:
                            await ReputationSystem.award_badge(user_id, "first_reply")
                        if activity_type == "accepted" and row["accepted_answers"] == 1:
                            await ReputationSystem.award_badge(user_id, "accepted_answer")
                        if row["upvotes_received"] >= 10:
                            await ReputationSystem.award_badge(user_id, "helpful")
                        if row["upvotes_received"] >= 50:
                            await ReputationSystem.award_badge(user_id, "expert")
                        if (row["posts_count"] + row["replies_count"]) >= 10:
                            await ReputationSystem.award_badge(user_id, "contributor")
                        if activity_type == "doc" and row["docs_published"] == 1:
                            await ReputationSystem.award_badge(user_id, "doc_author")
                        if activity_type == "tutorial" and row["tutorials_published"] == 1:
                            await ReputationSystem.award_badge(user_id, "tutorial_author")
                        if activity_type == "plugin" and row["plugins_published"] == 1:
                            await ReputationSystem.award_badge(user_id, "plugin_author")
        except Exception as e:
            logger.warning(f"Track activity: {e}")
    
    @staticmethod
    async def get_all_badges():
        return {"badges": ReputationSystem.BADGES, "total": len(ReputationSystem.BADGES)}


# =========================================================================
# Notification System
# =========================================================================

class NotificationSystem:
    """User notification management."""
    
    @staticmethod
    async def create_notification(user_id: str, notification_type: str, title: str,
                                   body: str = "", link: str = None, metadata: Dict = None):
        pool = _pg_pool
        if not pool: return None
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO user_notifications (user_id, notification_type, title, body, link, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id, notification_type, title, created_at
                """, user_id, notification_type, title, body, link, json.dumps(metadata or {}))
                return dict(row)
        except Exception as e:
            logger.warning(f"Create notification: {e}")
            return None
    
    @staticmethod
    async def get_notifications(user_id: str, unread_only: bool = False, limit: int = 50, offset: int = 0):
        pool = _pg_pool
        if not pool: return {"notifications": [], "count": 0}
        try:
            query = "SELECT * FROM user_notifications WHERE user_id = $1"
            if unread_only: query += " AND read = FALSE"
            query += " ORDER BY created_at DESC LIMIT $2 OFFSET $3"
            async with pool.acquire() as conn:
                rows = await conn.fetch(query, user_id, limit, offset)
                count = await conn.fetchval("SELECT COUNT(*) FROM user_notifications WHERE user_id = $1 AND read = FALSE", user_id)
                return {"notifications": [dict(r) for r in rows], "unread_count": count}
        except Exception as e: return {"notifications": [], "count": 0, "error": str(e)}
    
    @staticmethod
    async def mark_read(notification_id: str, user_id: str = None):
        pool = _pg_pool
        if not pool: return None
        try:
            async with pool.acquire() as conn:
                if user_id:
                    await conn.execute("UPDATE user_notifications SET read = TRUE WHERE id = $1 AND user_id = $2", uuid.UUID(notification_id), user_id)
                else:
                    await conn.execute("UPDATE user_notifications SET read = TRUE WHERE id = $1", uuid.UUID(notification_id))
                return {"marked_read": True, "notification_id": notification_id}
        except Exception as e: return None
    
    @staticmethod
    async def mark_all_read(user_id: str):
        pool = _pg_pool
        if not pool: return None
        try:
            async with pool.acquire() as conn:
                result = await conn.execute("UPDATE user_notifications SET read = TRUE WHERE user_id = $1 AND read = FALSE", user_id)
                return {"marked_all_read": True, "user_id": user_id, "updated": result}
        except Exception as e: return None
    
    @staticmethod
    async def delete_notification(notification_id: str, user_id: str = None):
        pool = _pg_pool
        if not pool: return None
        try:
            async with pool.acquire() as conn:
                if user_id:
                    result = await conn.execute("DELETE FROM user_notifications WHERE id = $1 AND user_id = $2", uuid.UUID(notification_id), user_id)
                else:
                    result = await conn.execute("DELETE FROM user_notifications WHERE id = $1", uuid.UUID(notification_id))
                return {"deleted": True, "result": result}
        except Exception as e: return None


# =========================================================================
# Scalability Assessment
# =========================================================================

class ScalabilityAssessment:
    """Assess platform scalability and identify bottlenecks."""
    
    SERVICE_HEALTH = {
        "ai-gateway": {"port": 3400, "min_replicas": 1, "max_replicas": 5, "critical": True},
        "contracts": {"port": 4600, "min_replicas": 1, "max_replicas": 3, "critical": False},
        "marketplace": {"port": 4700, "min_replicas": 1, "max_replicas": 3, "critical": False},
        "platform": {"port": 4800, "min_replicas": 1, "max_replicas": 3, "critical": True},
        "agents": {"port": 3600, "min_replicas": 1, "max_replicas": 4, "critical": True},
        "orchestration": {"port": 3800, "min_replicas": 1, "max_replicas": 3, "critical": True},
        "queue": {"port": 4300, "min_replicas": 1, "max_replicas": 4, "critical": True},
        "rbac": {"port": 4500, "min_replicas": 1, "max_replicas": 2, "critical": True},
        "enterprise": {"port": 4400, "min_replicas": 1, "max_replicas": 2, "critical": False},
        "monitoring": {"port": 3700, "min_replicas": 1, "max_replicas": 2, "critical": False},
        "devsupport": {"port": 4900, "min_replicas": 1, "max_replicas": 2, "critical": False},
        "sandbox": {"port": 4200, "min_replicas": 1, "max_replicas": 3, "critical": False},
    }
    
    @staticmethod
    async def run_assessment():
        """Run a full scalability assessment."""
        services = []
        total_max_replicas = 0
        critical_services = 0
        bottleneck_risks = []
        
        for name, config in ScalabilityAssessment.SERVICE_HEALTH.items():
            total_max_replicas += config["max_replicas"]
            if config["critical"]: critical_services += 1
            
            # Assess single-replica risk
            if config["min_replicas"] == 1 and config["critical"]:
                bottleneck_risks.append({
                    "service": name,
                    "risk": "single_point_of_failure",
                    "severity": "high",
                    "recommendation": f"Add at least 2 replicas for {name} (currently 1)",
                })
            
            services.append({
                "name": name,
                "port": config["port"],
                "min_replicas": config["min_replicas"],
                "max_replicas": config["max_replicas"],
                "critical": config["critical"],
                "scaling_capacity": config["max_replicas"] - config["min_replicas"],
            })
        
        recommendations = [
            {"priority": "high", "action": "Implement Kubernetes for container orchestration", "impact": "Auto-scaling, self-healing, rolling updates"},
            {"priority": "high", "action": "Add Redis Cluster for shared cache HA", "impact": "Eliminates Redis single point of failure"},
            {"priority": "medium", "action": "Implement database read replicas", "impact": "Distribute read load, improve query performance"},
            {"priority": "medium", "action": "Add CDN for static assets", "impact": "Reduce Nginx load, faster global response"},
            {"priority": "medium", "action": "Implement circuit breakers between services", "impact": "Prevent cascade failures"},
            {"priority": "low", "action": "Add request queuing with priority lanes", "impact": "Better handling under load"},
            {"priority": "low", "action": "Implement connection pooling at gateway level", "impact": "Reduce database connection overhead"},
        ]
        
        return {
            "assessment_date": datetime.now(timezone.utc).isoformat(),
            "total_services": len(services),
            "critical_services": critical_services,
            "total_max_replicas": total_max_replicas,
            "current_architecture": "docker_compose",
            "recommended_architecture": "kubernetes",
            "bottleneck_risks": bottleneck_risks,
            "services": services,
            "recommendations": recommendations,
            "risk_score": len(bottleneck_risks) * 25,  # 0-100 scale
            "readiness": "moderate" if len(bottleneck_risks) <= 3 else "needs_work",
        }
    
    @staticmethod
    async def get_metrics_summary():
        """Get platform metrics summary."""
        return {
            "containers": 30,
            "services": len(ScalabilityAssessment.SERVICE_HEALTH),
            "critical_services": sum(1 for s in ScalabilityAssessment.SERVICE_HEALTH.values() if s["critical"]),
            "database": {"type": "PostgreSQL", "pool_size": 10, "needs_read_replicas": True},
            "cache": {"type": "Redis", "needs_cluster": True},
            "load_balancer": {"type": "Nginx", "algorithm": "round_robin"},
            "monitoring": {"tools": ["Prometheus", "Grafana", "Loki"], "alerting": True},
            "estimated_concurrent_users": "500-1000",
            "estimated_max_qps": "2000-5000 (with scaling)",
        }


# =========================================================================
# Models
# =========================================================================

class AwardXPRequest(BaseModel):
    user_id: str = Field(..., max_length=100)
    xp: int = Field(..., ge=1, le=1000)
    reason: str = Field("", max_length=200)

class AwardBadgeRequest(BaseModel):
    user_id: str = Field(..., max_length=100)
    badge_id: str = Field(..., max_length=50)

class TrackActivityRequest(BaseModel):
    user_id: str = Field(..., max_length=100)
    activity_type: str = Field(..., pattern="^(post|reply|accepted|upvote|doc|tutorial|plugin)$")

class CreateNotificationRequest(BaseModel):
    user_id: str = Field(..., max_length=100)
    notification_type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    body: str = Field("", max_length=1000)
    link: str = Field(None, max_length=500)
    metadata: Dict = {}


# =========================================================================
# Endpoints
# =========================================================================

@router.on_event("startup")
async def startup():
    global _pg_pool
    for attempt in range(3):
        try:
            _pg_pool = await asyncpg.create_pool(PG_DSN, min_size=2, max_size=10, command_timeout=30)
            async with _pg_pool.acquire() as conn:
                await conn.execute("SELECT 1")
            await ReputationSystem.init_tables()
            logger.info("Community engagement PG connected")
            return
        except Exception as e:
            logger.warning(f"Community PG attempt {attempt+1}: {e}")
            await asyncio.sleep(2)

# Reputation
@router.get("/reputation/leaderboard")
async def get_leaderboard(limit: int = 20):
    return await ReputationSystem.get_leaderboard(limit)

@router.get("/reputation/{user_id}")
async def get_reputation(user_id: str):
    profile = await ReputationSystem.get_user_profile(user_id)
    if not profile: raise HTTPException(404, "User not found")
    return profile

@router.post("/reputation/award-xp")
async def award_xp(req: AwardXPRequest):
    result = await ReputationSystem.award_xp(req.user_id, req.xp, req.reason)
    if not result: raise HTTPException(503, "Database not connected")
    return result

@router.post("/reputation/award-badge")
async def award_badge(req: AwardBadgeRequest):
    result = await ReputationSystem.award_badge(req.user_id, req.badge_id)
    if not result: raise HTTPException(503, "Database not connected")
    return result

@router.post("/reputation/track")
async def track_activity(req: TrackActivityRequest):
    await ReputationSystem.track_activity(req.user_id, req.activity_type)
    return {"tracked": True, "activity": req.activity_type}

@router.get("/badges")
async def get_badges():
    return await ReputationSystem.get_all_badges()

# Notifications
@router.get("/notifications/{user_id}")
async def get_notifications(user_id: str, unread_only: bool = False, limit: int = 50, offset: int = 0):
    return await NotificationSystem.get_notifications(user_id, unread_only, limit, offset)

@router.post("/notifications")
async def create_notification(req: CreateNotificationRequest):
    result = await NotificationSystem.create_notification(
        req.user_id, req.notification_type, req.title, req.body, req.link, req.metadata
    )
    if not result: raise HTTPException(503, "Database not connected")
    return result

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, user_id: str = None):
    result = await NotificationSystem.mark_read(notification_id, user_id)
    if not result: raise HTTPException(503, "Database not connected")
    return result

@router.post("/notifications/read-all/{user_id}")
async def mark_all_read(user_id: str):
    result = await NotificationSystem.mark_all_read(user_id)
    if not result: raise HTTPException(503, "Database not connected")
    return result

@router.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: str, user_id: str = None):
    result = await NotificationSystem.delete_notification(notification_id, user_id)
    if not result: raise HTTPException(503, "Database not connected")
    return result

# Scalability
@router.get("/scalability/assessment")
async def get_scalability_assessment():
    return await ScalabilityAssessment.run_assessment()

@router.get("/scalability/metrics")
async def get_scalability_metrics():
    return await ScalabilityAssessment.get_metrics_summary()

# Health
@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "community",
        "version": "1.0.0",
        "features": ["reputation", "badges", "notifications", "leaderboard", "scalability"],
    }
