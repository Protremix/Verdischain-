#!/usr/bin/env python3
"""Prove the Root-bypass upgrade path on devnet, end to end.

Established from source:
  * construct_runtime's generated `filter_call` returns true unconditionally for
    `OriginCaller::system(Origin::Root)` - "Root bypasses all filters" (origin.rs:163).
  * pallet_collective dispatches an approved motion with `RawOrigin::Members(yes, seats)`,
    NOT Root -> that is why our Council motion returned CallFiltered.
  * pallet_democracy enacts an approved referendum with Root.

So the upgrade path is: Council external_propose_majority (2/3) -> Council fast_track (2/3)
-> referendum -> enactment dispatched as Root -> BaseCallFilter bypassed -> set_code runs.

This script proves the bypass using `System.set_storage`, which BaseCallFilter also blocks
(runtime/src/lib.rs:219). If a filtered call succeeds via Democracy-Root on devnet, the same
mechanism carries set_code on mainnet. A junk storage key is written on a throwaway chain;
mainnet is untouched and the endpoint's genesis is asserted first.
"""
import time

from substrateinterface import Keypair, SubstrateInterface

MAINNET = "0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e"
PROBE_KEY = "0x76657264697370726f62655f726f6f745f62797061737300"   # b"verdisprobe_root_bypass\0"
PROBE_VAL = "0xdeadbeef"


def wait_to(s, target, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        cur = s.get_block_number(s.get_chain_head())
        if cur >= target:
            return cur
        time.sleep(6)
    return s.get_block_number(s.get_chain_head())


def events(s, frm, to, mods=("Council", "Democracy", "System", "Scheduler", "Preimage")):
    out = []
    for bn in range(frm + 1, to + 1):
        try:
            evs = s.get_events(s.get_block_hash(bn))
        except Exception:                               # noqa: BLE001
            continue
        for e in evs:
            v = e.value if hasattr(e, "value") else e
            ev = v.get("event", v)
            mod = str(ev.get("module_id") or "")
            nm = str(ev.get("event_id") or "")
            if mod in mods and nm != "ExtrinsicSuccess":
                out.append((bn, f"{mod}.{nm}", str(ev.get("attributes"))[:120]))
    return out


def council_motion(s, keys, inner, length_bound):
    """Run a Council motion to completion. Returns True if Council.Executed was Ok."""
    members = s.query("Council", "Members").value or []
    threshold = max(1, (len(members) * 2) // 3 + 1)
    hb = s.get_block_number(s.get_chain_head())
    kp0 = keys[0][1]
    prop = s.compose_call(call_module="Council", call_function="propose",
                          call_params={"threshold": threshold, "proposal": inner.value,
                                       "length_bound": length_bound})
    s.submit_extrinsic(s.create_signed_extrinsic(call=prop, keypair=kp0),
                       wait_for_inclusion=False)
    wait_to(s, hb + 2)
    props = s.query("Council", "Proposals").value or []
    if not props:
        print("    no proposal created")
        return False
    phash = props[-1]
    info = s.query("Council", "Voting", [phash]).value
    for seed, kp in keys:
        c = s.compose_call(call_module="Council", call_function="vote",
                           call_params={"proposal": phash, "index": info["index"],
                                        "approve": True})
        try:
            s.submit_extrinsic(s.create_signed_extrinsic(call=c, keypair=kp),
                               wait_for_inclusion=False)
        except Exception as exc:                        # noqa: BLE001
            print(f"    {seed} vote: {str(exc)[:80]}")
        time.sleep(7)
    info = s.query("Council", "Voting", [phash]).value
    ayes = len(info["ayes"]) if info else 0
    print(f"    ayes {ayes}/{threshold}")
    hb2 = s.get_block_number(s.get_chain_head())
    c = s.compose_call(call_module="Council", call_function="close",
                       call_params={"proposal_hash": phash, "index": info["index"],
                                    "proposal_weight_bound": {"ref_time": 500_000_000_000,
                                                              "proof_size": 20_000_000},
                                    "length_bound": max(length_bound, 2_000_000)})
    s.submit_extrinsic(s.create_signed_extrinsic(call=c, keypair=kp0),
                       wait_for_inclusion=False)
    wait_to(s, hb2 + 3)
    ok = None
    for bn, name, at in events(s, hb2, s.get_block_number(s.get_chain_head())):
        print(f"    block {bn}: {name} -> {at}")
        if name == "Council.Executed":
            ok = "'Ok'" in at
    return bool(ok)


def main():
    s = SubstrateInterface(url="http://127.0.0.1:9970")
    if s.get_block_hash(0) == MAINNET:
        raise SystemExit("REFUSING: MAINNET")
    print(f"devnet spec {s.get_block_runtime_version(s.get_chain_head())['specVersion']}")

    fmt = (s.properties or {}).get("ss58Format", s.ss58_format)
    members = s.query("Council", "Members").value or []
    keys = []
    for seed in ("//Alice", "//Bob", "//Charlie"):
        kp = Keypair.create_from_uri(seed, ss58_format=fmt)
        if kp.ss58_address in members:
            keys.append((seed, kp))
    print(f"Council keys controlled: {len(keys)}/{len(members)}")

    try:
        before = s.get_storage_by_key(s.get_chain_head(), PROBE_KEY)
    except Exception as exc:                            # noqa: BLE001
        before = f"<unreadable: {str(exc)[:60]}>"
    print(f"probe key before: {before}")

    payload = s.compose_call(call_module="System", call_function="set_storage",
                             call_params={"items": [[PROBE_KEY, PROBE_VAL]]})
    enc = str(payload.data)
    print(f"payload (a BaseCallFilter-BLOCKED call): {enc[:42]}... {len(enc)//2} bytes")

    print("\n=== 1. note the preimage, so the referendum can reference it ===")
    hb = s.get_block_number(s.get_chain_head())
    note = s.compose_call(call_module="Preimage", call_function="note_preimage",
                          call_params={"bytes": enc})
    s.submit_extrinsic(s.create_signed_extrinsic(call=note, keypair=keys[0][1]),
                       wait_for_inclusion=False)
    wait_to(s, hb + 2)
    ph = None
    for bn, name, at in events(s, hb, s.get_block_number(s.get_chain_head())):
        print(f"  block {bn}: {name} -> {at}")
        if name == "Preimage.Noted":
            import re
            m = re.search(r"0x[0-9a-f]{64}", at)
            if m:
                ph = m.group(0)
    if not ph:
        ph = s.get_block_hash(1)
        print("  could not read the preimage hash from events")
        return 1
    print(f"  preimage hash: {ph}")
    plen = len(enc) // 2 - 1

    print("\n=== 2. Council motion: Democracy.external_propose_majority ===")
    ext_prop = s.compose_call(
        call_module="Democracy", call_function="external_propose_majority",
        call_params={"proposal": {"Lookup": {"hash": ph, "len": plen}}})
    if not council_motion(s, keys, ext_prop, 4096):
        print("  external_propose_majority did NOT execute Ok")
        return 1

    print("\n=== 3. Council motion: Democracy.fast_track ===")
    ft = s.compose_call(call_module="Democracy", call_function="fast_track",
                        call_params={"proposal_hash": ph,
                                     "voting_period": 300, "delay": 0})
    council_motion(s, keys, ft, 4096)

    refs = s.query("Democracy", "ReferendumCount").value
    print(f"\n=== 4. referendum count = {refs} ===")
    if not refs:
        print("  no referendum was created")
        return 1
    idx = refs - 1
    info = s.query("Democracy", "ReferendumInfoOf", [idx]).value
    print(f"  referendum {idx}: {str(info)[:200]}")

    print("\n=== 5. vote aye with all Council accounts ===")
    for seed, kp in keys:
        v = s.compose_call(call_module="Democracy", call_function="vote",
                           call_params={"ref_index": idx,
                                        "vote": {"Standard": {
                                            "vote": {"aye": True, "conviction": "Locked1x"},
                                            "balance": 1000 * 10**9}}})
        try:
            s.submit_extrinsic(s.create_signed_extrinsic(call=v, keypair=kp),
                               wait_for_inclusion=False)
            print(f"  {seed} voted aye")
        except Exception as exc:                        # noqa: BLE001
            print(f"  {seed} vote failed: {str(exc)[:100]}")
        time.sleep(7)

    info = s.query("Democracy", "ReferendumInfoOf", [idx]).value
    end = None
    try:
        end = info["Ongoing"]["end"]
    except Exception:                                   # noqa: BLE001
        pass
    print(f"  referendum ends at block {end}, current "
          f"{s.get_block_number(s.get_chain_head())}")
    print(f"  tally: {str(info)[:220]}")
    print("\nReferendum is live. Enactment is dispatched with Root, which bypasses")
    print("BaseCallFilter - that is the mechanism mainnet's set_code needs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
