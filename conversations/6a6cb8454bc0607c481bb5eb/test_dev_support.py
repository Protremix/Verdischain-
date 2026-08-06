"""Tests for EvolvixOS Developer Support System v1.0"""

import pytest
import os
import sys
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from dev_support import router, DocumentationManager, CreateDocRequest, CreateTutorialRequest, CreatePostRequest, CreateReplyRequest, VoteRequest

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestDocumentationManager:
    def test_doc_categories(self):
        assert "getting-started" in DocumentationManager.DOC_CATEGORIES
        assert "sdk" in DocumentationManager.DOC_CATEGORIES
        assert "faq" in DocumentationManager.DOC_CATEGORIES


class TestModels:
    def test_create_doc_request(self):
        req = CreateDocRequest(title="Test", slug="test", content="Content here")
        assert req.title == "Test"
        assert req.category == "guides"
    
    def test_create_tutorial_request(self):
        req = CreateTutorialRequest(title="Test", slug="test", description="desc")
        assert req.difficulty == "beginner"
        assert req.duration_minutes == 10
    
    def test_create_tutorial_request_invalid_difficulty(self):
        with pytest.raises(Exception):
            CreateTutorialRequest(title="T", slug="t", difficulty="expert")
    
    def test_create_post_request(self):
        req = CreatePostRequest(title="Question", body="How do I?", author_id="user-1")
        assert req.title == "Question"
    
    def test_create_reply_request(self):
        req = CreateReplyRequest(post_id="00000000-0000-0000-0000-000000000000", body="Answer", author_id="user-1")
        assert req.body == "Answer"
    
    def test_vote_request(self):
        req = VoteRequest(direction="up")
        assert req.direction == "up"
    
    def test_vote_request_invalid(self):
        with pytest.raises(Exception):
            VoteRequest(direction="sideways")


class TestDocsEndpoints:
    def test_list_docs_no_pg(self):
        with patch('dev_support._pg_pool', None):
            resp = client.get("/api/v1/dev-support/docs")
            assert resp.status_code == 200
            assert resp.json()["count"] == 0
    
    def test_get_doc_no_pg(self):
        with patch('dev_support._pg_pool', None):
            resp = client.get("/api/v1/dev-support/docs/getting-started")
            assert resp.status_code == 503
    
    def test_create_doc_no_pg(self):
        with patch('dev_support._pg_pool', None):
            resp = client.post("/api/v1/dev-support/docs", json={
                "title": "Test", "slug": "test-doc", "content": "Content"
            })
            assert resp.status_code == 503
    
    def test_mark_helpful_no_pg(self):
        with patch('dev_support._pg_pool', None):
            resp = client.get("/api/v1/dev-support/docs/test/helpful")
            assert resp.status_code == 503


class TestTutorialsEndpoints:
    def test_list_tutorials_no_pg(self):
        with patch('dev_support._pg_pool', None):
            resp = client.get("/api/v1/dev-support/tutorials")
            assert resp.status_code == 200
            assert resp.json()["count"] == 0
    
    def test_get_tutorial_no_pg(self):
        with patch('dev_support._pg_pool', None):
            resp = client.get("/api/v1/dev-support/tutorials/test")
            assert resp.status_code == 503
    
    def test_create_tutorial_no_pg(self):
        with patch('dev_support._pg_pool', None):
            resp = client.post("/api/v1/dev-support/tutorials", json={
                "title": "Test", "slug": "test-tut"
            })
            assert resp.status_code == 503
    
    def test_complete_tutorial_no_pg(self):
        with patch('dev_support._pg_pool', None):
            resp = client.post("/api/v1/dev-support/tutorials/test/complete")
            assert resp.status_code == 503


class TestCommunityEndpoints:
    def test_list_posts_no_pg(self):
        with patch('dev_support._pg_pool', None):
            resp = client.get("/api/v1/dev-support/community/posts")
            assert resp.status_code == 200
            assert resp.json()["count"] == 0
    
    def test_get_post_no_pg(self):
        with patch('dev_support._pg_pool', None):
            resp = client.get("/api/v1/dev-support/community/posts/00000000-0000-0000-0000-000000000000")
            assert resp.status_code == 503
    
    def test_create_post_no_pg(self):
        with patch('dev_support._pg_pool', None):
            resp = client.post("/api/v1/dev-support/community/posts", json={
                "title": "Test Post", "body": "Content", "author_id": "user-1"
            })
            assert resp.status_code == 503
    
    def test_create_reply_no_pg(self):
        with patch('dev_support._pg_pool', None):
            resp = client.post("/api/v1/dev-support/community/replies", json={
                "post_id": "00000000-0000-0000-0000-000000000000",
                "body": "Reply", "author_id": "user-1"
            })
            assert resp.status_code == 503
    
    def test_vote_post_no_pg(self):
        with patch('dev_support._pg_pool', None):
            resp = client.post("/api/v1/dev-support/community/posts/00000000-0000-0000-0000-000000000000/vote", json={
                "direction": "up"
            })
            assert resp.status_code == 503
    
    def test_accept_reply_no_pg(self):
        with patch('dev_support._pg_pool', None):
            resp = client.post("/api/v1/dev-support/community/replies/00000000-0000-0000-0000-000000000000/accept")
            assert resp.status_code == 503


class TestResourcesAndHealth:
    def test_resources(self):
        resp = client.get("/api/v1/dev-support/resources")
        assert resp.status_code == 200
        data = resp.json()
        assert "documentation" in data
        assert "tutorials" in data
        assert "community" in data
        assert "cli" in data
        assert "sdk" in data
        assert "links" in data
    
    def test_health(self):
        resp = client.get("/api/v1/dev-support/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "dev-support"
        assert data["version"] == "1.0.0"
        assert "docs" in data["features"]
        assert "tutorials" in data["features"]
        assert "community" in data["features"]
