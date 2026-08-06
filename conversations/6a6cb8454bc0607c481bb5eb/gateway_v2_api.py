"""
EvolvixOS Enhanced AI Gateway API
Integrates the universal plugin architecture, intelligent router, and all providers.
This is the unified entry point for ALL AI operations in EvolvixOS.
"""

from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import structlog
import os

from plugin_architecture import (
    registry as plugin_registry, manager as plugin_manager,
    PluginMetadata, PluginType, PluginStatus, Capability,
    PluginRegistry, PluginManager, ProviderPlugin
)
from intelligent_router import IntelligentRouter, RoutingPolicy
from specialized_providers import register_all_specialized, create_specialized_plugin, SPECIALIZED_PROVIDERS

logger = structlog.get_logger()

app = FastAPI(
    title="EvolvixOS AI Gateway v2",
    description="Unified multi-provider AI gateway with intelligent routing",
    version="2.0.0",
)

# Initialize router
router_policy = RoutingPolicy(prefer_local=True)
router = IntelligentRouter(plugin_registry, router_policy)


# =========================================================================
# Initialize providers on startup
# =========================================================================

@app.on_event("startup")
async def startup():
    """Register all providers on startup."""
    # Register specialized providers
    register_all_specialized(plugin_registry)
    
    # Try to register LLM providers if available
    try:
        from llm_providers import register_all_providers as register_llms
        register_llms(plugin_registry)
        logger.info("LLM providers registered")
    except ImportError:
        logger.warning("llm_providers module not found, skipping")
    
    logger.info(f"Plugin registry: {plugin_registry.stats()}")


# =========================================================================
# Request Models
# =========================================================================

class InvokeRequest(BaseModel):
    capability: str = Field(..., description="Capability to invoke (chat, completion, code_generation, etc.)")
    input_data: Dict[str, Any] = Field(default_factory=dict)
    options: Dict[str, Any] = Field(default_factory=dict)
    prefer_local: Optional[bool] = None
    max_fallbacks: int = 3
    provider: Optional[str] = None  # specific provider to use


class RegisterPluginRequest(BaseModel):
    plugin_id: str
    config: Dict[str, Any] = {}


class RouteRequest(BaseModel):
    capability: str
    prefer_local: Optional[bool] = None


# =========================================================================
# Endpoints
# =========================================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "plugins": plugin_registry.stats(),
        "router": router.stats(),
    }

@app.get("/stats")
async def stats():
    return {
        "plugins": plugin_registry.stats(),
        "router": router.stats(),
        "health": router.health_report(),
    }

# --- Plugin Management ---

@app.get("/plugins")
async def list_plugins(plugin_type: str = None, capability: str = None):
    """List all registered plugins"""
    if plugin_type:
        plugins = plugin_registry.list_by_type(PluginType(plugin_type))
    elif capability:
        plugins = plugin_registry.list_by_capability(Capability(capability))
    else:
        plugins = plugin_registry.list_all()
    return {"plugins": [p.to_dict() for p in plugins], "count": len(plugins)}

@app.get("/plugins/{plugin_id}")
async def get_plugin(plugin_id: str):
    """Get plugin details"""
    meta = plugin_registry.get_metadata(plugin_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Plugin not found")
    plugin = plugin_registry.get(plugin_id)
    health = router.get_health(plugin_id)
    return {
        "metadata": meta.to_dict(),
        "status": plugin.status.value if plugin else "not_loaded",
        "health": health.to_dict(),
    }

@app.post("/plugins/{plugin_id}/load")
async def load_plugin(plugin_id: str):
    """Load a plugin"""
    # Try to create from specialized providers
    plugin = create_specialized_plugin(plugin_id)
    if not plugin:
        try:
            from llm_providers import create_plugin as create_llm
            plugin = create_llm(plugin_id)
        except Exception:
            pass
    
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found in any provider registry")
    
    if not plugin_registry.get(plugin_id):
        plugin_registry.register(plugin)
    
    result = await plugin_manager.load_plugin(plugin_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to load plugin")
    return {"success": True, "plugin_id": plugin_id, "status": "active"}

@app.post("/plugins/{plugin_id}/unload")
async def unload_plugin(plugin_id: str):
    """Unload a plugin"""
    result = await plugin_manager.unload_plugin(plugin_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to unload plugin")
    return {"success": True, "plugin_id": plugin_id, "status": "inactive"}

@app.get("/plugins/types")
async def list_plugin_types():
    """List all plugin types"""
    return {
        "types": [t.value for t in PluginType],
        "capabilities": [c.value for c in Capability],
    }

# --- Routing ---

@app.post("/route")
async def route_request(req: RouteRequest):
    """Get routing decision without executing"""
    try:
        decision = router.route(req.capability, prefer_local=req.prefer_local)
        return decision.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/route/capabilities")
async def list_capabilities():
    """List all available capabilities and their providers"""
    caps = {}
    for cap in Capability:
        providers = plugin_registry.list_by_capability(cap)
        if providers:
            caps[cap.value] = [p.id for p in providers]
    return {"capabilities": caps}

# --- Invocation ---

@app.post("/invoke")
async def invoke(req: InvokeRequest):
    """Invoke a capability — routes to best provider with fallback"""
    if req.provider:
        # Use specific provider
        plugin = plugin_registry.get(req.provider)
        if not plugin:
            raise HTTPException(status_code=404, detail=f"Provider '{req.provider}' not loaded")
        if plugin.status != PluginStatus.ACTIVE:
            raise HTTPException(status_code=400, detail=f"Provider '{req.provider}' not active")
        
        try:
            result = await plugin.invoke(req.capability, req.input_data, req.options)
            return {"output": result, "provider": req.provider, "capability": req.capability}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Use intelligent routing
        try:
            result = await router.route_and_invoke(
                req.capability,
                req.input_data,
                req.options,
                prefer_local=req.prefer_local,
                max_fallbacks=req.max_fallbacks,
            )
            return result
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

# --- Health & Monitoring ---

@app.get("/providers/health")
async def providers_health():
    """Get health report for all providers"""
    return router.health_report()

@app.get("/providers/{plugin_id}/health")
async def provider_health(plugin_id: str):
    """Get health for a specific provider"""
    health = router.get_health(plugin_id)
    plugin = plugin_registry.get(plugin_id)
    return {
        "plugin_id": plugin_id,
        "health": health.to_dict(),
        "status": plugin.status.value if plugin else "not_loaded",
    }
