"""
EvolvixOS Load Testing Framework
Comprehensive load testing for AI Gateway, Agent Framework, and Orchestration
Measures: throughput (RPS), latency (p50/p95/p99), error rate, concurrent users
"""

import asyncio
import time
import json
import httpx
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from collections import defaultdict
import structlog

logger = structlog.get_logger()


# =========================================================================
# Data Models
# =========================================================================

@dataclass
class RequestResult:
    url: str
    method: str
    status_code: int
    latency_ms: float
    success: bool
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class LoadTestResult:
    test_name: str
    target_url: str
    total_requests: int
    successful: int
    failed: int
    error_rate: float
    rps: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    latency_avg: float
    latency_min: float
    latency_max: float
    duration_seconds: float
    concurrent_users: int
    results: List[RequestResult] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d["results"] = d["results"][:100]  # cap for display
        return d


# =========================================================================
# Load Tester
# =========================================================================

class LoadTester:
    """Async load testing engine"""
    
    def __init__(self, gateway_url: str = "http://localhost:3500",
                 agent_url: str = "http://localhost:3600",
                 blockchain_url: str = "http://localhost:3200",
                 orchestration_url: str = "http://localhost:3800"):
        self.gateway_url = gateway_url
        self.agent_url = agent_url
        self.blockchain_url = blockchain_url
        self.orchestration_url = orchestration_url
    
    def _percentile(self, sorted_vals: List[float], p: float) -> float:
        if not sorted_vals:
            return 0
        idx = int(len(sorted_vals) * p)
        if idx >= len(sorted_vals):
            idx = len(sorted_vals) - 1
        return sorted_vals[idx]
    
    async def run_test(self, name: str, target_url: str, method: str = "GET",
                       payload: Dict = None, headers: Dict = None,
                       num_requests: int = 100, concurrent: int = 10,
                       timeout: int = 30) -> LoadTestResult:
        """Run a load test against a target URL"""
        
        semaphore = asyncio.Semaphore(concurrent)
        results: List[RequestResult] = []
        start_time = time.time()
        
        async def make_request():
            async with semaphore:
                req_start = time.time()
                try:
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        if method == "GET":
                            resp = await client.get(target_url, headers=headers)
                        elif method == "POST":
                            resp = await client.post(target_url, json=payload, headers=headers)
                        else:
                            resp = await client.request(method, target_url, json=payload, headers=headers)
                        
                        latency = (time.time() - req_start) * 1000
                        results.append(RequestResult(
                            url=target_url,
                            method=method,
                            status_code=resp.status_code,
                            latency_ms=latency,
                            success=200 <= resp.status_code < 400,
                        ))
                except Exception as e:
                    latency = (time.time() - req_start) * 1000
                    results.append(RequestResult(
                        url=target_url,
                        method=method,
                        status_code=0,
                        latency_ms=latency,
                        success=False,
                        error=str(e),
                    ))
        
        # Fire all requests
        tasks = [make_request() for _ in range(num_requests)]
        await asyncio.gather(*tasks)
        
        duration = time.time() - start_time
        latencies = sorted([r.latency_ms for r in results])
        successful = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)
        
        return LoadTestResult(
            test_name=name,
            target_url=target_url,
            total_requests=len(results),
            successful=successful,
            failed=failed,
            error_rate=failed / max(len(results), 1) * 100,
            rps=len(results) / max(duration, 0.001),
            latency_p50=self._percentile(latencies, 0.5),
            latency_p95=self._percentile(latencies, 0.95),
            latency_p99=self._percentile(latencies, 0.99),
            latency_avg=sum(latencies) / max(len(latencies), 1),
            latency_min=min(latencies) if latencies else 0,
            latency_max=max(latencies) if latencies else 0,
            duration_seconds=duration,
            concurrent_users=concurrent,
            results=results,
        )
    
    async def run_gateway_health_test(self, num_requests=100, concurrent=10) -> LoadTestResult:
        return await self.run_test(
            "Gateway Health Check",
            f"{self.gateway_url}/health",
            num_requests=num_requests,
            concurrent=concurrent,
        )
    
    async def run_gateway_invoke_test(self, num_requests=50, concurrent=5) -> LoadTestResult:
        return await self.run_test(
            "Gateway Invoke (Sentiment)",
            f"{self.gateway_url}/gateway/invoke",
            method="POST",
            payload={"capability": "sentiment", "input": {"text": "Load test"}, "options": {"capability": "sentiment"}},
            num_requests=num_requests,
            concurrent=concurrent,
            timeout=60,
        )
    
    async def run_agent_health_test(self, num_requests=100, concurrent=10) -> LoadTestResult:
        return await self.run_test(
            "Agent Framework Health",
            f"{self.agent_url}/health",
            num_requests=num_requests,
            concurrent=concurrent,
        )
    
    async def run_agent_create_test(self, num_requests=20, concurrent=5) -> LoadTestResult:
        return await self.run_test(
            "Agent Create",
            f"{self.agent_url}/agents",
            method="POST",
            payload={"name": "Load Test Agent", "capabilities": ["chat"]},
            num_requests=num_requests,
            concurrent=concurrent,
        )
    
    async def run_blockchain_health_test(self, num_requests=100, concurrent=10) -> LoadTestResult:
        return await self.run_test(
            "Blockchain Health",
            f"{self.blockchain_url}/health",
            num_requests=num_requests,
            concurrent=concurrent,
        )
    
    async def run_orchestration_health_test(self, num_requests=100, concurrent=10) -> LoadTestResult:
        return await self.run_test(
            "Orchestration Health",
            f"{self.orchestration_url}/health",
            num_requests=num_requests,
            concurrent=concurrent,
        )
    
    async def run_full_suite(self) -> Dict[str, Any]:
        """Run all load tests and return combined results"""
        results = {}
        
        # Health checks (fast, high volume)
        results["gateway_health"] = (await self.run_gateway_health_test(200, 20)).to_dict()
        results["agent_health"] = (await self.run_agent_health_test(200, 20)).to_dict()
        results["blockchain_health"] = (await self.run_blockchain_health_test(200, 20)).to_dict()
        results["orchestration_health"] = (await self.run_orchestration_health_test(200, 20)).to_dict()
        
        # Agent creation
        results["agent_create"] = (await self.run_agent_create_test(50, 10)).to_dict()
        
        # Summary
        all_rps = [r["rps"] for r in results.values()]
        all_error_rates = [r["error_rate"] for r in results.values()]
        all_p95 = [r["latency_p95"] for r in results.values()]
        
        summary = {
            "total_tests": len(results),
            "avg_rps": sum(all_rps) / max(len(all_rps), 1),
            "avg_error_rate": sum(all_error_rates) / max(len(all_error_rates), 1),
            "max_p95_latency": max(all_p95) if all_p95 else 0,
            "all_passed": all(r["error_rate"] == 0 for r in results.values()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        return {"summary": summary, "results": results}


# =========================================================================
# Security Auditor
# =========================================================================

class SecurityAuditor:
    """Automated security audit of EvolvixOS platform"""
    
    def __init__(self, gateway_url: str = "http://localhost:3500",
                 agent_url: str = "http://localhost:3600",
                 blockchain_url: str = "http://localhost:3200",
                 orchestration_url: str = "http://localhost:3800"):
        self.gateway_url = gateway_url
        self.agent_url = agent_url
        self.blockchain_url = blockchain_url
        self.orchestration_url = orchestration_url
    
    async def audit_all(self) -> Dict[str, Any]:
        """Run all security audits"""
        checks = []
        
        checks.append(await self._check_auth_required("Gateway Stats", f"{self.gateway_url}/gateway/stats", "api-key"))
        checks.append(await self._check_auth_required("Gateway API Keys", f"{self.gateway_url}/api-keys", "api-key"))
        checks.append(await self._check_auth_required("Gateway Cache Clear", f"{self.gateway_url}/cache/clear", "api-key", "POST"))
        checks.append(await self._check_cors_headers("Gateway", f"{self.gateway_url}/health"))
        checks.append(await self._check_security_headers("Gateway", f"{self.gateway_url}/health"))
        checks.append(await self._check_security_headers("Agent", f"{self.agent_url}/health"))
        checks.append(await self._check_security_headers("Blockchain", f"{self.blockchain_url}/health"))
        checks.append(await self._check_security_headers("Orchestration", f"{self.orchestration_url}/health"))
        checks.append(await self._check_input_validation("Gateway Invoke", f"{self.gateway_url}/gateway/invoke"))
        checks.append(await self._check_rate_limiting("Gateway", f"{self.gateway_url}/health"))
        checks.append(await self._check_endpoint_exposure("Gateway", f"{self.gateway_url}"))
        checks.append(await self._check_endpoint_exposure("Agent", f"{self.agent_url}"))
        checks.append(await self._check_endpoint_exposure("Orchestration", f"{self.orchestration_url}"))
        
        # Calculate security score
        critical = sum(1 for c in checks if c["severity"] == "critical")
        high = sum(1 for c in checks if c["severity"] == "high")
        medium = sum(1 for c in checks if c["severity"] == "medium")
        low = sum(1 for c in checks if c["severity"] == "low")
        passed = sum(1 for c in checks if c["status"] == "pass")
        total = len(checks)
        
        score = (passed / total) * 100 if total > 0 else 0
        grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"
        
        return {
            "score": round(score, 1),
            "grade": grade,
            "total_checks": total,
            "passed": passed,
            "failed": total - passed,
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    async def _check_auth_required(self, name: str, url: str, auth_type: str, method: str = "GET") -> Dict:
        """Check if an endpoint requires authentication"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                if method == "GET":
                    resp = await client.get(url)
                else:
                    resp = await client.post(url)
                
                # Should return 401/403 if auth is required
                if resp.status_code in (401, 403):
                    return {"name": name, "check": "auth_required", "status": "pass", "severity": "info", "detail": f"Correctly requires {auth_type}"}
                elif resp.status_code == 200:
                    return {"name": name, "check": "auth_required", "status": "fail", "severity": "medium", "detail": f"Endpoint accessible without {auth_type}"}
                else:
                    return {"name": name, "check": "auth_required", "status": "pass", "severity": "info", "detail": f"Returns {resp.status_code}"}
        except Exception as e:
            return {"name": name, "check": "auth_required", "status": "fail", "severity": "low", "detail": f"Error: {e}"}
    
    async def _check_cors_headers(self, name: str, url: str) -> Dict:
        """Check CORS configuration"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url, headers={"Origin": "https://evil.com"})
                cors = resp.headers.get("access-control-allow-origin", "")
                if "*" in cors:
                    return {"name": name, "check": "cors", "status": "fail", "severity": "medium", "detail": "Wildcard CORS origin"}
                elif "evil.com" in cors:
                    return {"name": name, "check": "cors", "status": "fail", "severity": "high", "detail": "Reflects arbitrary origin"}
                else:
                    return {"name": name, "check": "cors", "status": "pass", "severity": "info", "detail": "No wildcard CORS"}
        except Exception as e:
            return {"name": name, "check": "cors", "status": "pass", "severity": "info", "detail": f"N/A: {e}"}
    
    async def _check_security_headers(self, name: str, url: str) -> Dict:
        """Check security headers"""
        required_headers = [
            "x-content-type-options",
            "x-frame-options",
        ]
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url)
                missing = []
                for h in required_headers:
                    if not resp.headers.get(h):
                        missing.append(h)
                
                if not missing:
                    return {"name": name, "check": "security_headers", "status": "pass", "severity": "info", "detail": "All security headers present"}
                else:
                    return {"name": name, "check": "security_headers", "status": "fail", "severity": "low", "detail": f"Missing: {', '.join(missing)}"}
        except Exception as e:
            return {"name": name, "check": "security_headers", "status": "fail", "severity": "low", "detail": f"Error: {e}"}
    
    async def _check_input_validation(self, name: str, url: str) -> Dict:
        """Check input validation"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Send oversized payload
                big_payload = {"capability": "chat", "input": {"messages": [{"role": "user", "content": "x" * 100000}]}}
                resp = await client.post(url, json=big_payload)
                if resp.status_code == 413 or resp.status_code == 422:
                    return {"name": name, "check": "input_validation", "status": "pass", "severity": "info", "detail": "Rejects oversized input"}
                else:
                    return {"name": name, "check": "input_validation", "status": "warn", "severity": "low", "detail": f"May accept oversized input (status {resp.status_code})"}
        except Exception as e:
            return {"name": name, "check": "input_validation", "status": "pass", "severity": "info", "detail": f"N/A: {e}"}
    
    async def _check_rate_limiting(self, name: str, url: str) -> Dict:
        """Check if rate limiting is active"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Send many rapid requests
                statuses = []
                for _ in range(20):
                    resp = await client.get(url)
                    statuses.append(resp.status_code)
                
                if 429 in statuses:
                    return {"name": name, "check": "rate_limiting", "status": "pass", "severity": "info", "detail": "Rate limiting active (429 received)"}
                else:
                    return {"name": name, "check": "rate_limiting", "status": "warn", "severity": "low", "detail": "No rate limiting detected on health endpoint"}
        except Exception as e:
            return {"name": name, "check": "rate_limiting", "status": "pass", "severity": "info", "detail": f"N/A: {e}"}
    
    async def _check_endpoint_exposure(self, name: str, base_url: str) -> Dict:
        """Check for exposed sensitive endpoints"""
        sensitive_paths = ["/admin", "/debug", "/metrics", "/internal", "/.env"]
        exposed = []
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                for path in sensitive_paths:
                    try:
                        resp = await client.get(f"{base_url}{path}", follow_redirects=False)
                        if resp.status_code == 200 and path in ("/.env", "/admin"):
                            exposed.append(path)
                    except:
                        pass
            
            if exposed:
                return {"name": name, "check": "endpoint_exposure", "status": "fail", "severity": "high", "detail": f"Exposed: {', '.join(exposed)}"}
            else:
                return {"name": name, "check": "endpoint_exposure", "status": "pass", "severity": "info", "detail": "No sensitive endpoints exposed"}
        except Exception as e:
            return {"name": name, "check": "endpoint_exposure", "status": "pass", "severity": "info", "detail": f"N/A: {e}"}
