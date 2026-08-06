"""
EvolvixOS Universal Plugin Architecture
The foundation for all extensibility — providers, agents, drivers, services, extensions.
The kernel never requires modification when adding new plugins.
"""

import abc
import asyncio
import importlib
import json
import os
import time
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Type, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from collections import defaultdict
import structlog

logger = structlog.get_logger()


# =========================================================================
# Enums
# =========================================================================

class PluginType(str, Enum):
    LLM_PROVIDER = "llm_provider"
    CODING_PROVIDER = "coding_provider"
    IMAGE_PROVIDER = "image_provider"
    VIDEO_PROVIDER = "video_provider"
    SPEECH_PROVIDER = "speech_provider"
    SPEECH_RECOGNITION = "speech_recognition"
    OCR_PROVIDER = "ocr_provider"
    SEARCH_PROVIDER = "search_provider"
    TRANSLATION_PROVIDER = "translation_provider"
    EMBEDDING_PROVIDER = "embedding_provider"
    VECTOR_MEMORY = "vector_memory"
    AGENT = "agent"
    DRIVER = "driver"
    FILE_SYSTEM = "file_system"
    DESKTOP_COMPONENT = "desktop_component"
    CLI_COMMAND = "cli_command"
    APPLICATION = "application"
    THEME = "theme"
    SERVICE = "service"
    EXTENSION = "extension"


class PluginStatus(str, Enum):
    REGISTERED = "registered"
    LOADING = "loading"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UNLOADING = "unloading"


class Capability(str, Enum):
    CHAT = "chat"
    COMPLETION = "completion"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    REASONING = "reasoning"
    VISION = "vision"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    SPEECH_SYNTHESIS = "speech_synthesis"
    SPEECH_RECOGNITION = "speech_recognition"
    OCR = "ocr"
    SEARCH = "search"
    TRANSLATION = "translation"
    EMBEDDING = "embedding"
    VECTOR_STORAGE = "vector_storage"
    SUMMARIZATION = "summarization"
    SENTIMENT = "sentiment"
    FUNCTION_CALLING = "function_calling"
    STREAMING = "streaming"
    JSON_MODE = "json_mode"


# =========================================================================
# Plugin Metadata
# =========================================================================

@dataclass
class PluginMetadata:
    id: str
    name: str
    version: str
    plugin_type: PluginType
    description: str = ""
    author: str = ""
    license: str = "MIT"
    homepage: str = ""
    capabilities: List[Capability] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    default_config: Dict[str, Any] = field(default_factory=dict)
    requires_api_key: bool = False
    api_key_env: Optional[str] = None  # environment variable name for API key
    is_local: bool = False  # True for local models (Ollama, vLLM)
    priority: int = 50  # 0-100, higher = preferred
    cost_per_1k_tokens: float = 0.0  # USD
    max_context_window: int = 4096
    max_output_tokens: int = 2048
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d["plugin_type"] = self.plugin_type.value
        d["capabilities"] = [c.value for c in self.capabilities]
        return d


# =========================================================================
# Universal Plugin Base Class
# =========================================================================

class UniversalPlugin(abc.ABC):
    """Base class for ALL EvolvixOS plugins — providers, agents, drivers, services."""
    
    def __init__(self, metadata: PluginMetadata, config: Dict[str, Any] = None):
        self.metadata = metadata
        self.config = config or metadata.default_config.copy()
        self.status: PluginStatus = PluginStatus.REGISTERED
        self._metrics: Dict[str, Any] = {
            "invocations": 0,
            "errors": 0,
            "total_latency_ms": 0.0,
            "last_invoked": None,
        }
    
    @property
    def id(self) -> str:
        return self.metadata.id
    
    @property
    def name(self) -> str:
        return self.metadata.name
    
    @property
    def is_local(self) -> bool:
        return self.metadata.is_local
    
    @abc.abstractmethod
    async def initialize(self) -> None:
        """Called when plugin is loaded. Set up connections, validate config."""
        pass
    
    @abc.abstractmethod
    async def invoke(self, capability: str, input_data: Dict[str, Any],
                     options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main entry point. Execute the requested capability."""
        pass
    
    async def shutdown(self) -> None:
        """Called when plugin is unloaded. Clean up resources."""
        self.status = PluginStatus.INACTIVE
        logger.info(f"Plugin {self.id} shut down")
    
    async def health_check(self) -> Dict[str, Any]:
        """Return health status."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "healthy": self.status == PluginStatus.ACTIVE,
            "metrics": self._metrics,
        }
    
    def _record_invocation(self, latency_ms: float, success: bool = True):
        self._metrics["invocations"] += 1
        if not success:
            self._metrics["errors"] += 1
        self._metrics["total_latency_ms"] += latency_ms
        self._metrics["last_invoked"] = datetime.now(timezone.utc).isoformat()
    
    @property
    def avg_latency_ms(self) -> float:
        inv = self._metrics["invocations"]
        return self._metrics["total_latency_ms"] / max(inv, 1)
    
    @property
    def error_rate(self) -> float:
        inv = self._metrics["invocations"]
        return (self._metrics["errors"] / max(inv, 1)) * 100 if inv > 0 else 0


# =========================================================================
# Provider Plugin Base Class (extends UniversalPlugin)
# =========================================================================

class ProviderPlugin(UniversalPlugin):
    """Base class for AI provider plugins (LLM, image, speech, etc.)."""
    
    def __init__(self, metadata: PluginMetadata, config: Dict[str, Any] = None):
        super().__init__(metadata, config)
        self._api_key: Optional[str] = None
        self._base_url: Optional[str] = None
        self._client = None  # httpx.AsyncClient or similar
    
    async def initialize(self) -> None:
        """Initialize provider — load API key from env, set up client."""
        if self.metadata.requires_api_key and self.metadata.api_key_env:
            self._api_key = os.getenv(self.metadata.api_key_env)
            if not self._api_key:
                logger.warning(f"Plugin {self.id}: API key not found in env {self.metadata.api_key_env}")
                self.status = PluginStatus.ERROR
                return
        
        self._base_url = self.config.get("base_url", "")
        self.status = PluginStatus.ACTIVE
        logger.info(f"Provider {self.id} initialized (local={self.is_local})")
    
    async def invoke(self, capability: str, input_data: Dict[str, Any],
                     options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Default invoke — providers override _execute."""
        start = time.time()
        try:
            result = await self._execute(capability, input_data, options or {})
            latency = (time.time() - start) * 1000
            self._record_invocation(latency, True)
            return result
        except Exception as e:
            latency = (time.time() - start) * 1000
            self._record_invocation(latency, False)
            raise
    
    @abc.abstractmethod
    async def _execute(self, capability: str, input_data: Dict[str, Any],
                      options: Dict[str, Any]) -> Dict[str, Any]:
        """Providers implement this."""
        pass
    
    async def stream(self, capability: str, input_data: Dict[str, Any],
                     options: Dict[str, Any] = None):
        """Streaming support — providers override if supported."""
        raise NotImplementedError(f"Plugin {self.id} does not support streaming")
    
    def supports_capability(self, capability: str) -> bool:
        return any(c.value == capability for c in self.metadata.capabilities)


# =========================================================================
# Plugin Registry
# =========================================================================

class PluginRegistry:
    """Central registry for all plugins — metadata, status, discovery."""
    
    def __init__(self, persist_path: str = None):
        self._plugins: Dict[str, UniversalPlugin] = {}
        self._metadata: Dict[str, PluginMetadata] = {}
        self._persist_path = persist_path
        self._type_index: Dict[PluginType, List[str]] = defaultdict(list)
        self._capability_index: Dict[Capability, List[str]] = defaultdict(list)
    
    def register(self, plugin: UniversalPlugin) -> None:
        """Register a plugin instance."""
        meta = plugin.metadata
        self._plugins[meta.id] = plugin
        self._metadata[meta.id] = meta
        self._type_index[meta.plugin_type].append(meta.id)
        for cap in meta.capabilities:
            self._capability_index[cap].append(meta.id)
        logger.info(f"Registered plugin: {meta.id} ({meta.plugin_type.value})")
    
    def register_metadata(self, metadata: PluginMetadata) -> None:
        """Register metadata only (plugin loaded lazily)."""
        self._metadata[metadata.id] = metadata
        self._type_index[metadata.plugin_type].append(metadata.id)
        for cap in metadata.capabilities:
            self._capability_index[cap].append(metadata.id)
    
    def unregister(self, plugin_id: str) -> bool:
        """Unregister a plugin."""
        if plugin_id in self._metadata:
            meta = self._metadata[plugin_id]
            self._type_index[meta.plugin_type].remove(plugin_id)
            for cap in meta.capabilities:
                if plugin_id in self._capability_index[cap]:
                    self._capability_index[cap].remove(plugin_id)
            del self._metadata[plugin_id]
            if plugin_id in self._plugins:
                del self._plugins[plugin_id]
            return True
        return False
    
    def get(self, plugin_id: str) -> Optional[UniversalPlugin]:
        return self._plugins.get(plugin_id)
    
    def get_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        return self._metadata.get(plugin_id)
    
    def list_by_type(self, plugin_type: PluginType) -> List[PluginMetadata]:
        return [self._metadata[pid] for pid in self._type_index[plugin_type] if pid in self._metadata]
    
    def list_by_capability(self, capability: Capability) -> List[PluginMetadata]:
        return [self._metadata[pid] for pid in self._capability_index[capability] if pid in self._metadata]
    
    def list_all(self) -> List[PluginMetadata]:
        return list(self._metadata.values())
    
    def list_active(self) -> List[UniversalPlugin]:
        return [p for p in self._plugins.values() if p.status == PluginStatus.ACTIVE]
    
    def find_providers(self, capability: str, prefer_local: bool = True) -> List[PluginMetadata]:
        """Find providers that support a capability, optionally preferring local."""
        cap = Capability(capability) if isinstance(capability, str) else capability
        providers = self.list_by_capability(cap)
        if prefer_local:
            providers.sort(key=lambda m: (not m.is_local, -m.priority, m.cost_per_1k_tokens))
        else:
            providers.sort(key=lambda m: (-m.priority, m.cost_per_1k_tokens))
        return providers
    
    def stats(self) -> Dict[str, Any]:
        type_counts = {t.value: len(ids) for t, ids in self._type_index.items() if ids}
        return {
            "total_plugins": len(self._metadata),
            "active_plugins": len(self.list_active()),
            "by_type": type_counts,
        }


# =========================================================================
# Plugin Manager
# =========================================================================

class PluginManager:
    """Manages plugin lifecycle — loading, unloading, hot-swap, discovery."""
    
    def __init__(self, registry: PluginRegistry, plugin_dirs: List[str] = None):
        self.registry = registry
        self.plugin_dirs = plugin_dirs or []
        self._load_order: List[str] = []
    
    async def load_plugin(self, plugin_id: str) -> bool:
        """Load and initialize a registered plugin."""
        plugin = self.registry.get(plugin_id)
        if not plugin:
            logger.error(f"Cannot load plugin {plugin_id}: not registered")
            return False
        
        if plugin.status == PluginStatus.ACTIVE:
            return True
        
        try:
            plugin.status = PluginStatus.LOADING
            await plugin.initialize()
            if plugin.status != PluginStatus.ERROR:
                plugin.status = PluginStatus.ACTIVE
                self._load_order.append(plugin_id)
                logger.info(f"Loaded plugin: {plugin_id}")
                return True
            return False
        except Exception as e:
            plugin.status = PluginStatus.ERROR
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            return False
    
    async def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin."""
        plugin = self.registry.get(plugin_id)
        if not plugin:
            return False
        
        try:
            plugin.status = PluginStatus.UNLOADING
            await plugin.shutdown()
            if plugin_id in self._load_order:
                self._load_order.remove(plugin_id)
            logger.info(f"Unloaded plugin: {plugin_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_id}: {e}")
            return False
    
    async def reload_plugin(self, plugin_id: str) -> bool:
        """Hot-swap a plugin."""
        await self.unload_plugin(plugin_id)
        return await self.load_plugin(plugin_id)
    
    async def load_all(self) -> Dict[str, bool]:
        """Load all registered plugins."""
        results = {}
        for plugin_id in list(self.registry._metadata.keys()):
            results[plugin_id] = await self.load_plugin(plugin_id)
        return results
    
    async def unload_all(self) -> Dict[str, bool]:
        """Unload all plugins."""
        results = {}
        for plugin_id in reversed(self._load_order):
            results[plugin_id] = await self.unload_plugin(plugin_id)
        return results
    
    async def invoke_plugin(self, plugin_id: str, capability: str,
                           input_data: Dict, options: Dict = None) -> Dict:
        """Invoke a specific plugin."""
        plugin = self.registry.get(plugin_id)
        if not plugin:
            raise ValueError(f"Plugin '{plugin_id}' not found or not loaded")
        if plugin.status != PluginStatus.ACTIVE:
            raise ValueError(f"Plugin '{plugin_id}' is not active (status: {plugin.status.value})")
        return await plugin.invoke(capability, input_data, options)
    
    def discover_plugins(self, directory: str) -> List[str]:
        """Scan a directory for plugin modules."""
        discovered = []
        if not os.path.isdir(directory):
            return discovered
        
        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('_'):
                module_name = filename[:-3]
                discovered.append(module_name)
                logger.info(f"Discovered plugin module: {module_name}")
        
        return discovered
    
    async def load_from_directory(self, directory: str) -> Dict[str, bool]:
        """Load all plugins from a directory."""
        results = {}
        modules = self.discover_plugins(directory)
        for mod_name in modules:
            try:
                # Dynamic import
                import sys
                if directory not in sys.path:
                    sys.path.insert(0, directory)
                module = importlib.import_module(mod_name)
                
                # Look for a create_plugin() factory function
                if hasattr(module, 'create_plugin'):
                    plugin = module.create_plugin()
                    self.registry.register(plugin)
                    results[plugin.id] = await self.load_plugin(plugin.id)
                elif hasattr(module, 'PLUGIN_METADATA'):
                    # Register metadata only (lazy load)
                    self.registry.register_metadata(module.PLUGIN_METADATA)
                    results[module.PLUGIN_METADATA.id] = True
            except Exception as e:
                logger.error(f"Failed to load plugin from {mod_name}: {e}")
                results[mod_name] = False
        
        return results


# =========================================================================
# Global instances
# =========================================================================

registry = PluginRegistry(
    persist_path=os.getenv("PLUGIN_REGISTRY_PATH", "/tmp/plugin_registry.json")
)
manager = PluginManager(registry)
