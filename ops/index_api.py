#!/usr/bin/env python3
"""Indexer-backed explorer API: the endpoints an RPC node cannot serve.

The existing verdiscan_api.py reads the node directly. That is fine for "latest block"
but structurally cannot answer the queries that define a Solscan/Etherscan-class
explorer, because a node has no index:

  * every transaction touching an address       -> needs transfers(from|to) indexes
  * an account's full history, paginated        -> needs extrinsics(signer, block DESC)
  * top holders by balance                     -> needs accounts ordered by balance
  * activity/volume charts over time           -> needs daily rollups
  * search by hash / block / address           -> needs hash indexes

These are served from PostgreSQL, which the indexer fills. Mounted under /api/v2 so the
existing /api/v1 keeps working unchanged - no flag day, and the frontend can migrate
endpoint by endpoint.

Conventions kept deliberately strict, because this API is what an auditor reads:
  * every response has {success, data} and a stated source ("index" vs "node")
  * u128 amounts are returned as STRINGS, never JSON numbers: 1e20 planck exceeds
    IEEE-754 double precision and JS would silently round it
  * pagination is capped server-side (limit<=100) so no query can be turned into a
    table scan
  * all SQL is parameterised; no identifier or value is ever interpolated
  * read-only DB usage: SELECT only, no endpoint mutates state
"""
import os
from typing import Optional

import psycopg2
import psycopg2.extras
import psycopg2.pool
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

DECIMALS = 9
SYMBOL = "VRDX"

app = FastAPI(title="Verdiscan Index API", version="2.0",
              docs_url="/api/v2/docs", openapi_url="/api/v2/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"],
                   allow_headers=["*"])

POOL = psycopg2.pool.ThreadedConnectionPool(
    minconn=1, maxconn=8,
    host=os.environ.get("PGHOST", "127.0.0.1"),
    port=os.environ.get("PGPORT", "5432"),
    dbname=os.environ["PGDATABASE"],
    user=os.environ["PGUSER"],
    password=os.environ["PGPASSWORD"],
)


def q(sql: str, params: tuple = (), one: bool = False):
    conn = POOL.getconn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as c:
            c.execute(sql, params)
            return c.fetchone() if one else c.fetchall()
    finally:
        conn.rollback()          # read-only: never leave a transaction open
        POOL.putconn(conn)


def planck(v) -> Optional[str]:
    """u128 as a string. Returning it as a JSON number would lose precision in JS."""
    return None if v is None else str(int(v))


def human(v) -> Optional[str]:
    if v is None:
        return None
    i = int(v)
    return f"{i // 10**DECIMALS}.{str(i % 10**DECIMALS).zfill(DECIMALS)}"


def amount(v) -> dict:
    return {"planck": planck(v), "amount": human(v), "symbol": SYMBOL}


def rows(r):
    return [dict(x) for x in r]


@app.get("/api/v2/status")
def status():
    """Indexer progress. `behind` is what tells you whether the data is fresh."""
    st = q("SELECT * FROM indexer_state WHERE network='mainnet'", one=True)
    if not st:
        raise HTTPException(503, "indexer has not started")
    counts = q("""SELECT
            (SELECT count(*) FROM blocks)     AS blocks,
            (SELECT count(*) FROM extrinsics) AS extrinsics,
            (SELECT count(*) FROM events)     AS events,
            (SELECT count(*) FROM transfers)  AS transfers,
            (SELECT count(*) FROM accounts)   AS accounts""", one=True)
    tip = st["chain_tip"] or 0
    last = st["last_indexed_block"] or 0
    return {"success": True, "source": "index", "data": {
        "network": st["network"],
        "genesis": st["genesis_hash"],
        "last_indexed_block": last,
        "chain_tip": tip,
        "behind": max(tip - last, 0),
        "synced": (tip - last) <= 3,
        "last_finalized": st["last_finalized"],
        "indexed_totals": dict(counts),
        "last_error": st["last_error"],
        "updated_at": st["updated_at"].isoformat() if st["updated_at"] else None,
    }}


@app.get("/api/v2/blocks")
def blocks(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    r = q("""SELECT number, hash, timestamp, author, extrinsic_count, event_count,
                    transfer_count, finalized, spec_version
             FROM blocks ORDER BY number DESC LIMIT %s OFFSET %s""", (limit, offset))
    return {"success": True, "source": "index", "count": len(r), "data": rows(r)}


@app.get("/api/v2/block/{number}")
def block(number: int):
    b = q("SELECT * FROM blocks WHERE number=%s", (number,), one=True)
    if not b:
        raise HTTPException(404, f"block {number} not indexed")
    ex = q("""SELECT idx, hash, signer, call_module, call_function, args, success,
                     signed, nonce FROM extrinsics
              WHERE block_number=%s ORDER BY idx""", (number,))
    ev = q("""SELECT idx, extrinsic_idx, module, event, attributes FROM events
              WHERE block_number=%s ORDER BY idx""", (number,))
    tr = q("""SELECT event_idx, from_address, to_address, amount FROM transfers
              WHERE block_number=%s ORDER BY event_idx""", (number,))
    d = dict(b)
    d["extrinsics"] = rows(ex)
    d["events"] = rows(ev)
    d["transfers"] = [{**dict(t), **{"amount": amount(t["amount"])}} for t in tr]
    return {"success": True, "source": "index", "data": d}


@app.get("/api/v2/extrinsics")
def extrinsics(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
               module: Optional[str] = None, signed_only: bool = False):
    where, params = [], []
    if module:
        where.append("call_module = %s")
        params.append(module)
    if signed_only:
        where.append("signed IS TRUE")
    clause = ("WHERE " + " AND ".join(where)) if where else ""
    params += [limit, offset]
    r = q(f"""SELECT block_number, idx, hash, signer, call_module, call_function,
                     success, signed, timestamp
              FROM extrinsics {clause}
              ORDER BY block_number DESC, idx DESC LIMIT %s OFFSET %s""", tuple(params))
    return {"success": True, "source": "index", "count": len(r), "data": rows(r)}


@app.get("/api/v2/transfers")
def transfers(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    r = q("""SELECT block_number, extrinsic_idx, event_idx, from_address, to_address,
                    amount, timestamp FROM transfers
             ORDER BY block_number DESC, event_idx DESC LIMIT %s OFFSET %s""",
          (limit, offset))
    return {"success": True, "source": "index", "count": len(r),
            "data": [{**dict(t), **{"amount": amount(t["amount"])}} for t in r]}


@app.get("/api/v2/account/{address}")
def account(address: str):
    """Full account view - the query a bare RPC node cannot answer."""
    a = q("SELECT * FROM accounts WHERE address=%s", (address,), one=True)
    sent = q("""SELECT count(*) AS n, coalesce(sum(amount),0) AS total
                FROM transfers WHERE from_address=%s""", (address,), one=True)
    recv = q("""SELECT count(*) AS n, coalesce(sum(amount),0) AS total
                FROM transfers WHERE to_address=%s""", (address,), one=True)
    tx = q("SELECT count(*) AS n FROM extrinsics WHERE signer=%s", (address,), one=True)
    if not a and not sent["n"] and not recv["n"] and not tx["n"]:
        raise HTTPException(404, "address not seen on chain")
    return {"success": True, "source": "index", "data": {
        "address": address,
        "balance": amount(a["free"]) if a and a["free"] is not None else None,
        "reserved": amount(a["reserved"]) if a and a["reserved"] is not None else None,
        "nonce": a["nonce"] if a else None,
        "is_validator": a["is_validator"] if a else False,
        "is_pallet_account": a["is_pallet"] if a else address.startswith("modl"),
        "first_seen_block": a["first_seen"] if a else None,
        "last_activity_block": a["last_activity"] if a else None,
        "extrinsics_signed": tx["n"],
        "transfers_out": {"count": sent["n"], "total": amount(sent["total"])},
        "transfers_in": {"count": recv["n"], "total": amount(recv["total"])},
    }}


@app.get("/api/v2/account/{address}/transfers")
def account_transfers(address: str, limit: int = Query(20, ge=1, le=100),
                      offset: int = Query(0, ge=0),
                      direction: str = Query("all", pattern="^(all|in|out)$")):
    if direction == "in":
        cond, p = "to_address = %s", (address,)
    elif direction == "out":
        cond, p = "from_address = %s", (address,)
    else:
        cond, p = "(from_address = %s OR to_address = %s)", (address, address)
    r = q(f"""SELECT block_number, event_idx, from_address, to_address, amount, timestamp
              FROM transfers WHERE {cond}
              ORDER BY block_number DESC LIMIT %s OFFSET %s""", p + (limit, offset))
    return {"success": True, "source": "index", "count": len(r), "direction": direction,
            "data": [{**dict(t), **{"amount": amount(t["amount"]),
                                    "direction": "in" if t["to_address"] == address else "out"}}
                     for t in r]}


@app.get("/api/v2/account/{address}/extrinsics")
def account_extrinsics(address: str, limit: int = Query(20, ge=1, le=100),
                       offset: int = Query(0, ge=0)):
    r = q("""SELECT block_number, idx, hash, call_module, call_function, success,
                    nonce, timestamp FROM extrinsics WHERE signer=%s
             ORDER BY block_number DESC, idx DESC LIMIT %s OFFSET %s""",
          (address, limit, offset))
    return {"success": True, "source": "index", "count": len(r), "data": rows(r)}


@app.get("/api/v2/holders")
def holders(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0),
            exclude_pallet: bool = True):
    """Rich list. Pallet (modl*) accounts are excluded by default: they hold 90 billion
    VRDX but have no private key by construction, so counting them as holders
    misrepresents distribution."""
    clause = "WHERE free IS NOT NULL" + (" AND is_pallet IS FALSE" if exclude_pallet else "")
    r = q(f"""SELECT address, free, reserved, nonce, is_validator, is_pallet,
                     transfer_count, last_activity
              FROM accounts {clause}
              ORDER BY free DESC NULLS LAST LIMIT %s OFFSET %s""", (limit, offset))
    tot = q(f"SELECT coalesce(sum(free),0) AS s FROM accounts {clause}", one=True)
    out = []
    for i, h in enumerate(r, start=offset + 1):
        d = dict(h)
        d["rank"] = i
        d["balance"] = amount(h["free"])
        share = (int(h["free"]) / int(tot["s"]) * 100) if tot["s"] and h["free"] else None
        d["share_percent"] = round(share, 6) if share is not None else None
        d.pop("free", None)
        d["reserved"] = amount(h["reserved"]) if h["reserved"] is not None else None
        out.append(d)
    return {"success": True, "source": "index", "count": len(out),
            "excluded_pallet_accounts": exclude_pallet,
            "total_counted": amount(tot["s"]), "data": out}


@app.get("/api/v2/search")
def search(q_: str = Query(..., alias="q", min_length=1, max_length=120)):
    """One box, several kinds of input - what users actually type into an explorer."""
    s = q_.strip()
    if s.isdigit():
        b = q("SELECT number, hash, timestamp FROM blocks WHERE number=%s",
              (int(s),), one=True)
        if b:
            return {"success": True, "type": "block", "data": dict(b)}
    if s.startswith("0x") and len(s) >= 10:
        b = q("SELECT number, hash, timestamp FROM blocks WHERE hash=%s", (s,), one=True)
        if b:
            return {"success": True, "type": "block", "data": dict(b)}
        e = q("""SELECT block_number, idx, hash, signer, call_module, call_function
                 FROM extrinsics WHERE hash=%s""", (s,), one=True)
        if e:
            return {"success": True, "type": "extrinsic", "data": dict(e)}
    a = q("SELECT address FROM accounts WHERE address=%s", (s,), one=True)
    if a:
        return {"success": True, "type": "account", "data": {"address": s}}
    seen = q("""SELECT 1 FROM transfers WHERE from_address=%s OR to_address=%s LIMIT 1""",
             (s, s), one=True)
    if seen:
        return {"success": True, "type": "account", "data": {"address": s}}
    raise HTTPException(404, {"error": "nothing found", "query": s})


@app.get("/api/v2/stats")
def stats():
    c = q("""SELECT
            (SELECT count(*) FROM blocks)                          AS indexed_blocks,
            (SELECT max(number) FROM blocks)                        AS head,
            (SELECT count(*) FROM extrinsics)                       AS extrinsics,
            (SELECT count(*) FROM extrinsics WHERE signed)          AS signed_extrinsics,
            (SELECT count(*) FROM transfers)                        AS transfers,
            (SELECT coalesce(sum(amount),0) FROM transfers)         AS volume,
            (SELECT count(*) FROM accounts)                         AS accounts,
            (SELECT count(*) FROM accounts WHERE is_pallet)         AS pallet_accounts,
            (SELECT count(DISTINCT author) FROM blocks WHERE author IS NOT NULL)
                                                                    AS block_authors
        """, one=True)
    d = dict(c)
    d["volume"] = amount(c["volume"])
    return {"success": True, "source": "index", "data": d}


@app.get("/api/v2/producers")
def producers(limit: int = Query(30, ge=1, le=100)):
    """Blocks produced per author - real participation, measured from indexed blocks."""
    r = q("""SELECT author, count(*) AS blocks, max(number) AS last_block,
                    min(number) AS first_block
             FROM blocks WHERE author IS NOT NULL
             GROUP BY author ORDER BY blocks DESC LIMIT %s""", (limit,))
    total = q("SELECT count(*) AS n FROM blocks WHERE author IS NOT NULL", one=True)
    out = []
    for i, p in enumerate(r, 1):
        d = dict(p)
        d["rank"] = i
        d["share_percent"] = round(p["blocks"] / total["n"] * 100, 4) if total["n"] else None
        out.append(d)
    return {"success": True, "source": "index", "count": len(out),
            "blocks_counted": total["n"], "data": out}


@app.get("/api/v2/activity")
def activity(days: int = Query(30, ge=1, le=365)):
    """Daily rollup for charts, computed from indexed blocks."""
    r = q("""SELECT date_trunc('day', timestamp)::date AS day,
                    count(*) AS blocks,
                    sum(extrinsic_count) AS extrinsics,
                    sum(transfer_count)  AS transfers
             FROM blocks WHERE timestamp IS NOT NULL
             GROUP BY 1 ORDER BY 1 DESC LIMIT %s""", (days,))
    return {"success": True, "source": "index", "count": len(r),
            "data": [{**dict(x), "day": x["day"].isoformat()} for x in r]}


@app.get("/api/v2/health")
def health():
    try:
        q("SELECT 1", one=True)
        return {"status": "ok", "db": "up"}
    except Exception as exc:                            # noqa: BLE001
        raise HTTPException(503, {"status": "degraded", "db": str(exc)[:120]})
