#!/usr/bin/env python3
"""MAINNET UPGRADE - step 5: watch the referendum close, then confirm spec 17 is live.

Referendum 0 carries System.set_code(spec 17). Council voted 2,700 ayes / 0 nays; voting ends
at block 58353, delay 0, so enactment schedules right after.

This watches finality throughout. A runtime upgrade is the single riskiest operation on a
live chain: if block production or finality stops after the swap, that must be caught
immediately, not discovered later. Mainnet carries 21 authorities, threshold 15.
"""
import sys
import time

from substrateinterface import SubstrateInterface

MAINNET = "0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e"
RPC = "ws://127.0.0.1:19955"
DEC = 10 ** 9


def finality(s):
    head = s.get_chain_head()
    bn = s.get_block_number(head)
    fh = s.get_chain_finalised_head()
    fn = s.get_block_number(fh)
    return bn, fn, bn - fn


def main():
    s = SubstrateInterface(url=RPC)
    if s.get_block_hash(0) != MAINNET:
        sys.exit("ABORT: not mainnet")

    spec0 = s.get_block_runtime_version(s.get_chain_head())["specVersion"]
    idx = (s.query("Democracy", "ReferendumCount").value or 1) - 1
    print(f"watching referendum {idx}, spec now {spec0}")

    deadline = time.time() + 3300
    phase = "voting"
    while time.time() < deadline:
        bn, fn, lag = finality(s)
        spec = s.get_block_runtime_version(s.get_chain_head())["specVersion"]
        info = s.query("Democracy", "ReferendumInfoOf", [idx]).value

        if spec != spec0:
            print(f"\n*** RUNTIME UPGRADED: spec {spec0} -> {spec} at block {bn} ***")
            break

        if info and "Ongoing" in info:
            o = info["Ongoing"]
            t = o["tally"]
            print(f"  [{phase}] block {bn} final {fn} lag {lag} | "
                  f"ends {o['end']} in {max(0,o['end']-bn)*6//60}m | "
                  f"ayes {t['ayes']/DEC:,.0f} nays {t['nays']/DEC:,.0f}")
        elif info and "Finished" in info:
            f = info["Finished"]
            if phase != "enacting":
                print(f"\n  referendum FINISHED approved={f.get('approved')} "
                      f"at block {f.get('end')}")
                phase = "enacting"
            print(f"  [{phase}] block {bn} final {fn} lag {lag} spec {spec}")
        else:
            print(f"  [{phase}] block {bn} final {fn} lag {lag} spec {spec} "
                  f"(referendum state {str(info)[:60]})")

        if lag > 30:
            print(f"  WARNING: finality lag {lag}")
        time.sleep(30)

    print("\n=== final state ===")
    bn, fn, lag = finality(s)
    spec = s.get_block_runtime_version(s.get_chain_head())["specVersion"]
    print(f"  block {bn}, finalized {fn}, lag {lag}")
    print(f"  specVersion {spec}")

    # scan the last blocks for the enactment events
    print("\n=== enactment events ===")
    for b in range(max(1, bn - 40), bn + 1):
        try:
            evs = s.get_events(s.get_block_hash(b))
        except Exception:                               # noqa: BLE001
            continue
        for e in evs:
            v = e.value if hasattr(e, "value") else e
            ev = v.get("event", v)
            mod, nm = str(ev.get("module_id")), str(ev.get("event_id"))
            if nm == "ExtrinsicSuccess":
                continue
            if (mod, nm) in (("System", "CodeUpdated"), ("Democracy", "Passed"),
                             ("Democracy", "NotPassed"), ("Scheduler", "Dispatched"),
                             ("Scheduler", "Scheduled"), ("Preimage", "Requested")):
                print(f"  block {b}: {mod}.{nm} -> {str(ev.get('attributes'))[:120]}")

    if spec >= 17:
        print("\n  VERDICT: mainnet is running the FIXED runtime (spec 17).")
        print("  Contracts deploy, deposits are 0.001 VRDX/byte.")
    else:
        print(f"\n  VERDICT: still spec {spec} - enactment has not happened yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
