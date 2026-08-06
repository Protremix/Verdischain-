"""
EvolvixOS Load Testing & Security Audit API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import asyncio
import structlog

from load_test import LoadTester, SecurityAuditor

logger = structlog.get_logger()

app = FastAPI(
    title="EvolvixOS Load Testing & Security Audit",
    description="Automated load testing and security auditing",
    version="1.0.0",
)

tester = LoadTester()
auditor = SecurityAuditor()


class LoadTestRequest(BaseModel):
    target_url: str
    method: str = "GET"
    payload: Optional[Dict] = None
    num_requests: int = 100
    concurrent: int = 10
    timeout: int = 30


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.post("/load-test")
async def run_load_test(req: LoadTestRequest):
    """Run a custom load test"""
    result = await tester.run_test(
        name="Custom Load Test",
        target_url=req.target_url,
        method=req.method,
        payload=req.payload,
        num_requests=req.num_requests,
        concurrent=req.concurrent,
        timeout=req.timeout,
    )
    return result.to_dict()

@app.get("/load-test/suite")
async def run_full_suite():
    """Run the full load test suite"""
    result = await tester.run_full_suite()
    return result

@app.get("/load-test/gateway-health")
async def load_test_gateway_health(num_requests: int = 100, concurrent: int = 10):
    """Quick load test on gateway health endpoint"""
    result = await tester.run_gateway_health_test(num_requests, concurrent)
    return result.to_dict()

@app.get("/load-test/agent-health")
async def load_test_agent_health(num_requests: int = 100, concurrent: int = 10):
    """Quick load test on agent framework health"""
    result = await tester.run_agent_health_test(num_requests, concurrent)
    return result.to_dict()

@app.get("/load-test/blockchain-health")
async def load_test_blockchain_health(num_requests: int = 100, concurrent: int = 10):
    """Quick load test on blockchain health"""
    result = await tester.run_blockchain_health_test(num_requests, concurrent)
    return result.to_dict()

@app.get("/load-test/orchestration-health")
async def load_test_orchestration_health(num_requests: int = 100, concurrent: int = 10):
    """Quick load test on orchestration health"""
    result = await tester.run_orchestration_health_test(num_requests, concurrent)
    return result.to_dict()

@app.get("/security-audit")
async def run_security_audit():
    """Run full security audit"""
    result = await auditor.audit_all()
    return result

@app.get("/security-audit/score")
async def security_score():
    """Get just the security score"""
    audit = await auditor.audit_all()
    return {
        "score": audit["score"],
        "grade": audit["grade"],
        "passed": audit["passed"],
        "failed": audit["failed"],
        "critical": audit["critical"],
        "high": audit["high"],
        "medium": audit["medium"],
        "low": audit["low"],
    }
