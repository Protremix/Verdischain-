"""
EvolvixOS Enhanced Intelligent Router
Capability-based routing, automatic fallback, cost optimization, provider health tracking.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import defaultdict
import structlog

from plugin_architecture import (
    PluginRegistry, PluginManager, PluginMetadata, PluginType,
    Capability, ProviderPlugin, PluginStatus
)

logger = structlog.get_logger()


# =========================================================================
# Routing Models
# =========================================================================

@dataclass
class RoutingDecision:
    """Result of a routing decision"""
    selected_plugin_id: str
    selected_capability: str
    fallback_chain: List[str]  # ordered list of fallback plugin IDs
    reason: str
    estimated_cost: float
    estimated_latency_ms: float
    is_local: bool
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict:
        from dataclasses import asdict
        return asdict(self)


@dataclass
class ProviderHealth:
    """Health tracking for a provider"""
    plugin_id: str
    healthy: bool = True
    consecutive_failures: int = 0
    last_success: str = None
    last_failure: str = None
    avg_latency_ms: float = 0.0
    total_requests: int = 0
    total_errors: int = 0
    circuit_open: bool = False  # circuit breaker
    circuit_opened_at: str = None
    
    def record_success(self, latency_ms: float):
        self.healthy = True
        self.consecutive_failures = 0
        self.last_success = datetime.now(timezone.utc).isoformat()
        self.total_requests += 1
        # Exponential moving average
        self.avg_latency_ms = self.avg_latency_ms * 0.9 + latency_ms * 0.1
        # Close circuit if it was open
        if self.circuit_open:
            self.circuit_open = False
            self.circuit_opened_at = None
            logger.info(f"Provider {self.plugin_id}: circuit breaker closed")
    
    def record_failure(self):
        self.consecutive_failures += 1
        self.total_errors += 1
        self.total_requests += 1
        self.last_failure = datetime.now(timezone.utc).isoformat()
        
        # Open circuit after 3 consecutive failures
        if self.consecutive_failures >= 3 and not self.circuit_open:
            self.circuit_open = True
            self.circuit_opened_at = datetime.now(timezone.utc).isoformat()
            self.healthy = False
            logger.warning(f"Provider {self.plugin_id}: circuit breaker opened after {self.consecutive_failures} failures")
    
    def to_dict(self) -> Dict:
        from dataclasses import asdict
        return asdict(self)


# =========================================================================
# Routing Policy
# =========================================================================

class RoutingPolicy:
    """Configurable routing policy for provider selection."""
    
    def __init__(self,
                 prefer_local: bool = True,
                 max_cost_per_request: float = 0.50,
                 max_latency_ms: float = 30000,
                 require_streaming: bool = False,
                 min_context_window: int = 4096,
                 user_preferences: Dict[str, Any] = None,
                 weights: Dict[str, float] = None):
        self.prefer_local = prefer_local
        self.max_cost_per_request = max_cost_per_request
        self.max_latency_ms = max_latency_ms
        self.require_streaming = require_streaming
        self.min_context_window = min_context_window
        self.user_preferences = user_preferences or {}
        
        # Default weights for scoring
        self.weights = weights or {
            "capability_match": 30.0,
            "reliability": 25.0,
            "latency": 15.0,
            "cost": 15.0,
            "local_preference": 10.0,
            "priority": 5.0,
        }
    
    def score_provider(self, metadata: PluginMetadata,
                       health: ProviderHealth,
                       capability: str) -> float:
        """Score a provider for a given capability. Higher = better."""
        score = 0.0
        
        # Capability match (must have the capability)
        caps = [c.value for c in metadata.capabilities]
        if capability in caps:
            score += self.weights["capability_match"]
        
        # Reliability (inverse of error rate)
        if health.total_requests > 0:
            reliability = 1.0 - (health.total_errors / health.total_requests)
            score += reliability * self.weights["reliability"]
        else:
            score += self.weights["reliability"] * 0.8  # unknown reliability
        
        # Latency (lower is better)
        if health.avg_latency_ms > 0:
            latency_score = max(0, 1.0 - (health.avg_latency_ms / self.max_latency_ms))
            score += latency_score * self.weights["latency"]
        else:
            score += self.weights["latency"] * 0.7
        
        # Cost (lower is better)
        if metadata.cost_per_1k_tokens > 0:
            cost_score = max(0, 1.0 - (metadata.cost_per_1k_tokens / 0.10))
            score += cost_score * self.weights["cost"]
        else:
            score += self.weights["cost"]  # free (local models)
        
        # Local preference
        if self.prefer_local and metadata.is_local:
            score += self.weights["local_preference"]
        
        # Priority
        score += (metadata.priority / 100.0) * self.weights["priority"]
        
        # Penalty for circuit breaker
        if health.circuit_open:
            score -= 50.0
        
        # Penalty for not meeting context window
        if metadata.max_context_window < self.min_context_window:
            score -= 20.0
        
        return score


# =========================================================================
# Enhanced Intelligent Router
# =========================================================================

class IntelligentRouter:
    """Advanced AI router with capability-based routing, fallback, and circuit breakers."""
    
    def __init__(self, registry: PluginRegistry, policy: RoutingPolicy = None):
        self.registry = registry
        self.policy = policy or RoutingPolicy()
        self._health: Dict[str, ProviderHealth] = {}
        self._routing_history: List[RoutingDecision] = []
        self._max_history = 1000
    
    def get_health(self, plugin_id: str) -> ProviderHealth:
        """Get or create health tracker for a provider."""
        if plugin_id not in self._health:
            self._health[plugin_id] = ProviderHealth(plugin_id=plugin_id)
        return self._health[plugin_id]
    
    def route(self, capability: str,
              input_data: Dict = None,
              prefer_local: bool = None,
              exclude: List[str] = None) -> RoutingDecision:
        """Route a request to the best provider."""
        exclude = exclude or []
        
        # Override policy preference if specified
        policy = self.policy
        if prefer_local is not None:
            policy = RoutingPolicy(
                prefer_local=prefer_local,
                max_cost_per_request=self.policy.max_cost_per_request,
                max_latency_ms=self.policy.max_latency_ms,
                require_streaming=self.policy.require_streaming,
                min_context_window=self.policy.min_context_window,
                user_preferences=self.policy.user_preferences,
                weights=self.policy.weights,
            )
        
        # Find all providers with this capability
        try:
            providers = self.registry.find_providers(capability, prefer_local=policy.prefer_local)
        except Exception:
            providers = self.registry.list_by_capability(Capability(capability)) if capability in [c.value for c in Capability] else []
        
        # Filter out excluded and circuit-broken providers
        available = []
        for meta in providers:
            if meta.id in exclude:
                continue
            health = self.get_health(meta.id)
            if health.circuit_open:
                continue
            available.append((meta, health))
        
        if not available:
            # Try with circuit-broken providers as last resort
            available = [
                (meta, self.get_health(meta.id))
                for meta in providers
                if meta.id not in exclude
            ]
        
        if not available:
            raise ValueError(f"No providers available for capability '{capability}'")
        
        # Score all available providers
        scored = []
        for meta, health in available:
            score = policy.score_provider(meta, health, capability)
            scored.append((meta, health, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[2], reverse=True)
        
        # Select best and build fallback chain
        best_meta, best_health, best_score = scored[0]
        fallback_chain = [s[0].id for s in scored[1:]]
        
        # Estimate cost and latency
        est_cost = best_meta.cost_per_1k_tokens * (len(str(input_data or {})) / 4000) if best_meta.cost_per_1k_tokens > 0 else 0
        est_latency = best_health.avg_latency_ms if best_health.avg_latency_ms > 0 else 1000
        
        decision = RoutingDecision(
            selected_plugin_id=best_meta.id,
            selected_capability=capability,
            fallback_chain=fallback_chain,
            reason=f"Highest score ({best_score:.1f}) among {len(scored)} providers",
            estimated_cost=est_cost,
            estimated_latency_ms=est_latency,
            is_local=best_meta.is_local,
        )
        
        self._record_decision(decision)
        return decision
    
    async def route_and_invoke(self, capability: str,
                               input_data: Dict[str, Any],
                               options: Dict[str, Any] = None,
                               prefer_local: bool = None,
                               max_fallbacks: int = 3) -> Dict[str, Any]:
        """Route and execute with automatic fallback."""
        decision = self.route(capability, input_data, prefer_local)
        exclude = []
        
        for attempt in range(max_fallbacks + 1):
            plugin_id = decision.selected_plugin_id if attempt == 0 else (
                decision.fallback_chain[attempt - 1] if attempt - 1 < len(decision.fallback_chain) else None
            )
            
            if not plugin_id:
                break
            
            plugin = self.registry.get(plugin_id)
            if not plugin or plugin.status != PluginStatus.ACTIVE:
                exclude.append(plugin_id)
                continue
            
            start = time.time()
            try:
                result = await plugin.invoke(capability, input_data, options)
                latency = (time.time() - start) * 1000
                self.get_health(plugin_id).record_success(latency)
                
                return {
                    "output": result,
                    "provider": plugin_id,
                    "capability": capability,
                    "latency_ms": latency,
                    "fallback_used": attempt > 0,
                    "decision": decision.to_dict(),
                }
            except Exception as e:
                latency = (time.time() - start) * 1000
                self.get_health(plugin_id).record_failure()
                logger.warning(f"Provider {plugin_id} failed for {capability}: {e}")
                exclude.append(plugin_id)
                continue
        
        raise RuntimeError(f"All providers failed for capability '{capability}' after {attempt + 1} attempts")
    
    def _record_decision(self, decision: RoutingDecision):
        self._routing_history.append(decision)
        if len(self._routing_history) > self._max_history:
            self._routing_history = self._routing_history[-self._max_history:]
    
    def stats(self) -> Dict[str, Any]:
        total = len(self._routing_history)
        local_count = sum(1 for d in self._routing_history if d.is_local)
        fallback_count = sum(1 for d in self._routing_history if d.fallback_chain and d.fallback_chain[0] != d.selected_plugin_id)
        
        return {
            "total_routes": total,
            "local_routes": local_count,
            "local_ratio": (local_count / max(total, 1)) * 100,
            "providers_tracked": len(self._health),
            "circuit_open": sum(1 for h in self._health.values() if h.circuit_open),
            "avg_cost": sum(d.estimated_cost for d in self._routing_history) / max(total, 1),
            "avg_estimated_latency": sum(d.estimated_latency_ms for d in self._routing_history) / max(total, 1),
        }
    
    def health_report(self) -> Dict[str, Any]:
        return {
            "providers": {pid: h.to_dict() for pid, h in self._health.items()},
            "circuit_breakers": {
                pid: h.to_dict() for pid, h in self._health.items() if h.circuit_open
            },
        }
