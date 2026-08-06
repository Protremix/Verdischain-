"""
EvolvixOS Unified AI Gateway
============================
A modular, plugin-based AI service gateway that provides:
- Multi-provider AI support (OpenAI, Anthropic, local models)
- Intelligent routing based on load, cost, and performance
- Plugin architecture with dynamic loading/unloading
- Request/response middleware pipeline
- Rate limiting and quota management
- Caching and response optimization
- Usage analytics and monitoring

Architecture:
  Client → Gateway → Router → Plugin/Provider → Response Pipeline → Client
"""

import os
import sys
import json
import time
import uuid
import hashlib
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import asyncio

from fastapi import FastAPI, Request, Response, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger()

# =========================================================================
# Configuration
# =========================================================================

GATEWAY_VERSION = "1.0.0"
GATEWAY_PORT = int(os.getenv("AI_GATEWAY_PORT", "3400"))
GATEWAY_HOST = os.getenv("AI_GATEWAY_HOST", "0.0.0.0")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_2", os.getenv("OPENAI_API_KEY", ""))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/2")
PLUGIN_DIR = os.getenv("PLUGIN_DIR", "/app/plugins")
REGISTRY_FILE = os.getenv("REGISTRY_FILE", "/app/plugin_registry.json")
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30"))
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))

# =========================================================================
# Data Models
# =========================================================================

class PluginStatus(str, Enum):
    REGISTERED = "registered"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    DISABLED = "disabled"

class ProviderType(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    CUSTOM = "custom"

class RequestPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PluginMetadata:
    name: str
    version: str
    description: str
    author: str
    provider: ProviderType
    capabilities: List[str]  # e.g., ["chat", "completion", "embedding"]
    model: str
    max_tokens: int
    cost_per_1k: float  # cost in USD per 1K tokens
    avg_latency_ms: int
    reliability_score: float  # 0.0-1.0
    tags: List[str] = field(default_factory=list)

@dataclass
class PluginEntry:
    metadata: PluginMetadata
    status: PluginStatus
    file_path: str
    loaded_at: str
    request_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    avg_response_time_ms: float = 0.0
    total_tokens_used: int = 0
    health_check_ts: Optional[str] = None

class GatewayRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plugin: Optional[str] = None  # specific plugin name, or None for auto-routing
    capability: str  # e.g., "chat", "completion", "embedding", "translation"
    input: Dict[str, Any]
    options: Dict[str, Any] = Field(default_factory=dict)
    priority: RequestPriority = RequestPriority.NORMAL
    max_tokens: Optional[int] = None
    timeout: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GatewayResponse(BaseModel):
    request_id: str
    plugin: str
    capability: str
    output: Dict[str, Any]
    tokens_used: int
    latency_ms: int
    cost_usd: float
    cached: bool = False
    timestamp: str

# =========================================================================
# Plugin Manager
# =========================================================================

class PluginManager:
    """Manages plugin lifecycle: registration, loading, execution, unloading"""
    
    def __init__(self):
        self.plugins: Dict[str, PluginEntry] = {}
        self.instances: Dict[str, Any] = {}  # loaded plugin instances
        self.registry_path = Path(REGISTRY_FILE)
        self.plugin_dir = Path(PLUGIN_DIR)
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self._load_registry()
    
    def _load_registry(self):
        """Load plugin registry from file"""
        if self.registry_path.exists():
            with open(self.registry_path) as f:
                data = json.load(f)
            for entry in data.get("plugins", []):
                meta = PluginMetadata(**entry["metadata"])
                plugin = PluginEntry(
                    metadata=meta,
                    status=PluginStatus(entry.get("status", "registered")),
                    file_path=entry["file_path"],
                    loaded_at=entry.get("loaded_at", ""),
                )
                self.plugins[meta.name] = plugin
            logger.info(f"Loaded {len(self.plugins)} plugins from registry")
        else:
            self._save_registry()
    
    def _save_registry(self):
        """Save plugin registry to file"""
        data = {
            "version": GATEWAY_VERSION,
            "plugins": []
        }
        for name, entry in self.plugins.items():
            data["plugins"].append({
                "metadata": asdict(entry.metadata),
                "status": entry.status.value,
                "file_path": entry.file_path,
                "loaded_at": entry.loaded_at,
                "request_count": entry.request_count,
                "error_count": entry.error_count,
                "last_error": entry.last_error,
                "avg_response_time_ms": entry.avg_response_time_ms,
                "total_tokens_used": entry.total_tokens_used,
            })
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register_plugin(self, metadata: PluginMetadata, file_path: str) -> bool:
        """Register a new plugin"""
        if metadata.name in self.plugins:
            logger.warning(f"Plugin {metadata.name} already registered")
            return False
        
        entry = PluginEntry(
            metadata=metadata,
            status=PluginStatus.REGISTERED,
            file_path=file_path,
            loaded_at=datetime.now(timezone.utc).isoformat(),
        )
        self.plugins[metadata.name] = entry
        self._save_registry()
        logger.info(f"Registered plugin: {metadata.name} v{metadata.version}")
        return True
    
    def load_plugin(self, name: str) -> bool:
        """Load a registered plugin into memory"""
        if name not in self.plugins:
            raise HTTPException(status_code=404, detail=f"Plugin {name} not registered")
        
        entry = self.plugins[name]
        if name in self.instances:
            logger.warning(f"Plugin {name} already loaded")
            return True
        
        try:
            spec = importlib.util.spec_from_file_location(name, entry.file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Verify plugin interface
            if not hasattr(module, 'handle_request'):
                raise ValueError(f"Plugin {name} missing handle_request function")
            if not hasattr(module, 'PLUGIN_METADATA'):
                raise ValueError(f"Plugin {name} missing PLUGIN_METADATA")
            
            self.instances[name] = module
            entry.status = PluginStatus.ACTIVE
            self._save_registry()
            logger.info(f"Loaded plugin: {name}")
            return True
        except Exception as e:
            entry.status = PluginStatus.ERROR
            entry.last_error = str(e)
            self._save_registry()
            logger.error(f"Failed to load plugin {name}: {e}")
            return False
    
    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin from memory"""
        if name not in self.instances:
            return False
        
        # Call cleanup if available
        if hasattr(self.instances[name], 'cleanup'):
            try:
                self.instances[name].cleanup()
            except Exception as e:
                logger.error(f"Plugin {name} cleanup error: {e}")
        
        del self.instances[name]
        self.plugins[name].status = PluginStatus.PAUSED
        self._save_registry()
        logger.info(f"Unloaded plugin: {name}")
        return True
    
    def remove_plugin(self, name: str) -> bool:
        """Remove a plugin from the registry"""
        if name in self.instances:
            self.unload_plugin(name)
        if name in self.plugins:
            del self.plugins[name]
            self._save_registry()
            logger.info(f"Removed plugin: {name}")
            return True
        return False
    
    def get_plugin(self, name: str) -> Optional[Any]:
        """Get a loaded plugin instance"""
        return self.instances.get(name)
    
    def list_plugins(self, status: Optional[PluginStatus] = None) -> List[Dict]:
        """List all registered plugins"""
        result = []
        for name, entry in self.plugins.items():
            if status and entry.status != status:
                continue
            result.append({
                "name": name,
                "version": entry.metadata.version,
                "description": entry.metadata.description,
                "provider": entry.metadata.provider.value,
                "capabilities": entry.metadata.capabilities,
                "model": entry.metadata.model,
                "status": entry.status.value,
                "request_count": entry.request_count,
                "error_count": entry.error_count,
                "avg_response_time_ms": entry.avg_response_time_ms,
                "reliability_score": entry.metadata.reliability_score,
            })
        return result
    
    def get_plugins_by_capability(self, capability: str) -> List[str]:
        """Get all active plugins that support a given capability"""
        result = []
        for name, entry in self.plugins.items():
            if entry.status == PluginStatus.ACTIVE and capability in entry.metadata.capabilities:
                result.append(name)
        return result
    
    def record_request(self, name: str, latency_ms: int, tokens: int, error: bool = False, error_msg: str = None):
        """Record request metrics for a plugin"""
        if name not in self.plugins:
            return
        entry = self.plugins[name]
        entry.request_count += 1
        entry.total_tokens_used += tokens
        if error:
            entry.error_count += 1
            entry.last_error = error_msg
        # Rolling average latency
        if entry.avg_response_time_ms == 0:
            entry.avg_response_time_ms = latency_ms
        else:
            entry.avg_response_time_ms = (entry.avg_response_time_ms * 0.9) + (latency_ms * 0.1)
        self._save_registry()

# =========================================================================
# Intelligent Router
# =========================================================================

class IntelligentRouter:
    """Routes requests to the best plugin based on capability, load, cost, and performance"""
    
    def __init__(self, plugin_manager: PluginManager):
        self.pm = plugin_manager
        self.request_history: deque = deque(maxlen=1000)
        self.load_counters: Dict[str, int] = defaultdict(int)
    
    def route(self, request: GatewayRequest) -> str:
        """Select the best plugin for a request"""
        # If specific plugin requested, use it
        if request.plugin:
            if request.plugin not in self.pm.plugins:
                raise HTTPException(status_code=404, detail=f"Plugin {request.plugin} not found")
            if self.pm.plugins[request.plugin].status != PluginStatus.ACTIVE:
                raise HTTPException(status_code=503, detail=f"Plugin {request.plugin} not active")
            return request.plugin
        
        # Auto-route: find all plugins with matching capability
        candidates = self.pm.get_plugins_by_capability(request.capability)
        if not candidates:
            raise HTTPException(status_code=404, detail=f"No plugins available for capability: {request.capability}")
        
        if len(candidates) == 1:
            return candidates[0]
        
        # Score each candidate
        scores = {}
        for name in candidates:
            entry = self.pm.plugins[name]
            score = self._calculate_score(entry, request)
            scores[name] = score
        
        # Return highest scoring plugin
        best = max(scores, key=scores.get)
        logger.info(f"Routed to {best} (score: {scores[best]:.2f}) among {len(candidates)} candidates")
        return best
    
    def _calculate_score(self, entry: PluginEntry, request: GatewayRequest) -> float:
        """Calculate a routing score for a plugin (higher is better)"""
        score = 0.0
        
        # Reliability (40% weight)
        score += entry.metadata.reliability_score * 40
        
        # Latency (25% weight) - lower is better
        max_latency = 10000  # 10s max
        latency_score = 1.0 - min(entry.avg_response_time_ms / max_latency, 1.0)
        score += latency_score * 25
        
        # Cost (20% weight) - lower is better
        max_cost = 0.10  # $0.10 per 1K tokens max
        cost_score = 1.0 - min(entry.metadata.cost_per_1k / max_cost, 1.0)
        score += cost_score * 20
        
        # Current load (15% weight) - lower is better
        max_load = MAX_CONCURRENT_REQUESTS
        load_score = 1.0 - min(self.load_counters[entry.metadata.name] / max_load, 1.0)
        score += load_score * 15
        
        # Priority bonus
        if request.priority == RequestPriority.HIGH:
            score *= 1.1
        elif request.priority == RequestPriority.CRITICAL:
            score *= 1.2
        
        return score
    
    def record_load(self, name: str):
        self.load_counters[name] += 1
    
    def release_load(self, name: str):
        if self.load_counters[name] > 0:
            self.load_counters[name] -= 1

# =========================================================================
# Cache Manager
# =========================================================================

class CacheManager:
    """Simple in-memory cache with TTL for AI responses"""
    
    def __init__(self, max_size: int = 500, ttl_seconds: int = 300):
        self.cache: Dict[str, tuple] = {}  # key -> (value, expiry_ts)
        self.max_size = max_size
        self.ttl = ttl_seconds
        self.hits = 0
        self.misses = 0
    
    def _make_key(self, plugin: str, capability: str, input_data: Dict) -> str:
        """Create a deterministic cache key"""
        data_str = json.dumps({"plugin": plugin, "capability": capability, "input": input_data}, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def get(self, plugin: str, capability: str, input_data: Dict) -> Optional[Any]:
        key = self._make_key(plugin, capability, input_data)
        if key in self.cache:
            value, expiry = self.cache[key]
            if time.time() < expiry:
                self.hits += 1
                return value
            else:
                del self.cache[key]
        self.misses += 1
        return None
    
    def set(self, plugin: str, capability: str, input_data: Dict, value: Any):
        key = self._make_key(plugin, capability, input_data)
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest = min(self.cache.items(), key=lambda x: x[1][1])
            del self.cache[oldest[0]]
        self.cache[key] = (value, time.time() + self.ttl)
    
    def stats(self) -> Dict:
        total = self.hits + self.misses
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": (self.hits / total * 100) if total > 0 else 0,
        }
    
    def clear(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0

# =========================================================================
# Rate Limiter
# =========================================================================

class RateLimiter:
    """Token bucket rate limiter per client"""
    
    def __init__(self, rate_per_min: int = 60):
        self.rate = rate_per_min
        self.clients: Dict[str, List[float]] = defaultdict(list)
    
    def check(self, client_id: str) -> bool:
        """Check if client is within rate limit. Returns True if allowed."""
        now = time.time()
        window = 60.0  # 1 minute window
        
        # Clean old entries
        self.clients[client_id] = [ts for ts in self.clients[client_id] if now - ts < window]
        
        if len(self.clients[client_id]) >= self.rate:
            return False
        
        self.clients[client_id].append(now)
        return True

# =========================================================================
# Gateway Application
# =========================================================================

# Initialize components
plugin_manager = PluginManager()
router = IntelligentRouter(plugin_manager)
cache = CacheManager()
rate_limiter = RateLimiter(RATE_LIMIT_PER_MIN)

app = FastAPI(
    title="EvolvixOS AI Gateway",
    description="Unified AI Gateway with plugin architecture, intelligent routing, and multi-provider support",
    version=GATEWAY_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def request_logger(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = int((time.time() - start) * 1000)
    logger.info(
        "gateway_request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=duration_ms,
    )
    return response

# =========================================================================
# API Endpoints
# =========================================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": GATEWAY_VERSION,
        "plugins": {
            "total": len(plugin_manager.plugins),
            "active": len([p for p in plugin_manager.plugins.values() if p.status == PluginStatus.ACTIVE]),
        },
        "cache": cache.stats(),
    }

@app.get("/plugins")
async def list_plugins(status: Optional[str] = None):
    plugin_status = PluginStatus(status) if status else None
    return {"plugins": plugin_manager.list_plugins(plugin_status)}

@app.post("/plugins/register")
async def register_plugin(metadata: Dict[str, Any], file_path: str):
    """Register a new plugin"""
    meta = PluginMetadata(**metadata)
    success = plugin_manager.register_plugin(meta, file_path)
    if success:
        # Auto-load the plugin
        plugin_manager.load_plugin(meta.name)
    return {"success": success, "name": meta.name}

@app.post("/plugins/{name}/load")
async def load_plugin(name: str):
    success = plugin_manager.load_plugin(name)
    return {"success": success, "name": name}

@app.post("/plugins/{name}/unload")
async def unload_plugin(name: str):
    success = plugin_manager.unload_plugin(name)
    return {"success": success, "name": name}

@app.delete("/plugins/{name}")
async def remove_plugin(name: str):
    success = plugin_manager.remove_plugin(name)
    return {"success": success, "name": name}

@app.get("/plugins/{name}/health")
async def plugin_health(name: str):
    if name not in plugin_manager.plugins:
        raise HTTPException(status_code=404, detail=f"Plugin {name} not found")
    entry = plugin_manager.plugins[name]
    return {
        "name": name,
        "status": entry.status.value,
        "request_count": entry.request_count,
        "error_count": entry.error_count,
        "error_rate": (entry.error_count / entry.request_count * 100) if entry.request_count > 0 else 0,
        "avg_response_time_ms": entry.avg_response_time_ms,
        "total_tokens_used": entry.total_tokens_used,
        "last_error": entry.last_error,
    }

@app.post("/gateway/invoke")
async def invoke_gateway(request: GatewayRequest, http_request: Request):
    """Main gateway endpoint — routes request to the best plugin"""
    # Rate limiting
    client_id = http_request.client.host if http_request.client else "unknown"
    if not rate_limiter.check(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Route to plugin
    plugin_name = router.route(request)
    router.record_load(plugin_name)
    
    try:
        # Check cache
        cached = cache.get(plugin_name, request.capability, request.input)
        if cached:
            router.release_load(plugin_name)
            return GatewayResponse(
                request_id=request.request_id,
                plugin=plugin_name,
                capability=request.capability,
                output=cached,
                tokens_used=0,
                latency_ms=0,
                cost_usd=0,
                cached=True,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        
        # Execute plugin
        plugin = plugin_manager.get_plugin(plugin_name)
        if not plugin:
            raise HTTPException(status_code=503, detail=f"Plugin {plugin_name} not loaded")
        
        start_time = time.time()
        timeout = request.timeout or DEFAULT_TIMEOUT
        
        try:
            result = await asyncio.wait_for(
                plugin.handle_request(request.input, request.options),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail=f"Plugin {plugin_name} timed out after {timeout}s")
        
        latency_ms = int((time.time() - start_time) * 1000)
        tokens_used = result.get("tokens_used", 0)
        
        # Calculate cost
        entry = plugin_manager.plugins[plugin_name]
        cost_usd = (tokens_used / 1000) * entry.metadata.cost_per_1k
        
        # Record metrics
        plugin_manager.record_request(plugin_name, latency_ms, tokens_used)
        
        # Cache the result
        cache.set(plugin_name, request.capability, request.input, result)
        
        router.release_load(plugin_name)
        
        return GatewayResponse(
            request_id=request.request_id,
            plugin=plugin_name,
            capability=request.capability,
            output=result,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            cost_usd=round(cost_usd, 6),
            cached=False,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    
    except HTTPException:
        router.release_load(plugin_name)
        raise
    except Exception as e:
        router.release_load(plugin_name)
        plugin_manager.record_request(plugin_name, 0, 0, error=True, error_msg=str(e))
        logger.error(f"Plugin {plugin_name} error: {e}")
        raise HTTPException(status_code=500, detail=f"Plugin execution error: {str(e)}")

@app.get("/gateway/stats")
async def gateway_stats():
    """Get gateway statistics"""
    total_requests = sum(p.request_count for p in plugin_manager.plugins.values())
    total_errors = sum(p.error_count for p in plugin_manager.plugins.values())
    total_tokens = sum(p.total_tokens_used for p in plugin_manager.plugins.values())
    
    return {
        "version": GATEWAY_VERSION,
        "uptime": "running",
        "total_requests": total_requests,
        "total_errors": total_errors,
        "error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
        "total_tokens_used": total_tokens,
        "active_plugins": len([p for p in plugin_manager.plugins.values() if p.status == PluginStatus.ACTIVE]),
        "total_plugins": len(plugin_manager.plugins),
        "cache": cache.stats(),
        "plugins": [
            {
                "name": name,
                "requests": entry.request_count,
                "errors": entry.error_count,
                "avg_latency_ms": entry.avg_response_time_ms,
                "tokens": entry.total_tokens_used,
            }
            for name, entry in plugin_manager.plugins.items()
        ],
    }

@app.get("/capabilities")
async def list_capabilities():
    """List all available capabilities and their plugins"""
    capabilities = defaultdict(list)
    for name, entry in plugin_manager.plugins.items():
        if entry.status == PluginStatus.ACTIVE:
            for cap in entry.metadata.capabilities:
                capabilities[cap].append(name)
    return {"capabilities": dict(capabilities)}

@app.post("/cache/clear")
async def clear_cache():
    cache.clear()
    return {"success": True, "message": "Cache cleared"}

# =========================================================================
# Startup: Register built-in plugins
# =========================================================================

@app.on_event("startup")
async def startup_event():
    """Register and load built-in plugins on startup"""
    logger.info(f"EvolvixOS AI Gateway v{GATEWAY_VERSION} starting...")
    
    # Ensure plugin directory exists
    Path(PLUGIN_DIR).mkdir(parents=True, exist_ok=True)
    
    # Auto-load all registered plugins
    for name, entry in list(plugin_manager.plugins.items()):
        if entry.status in (PluginStatus.REGISTERED, PluginStatus.PAUSED):
            plugin_manager.load_plugin(name)
    
    logger.info(f"Gateway ready with {len(plugin_manager.instances)} active plugins")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=GATEWAY_HOST, port=GATEWAY_PORT)
