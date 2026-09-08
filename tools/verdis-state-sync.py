#!/usr/bin/env python3
"""Populate `accounts` and `validators` from CHAIN STATE, not from transfer history.

Why this exists. The indexer only records an account when it appears as a transfer party or
an extrinsic signer. Verdis mainnet is pre-launch: 58,025 extrinsics are all `Timestamp.set`
inherents, zero signed, zero Balances events. So the history-driven path legitimately yields
nothing, and `/api/v2/account/<addr>` answers "address not seen on chain" for accounts that
demonstrably hold funds.

Solscan and Etherscan do not work that way. They show every account that EXISTS with its
current balance, and every validator with its performance - state, not just history. Chain
state is the authoritative source here, and `System.Account` can be iterated.

`validators` is worse: the indexer contains zero `INSERT INTO validators`, so the table was
never going to fill. 21 authorities exist on chain.

This is a state sync, run repeatedly. It invents nothing: every number is read from the node
or computed from indexed blocks.
"""
import argparse
import logging
import os
import sys
import time

import psycopg2
import psycopg2.extras
from substrateinterface import SubstrateInterface

LOG = logging.getLogger("sync")
MAINNET = "0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e"
# Same RPC the indexer follows for mainnet, and the same PG* env contract
# (/etc/verdis/indexer.env) so credentials live in one place only.
RPC = "http://127.0.0.1:9960"
DEC = 10 ** 9


def connect_db():
    db = psycopg2.connect(
        host=os.environ.get("PGHOST", "127.0.0.1"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
    )
    db.autocommit = True
    return db


def sync_accounts(s, db, limit=None):
    """Iterate System.Account and upsert every account with its live balance.

    `is_pallet` marks PalletId-derived accounts (treasury, presale, dpos pools ...): they hold
    most of the supply but are keyless by design, so a holders list must be able to exclude
    them - exactly what Solscan does for program-owned accounts.
    """
    LOG.info("iterating System.Account ...")
    rows = []
    n = 0
    t0 = time.time()
    head = s.get_chain_head()
    for addr, info in s.query_map("System", "Account", page_size=1000, block_hash=head):
        a = str(addr.value if hasattr(addr, "value") else addr)
        d = info.value if hasattr(info, "value") else info
        data = d.get("data", {})
        rows.append((
            a,
            int(data.get("free", 0)),
            int(data.get("reserved", 0)),
            int(data.get("frozen", 0) or data.get("misc_frozen", 0) or 0),
            int(d.get("nonce", 0)),
            _is_pallet(a),
        ))
        n += 1
        if limit and n >= limit:
            break
    LOG.info("read %d accounts in %.1fs", n, time.time() - t0)

    with db.cursor() as c:
        psycopg2.extras.execute_values(c, """
            INSERT INTO accounts (address, free, reserved, frozen, nonce, is_pallet,
                                  updated_at)
            VALUES %s
            ON CONFLICT (address) DO UPDATE SET
                free=EXCLUDED.free, reserved=EXCLUDED.reserved, frozen=EXCLUDED.frozen,
                nonce=EXCLUDED.nonce, is_pallet=EXCLUDED.is_pallet, updated_at=now()
        """, [(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows],
            template="(%s,%s,%s,%s,%s,%s,now())")

        # tx_count from indexed extrinsics; transfer_count from indexed transfers.
        c.execute("""
            UPDATE accounts a SET tx_count = COALESCE(x.n, 0) FROM (
                SELECT signer, count(*) n FROM extrinsics
                WHERE signer IS NOT NULL GROUP BY signer
            ) x WHERE a.address = x.signer
        """)
        c.execute("""
            UPDATE accounts a SET transfer_count = COALESCE(t.n, 0) FROM (
                SELECT addr, count(*) n FROM (
                    SELECT from_address addr FROM transfers WHERE from_address IS NOT NULL
                    UNION ALL
                    SELECT to_address FROM transfers WHERE to_address IS NOT NULL
                ) u GROUP BY addr
            ) t WHERE a.address = t.addr
        """)
    return n


def _is_pallet(addr: str) -> bool:
    """PalletId accounts on Verdis derive from b"modl"+PalletId, so the SS58 payload starts
    with the ASCII bytes 'modl'. Detecting them by prefix on the SS58 string is unreliable
    across formats, so decode instead."""
    try:
        from substrateinterface.utils.ss58 import ss58_decode
        pub = bytes.fromhex(ss58_decode(addr))
        return pub[:4] == b"modl"
    except Exception:                                   # noqa: BLE001
        return False


def sync_validators(s, db):
    """Upsert the active validator set with real block-production counts.

    `blocks_produced` and `last_block` come from the indexed `blocks.author` column - measured
    output, not an estimate. `stake` is read from pallet_dpos if it exposes a stake map;
    otherwise it stays NULL rather than being invented.
    """
    vals = [str(v.value if hasattr(v, "value") else v)
            for v in (s.query("Session", "Validators").value or [])]
    LOG.info("Session.Validators: %d", len(vals))
    if not vals:
        return 0

    with db.cursor() as c:
        c.execute("""SELECT author, count(*) n, max(number) last FROM blocks
                     WHERE author IS NOT NULL GROUP BY author""")
        prod = {r[0]: (r[1], r[2]) for r in c.fetchall()}

    stakes = {}
    for pallet, storage in (("Dpos", "Validators"), ("Dpos", "ValidatorStake"),
                            ("Dpos", "Stakes")):
        try:
            for k, v in s.query_map(pallet, storage, page_size=500):
                addr = str(k.value if hasattr(k, "value") else k)
                val = v.value if hasattr(v, "value") else v
                amt = None
                if isinstance(val, int):
                    amt = val
                elif isinstance(val, dict):
                    for key in ("stake", "total", "bonded", "amount", "self_stake"):
                        if key in val:
                            amt = int(val[key])
                            break
                if amt is not None:
                    stakes[addr] = amt
            if stakes:
                LOG.info("read stake for %d validators from %s.%s", len(stakes),
                         pallet, storage)
                break
        except Exception:                               # noqa: BLE001
            continue

    rows = []
    for v in vals:
        n, last = prod.get(v, (0, None))
        rows.append((v, None, stakes.get(v), True, n, last))

    with db.cursor() as c:
        # Mark everyone inactive first so a rotated-out validator does not stay "active".
        c.execute("UPDATE validators SET is_active=false")
        psycopg2.extras.execute_values(c, """
            INSERT INTO validators (address, name, stake, is_active, blocks_produced,
                                    last_block, updated_at)
            VALUES %s
            ON CONFLICT (address) DO UPDATE SET
                stake=EXCLUDED.stake, is_active=EXCLUDED.is_active,
                blocks_produced=EXCLUDED.blocks_produced,
                last_block=EXCLUDED.last_block, updated_at=now()
        """, rows, template="(%s,%s,%s,%s,%s,%s,now())")
        c.execute("""UPDATE accounts SET is_validator=true
                     WHERE address IN (SELECT address FROM validators WHERE is_active)""")
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", default=RPC)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--loop", type=int, help="repeat every N seconds")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    s = SubstrateInterface(url=args.rpc)
    g = s.get_block_hash(0)
    if g != MAINNET:
        LOG.warning("endpoint genesis %s is not mainnet", g[:20])
    db = connect_db()

    while True:
        try:
            na = sync_accounts(s, db, args.limit)
            nv = sync_validators(s, db)
            with db.cursor() as c:
                c.execute("SELECT count(*) FROM accounts WHERE NOT is_pallet")
                keyed = c.fetchone()[0]
                c.execute("SELECT coalesce(sum(free),0) FROM accounts WHERE NOT is_pallet")
                circ = int(c.fetchone()[0] or 0)
            LOG.info("accounts %d (non-pallet %d, holding %.4f VRDX), validators %d",
                     na, keyed, circ / DEC, nv)
        except Exception as exc:                        # noqa: BLE001
            LOG.error("sync failed: %s", exc)
            if not args.loop:
                return 1
        if not args.loop:
            return 0
        time.sleep(args.loop)


if __name__ == "__main__":
    sys.exit(main())
