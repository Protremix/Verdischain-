"""
EvolvixOS Migration Script: JSONL → PostgreSQL
Migrates existing execution records from JSONL files to PostgreSQL.
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger()


async def migrate_jsonl_to_postgres(jsonl_path: str, pg_persistence) -> Dict[str, Any]:
    """Migrate execution records from a JSONL file to PostgreSQL.
    
    Args:
        jsonl_path: Path to the JSONL file
        pg_persistence: PostgresExecutionPersistence instance
        
    Returns:
        Migration statistics
    """
    if not os.path.exists(jsonl_path):
        logger.info(f"JSONL file not found: {jsonl_path} — nothing to migrate")
        return {"migrated": 0, "skipped": 0, "errors": 0, "file": jsonl_path}
    
    # Ensure PG is connected
    if not pg_persistence.is_connected:
        connected = await pg_persistence.connect()
        if not connected:
            logger.error("PostgreSQL not available — cannot migrate")
            return {"migrated": 0, "skipped": 0, "errors": 0, "error": "PG not connected"}
    
    migrated = 0
    skipped = 0
    errors = 0
    total = 0
    
    with open(jsonl_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            total += 1
            
            try:
                record = json.loads(line)
                result = await pg_persistence.record(record)
                if result:
                    migrated += 1
                else:
                    skipped += 1
            except json.JSONDecodeError as e:
                logger.warning(f"Line {line_num}: JSON decode error: {e}")
                errors += 1
            except Exception as e:
                logger.warning(f"Line {line_num}: error: {e}")
                errors += 1
    
    stats = {
        "migrated": migrated,
        "skipped": skipped,
        "errors": errors,
        "total_read": total,
        "file": jsonl_path,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    logger.info(f"Migration complete: {migrated} migrated, {skipped} skipped, {errors} errors")
    return stats


async def migrate_all_jsonl_files(directory: str, pg_persistence) -> List[Dict]:
    """Migrate all JSONL files in a directory to PostgreSQL."""
    results = []
    for fname in os.listdir(directory):
        if fname.endswith('.jsonl'):
            path = os.path.join(directory, fname)
            result = await migrate_jsonl_to_postgres(path, pg_persistence)
            results.append(result)
    return results


# =========================================================================
# CLI entry point
# =========================================================================

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Migrate JSONL execution records to PostgreSQL")
    parser.add_argument("jsonl_path", nargs="?", default="/tmp/evolvixos_executions.jsonl",
                       help="Path to JSONL file (default: /tmp/evolvixos_executions.jsonl)")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", ""),
                       help="PostgreSQL connection URL")
    args = parser.parse_args()
    
    # Set up database URL
    if args.database_url:
        os.environ["DATABASE_URL"] = args.database_url
    
    from pg_persistence import pg_persistence
    
    # Connect to PG
    connected = await pg_persistence.connect()
    if not connected:
        print("ERROR: Could not connect to PostgreSQL")
        sys.exit(1)
    
    # Run migration
    stats = await migrate_jsonl_to_postgres(args.jsonl_path, pg_persistence)
    print(json.dumps(stats, indent=2))
    
    await pg_persistence.close()


if __name__ == "__main__":
    asyncio.run(main())
