"""Tests for EvolvixOS Community Engagement + Scalability v1.0"""

import pytest
import os
import sys
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from community_engagement import router, ReputationSystem, NotificationSystem, ScalabilityAssessment, \
    AwardXPRequest, AwardBadgeRequest, TrackActivityRequest, CreateNotificationRequest

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestReputationSystem:
    def test_badges_defined(self):
        assert len(ReputationSystem.BADGES) >= 10
    
    def test_badge_has_required_fields(self):
        for badge in ReputationSystem.BADGES:
            assert "id" in badge
            assert "name" in badge
            assert "xp" in badge
            assert "category" in badge
    
    def test_xp_levels_defined(self):
        assert len(ReputationSystem.XP_LEVELS) >= 10
    
    def test_calculate_level_newcomer(self):
        level = ReputationSystem.calculate_level(0)
        assert level["level"] == 1
        assert level["title"] == "Newcomer"
    
    def test_calculate_level_visionary(self):
        level = ReputationSystem.calculate_level(3000)
        assert level["level"] == 10
        assert level["title"] == "Visionary"
    
    def test_calculate_level_intermediate(self):
        level = ReputationSystem.calculate_level(150)
        assert level["level"] == 4
        assert level["title"] == "Regular"
    
    def test_get_next_level(self):
        next_level = ReputationSystem.get_next_level(0)
        assert next_level is not None
        assert next_level["level"] == 2
    
    def test_get_next_level_max(self):
        next_level = ReputationSystem.get_next_level(5000)
        assert next_level is None
    
    @pytest.mark.asyncio
    async def test_get_or_create_user_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            result = await ReputationSystem.get_or_create_user("user-1")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_award_xp_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            result = await ReputationSystem.award_xp("user-1", 10)
            assert result is None
    
    @pytest.mark.asyncio
    async def test_award_badge_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            result = await ReputationSystem.award_badge("user-1", "first_post")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_leaderboard_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            result = await ReputationSystem.get_leaderboard()
            assert result["count"] == 0
    
    @pytest.mark.asyncio
    async def test_track_activity_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            result = await ReputationSystem.track_activity("user-1", "post")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_all_badges(self):
        result = await ReputationSystem.get_all_badges()
        assert result["total"] >= 10
        assert "badges" in result


class TestNotificationSystem:
    @pytest.mark.asyncio
    async def test_create_notification_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            result = await NotificationSystem.create_notification("user-1", "test", "Test")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_notifications_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            result = await NotificationSystem.get_notifications("user-1")
            assert result["count"] == 0
    
    @pytest.mark.asyncio
    async def test_mark_read_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            result = await NotificationSystem.mark_read("00000000-0000-0000-0000-000000000000")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_mark_all_read_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            result = await NotificationSystem.mark_all_read("user-1")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_notification_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            result = await NotificationSystem.delete_notification("00000000-0000-0000-0000-000000000000")
            assert result is None


class TestScalabilityAssessment:
    @pytest.mark.asyncio
    async def test_run_assessment(self):
        result = await ScalabilityAssessment.run_assessment()
        assert "services" in result
        assert "recommendations" in result
        assert "bottleneck_risks" in result
        assert result["total_services"] > 0
    
    @pytest.mark.asyncio
    async def test_get_metrics_summary(self):
        result = await ScalabilityAssessment.get_metrics_summary()
        assert result["containers"] > 0
        assert "database" in result
        assert "cache" in result
    
    def test_service_health_defined(self):
        assert "ai-gateway" in ScalabilityAssessment.SERVICE_HEALTH
        assert "marketplace" in ScalabilityAssessment.SERVICE_HEALTH


class TestModels:
    def test_award_xp_request(self):
        req = AwardXPRequest(user_id="user-1", xp=10, reason="test")
        assert req.xp == 10
    
    def test_award_xp_request_negative(self):
        with pytest.raises(Exception):
            AwardXPRequest(user_id="user-1", xp=-1)
    
    def test_award_xp_request_too_much(self):
        with pytest.raises(Exception):
            AwardXPRequest(user_id="user-1", xp=1001)
    
    def test_award_badge_request(self):
        req = AwardBadgeRequest(user_id="user-1", badge_id="first_post")
        assert req.badge_id == "first_post"
    
    def test_track_activity_request(self):
        req = TrackActivityRequest(user_id="user-1", activity_type="post")
        assert req.activity_type == "post"
    
    def test_track_activity_request_invalid(self):
        with pytest.raises(Exception):
            TrackActivityRequest(user_id="user-1", activity_type="invalid")
    
    def test_create_notification_request(self):
        req = CreateNotificationRequest(user_id="user-1", notification_type="test", title="Test")
        assert req.title == "Test"


class TestEndpoints:
    def test_health(self):
        resp = client.get("/api/v1/community/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "community"
        assert data["version"] == "1.0.0"
    
    def test_get_badges(self):
        resp = client.get("/api/v1/community/badges")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 10
        assert len(data["badges"]) >= 10
    
    def test_get_reputation_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            resp = client.get("/api/v1/community/reputation/user-1")
            assert resp.status_code == 404
    
    def test_award_xp_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            resp = client.post("/api/v1/community/reputation/award-xp", json={
                "user_id": "user-1", "xp": 10
            })
            assert resp.status_code == 503
    
    def test_award_badge_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            resp = client.post("/api/v1/community/reputation/award-badge", json={
                "user_id": "user-1", "badge_id": "first_post"
            })
            assert resp.status_code == 503
    
    def test_track_activity_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            resp = client.post("/api/v1/community/reputation/track", json={
                "user_id": "user-1", "activity_type": "post"
            })
            assert resp.status_code == 200
    
    def test_leaderboard_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            resp = client.get("/api/v1/community/reputation/leaderboard")
            assert resp.status_code == 200
            data = resp.json()
            assert data["count"] == 0 or "users" in data
    
    def test_get_notifications_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            resp = client.get("/api/v1/community/notifications/user-1")
            assert resp.status_code == 200
            assert "notifications" in resp.json()
    
    def test_create_notification_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            resp = client.post("/api/v1/community/notifications", json={
                "user_id": "user-1", "notification_type": "test", "title": "Test"
            })
            assert resp.status_code == 503
    
    def test_mark_read_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            resp = client.post("/api/v1/community/notifications/00000000-0000-0000-0000-000000000000/read")
            assert resp.status_code == 503
    
    def test_mark_all_read_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            resp = client.post("/api/v1/community/notifications/read-all/user-1")
            assert resp.status_code == 503
    
    def test_delete_notification_no_pg(self):
        with patch('community_engagement._pg_pool', None):
            resp = client.delete("/api/v1/community/notifications/00000000-0000-0000-0000-000000000000")
            assert resp.status_code == 503
    
    def test_scalability_assessment(self):
        resp = client.get("/api/v1/community/scalability/assessment")
        assert resp.status_code == 200
        data = resp.json()
        assert "services" in data
        assert "recommendations" in data
        assert "bottleneck_risks" in data
    
    def test_scalability_metrics(self):
        resp = client.get("/api/v1/community/scalability/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert "containers" in data
        assert "database" in data
