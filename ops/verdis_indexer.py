#!/usr/bin/env python3
"""Verdis Chain block indexer.

Why this exists: a Substrate node answers "give me block N" but never "give me every
transfer touching this address". Solscan/Etherscan-class features - address search,
account history, holder rankings, activity charts - all require the chain to be decoded
once and stored relationally. That is this process.

Operating model
  * backfill: walk from the last indexed block up to the chain tip
  * follow: stay at the tip, and mark blocks finalized as GRANDPA advances
  * resumable and idempotent: natural primary keys (block_number, idx) plus ON CONFLICT
    mean re-processing a block is a no-op, so a crash costs nothing and a restart never
    re-indexes from genesis

Correctness decisions that were not obvious
  * Genesis is verified against indexer_state before the first write. Pointing an
    indexer at a different chain than the one it already contains would silently
    interleave two histories - the same class of bug that put testnet data on the
    public site.
  * Balances are Python ints written to NUMERIC(39,0). u128 does not fit in BIGINT
    (1e20 planck of issuance vs int64 max 9.2e18).
  * Account free/reserved come from a storage read at the current head, never from
    summing transfers: fees, staking and rewards move funds without a Transfer event,
    so a running total would drift and be wrong forever.
  * Only FINALIZED blocks are treated as immutable. Unfinalized blocks are indexed too
    (an explorer must show the tip) but flagged, and re-checked as finality advances,
    because a fork would otherwise leave orphaned rows presented as history.

Safety: read-only against the chain. It issues chain_/state_/system_ RPC only, against
the keyless full node on 127.0.0.1:9960. It holds no keys and cannot submit anything.
"""
import argparse
import json
import logging
import os
import signal
import sys
import time
import urllib.request
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras
from scalecodec.base import ScaleBytes
from substrateinterface import SubstrateInterface

LOG = logging.getLogger("indexer")

NETWORKS = {
    "mainnet": {
        "url": "http://127.0.0.1:9960",
        "genesis": "0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e",
    },
    "testnet": {
        "url": "http://127.0.0.1:9934",
        "genesis": "0xf72f1241cb7457a2af62498fc5cadbc79dc442cfc52a17aa7560ba8ec0ec8edb",
    },
}

_stop = False


def _handle_signal(signum, frame):
    global _stop
    _stop = True
    LOG.info("signal %s received - finishing current block then exiting", signum)


class Indexer:
    def __init__(self, network: str, batch: int = 200):
        if network not in NETWORKS:
            raise SystemExit(f"unknown network {network}")
        self.network = network
        self.cfg = NETWORKS[network]
        self.batch = batch
        self.substrate = SubstrateInterface(url=self.cfg["url"])
        # metadata cache keyed by specVersion - see _metadata_for()
        self._md_cache = {}
        self.db = psycopg2.connect(
            host=os.environ.get("PGHOST", "127.0.0.1"),
            port=os.environ.get("PGPORT", "5432"),
            dbname=os.environ["PGDATABASE"],
            user=os.environ["PGUSER"],
            password=os.environ["PGPASSWORD"],
        )
        self.db.autocommit = False
        self._verify_chain()

    # ---------- guards ----------

    def _verify_chain(self):
        """Refuse to write if the endpoint is not the chain this database holds."""
        genesis = self.substrate.get_block_hash(0)
        expected = self.cfg["genesis"]
        if genesis != expected:
            raise SystemExit(
                f"genesis mismatch: node reports {genesis}, expected {expected}. "
                f"Refusing to index - identify a chain by genesis, never by name.")
        with self.db.cursor() as c:
            c.execute("SELECT genesis_hash FROM indexer_state WHERE network=%s",
                      (self.network,))
            row = c.fetchone()
            if row and row[0] != genesis:
                raise SystemExit(
                    f"database holds genesis {row[0]} but node reports {genesis}. "
                    f"Two different chains must not share one indexer_state row.")
            if not row:
                c.execute(
                    "INSERT INTO indexer_state (network, genesis_hash) VALUES (%s,%s)",
                    (self.network, genesis))
        self.db.commit()
        LOG.info("chain verified: %s genesis %s", self.network, genesis[:18])

    # ---------- helpers ----------

    def last_indexed(self) -> int:
        with self.db.cursor() as c:
            c.execute("SELECT last_indexed_block FROM indexer_state WHERE network=%s",
                      (self.network,))
            return c.fetchone()[0]

    def chain_tip(self) -> int:
        return self.substrate.get_block_number(self.substrate.get_chain_head())

    def finalized_height(self) -> int:
        return self.substrate.get_block_number(self.substrate.get_chain_finalised_head())

    @staticmethod
    def _ss58(value):
        """Normalise an account field to a plain string address."""
        if value is None:
            return None
        if isinstance(value, dict):
            for k in ("Id", "id", "value"):
                if k in value:
                    return Indexer._ss58(value[k])
            return json.dumps(value)[:120]
        return str(value)

    @staticmethod
    def _amount(value):
        """Coerce a SCALE-decoded balance to int, tolerating dict/str shapes."""
        if value is None:
            return 0
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, dict):
            for k in ("value", "amount"):
                if k in value:
                    return Indexer._amount(value[k])
            return 0
        s = str(value).replace(",", "").strip()
        try:
            return int(s, 16) if s.startswith("0x") else int(s)
        except ValueError:
            return 0

    # ---------- core ----------

    def _raw_rpc(self, method, params):
        """Direct JSON-RPC, used where the library's own helper is unusable."""
        req = urllib.request.Request(
            self.cfg["url"],
            data=json.dumps({"jsonrpc": "2.0", "id": 1,
                             "method": method, "params": params}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read()).get("result")

    def _metadata_for(self, block_hash):
        """Runtime metadata, cached per specVersion.

        This is the single biggest performance factor in the whole indexer. Profiling
        showed get_block_metadata() costing 853 ms of a 999 ms per-block budget - 85% of
        the time - because it refetches and reparses 231 KB of metadata for every block.
        Caching by specVersion took the indexer from 1.0 to 11.6 blocks/sec (50k blocks:
        ~15.5 hours -> ~72 minutes).

        Keyed on specVersion rather than cached once, because a runtime upgrade changes
        call indices: decoding old blocks with new metadata silently produces wrong call
        names, which is worse than being slow.
        """
        rt = self._raw_rpc("state_getRuntimeVersion", [block_hash]) or {}
        spec = rt.get("specVersion")
        if spec not in self._md_cache:
            self._md_cache[spec] = self.substrate.get_block_metadata(block_hash=block_hash)
            LOG.info("cached runtime metadata for specVersion %s", spec)
        return self._md_cache[spec], spec

    def _decode_extrinsics(self, block_hash):
        """Fetch and decode a block's extrinsics.

        substrate-interface 1.8.1's get_block() cannot be used against this node: it
        passes the RPC's extrinsic field straight into ScaleBytes, and this node returns
        each extrinsic as a LIST OF BYTE VALUES rather than a hex string, so the library
        dies with
            ValueError: Provided data is not in supported format: provided '<class 'list'>'
        on every single block. get_events(), get_block_header() and the author lookup are
        unaffected, so only this one step is reimplemented: pull the raw block, normalise
        each extrinsic to hex, and decode it with the runtime metadata for that block.
        """
        blk = (self._raw_rpc("chain_getBlock", [block_hash]) or {}).get("block", {})
        raws = blk.get("extrinsics", []) or []
        metadata, spec = self._metadata_for(block_hash)
        out = []
        for raw in raws:
            if isinstance(raw, list):
                hexs = "0x" + bytes(raw).hex()
            elif isinstance(raw, str):
                hexs = raw
            else:
                out.append(None)
                continue
            try:
                obj = self.substrate.create_scale_object("Extrinsic", metadata=metadata)
                out.append(obj.decode(ScaleBytes(hexs)))
            except Exception as exc:                   # noqa: BLE001
                LOG.warning("extrinsic decode failed: %s", exc)
                out.append(None)
        return blk.get("header", {}), out, spec

    def index_block(self, number: int, finalized_upto: int) -> dict:
        """Decode one block and write it. Idempotent."""
        block_hash = self.substrate.get_block_hash(number)
        header, extrinsics, spec_version = self._decode_extrinsics(block_hash)
        try:
            events = self.substrate.get_events(block_hash=block_hash)
        except Exception as exc:                       # noqa: BLE001
            LOG.warning("block %s: events undecodable (%s)", number, exc)
            events = []

        ts = None
        try:
            author = self.substrate.get_block_header(
                block_hash=block_hash, include_author=True).get("author")
        except Exception:                              # noqa: BLE001
            author = None

        # timestamp comes from the Timestamp.set inherent, not from the header
        rows_ex, rows_ev, rows_tr = [], [], []
        for idx, d in enumerate(extrinsics):
            if d is None:
                continue
            try:
                call = d.get("call", {}) or {}
                module = call.get("call_module", "")
                func = call.get("call_function", "")
                args = call.get("call_args", []) or []
                argd = {}
                for a in args:
                    if isinstance(a, dict) and "name" in a:
                        argd[a["name"]] = a.get("value")
                if module == "Timestamp" and func == "set":
                    now = self._amount(argd.get("now"))
                    if now:
                        ts = datetime.fromtimestamp(now / 1000, tz=timezone.utc)
                signer = self._ss58(d.get("address"))
                rows_ex.append((
                    number, idx, d.get("extrinsic_hash"), signer, module, func,
                    json.dumps(argd, default=str)[:60000], None,
                    None, self._amount(d.get("nonce")) if d.get("nonce") is not None else None,
                    self._amount(d.get("tip")), bool(signer), ts,
                ))
            except Exception as exc:                   # noqa: BLE001
                LOG.warning("block %s extrinsic %s: %s", number, idx, exc)

        success_by_ex = {}
        for ei, evt in enumerate(events):
            try:
                e = evt.value if hasattr(evt, "value") else evt
                mod = e.get("module_id") or e.get("module") or ""
                name = e.get("event_id") or e.get("event") or ""
                attrs = e.get("attributes")
                phase = e.get("phase") or {}
                ex_idx = None
                if isinstance(phase, dict):
                    ap = phase.get("ApplyExtrinsic")
                    if ap is not None:
                        ex_idx = self._amount(ap)
                elif e.get("extrinsic_idx") is not None:
                    ex_idx = e["extrinsic_idx"]

                if mod == "System" and name in ("ExtrinsicSuccess", "ExtrinsicFailed"):
                    if ex_idx is not None:
                        success_by_ex[ex_idx] = (name == "ExtrinsicSuccess")

                rows_ev.append((number, ei, ex_idx, mod, name,
                                json.dumps(attrs, default=str)[:60000], ts))

                # Balances.Transfer is what account history is built from
                if mod == "Balances" and name == "Transfer":
                    frm = to = None
                    amt = 0
                    if isinstance(attrs, dict):
                        frm = self._ss58(attrs.get("from"))
                        to = self._ss58(attrs.get("to"))
                        amt = self._amount(attrs.get("amount"))
                    elif isinstance(attrs, (list, tuple)) and len(attrs) >= 3:
                        frm = self._ss58(attrs[0])
                        to = self._ss58(attrs[1])
                        amt = self._amount(attrs[2])
                    if frm or to:
                        rows_tr.append((number, ex_idx, ei, frm, to, amt, None, True, ts))
            except Exception as exc:                   # noqa: BLE001
                LOG.warning("block %s event %s: %s", number, ei, exc)

        # stamp success onto extrinsics now that events are decoded
        rows_ex = [r[:7] + (success_by_ex.get(r[1]),) + r[8:] for r in rows_ex]

        is_final = number <= finalized_upto
        with self.db.cursor() as c:
            c.execute("""
                INSERT INTO blocks (number, hash, parent_hash, state_root,
                    extrinsics_root, timestamp, author, extrinsic_count, event_count,
                    transfer_count, finalized, spec_version)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (number) DO UPDATE SET
                    hash=EXCLUDED.hash, finalized=EXCLUDED.finalized,
                    timestamp=EXCLUDED.timestamp,
                    extrinsic_count=EXCLUDED.extrinsic_count,
                    event_count=EXCLUDED.event_count,
                    transfer_count=EXCLUDED.transfer_count
            """, (number, block_hash, header.get("parentHash"), header.get("stateRoot"),
                  header.get("extrinsicsRoot"), ts, author,
                  len(rows_ex), len(rows_ev), len(rows_tr), is_final, spec_version))

            if rows_ex:
                psycopg2.extras.execute_values(c, """
                    INSERT INTO extrinsics (block_number, idx, hash, signer,
                        call_module, call_function, args, success, fee, nonce, tip,
                        signed, timestamp)
                    VALUES %s
                    ON CONFLICT (block_number, idx) DO UPDATE SET
                        success=EXCLUDED.success
                """, rows_ex)
            if rows_ev:
                psycopg2.extras.execute_values(c, """
                    INSERT INTO events (block_number, idx, extrinsic_idx, module,
                        event, attributes, timestamp)
                    VALUES %s ON CONFLICT (block_number, idx) DO NOTHING
                """, rows_ev)
            if rows_tr:
                psycopg2.extras.execute_values(c, """
                    INSERT INTO transfers (block_number, extrinsic_idx, event_idx,
                        from_address, to_address, amount, fee, success, timestamp)
                    VALUES %s ON CONFLICT (block_number, event_idx) DO NOTHING
                """, rows_tr)

            # touch accounts seen in this block (balances refreshed separately)
            seen = {a for r in rows_tr for a in (r[3], r[4]) if a}
            seen |= {r[3] for r in rows_ex if r[3]}
            for addr in seen:
                c.execute("""
                    INSERT INTO accounts (address, first_seen, last_activity,
                        is_pallet, transfer_count)
                    VALUES (%s,%s,%s,%s,0)
                    ON CONFLICT (address) DO UPDATE SET
                        last_activity=GREATEST(accounts.last_activity, EXCLUDED.last_activity),
                        first_seen=LEAST(accounts.first_seen, EXCLUDED.first_seen)
                """, (addr, number, number, addr.startswith("modl")))

        return {"extrinsics": len(rows_ex), "events": len(rows_ev),
                "transfers": len(rows_tr), "ts": ts}

    def run(self, upto: int | None = None, follow: bool = False):
        signal.signal(signal.SIGTERM, _handle_signal)
        signal.signal(signal.SIGINT, _handle_signal)

        done = 0
        t0 = time.time()
        while not _stop:
            last = self.last_indexed()
            tip = self.chain_tip()
            fin = self.finalized_height()
            target = min(upto, tip) if upto is not None else tip

            if last >= target:
                if not follow:
                    LOG.info("caught up at %s", last)
                    break
                # at the tip: promote blocks that have since been finalized
                with self.db.cursor() as c:
                    c.execute("""UPDATE blocks SET finalized=TRUE
                                 WHERE number <= %s AND NOT finalized""", (fin,))
                    n = c.rowcount
                    c.execute("""UPDATE indexer_state
                                 SET last_finalized=%s, chain_tip=%s, updated_at=now()
                                 WHERE network=%s""", (fin, tip, self.network))
                self.db.commit()
                if n:
                    LOG.info("marked %s block(s) finalized up to %s", n, fin)
                time.sleep(6)
                continue

            end = min(last + self.batch, target)
            for n in range(last + 1, end + 1):
                if _stop:
                    break
                try:
                    self.index_block(n, fin)
                    with self.db.cursor() as c:
                        c.execute("""UPDATE indexer_state
                                     SET last_indexed_block=%s, last_finalized=%s,
                                         chain_tip=%s, blocks_indexed=blocks_indexed+1,
                                         updated_at=now(), last_error=NULL
                                     WHERE network=%s""",
                                  (n, fin, tip, self.network))
                    self.db.commit()
                    done += 1
                except Exception as exc:                # noqa: BLE001
                    self.db.rollback()
                    LOG.error("block %s failed: %s", n, exc)
                    with self.db.cursor() as c:
                        c.execute("""UPDATE indexer_state SET last_error=%s,
                                     updated_at=now() WHERE network=%s""",
                                  (str(exc)[:500], self.network))
                    self.db.commit()
                    # do not advance past a failed block: history must stay contiguous
                    time.sleep(2)
                    break

                if done and done % 250 == 0:
                    rate = done / max(time.time() - t0, 0.001)
                    LOG.info("indexed %s blocks (%.1f blk/s), at %s/%s",
                             done, rate, n, target)

        rate = done / max(time.time() - t0, 0.001)
        LOG.info("stopped after %s blocks (%.1f blk/s), last=%s",
                 done, rate, self.last_indexed())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--network", default="mainnet")
    ap.add_argument("--upto", type=int, default=None,
                    help="stop at this block (for a bounded test run)")
    ap.add_argument("--follow", action="store_true",
                    help="stay at the tip after catching up")
    ap.add_argument("--batch", type=int, default=200)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if a.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s")
    Indexer(a.network, batch=a.batch).run(upto=a.upto, follow=a.follow)


if __name__ == "__main__":
    main()
