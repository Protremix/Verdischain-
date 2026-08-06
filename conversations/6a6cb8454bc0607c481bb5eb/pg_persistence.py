"""
EvolvixOS Execution Persistence (PostgreSQL)
Migrates execution records from JSONL to PostgreSQL for scalability.
"""

import asyncio
import os
import time
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from collections import defaultdict
import structlog

logger = structlog.get_logger()

try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False
    logger.warning("asyncpg not available — PostgreSQL persistence disabled")


class PostgresExecutionPersistence:
    """PostgreSQL-based execution persistence for scalability."""
    
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS agent_executions (
        id VARCHAR(32) PRIMARY KEY,
        timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        execution_id VARCHAR(64),
        agent_id VARCHAR(64),
        agent_name VARCHAR(128),
        status VARCHAR(32) NOT NULL,
        capability VARCHAR(64),
        provider VARCHAR(64),
        fallback_used BOOLEAN DEFAULT FALSE,
        latency_ms FLOAT,
        input_data JSONB,
        output_data JSONB,
        error TEXT,
        sandboxed BOOLEAN DEFAULT FALSE,
        metadata JSONB
    );
    CREATE INDEX IF NOT EXISTS idx_exec_agent_id ON agent_executions(agent_id);
    CREATE INDEX IF NOT EXISTS idx_exec_status ON agent_executions(status);
    CREATE INDEX IF NOT EXISTS idx_exec_timestamp ON agent_executions(timestamp DESC);
    CREATE INDEX IF NOT EXISTS idx_exec_provider ON agent_executions(provider);
    """
    
    def __init__(self, database_url: str = None):
        self._database_url = database_url or os.getenv("DATABASE_URL", "")
        self._pool = None
        self._connected = False
        self._fallback_buffer: List[Dict] = []
        self._total_persisted = 0
    
    async def connect(self):
        if not HAS_ASYNCPG or not self._database_url:
            logger.info("PostgreSQL persistence: using fallback (in-memory)")
            return False
        try:
            self._pool = await asyncpg.create_pool(
                self._database_url, min_size=2, max_size=10, command_timeout=30,
            )
            async with self._pool.acquire() as conn:
                await conn.execute(self.SCHEMA)
            self._connected = True
            logger.info("PostgreSQL execution persistence connected")
            return True
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed: {e}")
            self._connected = False
            return False
    
    async def record(self, execution: Dict[str, Any]):
        entry_id = hashlib.sha256(
            f"{execution.get('execution_id', '')}:{time.time()}".encode()
        ).hexdigest()[:32]
        
        if self._connected and self._pool:
            try:
                async with self._pool.acquire() as conn:
                    await conn.execute(
                        """INSERT INTO agent_executions
                        (id, timestamp, execution_id, agent_id, agent_name, status,
                         capability, provider, fallback_used, latency_ms,
                         input_data, output_data, error, sandboxed, metadata)
                        VALUES ($1, NOW(), $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                        ON CONFLICT (id) DO NOTHING""",
                        entry_id,
                        execution.get("execution_id", ""),
                        execution.get("agent_id", ""),
                        execution.get("agent_name", ""),
                        execution.get("status", "unknown"),
                        execution.get("capability", ""),
                        execution.get("provider", ""),
                        execution.get("fallback_used", False),
                        execution.get("latency_ms", 0),
                        json.dumps(execution.get("input", {})),
                        json.dumps(execution.get("output", {})),
                        execution.get("error", ""),
                        execution.get("sandboxed", False),
                        json.dumps({k: v for k, v in execution.items()
                                   if k not in ["input", "output", "error", "input_data", "output_data"]}),
                    )
                self._total_persisted += 1
                return True
            except Exception as e:
                logger.warning(f"PostgreSQL insert failed: {e}")
                self._fallback_buffer.append({**execution, "id": entry_id})
                return False
        else:
            self._fallback_buffer.append({**execution, "id": entry_id})
            return False
    
    async def query(self, limit: int = 100, agent_id: str = None,
                    status: str = None, provider: str = None) -> List[Dict]:
        if not self._connected or not self._pool:
            return self._fallback_buffer[-limit:] if self._fallback_buffer else []
        
        conditions = []
        params = []
        idx = 1
        
        if agent_id:
            conditions.append(f"agent_id = ${idx}")
            params.append(agent_id)
            idx += 1
        if status:
            conditions.append(f"status = ${idx}")
            params.append(status)
            idx += 1
        if provider:
            conditions.append(f"provider = ${idx}")
            params.append(provider)
            idx += 1
        
        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        params.append(limit)
        
        query = f"""
            SELECT id, timestamp, execution_id, agent_id, agent_name, status,
                   capability, provider, fallback_used, latency_ms,
                   input_data, output_data, error, sandboxed, metadata
            FROM agent_executions
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ${idx}
        """
        
        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.warning(f"PostgreSQL query failed: {e}")
            return []
    
    def _row_to_dict(self, row) -> Dict:
        return {
            "id": row["id"],
            "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
            "execution_id": row["execution_id"],
            "agent_id": row["agent_id"],
            "agent_name": row["agent_name"],
            "status": row["status"],
            "capability": row["capability"],
            "provider": row["provider"],
            "fallback_used": row["fallback_used"],
            "latency_ms": row["latency_ms"],
            "input": json.loads(row["input_data"]) if row["input_data"] else {},
            "output": json.loads(row["output_data"]) if row["output_data"] else {},
            "error": row["error"],
            "sandboxed": row["sandboxed"],
            "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
        }
    
    async def stats(self) -> Dict[str, Any]:
        if not self._connected or not self._pool:
            return {
                "connected": False,
                "total_persisted": self._total_persisted,
                "fallback_buffer": len(self._fallback_buffer),
            }
        try:
            async with self._pool.acquire() as conn:
                total = await conn.fetchval("SELECT COUNT(*) FROM agent_executions")
                by_status = await conn.fetch(
                    "SELECT status, COUNT(*) as count FROM agent_executions GROUP BY status"
                )
                by_agent = await conn.fetch(
                    "SELECT agent_id, COUNT(*) as count FROM agent_executions GROUP BY agent_id"
                )
                avg_latency = await conn.fetchval(
                    "SELECT AVG(latency_ms) FROM agent_executions WHERE status = 'completed'"
                )
                return {
                    "connected": True,
                    "total_persisted": total,
                    "by_status": {r["status"]: r["count"] for r in by_status},
                    "by_agent": {r["agent_id"]: r["count"] for r in by_agent if r["agent_id"]},
                    "avg_latency_ms": float(avg_latency) if avg_latency else 0,
                    "fallback_buffer": len(self._fallback_buffer),
                }
        except Exception as e:
            logger.warning(f"PostgreSQL stats failed: {e}")
            return {"connected": True, "error": str(e)}
    
    async def close(self):
        if self._pool:
            await self._pool.close()
            self._connected = False
            logger.info("PostgreSQL execution persistence closed")
    
    @property
    def is_connected(self) -> bool:
        return self._connected


pg_persistence = PostgresExecutionPersistence()
