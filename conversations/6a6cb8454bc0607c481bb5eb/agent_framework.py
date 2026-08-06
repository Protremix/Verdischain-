"""
EvolvixOS Agent Framework — Core Module
Agent lifecycle management, task execution, and long-term memory

Architecture:
- Agent: Autonomous entity with capabilities, memory, and task queue
- Task: Unit of work assigned to an agent (executed via AI Gateway or custom handlers)
- Memory: Persistent context storage (PostgreSQL-backed with JSONB)
- Scheduler: Manages agent execution lifecycle (start, run, stop, restart)
"""

import os
import json
import uuid
import time
import asyncio
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import threading
import structlog

logger = structlog.get_logger()

# =========================================================================
# Enums
# =========================================================================

class AgentStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    TERMINATED = "terminated"

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class TaskPriority(int, Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class MemoryType(str, Enum):
    SHORT_TERM = "short_term"      # Current session context
    LONG_TERM = "long_term"         # Persistent across sessions
    EPISODIC = "episodic"           # Event-based memories
    SEMANTIC = "semantic"          # Knowledge/facts
    PROCEDURAL = "procedural"       # How-to knowledge

class AgentCapability(str, Enum):
    CHAT = "chat"
    CODE_REVIEW = "code_review"
    SENTIMENT = "sentiment"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    CUSTOM = "custom"

# =========================================================================
# Data Models
# =========================================================================

@dataclass
class MemoryEntry:
    """A single memory entry for an agent"""
    id: str
    agent_id: str
    memory_type: MemoryType
    key: str                    # Lookup key (e.g., "user_preference", "project_context")
    value: Any                  # JSON-serializable value
    context: Dict[str, Any] = field(default_factory=dict)  # Additional context metadata
    importance: float = 0.5     # 0.0-1.0, affects retention priority
    created_at: str = ""
    updated_at: str = ""
    last_accessed: str = ""
    access_count: int = 0
    expires_at: Optional[str] = None  # TTL-based expiry

    def __post_init__(self):
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
        if not self.last_accessed:
            self.last_accessed = now
        if not self.id:
            self.id = uuid.uuid4().hex

    def touch(self):
        """Update last_accessed and increment access_count"""
        self.last_accessed = datetime.now(timezone.utc).isoformat()
        self.access_count += 1

    def is_expired(self) -> bool:
        if self.expires_at:
            return datetime.fromisoformat(self.expires_at.replace("Z", "+00:00")) < datetime.now(timezone.utc)
        return False

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "memory_type": self.memory_type.value,
            "key": self.key,
            "value": self.value,
            "context": self.context,
            "importance": self.importance,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "expires_at": self.expires_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "MemoryEntry":
        return cls(
            id=data.get("id", uuid.uuid4().hex),
            agent_id=data["agent_id"],
            memory_type=MemoryType(data.get("memory_type", "long_term")),
            key=data["key"],
            value=data.get("value"),
            context=data.get("context", {}),
            importance=data.get("importance", 0.5),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            last_accessed=data.get("last_accessed", ""),
            access_count=data.get("access_count", 0),
            expires_at=data.get("expires_at"),
        )


@dataclass
class Task:
    """A unit of work for an agent"""
    id: str
    agent_id: str
    task_type: str               # e.g., "chat", "code_review", "sentiment", "custom"
    input_data: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str = ""
    started_at: str = ""
    completed_at: str = ""
    timeout_seconds: int = 120
    retry_count: int = 0
    max_retries: int = 3
    parent_task_id: Optional[str] = None  # For subtasks
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = uuid.uuid4().hex
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "task_type": self.task_type,
            "input_data": self.input_data,
            "priority": self.priority.value,
            "status": self.status.value,
            "output_data": self.output_data,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "parent_task_id": self.parent_task_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Task":
        return cls(
            id=data.get("id", uuid.uuid4().hex),
            agent_id=data["agent_id"],
            task_type=data["task_type"],
            input_data=data.get("input_data", {}),
            priority=TaskPriority(data.get("priority", 2)),
            status=TaskStatus(data.get("status", "pending")),
            output_data=data.get("output_data"),
            error=data.get("error"),
            created_at=data.get("created_at", ""),
            started_at=data.get("started_at", ""),
            completed_at=data.get("completed_at", ""),
            timeout_seconds=data.get("timeout_seconds", 120),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            parent_task_id=data.get("parent_task_id"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Agent:
    """An autonomous AI agent"""
    id: str
    name: str
    description: str = ""
    capabilities: List[AgentCapability] = field(default_factory=list)
    status: AgentStatus = AgentStatus.CREATED
    config: Dict[str, Any] = field(default_factory=dict)
    system_prompt: str = ""
    model: str = "gpt-4o"
    memory_ids: List[str] = field(default_factory=list)
    task_history: List[str] = field(default_factory=list)
    current_task_id: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    last_active: str = ""
    error_count: int = 0
    success_count: int = 0
    total_tokens_used: int = 0
    max_concurrent_tasks: int = 1
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        now = datetime.now(timezone.utc).isoformat()
        if not self.id:
            self.id = uuid.uuid4().hex
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
        if not self.last_active:
            self.last_active = now

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "capabilities": [c.value for c in self.capabilities],
            "status": self.status.value,
            "config": self.config,
            "system_prompt": self.system_prompt,
            "model": self.model,
            "memory_ids": self.memory_ids,
            "task_history": self.task_history[-50:],  # Last 50 tasks
            "current_task_id": self.current_task_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_active": self.last_active,
            "error_count": self.error_count,
            "success_count": self.success_count,
            "total_tokens_used": self.total_tokens_used,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Agent":
        return cls(
            id=data.get("id", uuid.uuid4().hex),
            name=data["name"],
            description=data.get("description", ""),
            capabilities=[AgentCapability(c) for c in data.get("capabilities", [])],
            status=AgentStatus(data.get("status", "created")),
            config=data.get("config", {}),
            system_prompt=data.get("system_prompt", ""),
            model=data.get("model", "gpt-4o"),
            memory_ids=data.get("memory_ids", []),
            task_history=data.get("task_history", []),
            current_task_id=data.get("current_task_id"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            last_active=data.get("last_active", ""),
            error_count=data.get("error_count", 0),
            success_count=data.get("success_count", 0),
            total_tokens_used=data.get("total_tokens_used", 0),
            max_concurrent_tasks=data.get("max_concurrent_tasks", 1),
            tags=data.get("tags", []),
        )

    def touch(self):
        self.last_active = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.last_active


# =========================================================================
# Long-Term Memory Manager
# =========================================================================

class MemoryManager:
    """Manages persistent agent memory with PostgreSQL backend"""

    def __init__(self, db_url: str = None):
        self.db_url = db_url or os.getenv("DATABASE_URL", "postgresql://evolvixos:evolvixos@localhost:5432/evolvixos")
        self._store: Dict[str, Dict[str, MemoryEntry]] = defaultdict(dict)  # agent_id -> {memory_id -> entry}
        self._key_index: Dict[str, Dict[str, str]] = defaultdict(dict)  # agent_id -> {key -> memory_id}
        self._use_db = False
        self._init_db()

    def _init_db(self):
        """Initialize database table"""
        try:
            import psycopg2
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_memories (
                    id VARCHAR(64) PRIMARY KEY,
                    agent_id VARCHAR(64) NOT NULL,
                    memory_type VARCHAR(32) NOT NULL,
                    key TEXT NOT NULL,
                    value JSONB NOT NULL,
                    context JSONB DEFAULT '{}',
                    importance FLOAT DEFAULT 0.5,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    access_count INTEGER DEFAULT 0,
                    expires_at TIMESTAMP WITH TIME ZONE
                );
                CREATE INDEX IF NOT EXISTS idx_agent_memories_agent_id ON agent_memories(agent_id);
                CREATE INDEX IF NOT EXISTS idx_agent_memories_key ON agent_memories(agent_id, key);
                CREATE INDEX IF NOT EXISTS idx_agent_memories_type ON agent_memories(agent_id, memory_type);
                CREATE INDEX IF NOT EXISTS idx_agent_memories_importance ON agent_memories(agent_id, importance DESC);
            """)
            conn.commit()
            cursor.close()
            conn.close()
            self._use_db = True
            logger.info("Agent memory database initialized")
        except Exception as e:
            logger.warning(f"Database not available, using in-memory storage: {e}")
            self._use_db = False

    def store(self, agent_id: str, key: str, value: Any,
              memory_type: MemoryType = MemoryType.LONG_TERM,
              context: Dict = None, importance: float = 0.5,
              ttl_seconds: Optional[int] = None) -> MemoryEntry:
        """Store a memory entry. Overwrites if key exists for this agent."""
        expires_at = None
        if ttl_seconds:
            expires_at = (datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)).isoformat()

        entry = MemoryEntry(
            id=uuid.uuid4().hex,
            agent_id=agent_id,
            memory_type=memory_type,
            key=key,
            value=value,
            context=context or {},
            importance=importance,
            expires_at=expires_at,
        )

        # Remove existing entry with same key
        if key in self._key_index[agent_id]:
            old_id = self._key_index[agent_id][key]
            self._store[agent_id].pop(old_id, None)

        # Store new entry
        self._store[agent_id][entry.id] = entry
        self._key_index[agent_id][key] = entry.id

        # Persist to database
        if self._use_db:
            self._db_store(entry)

        return entry

    def retrieve(self, agent_id: str, key: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by key"""
        # Check in-memory first
        if key in self._key_index[agent_id]:
            entry_id = self._key_index[agent_id][key]
            entry = self._store[agent_id].get(entry_id)
            if entry and not entry.is_expired():
                entry.touch()
                if self._use_db:
                    self._db_touch(entry)
                return entry
            elif entry and entry.is_expired():
                self.delete(agent_id, key)
                return None

        # Check database
        if self._use_db:
            entry = self._db_retrieve(agent_id, key)
            if entry:
                self._store[agent_id][entry.id] = entry
                self._key_index[agent_id][key] = entry.id
                entry.touch()
                self._db_touch(entry)
                return entry

        return None

    def retrieve_all(self, agent_id: str, memory_type: Optional[MemoryType] = None) -> List[MemoryEntry]:
        """Retrieve all memories for an agent, optionally filtered by type"""
        results = []

        # From in-memory
        for entry in self._store[agent_id].values():
            if not entry.is_expired():
                if memory_type is None or entry.memory_type == memory_type:
                    results.append(entry)

        # From database if not enough in-memory
        if self._use_db:
            db_entries = self._db_retrieve_all(agent_id, memory_type)
            existing_ids = {e.id for e in results}
            for entry in db_entries:
                if entry.id not in existing_ids and not entry.is_expired():
                    results.append(entry)
                    self._store[agent_id][entry.id] = entry
                    self._key_index[agent_id][entry.key] = entry.id

        return results

    def search(self, agent_id: str, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Search memories by key or value content"""
        results = []
        query_lower = query.lower()

        for entry in self.retrieve_all(agent_id):
            if query_lower in entry.key.lower() or (
                isinstance(entry.value, str) and query_lower in entry.value.lower()
            ) or (
                isinstance(entry.value, dict) and query_lower in json.dumps(entry.value).lower()
            ):
                results.append(entry)

        # Sort by importance and access count
        results.sort(key=lambda e: (e.importance, e.access_count), reverse=True)
        return results[:limit]

    def update(self, agent_id: str, key: str, value: Any,
               importance: Optional[float] = None) -> Optional[MemoryEntry]:
        """Update an existing memory entry"""
        entry = self.retrieve(agent_id, key)
        if not entry:
            return None

        entry.value = value
        entry.updated_at = datetime.now(timezone.utc).isoformat()
        if importance is not None:
            entry.importance = importance

        if self._use_db:
            self._db_store(entry)

        return entry

    def delete(self, agent_id: str, key: str) -> bool:
        """Delete a memory entry by key"""
        if key in self._key_index[agent_id]:
            entry_id = self._key_index[agent_id][key]
            self._store[agent_id].pop(entry_id, None)
            del self._key_index[agent_id][key]

            if self._use_db:
                self._db_delete(entry_id)

            return True
        return False

    def clear_agent(self, agent_id: str) -> int:
        """Clear all memories for an agent. Returns count deleted."""
        count = len(self._store[agent_id])
        self._store[agent_id].clear()
        self._key_index[agent_id].clear()

        if self._use_db:
            try:
                import psycopg2
                conn = psycopg2.connect(self.db_url)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM agent_memories WHERE agent_id = %s", (agent_id,))
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                logger.error(f"Failed to clear agent memories from DB: {e}")

        return count

    def get_stats(self, agent_id: str) -> Dict:
        """Get memory statistics for an agent"""
        entries = self.retrieve_all(agent_id)
        by_type = defaultdict(int)
        total_importance = 0.0
        total_access = 0

        for entry in entries:
            by_type[entry.memory_type.value] += 1
            total_importance += entry.importance
            total_access += entry.access_count

        return {
            "total_memories": len(entries),
            "by_type": dict(by_type),
            "avg_importance": total_importance / max(len(entries), 1),
            "total_accesses": total_access,
        }

    def cleanup_expired(self, agent_id: Optional[str] = None) -> int:
        """Remove expired memories. Returns count deleted."""
        count = 0
        agent_ids = [agent_id] if agent_id else list(self._store.keys())

        for aid in agent_ids:
            expired_keys = []
            for key, entry_id in list(self._key_index[aid].items()):
                entry = self._store[aid].get(entry_id)
                if entry and entry.is_expired():
                    expired_keys.append(key)

            for key in expired_keys:
                self.delete(aid, key)
                count += 1

        return count

    # --- Database operations ---

    def _db_store(self, entry: MemoryEntry):
        try:
            import psycopg2
            from psycopg2.extras import Json
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_memories (id, agent_id, memory_type, key, value, context, importance, created_at, updated_at, last_accessed, access_count, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    value = EXCLUDED.value,
                    context = EXCLUDED.context,
                    importance = EXCLUDED.importance,
                    updated_at = EXCLUDED.updated_at,
                    last_accessed = EXCLUDED.last_accessed,
                    access_count = EXCLUDED.access_count,
                    expires_at = EXCLUDED.expires_at
            """, (
                entry.id, entry.agent_id, entry.memory_type.value, entry.key,
                Json(entry.value), Json(entry.context), entry.importance,
                entry.created_at, entry.updated_at, entry.last_accessed,
                entry.access_count, entry.expires_at,
            ))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"DB store failed: {e}")

    def _db_retrieve(self, agent_id: str, key: str) -> Optional[MemoryEntry]:
        try:
            import psycopg2
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, agent_id, memory_type, key, value, context, importance,
                       created_at, updated_at, last_accessed, access_count, expires_at
                FROM agent_memories
                WHERE agent_id = %s AND key = %s
            """, (agent_id, key))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row:
                return MemoryEntry(
                    id=row[0], agent_id=row[1], memory_type=MemoryType(row[2]),
                    key=row[3], value=row[4], context=row[5], importance=row[6],
                    created_at=row[7].isoformat() if row[7] else "",
                    updated_at=row[8].isoformat() if row[8] else "",
                    last_accessed=row[9].isoformat() if row[9] else "",
                    access_count=row[10], expires_at=row[11].isoformat() if row[11] else None,
                )
        except Exception as e:
            logger.error(f"DB retrieve failed: {e}")
        return None

    def _db_retrieve_all(self, agent_id: str, memory_type: Optional[MemoryType] = None) -> List[MemoryEntry]:
        try:
            import psycopg2
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            if memory_type:
                cursor.execute("""
                    SELECT id, agent_id, memory_type, key, value, context, importance,
                           created_at, updated_at, last_accessed, access_count, expires_at
                    FROM agent_memories
                    WHERE agent_id = %s AND memory_type = %s
                    ORDER BY importance DESC, access_count DESC
                """, (agent_id, memory_type.value))
            else:
                cursor.execute("""
                    SELECT id, agent_id, memory_type, key, value, context, importance,
                           created_at, updated_at, last_accessed, access_count, expires_at
                    FROM agent_memories
                    WHERE agent_id = %s
                    ORDER BY importance DESC, access_count DESC
                """, (agent_id,))

            entries = []
            for row in cursor.fetchall():
                entries.append(MemoryEntry(
                    id=row[0], agent_id=row[1], memory_type=MemoryType(row[2]),
                    key=row[3], value=row[4], context=row[5], importance=row[6],
                    created_at=row[7].isoformat() if row[7] else "",
                    updated_at=row[8].isoformat() if row[8] else "",
                    last_accessed=row[9].isoformat() if row[9] else "",
                    access_count=row[10], expires_at=row[11].isoformat() if row[11] else None,
                ))
            cursor.close()
            conn.close()
            return entries
        except Exception as e:
            logger.error(f"DB retrieve_all failed: {e}")
            return []

    def _db_touch(self, entry: MemoryEntry):
        try:
            import psycopg2
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE agent_memories
                SET last_accessed = %s, access_count = %s
                WHERE id = %s
            """, (entry.last_accessed, entry.access_count, entry.id))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"DB touch failed: {e}")

    def _db_delete(self, entry_id: str):
        try:
            import psycopg2
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM agent_memories WHERE id = %s", (entry_id,))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"DB delete failed: {e}")


# =========================================================================
# Agent Manager
# =========================================================================

class AgentManager:
    """Manages agent lifecycle and task execution"""

    def __init__(self, memory_manager: MemoryManager, gateway_url: str = "http://localhost:3500"):
        self.memory = memory_manager
        self.gateway_url = gateway_url
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self._task_queue: List[str] = []  # Task IDs ordered by priority
        self._running_tasks: Dict[str, asyncio.Task] = {}  # task_id -> asyncio task
        self._agent_registry_file = os.getenv("AGENT_REGISTRY_FILE", "/app/agent_registry.json")
        self._task_history_file = os.getenv("TASK_HISTORY_FILE", "/app/task_history.json")
        self._load_agents()

    def _load_agents(self):
        """Load agents from registry file"""
        if os.path.exists(self._agent_registry_file):
            try:
                with open(self._agent_registry_file) as f:
                    data = json.load(f)
                for agent_data in data.get("agents", []):
                    agent = Agent.from_dict(agent_data)
                    self.agents[agent.id] = agent
                logger.info(f"Loaded {len(self.agents)} agents from registry")
            except Exception as e:
                logger.error(f"Failed to load agent registry: {e}")

    def _save_agents(self):
        """Save agents to registry file"""
        try:
            data = {
                "version": "1.0.0",
                "agents": [a.to_dict() for a in self.agents.values()]
            }
            with open(self._agent_registry_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save agent registry: {e}")

    def create_agent(self, name: str, description: str = "",
                     capabilities: List[AgentCapability] = None,
                     system_prompt: str = "", model: str = "gpt-4o",
                     config: Dict = None, tags: List[str] = None) -> Agent:
        """Create a new agent"""
        agent = Agent(
            id=uuid.uuid4().hex,
            name=name,
            description=description,
            capabilities=capabilities or [AgentCapability.CHAT],
            system_prompt=system_prompt,
            model=model,
            config=config or {},
            tags=tags or [],
        )
        self.agents[agent.id] = agent
        self._save_agents()
        logger.info(f"Created agent: {name} ({agent.id})")
        return agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self.agents.get(agent_id)

    def list_agents(self, status: Optional[AgentStatus] = None) -> List[Agent]:
        if status:
            return [a for a in self.agents.values() if a.status == status]
        return list(self.agents.values())

    def update_agent(self, agent_id: str, **kwargs) -> Optional[Agent]:
        """Update agent properties"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None

        for key, value in kwargs.items():
            if hasattr(agent, key) and key not in ("id", "created_at"):
                if key == "capabilities" and isinstance(value, list):
                    value = [AgentCapability(c) if isinstance(c, str) else c for c in value]
                setattr(agent, key, value)

        agent.touch()
        self._save_agents()
        return agent

    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent and its memories"""
        if agent_id not in self.agents:
            return False

        # Clear memories
        self.memory.clear_agent(agent_id)

        # Cancel any running tasks
        for task_id, agent_task in list(self._running_tasks.items()):
            if self.tasks.get(task_id) and self.tasks[task_id].agent_id == agent_id:
                agent_task.cancel()
                self._running_tasks.pop(task_id, None)

        del self.agents[agent_id]
        self._save_agents()
        logger.info(f"Deleted agent: {agent_id}")
        return True

    def start_agent(self, agent_id: str) -> bool:
        """Start an agent (transition to running state)"""
        agent = self.agents.get(agent_id)
        if not agent:
            return False
        if agent.status in (AgentStatus.RUNNING,):
            return True
        agent.status = AgentStatus.RUNNING
        agent.touch()
        self._save_agents()
        logger.info(f"Agent started: {agent.name}")
        return True

    def pause_agent(self, agent_id: str) -> bool:
        """Pause an agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            return False
        agent.status = AgentStatus.PAUSED
        agent.touch()
        self._save_agents()
        return True

    def stop_agent(self, agent_id: str) -> bool:
        """Stop an agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            return False
        agent.status = AgentStatus.STOPPED
        agent.touch()
        self._save_agents()
        return True

    def create_task(self, agent_id: str, task_type: str,
                    input_data: Dict[str, Any],
                    priority: TaskPriority = TaskPriority.NORMAL,
                    timeout: int = 120,
                    parent_task_id: str = None) -> Optional[Task]:
        """Create a task for an agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None

        if agent.status != AgentStatus.RUNNING:
            return None

        task = Task(
            id=uuid.uuid4().hex,
            agent_id=agent_id,
            task_type=task_type,
            input_data=input_data,
            priority=priority,
            timeout_seconds=timeout,
            parent_task_id=parent_task_id,
        )

        self.tasks[task.id] = task
        self._task_queue.append(task.id)
        agent.task_history.append(task.id)
        agent.current_task_id = task.id
        agent.touch()
        self._save_agents()

        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def list_tasks(self, agent_id: Optional[str] = None,
                   status: Optional[TaskStatus] = None,
                   limit: int = 50) -> List[Task]:
        """List tasks, optionally filtered by agent and/or status"""
        tasks = list(self.tasks.values())

        if agent_id:
            tasks = [t for t in tasks if t.agent_id == agent_id]
        if status:
            tasks = [t for t in tasks if t.status == status]

        # Sort by created_at descending
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks[:limit]

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task"""
        task = self.tasks.get(task_id)
        if not task or task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
            return False

        # Cancel asyncio task if running
        if task_id in self._running_tasks:
            self._running_tasks[task_id].cancel()
            self._running_tasks.pop(task_id, None)

        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now(timezone.utc).isoformat()

        # Clear agent current task
        agent = self.agents.get(task.agent_id)
        if agent and agent.current_task_id == task_id:
            agent.current_task_id = None
            agent.touch()

        return True

    async def execute_task(self, task_id: str) -> Optional[Task]:
        """Execute a task by calling the AI Gateway"""
        task = self.tasks.get(task_id)
        if not task:
            return None

        agent = self.agents.get(task.agent_id)
        if not agent or agent.status != AgentStatus.RUNNING:
            task.status = TaskStatus.FAILED
            task.error = "Agent not available or not running"
            return task

        # Mark task as running
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc).isoformat()
        agent.touch()

        try:
            # Build gateway request
            gateway_input = self._build_gateway_input(task, agent)

            # Call AI Gateway
            import httpx
            async with httpx.AsyncClient(timeout=task.timeout_seconds) as client:
                response = await client.post(
                    f"{self.gateway_url}/gateway/invoke",
                    json={
                        "capability": task.task_type,
                        "input": gateway_input,
                        "options": {
                            "capability": task.task_type,
                            "model": agent.model,
                            "max_tokens": agent.config.get("max_tokens", 4096),
                        },
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    task.output_data = result
                    task.status = TaskStatus.COMPLETED
                    agent.success_count += 1
                    agent.total_tokens_used += result.get("tokens_used", 0)

                    # Store result in memory
                    self.memory.store(
                        agent_id=agent.id,
                        key=f"task_result:{task.id}",
                        value=result,
                        memory_type=MemoryType.EPISODIC,
                        importance=0.3,
                    )
                else:
                    task.status = TaskStatus.FAILED
                    task.error = f"Gateway returned {response.status_code}: {response.text}"
                    agent.error_count += 1

        except asyncio.TimeoutError:
            task.status = TaskStatus.TIMEOUT
            task.error = "Task timed out"
            agent.error_count += 1
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            agent.error_count += 1

            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                logger.info(f"Retrying task {task.id} (attempt {task.retry_count}/{task.max_retries})")

        task.completed_at = datetime.now(timezone.utc).isoformat()
        agent.touch()

        # Clear current task
        if agent.current_task_id == task.id:
            agent.current_task_id = None

        self._save_agents()
        return task

    def _build_gateway_input(self, task: Task, agent: Agent) -> Dict:
        """Build input for the AI Gateway based on task type"""
        input_data = task.input_data.copy()

        # Add system prompt if configured
        if agent.system_prompt and "messages" not in input_data:
            input_data["messages"] = [
                {"role": "system", "content": agent.system_prompt},
                {"role": "user", "content": input_data.get("text", input_data.get("content", ""))},
            ]
        elif agent.system_prompt and "messages" in input_data:
            # Prepend system prompt
            input_data["messages"] = [
                {"role": "system", "content": agent.system_prompt},
                *input_data["messages"],
            ]

        # Add relevant memories as context
        memories = self.memory.retrieve_all(agent.id, MemoryType.LONG_TERM)
        if memories:
            context_parts = []
            for m in memories[:5]:  # Top 5 memories
                context_parts.append(f"[{m.key}]: {json.dumps(m.value) if not isinstance(m.value, str) else m.value}")
            if context_parts:
                context_str = "Agent Memory Context:\n" + "\n".join(context_parts)
                if "messages" in input_data:
                    input_data["messages"] = [
                        {"role": "system", "content": context_str},
                        *input_data["messages"],
                    ]
                else:
                    input_data["context"] = context_str

        return input_data

    def get_agent_stats(self, agent_id: str) -> Dict:
        """Get statistics for an agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            return {}

        tasks = self.list_tasks(agent_id)
        task_status_counts = defaultdict(int)
        for t in tasks:
            task_status_counts[t.status.value] += 1

        memory_stats = self.memory.get_stats(agent_id)

        return {
            "agent_id": agent_id,
            "name": agent.name,
            "status": agent.status.value,
            "capabilities": [c.value for c in agent.capabilities],
            "total_tasks": len(tasks),
            "task_status": dict(task_status_counts),
            "success_rate": agent.success_count / max(agent.success_count + agent.error_count, 1) * 100,
            "total_tokens": agent.total_tokens_used,
            "memory": memory_stats,
            "uptime_since": agent.created_at,
            "last_active": agent.last_active,
        }

    def get_framework_stats(self) -> Dict:
        """Get overall framework statistics"""
        agent_status_counts = defaultdict(int)
        for a in self.agents.values():
            agent_status_counts[a.status.value] += 1

        task_status_counts = defaultdict(int)
        for t in self.tasks.values():
            task_status_counts[t.status.value] += 1

        return {
            "total_agents": len(self.agents),
            "agents_by_status": dict(agent_status_counts),
            "total_tasks": len(self.tasks),
            "tasks_by_status": dict(task_status_counts),
            "running_tasks": len(self._running_tasks),
            "queue_length": len(self._task_queue),
            "total_tokens_used": sum(a.total_tokens_used for a in self.agents.values()),
        }
