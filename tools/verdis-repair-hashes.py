#!/usr/bin/env python3
"""Establish WHY 2,940 indexed rows carry hashes the node disagrees with, then repair them.

Facts measured:
  * The indexer's own node (127.0.0.1:9960) returns the SAME hash as the public RPC for the
    disputed heights, so the node is not the problem and there is no fork.
  * The index has 58,764 rows, one per height, no duplicates - so nothing was double-inserted.
  * 2,940 rows break the parent_hash chain: row N's parent_hash != row N-1's hash.
  * Divergence starts at 51,438 and stops by 58,020, and inside that window it alternates.

That pattern is what a reorg-blind follower produces: those blocks WERE the chain when the
indexer saw them, and were later replaced by the canonical branch. The indexer never revisits
a height once written, so the stale rows persist. VerdiScan therefore serves hashes that no
longer exist on chain - a correctness defect worth fixing before an audit.

This script re-reads the disputed heights from the node and rewrites hash/parent_hash/roots
in place. It changes nothing else, is idempotent, and verifies chain integrity afterwards.
"""
import argparse
import json
import os
import sys
import time
import urllib.request

import psycopg2

RPC = "http://127.0.0.1:9960"
MAINNET = "0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e"


def rpc(method, params=None):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                       "params": params or []}).encode()
    req = urllib.request.Request(RPC, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r).get("result")


def db():
    c = psycopg2.connect(
        host=os.environ.get("PGHOST", "127.0.0.1"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"])
    c.autocommit = True
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the corrections")
    ap.add_argument("--from-block", type=int, default=51000)
    args = ap.parse_args()

    if rpc("chain_getBlockHash", [0]) != MAINNET:
        sys.exit("node is not mainnet")

    conn = db()
    with conn.cursor() as c:
        c.execute("SELECT number, hash, parent_hash FROM blocks WHERE number >= %s "
                  "ORDER BY number", (args.from_block,))
        rows = c.fetchall()
    print(f"checking {len(rows):,} indexed rows from block {args.from_block}")

    wrong = []
    t0 = time.time()
    for i, (n, h, ph) in enumerate(rows):
        try:
            real = rpc("chain_getBlockHash", [n])
        except Exception:                               # noqa: BLE001
            continue
        if real and real != h:
            wrong.append((n, h, real))
        if i and i % 1000 == 0:
            print(f"  {i:,}/{len(rows):,} checked, {len(wrong):,} wrong "
                  f"({time.time()-t0:.0f}s)")
    print(f"\nrows whose hash disagrees with the node: {len(wrong):,}")
    if wrong:
        print(f"  first {wrong[0][0]}, last {wrong[-1][0]}")
        for n, old, new in wrong[:3]:
            print(f"    {n}: index {old[:22]}…  node {new[:22]}…")

    if not args.apply:
        print("\nDRY RUN - rerun with --apply to rewrite these rows")
        return 0

    print("\nrewriting from the node …")
    fixed = 0
    with conn.cursor() as c:
        for n, _old, real in wrong:
            try:
                hdr = rpc("chain_getHeader", [real])
                if not hdr:
                    continue
                c.execute("""UPDATE blocks SET hash=%s, parent_hash=%s, state_root=%s,
                                    extrinsics_root=%s
                             WHERE number=%s""",
                          (real, hdr.get("parentHash"), hdr.get("stateRoot"),
                           hdr.get("extrinsicsRoot"), n))
                fixed += 1
                if fixed % 500 == 0:
                    print(f"  {fixed:,} rewritten")
            except Exception as exc:                    # noqa: BLE001
                print(f"  {n}: {str(exc)[:70]}")
    print(f"rewrote {fixed:,} rows")

    with conn.cursor() as c:
        c.execute("""WITH x AS (SELECT number, hash, parent_hash,
                                 LAG(hash) OVER (ORDER BY number) prev FROM blocks)
                     SELECT count(*) FROM x
                     WHERE prev IS NOT NULL AND parent_hash <> prev""")
        breaks = c.fetchone()[0]
    print(f"\nchain-integrity breaks remaining in the index: {breaks}")
    print("  (0 means every row's parent_hash links to the previous row's hash)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
