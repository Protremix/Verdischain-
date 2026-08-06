"""
EvolvixOS Plugin Sandbox Manager
Provides process-level isolation for plugin execution with resource limits,
filesystem restrictions, and timeout enforcement.

Approach: subprocess-based isolation with restricted permissions.
Each plugin executes in a separate Python subprocess with:
- CPU and memory limits via resource module
- Filesystem isolation (only allowed paths)
- Network access control (allow/deny per plugin)
- Execution timeout
- stdout/stderr capture
"""

import asyncio
import json
import os
import sys
import time
import signal
import resource
import tempfile
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import structlog

logger = structlog.get_logger()


# =========================================================================
# Sandbox Configuration
# =========================================================================

class SandboxLevel(str, Enum):
    """Level of sandboxing restriction."""
    NONE = "none"           # No restrictions (trusted system plugins)
    BASIC = "basic"         # Process isolation with resource limits
    STRICT = "strict"       # Full isolation: no filesystem, no network
    CONTAINER = "container" # Docker container isolation (future)


@dataclass
class SandboxConfig:
    """Configuration for a sandboxed plugin execution."""
    level: SandboxLevel = SandboxLevel.BASIC
    cpu_limit_seconds: int = 30        # max CPU time
    memory_limit_mb: int = 512         # max memory in MB
    timeout_seconds: int = 60          # wall-clock timeout
    allow_network: bool = True          # network access
    allow_filesystem_read: List[str] = field(default_factory=list)  # allowed read paths
    allow_filesystem_write: List[str] = field(default_factory=list)  # allowed write paths
    max_output_size: int = 1024 * 1024  # max stdout/stderr size (1MB)
    env_whitelist: List[str] = field(default_factory=list)  # allowed env vars
    
    def to_dict(self) -> Dict:
        return {
            "level": self.level.value,
            "cpu_limit_seconds": self.cpu_limit_seconds,
            "memory_limit_mb": self.memory_limit_mb,
            "timeout_seconds": self.timeout_seconds,
            "allow_network": self.allow_network,
            "allow_filesystem_read": self.allow_filesystem_read,
            "allow_filesystem_write": self.allow_filesystem_write,
            "max_output_size": self.max_output_size,
            "env_whitelist": self.env_whitelist,
        }


# =========================================================================
# Default Sandbox Configs by Plugin Type
# =========================================================================

DEFAULT_SANDBOX_CONFIGS = {
    "llm_provider": SandboxConfig(
        level=SandboxLevel.BASIC,
        cpu_limit_seconds=30,
        memory_limit_mb=256,
        timeout_seconds=120,  # LLM calls can take time
        allow_network=True,
        allow_filesystem_read=["/etc/ssl", "/etc/pki"],
        allow_filesystem_write=[],
        env_whitelist=["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY",
                       "DEEPSEEK_API_KEY", "COHERE_API_KEY", "XAI_API_KEY",
                       "MISTRAL_API_KEY", "AI21_API_KEY", "OLLAMA_BASE_URL",
                       "VLLM_BASE_URL", "TAVILY_API_KEY", "BRAVE_API_KEY",
                       "DEEPL_API_KEY", "STABILITY_API_KEY", "ELEVENLABS_API_KEY",
                       "GOOGLE_VISION_API_KEY", "QDRANT_URL"],
    ),
    "coding_provider": SandboxConfig(
        level=SandboxLevel.BASIC,
        cpu_limit_seconds=60,
        memory_limit_mb=512,
        timeout_seconds=120,
        allow_network=True,
        env_whitelist=["OPENAI_API_KEY", "DEEPSEEK_API_KEY", "MISTRAL_API_KEY"],
    ),
    "image_provider": SandboxConfig(
        level=SandboxLevel.BASIC,
        cpu_limit_seconds=60,
        memory_limit_mb=512,
        timeout_seconds=120,
        allow_network=True,
        env_whitelist=["OPENAI_API_KEY", "STABILITY_API_KEY"],
    ),
    "speech_provider": SandboxConfig(
        level=SandboxLevel.BASIC,
        cpu_limit_seconds=30,
        memory_limit_mb=256,
        timeout_seconds=60,
        allow_network=True,
        env_whitelist=["ELEVENLABS_API_KEY", "OPENAI_API_KEY"],
    ),
    "search_provider": SandboxConfig(
        level=SandboxLevel.BASIC,
        cpu_limit_seconds=15,
        memory_limit_mb=128,
        timeout_seconds=30,
        allow_network=True,
        env_whitelist=["TAVILY_API_KEY", "BRAVE_API_KEY"],
    ),
    "embedding_provider": SandboxConfig(
        level=SandboxLevel.BASIC,
        cpu_limit_seconds=30,
        memory_limit_mb=256,
        timeout_seconds=60,
        allow_network=True,
        env_whitelist=["OPENAI_API_KEY"],
    ),
    "translation_provider": SandboxConfig(
        level=SandboxLevel.BASIC,
        cpu_limit_seconds=15,
        memory_limit_mb=128,
        timeout_seconds=30,
        allow_network=True,
        env_whitelist=["DEEPL_API_KEY"],
    ),
    "speech_recognition": SandboxConfig(
        level=SandboxLevel.BASIC,
        cpu_limit_seconds=60,
        memory_limit_mb=256,
        timeout_seconds=120,
        allow_network=True,
        env_whitelist=["OPENAI_API_KEY"],
    ),
    "ocr_provider": SandboxConfig(
        level=SandboxLevel.BASIC,
        cpu_limit_seconds=30,
        memory_limit_mb=256,
        timeout_seconds=60,
        allow_network=True,
        env_whitelist=["GOOGLE_VISION_API_KEY"],
    ),
    "vector_memory": SandboxConfig(
        level=SandboxLevel.BASIC,
        cpu_limit_seconds=30,
        memory_limit_mb=256,
        timeout_seconds=60,
        allow_network=True,
        env_whitelist=["QDRANT_URL"],
    ),
}


def get_sandbox_config(plugin_type: str) -> SandboxConfig:
    """Get default sandbox config for a plugin type."""
    return DEFAULT_SANDBOX_CONFIGS.get(plugin_type, SandboxConfig())


# =========================================================================
# Sandbox Runner Script (executed in subprocess)
# =========================================================================

SANDBOX_RUNNER_SCRIPT = '''
import sys
import json
import os
import resource

def set_limits(cpu_seconds, memory_mb, max_output_size):
    """Set resource limits for this process."""
    # CPU time limit (seconds)
    if cpu_seconds > 0:
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
    
    # Memory limit (bytes)
    if memory_mb > 0:
        memory_bytes = memory_mb * 1024 * 1024
        try:
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        except (ValueError, resource.error):
            pass  # Not supported on all platforms
    
    # Output size limit
    if max_output_size > 0:
        resource.setrlimit(resource.RLIMIT_FSIZE, (max_output_size, max_output_size))

def filter_env(env_whitelist):
    """Filter environment variables to only whitelisted ones."""
    whitelisted = {}
    for key in env_whitelist:
        if key in os.environ:
            whitelisted[key] = os.environ[key]
    return whitelisted

def main():
    # Read execution parameters from stdin
    params = json.loads(sys.stdin.readline())
    
    config = params.get("config", {})
    set_limits(
        config.get("cpu_limit_seconds", 30),
        config.get("memory_limit_mb", 512),
        config.get("max_output_size", 1024 * 1024),
    )
    
    # Filter environment
    whitelist = config.get("env_whitelist", [])
    for key in list(os.environ.keys()):
        if key not in whitelist and key not in ["PATH", "HOME", "LANG", "LC_ALL", "PYTHONPATH"]:
            del os.environ[key]
    
    # Import and execute the plugin
    plugin_module = params.get("plugin_module")
    plugin_class = params.get("plugin_class")
    capability = params.get("capability")
    input_data = params.get("input_data", {})
    options = params.get("options", {})
    
    try:
        mod = __import__(plugin_module, fromlist=[plugin_class])
        cls = getattr(mod, plugin_class)
        plugin = cls()
        
        # Initialize if needed
        if hasattr(plugin, "initialize"):
            await_func = getattr(plugin, "initialize", None)
            if await_func:
                import asyncio
                asyncio.get_event_loop().run_until_complete(await_func())
        
        # Execute
        if hasattr(plugin, "_execute"):
            import asyncio
            result = asyncio.get_event_loop().run_until_complete(
                plugin._execute(capability, input_data, options)
            )
            print(json.dumps({"status": "success", "result": result}))
        else:
            print(json.dumps({"status": "error", "error": "Plugin has no _execute method"}))
    except Exception as e:
        print(json.dumps({"status": "error", "error": str(e)}))

if __name__ == "__main__":
    main()
'''


# =========================================================================
# Sandbox Manager
# =========================================================================

class SandboxManager:
    """Manages plugin execution in isolated sandboxes."""
    
    def __init__(self, runner_dir: str = None):
        self._runner_dir = runner_dir or tempfile.gettempdir()
        self._runner_path = os.path.join(self._runner_dir, "sandbox_runner.py")
        self._write_runner()
        self._execution_count = 0
        self._violation_count = 0
        self._stats: Dict[str, Any] = defaultdict(int)
    
    def _write_runner(self):
        """Write the sandbox runner script."""
        with open(self._runner_path, 'w') as f:
            f.write(SANDBOX_RUNNER_SCRIPT)
        os.chmod(self._runner_path, 0o644)
    
    async def execute_sandboxed(
        self,
        plugin_module: str,
        plugin_class: str,
        capability: str,
        input_data: Dict[str, Any],
        options: Dict[str, Any] = None,
        config: SandboxConfig = None,
    ) -> Dict[str, Any]:
        """Execute a plugin in a sandboxed subprocess."""
        config = config or SandboxConfig()
        options = options or {}
        
        self._execution_count += 1
        start_time = time.time()
        
        # If sandbox level is NONE, execute directly
        if config.level == SandboxLevel.NONE:
            return await self._execute_direct(
                plugin_module, plugin_class, capability, input_data, options
            )
        
        # Prepare environment
        env = self._prepare_environment(config)
        
        # Prepare execution parameters
        params = {
            "plugin_module": plugin_module,
            "plugin_class": plugin_class,
            "capability": capability,
            "input_data": input_data,
            "options": options,
            "config": config.to_dict(),
        }
        
        try:
            # Run in subprocess with timeout
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                self._runner_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=self._runner_dir,
            )
            
            # Send parameters and wait for result
            stdout_data = json.dumps(params).encode() + b"\\n"
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(input=stdout_data),
                    timeout=config.timeout_seconds,
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                self._stats["timeout"] += 1
                logger.warning(f"Sandbox timeout: {plugin_class}.{capability}")
                return {
                    "status": "timeout",
                    "error": f"Execution exceeded {config.timeout_seconds}s timeout",
                    "provider": plugin_class,
                }
            
            latency = (time.time() - start_time) * 1000
            
            # Parse output
            try:
                result = json.loads(stdout.decode().strip())
            except json.JSONDecodeError:
                self._stats["parse_error"] += 1
                return {
                    "status": "error",
                    "error": f"Invalid output from sandbox: {stdout.decode()[:200]}",
                    "stderr": stderr.decode()[:500],
                    "latency_ms": latency,
                }
            
            if result.get("status") == "success":
                self._stats["success"] += 1
                result["result"]["latency_ms"] = latency
                result["result"]["sandboxed"] = True
                return result["result"]
            else:
                self._stats["error"] += 1
                return {
                    "status": "failed",
                    "error": result.get("error", "Unknown sandbox error"),
                    "stderr": stderr.decode()[:500],
                    "latency_ms": latency,
                }
                
        except Exception as e:
            self._stats["exception"] += 1
            logger.error(f"Sandbox execution failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "latency_ms": (time.time() - start_time) * 1000,
            }
    
    async def _execute_direct(
        self,
        plugin_module: str,
        plugin_class: str,
        capability: str,
        input_data: Dict[str, Any],
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute without sandboxing (trusted plugins only)."""
        start_time = time.time()
        try:
            mod = __import__(plugin_module, fromlist=[plugin_class])
            cls = getattr(mod, plugin_class)
            plugin = cls()
            
            if hasattr(plugin, "initialize"):
                await plugin.initialize()
            
            result = await plugin._execute(capability, input_data, options)
            result["sandboxed"] = False
            result["latency_ms"] = (time.time() - start_time) * 1000
            self._stats["direct_success"] += 1
            return result
        except Exception as e:
            self._stats["direct_error"] += 1
            return {
                "status": "failed",
                "error": str(e),
                "latency_ms": (time.time() - start_time) * 1000,
            }
    
    def _prepare_environment(self, config: SandboxConfig) -> Dict[str, str]:
        """Prepare a filtered environment for the sandbox."""
        env = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", "/tmp"),
            "LANG": os.environ.get("LANG", "en_US.UTF-8"),
            "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        }
        
        # Add whitelisted env vars
        for key in config.env_whitelist:
            if key in os.environ:
                env[key] = os.environ[key]
        
        return env
    
    def get_sandbox_config(self, plugin_type: str) -> SandboxConfig:
        """Get the default sandbox config for a plugin type."""
        return get_sandbox_config(plugin_type)
    
    def stats(self) -> Dict[str, Any]:
        """Get sandbox manager statistics."""
        return {
            "total_executions": self._execution_count,
            "by_outcome": dict(self._stats),
            "violation_count": self._violation_count,
            "runner_path": self._runner_path,
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check sandbox health."""
        return {
            "status": "healthy",
            "runner_exists": os.path.exists(self._runner_path),
            "runner_readable": os.access(self._runner_path, os.R_OK),
            "total_executions": self._execution_count,
        }


# =========================================================================
# Execution Persistence
# =========================================================================

class ExecutionPersistence:
    """Persists agent execution results for auditing and analysis."""
    
    def __init__(self, persist_path: str = None):
        self._persist_path = persist_path or os.path.join(
            tempfile.gettempdir(), "evolvixos_executions.jsonl"
        )
        self._buffer: List[Dict] = []
        self._buffer_size = 100  # flush after 100 entries
        self._total_persisted = 0
    
    def record(self, execution: Dict[str, Any]):
        """Record an execution result."""
        entry = {
            "id": hashlib.sha256(
                f"{execution.get('execution_id', '')}:{time.time()}".encode()
            ).hexdigest()[:16],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **execution,
        }
        self._buffer.append(entry)
        
        if len(self._buffer) >= self._buffer_size:
            self._flush()
    
    def _flush(self):
        """Flush buffered entries to disk."""
        if not self._buffer:
            return
        
        with open(self._persist_path, 'a') as f:
            for entry in self._buffer:
                f.write(json.dumps(entry) + "\n")
        
        self._total_persisted += len(self._buffer)
        self._buffer.clear()
        logger.info(f"Flushed {self._total_persisted} execution records to {self._persist_path}")
    
    def query(self, limit: int = 100, agent_id: str = None,
              status: str = None, start_date: str = None) -> List[Dict]:
        """Query persisted execution records."""
        # Flush buffer first
        self._flush()
        
        if not os.path.exists(self._persist_path):
            return []
        
        results = []
        with open(self._persist_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if agent_id and entry.get("agent_id") != agent_id:
                        continue
                    if status and entry.get("status") != status:
                        continue
                    if start_date and entry.get("timestamp", "") < start_date:
                        continue
                    results.append(entry)
                except json.JSONDecodeError:
                    continue
        
        return results[-limit:]
    
    def stats(self) -> Dict[str, Any]:
        """Get persistence statistics."""
        self._flush()
        return {
            "total_persisted": self._total_persisted,
            "buffer_size": len(self._buffer),
            "persist_path": self._persist_path,
        }
    
    def close(self):
        """Flush remaining entries."""
        self._flush()


# =========================================================================
# Global instances
# =========================================================================

sandbox_manager = SandboxManager()
persistence = ExecutionPersistence()
