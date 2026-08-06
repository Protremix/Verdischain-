"""
EvolvixOS Monitoring — Prometheus Metrics for AI Gateway + Agent Framework
Exposes /metrics endpoint for Prometheus scraping
"""

import time
import threading
from collections import defaultdict
from typing import Dict, Any
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger()

# =========================================================================
# Metrics Collector (Singleton)
# =========================================================================

class MetricsCollector:
    """Thread-safe metrics collector for Prometheus export"""
    
    def __init__(self):
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()
        
        # Initialize default metrics
        self._gauges["evolvixos_gateway_active_plugins"] = 0
        self._gauges["evolvixos_gateway_cache_size"] = 0
        self._gauges["evolvixos_gateway_cache_hit_rate"] = 0
        self._gauges["evolvixos_agent_total"] = 0
        self._gauges["evolvixos_agent_running"] = 0
        self._gauges["evolvixos_agent_total_tasks"] = 0
        self._gauges["evolvixos_agent_running_tasks"] = 0
        self._counters["evolvixos_gateway_requests_total"] = 0
        self._counters["evolvixos_gateway_errors_total"] = 0
        self._counters["evolvixos_gateway_cache_hits_total"] = 0
        self._counters["evolvixos_gateway_cache_misses_total"] = 0
        self._counters["evolvixos_agent_tasks_completed_total"] = 0
        self._counters["evolvixos_agent_tasks_failed_total"] = 0
        self._counters["evolvixos_agent_tokens_used_total"] = 0
    
    def increment(self, name: str, value: float = 1):
        with self._lock:
            self._counters[name] += value
    
    def set_gauge(self, name: str, value: float):
        with self._lock:
            self._gauges[name] = value
    
    def observe(self, name: str, value: float):
        with self._lock:
            self._histograms[name].append(value)
            if len(self._histograms[name]) > 1000:
                self._histograms[name] = self._histograms[name][-1000:]
    
    def record_latency(self, name: str, latency_ms: float):
        self.observe(f"{name}_latency_ms", latency_ms)
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus text format"""
        lines = []
        
        # Counters
        for name, value in sorted(self._counters.items()):
            metric_name = name
            help_text = self._get_help(metric_name)
            metric_type = "counter"
            lines.append(f"# HELP {metric_name} {help_text}")
            lines.append(f"# TYPE {metric_name} {metric_type}")
            lines.append(f"{metric_name} {value}")
        
        # Gauges
        for name, value in sorted(self._gauges.items()):
            help_text = self._get_help(name)
            lines.append(f"# HELP {name} {help_text}")
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")
        
        # Histograms (summary stats)
        for name, values in sorted(self._histograms.items()):
            if not values:
                continue
            help_text = self._get_help(name)
            lines.append(f"# HELP {name} {help_text}")
            lines.append(f"# TYPE {name} summary")
            
            sorted_vals = sorted(values)
            count = len(sorted_vals)
            avg = sum(sorted_vals) / count
            p50 = sorted_vals[int(count * 0.5)]
            p95 = sorted_vals[int(count * 0.95)] if count > 20 else sorted_vals[-1]
            p99 = sorted_vals[int(count * 0.99)] if count > 100 else sorted_vals[-1]
            
            lines.append(f'{name}{{quantile="0.5"}} {p50}')
            lines.append(f'{name}{{quantile="0.95"}} {p95}')
            lines.append(f'{name}{{quantile="0.99"}} {p99}')
            lines.append(f'{name}_sum {sum(sorted_vals)}')
            lines.append(f'{name}_count {count}')
        
        return "\n".join(lines) + "\n"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get metrics as a dictionary"""
        with self._lock:
            stats = {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
            }
            # Histogram summaries
            for name, values in self._histograms.items():
                if values:
                    sorted_vals = sorted(values)
                    count = len(sorted_vals)
                    stats[name] = {
                        "count": count,
                        "avg": sum(sorted_vals) / count,
                        "p50": sorted_vals[int(count * 0.5)],
                        "p95": sorted_vals[int(count * 0.95)] if count > 20 else sorted_vals[-1],
                    }
            return stats
    
    def _get_help(self, name: str) -> str:
        help_map = {
            "evolvixos_gateway_requests_total": "Total gateway requests",
            "evolvixos_gateway_errors_total": "Total gateway errors",
            "evolvixos_gateway_cache_hits_total": "Total cache hits",
            "evolvixos_gateway_cache_misses_total": "Total cache misses",
            "evolvixos_gateway_active_plugins": "Number of active plugins",
            "evolvixos_gateway_cache_size": "Current cache size",
            "evolvixos_gateway_cache_hit_rate": "Cache hit rate percentage",
            "evolvixos_agent_total": "Total agents",
            "evolvixos_agent_running": "Running agents",
            "evolvixos_agent_total_tasks": "Total tasks",
            "evolvixos_agent_running_tasks": "Running tasks",
            "evolvixos_agent_tasks_completed_total": "Total completed tasks",
            "evolvixos_agent_tasks_failed_total": "Total failed tasks",
            "evolvixos_agent_tokens_used_total": "Total tokens used by agents",
        }
        return help_map.get(name, name.replace("_", " ").title())


# Global collector instance
metrics = MetricsCollector()


# =========================================================================
# Metrics Updater — Background thread to pull stats from services
# =========================================================================

class MetricsUpdater:
    """Background thread that updates metrics from live services"""
    
    def __init__(self, gateway_url: str = "http://localhost:3500",
                 agent_url: str = "http://localhost:3600",
                 update_interval: int = 15):
        self.gateway_url = gateway_url
        self.agent_url = agent_url
        self.update_interval = update_interval
        self._running = False
        self._thread = None
    
    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()
        logger.info("Metrics updater started")
    
    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
    
    def _update_loop(self):
        import httpx
        while self._running:
            try:
                # Update gateway metrics
                try:
                    with httpx.Client(timeout=5) as client:
                        resp = client.get(f"{self.gateway_url}/health")
                        if resp.status_code == 200:
                            data = resp.json()
                            metrics.set_gauge("evolvixos_gateway_active_plugins", 
                                             data.get("plugins", {}).get("active", 0))
                            metrics.set_gauge("evolvixos_gateway_cache_size",
                                             data.get("cache", {}).get("size", 0))
                            cache = data.get("cache", {})
                            hits = cache.get("hits", 0)
                            misses = cache.get("misses", 0)
                            total = hits + misses
                            hit_rate = (hits / total * 100) if total > 0 else 0
                            metrics.set_gauge("evolvixos_gateway_cache_hit_rate", hit_rate)
                except Exception as e:
                    logger.debug(f"Gateway metrics update failed: {e}")
                
                # Update agent framework metrics
                try:
                    with httpx.Client(timeout=5) as client:
                        resp = client.get(f"{self.agent_url}/stats")
                        if resp.status_code == 200:
                            data = resp.json()
                            metrics.set_gauge("evolvixos_agent_total", data.get("total_agents", 0))
                            agents_by_status = data.get("agents_by_status", {})
                            metrics.set_gauge("evolvixos_agent_running", 
                                             agents_by_status.get("running", 0))
                            metrics.set_gauge("evolvixos_agent_total_tasks", data.get("total_tasks", 0))
                            metrics.set_gauge("evolvixos_agent_running_tasks", 
                                             data.get("running_tasks", 0))
                            metrics.set_gauge("evolvixos_agent_tokens_used", 
                                             data.get("total_tokens_used", 0))
                except Exception as e:
                    logger.debug(f"Agent metrics update failed: {e}")
                
            except Exception as e:
                logger.error(f"Metrics update error: {e}")
            
            time.sleep(self.update_interval)


# Global updater instance
updater = MetricsUpdater()
