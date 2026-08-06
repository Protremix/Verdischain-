"""
EvolvixOS Monitoring & Documentation Server
Combines Prometheus metrics export, documentation API, and health monitoring
"""

from fastapi import FastAPI, Response, HTTPException, Query
from fastapi.responses import PlainTextResponse
from datetime import datetime, timezone
import structlog

from monitoring_metrics import metrics, updater
from documentation_api import (
    ARCHITECTURE_OVERVIEW, API_REFERENCE, DEVELOPER_GUIDES, FAQS, RUNBOOKS
)

logger = structlog.get_logger()

app = FastAPI(
    title="EvolvixOS Monitoring & Documentation",
    description="Prometheus metrics, API documentation, developer guides, and runbooks",
    version="1.0.0",
)

# =========================================================================
# Metrics Endpoints
# =========================================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "updater_running": updater._running,
    }

@app.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=metrics.export_prometheus(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )

@app.get("/metrics/json")
async def metrics_json():
    """Metrics as JSON (for dashboards)"""
    return metrics.get_stats()

@app.post("/metrics/increment/{name}")
async def increment_metric(name: str, value: float = 1):
    """Manually increment a counter"""
    metrics.increment(name, value)
    return {"success": True, "name": name, "value": value}

@app.post("/metrics/gauge/{name}")
async def set_gauge(name: str, value: float):
    """Manually set a gauge"""
    metrics.set_gauge(name, value)
    return {"success": True, "name": name, "value": value}

@app.post("/metrics/observe/{name}")
async def observe_metric(name: str, value: float):
    """Observe a histogram value"""
    metrics.observe(name, value)
    return {"success": True, "name": name, "value": value}

@app.on_event("startup")
async def startup_event():
    """Start the metrics updater on startup"""
    updater.start()
    logger.info("Monitoring server started with metrics updater")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the metrics updater on shutdown"""
    updater.stop()
    logger.info("Monitoring server stopped")

# =========================================================================
# Documentation Endpoints
# =========================================================================

@app.get("/architecture")
async def get_architecture():
    return ARCHITECTURE_OVERVIEW

@app.get("/api-reference")
async def get_api_reference(service: str = None):
    if service:
        if service in API_REFERENCE:
            return API_REFERENCE[service]
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    return API_REFERENCE

@app.get("/guides")
async def list_guides():
    return {"guides": DEVELOPER_GUIDES, "count": len(DEVELOPER_GUIDES)}

@app.get("/guides/{guide_id}")
async def get_guide(guide_id: str):
    for guide in DEVELOPER_GUIDES:
        if guide["id"] == guide_id:
            return guide
    raise HTTPException(status_code=404, detail="Guide not found")

@app.get("/faq")
async def list_faqs():
    return {"faqs": FAQS, "count": len(FAQS)}

@app.get("/runbooks")
async def list_runbooks():
    return {"runbooks": RUNBOOKS, "count": len(RUNBOOKS)}

@app.get("/runbooks/{runbook_id}")
async def get_runbook(runbook_id: str):
    for runbook in RUNBOOKS:
        if runbook["id"] == runbook_id:
            return runbook
    raise HTTPException(status_code=404, detail="Runbook not found")

@app.get("/sdk/quickstart")
async def sdk_quickstart(language: str = "python"):
    if language == "python":
        return {
            "language": "python",
            "code": "from evolvixos_sdk import EvolvixOSClient\nclient = EvolvixOSClient(base_url='https://evolvixos.com', api_key='your-key')",
        }
    elif language == "typescript":
        return {
            "language": "typescript",
            "code": "import { EvolvixOSClient } from 'evolvixos-sdk';\nconst client = new EvolvixOSClient({ baseUrl: 'https://evolvixos.com', apiKey: 'your-key' });",
        }
    raise HTTPException(status_code=400, detail=f"Language '{language}' not supported")

@app.get("/stats")
async def doc_stats():
    return {
        "architecture_components": len(ARCHITECTURE_OVERVIEW["components"]),
        "api_endpoints": sum(len(s["endpoints"]) for s in API_REFERENCE.values()),
        "guides": len(DEVELOPER_GUIDES),
        "faqs": len(FAQS),
        "runbooks": len(RUNBOOKS),
        "total_tests": ARCHITECTURE_OVERVIEW["total_tests"],
        "containers": ARCHITECTURE_OVERVIEW["containers"],
    }
