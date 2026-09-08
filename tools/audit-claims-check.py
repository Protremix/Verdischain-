#!/usr/bin/env python3
"""Audit-readiness gate: every public claim must be provable against the live chain.

Halborn compares documentation and marketing against the code. Any statement on the site or in
the repo that the runtime does not implement becomes a finding. This script is the reverse
check: it reads the claims out of the published pages and verifies each against mainnet, so a
discrepancy is caught by us before it is caught by an auditor.

Exit code is non-zero when a claim cannot be proven, so this can gate a release.
"""
import json
import re
import sys
import urllib.request

API = "https://verdischain.com/api/v2"
SITE = "https://verdischain.com"
MAINNET_GENESIS = "0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e"


def get(url, raw=False):
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache",
                                               "User-Agent": "verdis-audit-check"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read().decode("utf-8", "replace")
    return data if raw else json.loads(data)


def main():
    failures = []
    print("=" * 70)
    print("AUDIT READINESS: public claims vs the live chain")
    print("=" * 70)

    # ---- chain facts ----------------------------------------------------------------
    rt = get(f"{API}/runtime")["data"]
    net = get(f"{API}/network")["data"]
    sup = get(f"{API}/supply")["data"]
    st = get(f"{API}/status")["data"]
    pallets = {p["name"] for p in rt["pallets"]}

    print(f"\nCHAIN (read live)")
    print(f"  genesis            {st.get('genesis')}")
    print(f"  spec_version       {rt['spec_version']}")
    print(f"  pallets            {rt['pallet_count']}")
    print(f"  validators         {net['authorities']} (threshold {net['grandpa_threshold']})")
    print(f"  block time         {net['block_time_seconds']}s")
    print(f"  total issuance     {sup['total_issuance']['amount']} VRDX")
    print(f"  EVM present        {'Evm' in pallets or 'EVM' in pallets}")
    print(f"  Ethereum present   {'Ethereum' in pallets}")
    print(f"  Contracts (ink!)   {'Contracts' in pallets}")
    print(f"  Sudo present       {'Sudo' in pallets}")

    if st.get("genesis") != MAINNET_GENESIS:
        failures.append(f"API serves genesis {st.get('genesis')}, not mainnet")

    # ---- landing page --------------------------------------------------------------
    html = get(f"{SITE}/?audit=1", raw=True)
    print(f"\nLANDING PAGE ({len(html):,} bytes)")

    checks = [
        # (label, condition that must hold, detail)
        ("no '143 opcodes' claim", "143" not in html, "EVM opcode count still advertised"),
        ("no 'Chain ID 909' claim", "Chain ID 909" not in html,
         "Solidity chain id advertised but pallet-evm absent"),
        ("no 'Testnet Live' banner", "Testnet Live" not in html,
         "mainnet is live, banner says testnet"),
        ("no '16 pallets' claim", "16 pallets" not in html,
         f"runtime has {rt['pallet_count']} pallets"),
    ]
    for label, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {label}")
        if not ok:
            failures.append(f"landing page: {detail}")

    # pallet count actually stated
    m = re.search(r"(\d+)\s+pallets", html)
    if m:
        stated = int(m.group(1))
        ok = stated == rt["pallet_count"]
        print(f"  {'PASS' if ok else 'FAIL'}  states {stated} pallets, chain has {rt['pallet_count']}")
        if not ok:
            failures.append(f"landing page states {stated} pallets, chain has {rt['pallet_count']}")

    # if EVM is mentioned at all, it must be flagged as roadmap
    if "EVM" in html:
        near = " ".join(re.findall(r".{0,120}EVM.{0,120}", html))
        flagged = any(w in near for w in ("Roadmap", "roadmap", "not yet", "in development",
                                          "planned", "Planned"))
        print(f"  {'PASS' if flagged else 'FAIL'}  EVM mentioned and marked as roadmap")
        if not flagged:
            failures.append("EVM mentioned without a roadmap/not-yet qualifier")

    # ---- claims that must be TRUE --------------------------------------------------
    print(f"\nCLAIMS THAT MUST HOLD")
    positives = [
        ("ink! contracts live on mainnet", get(f"{API}/contracts")["count"] >= 1),
        ("21 validators", net["authorities"] == 21),
        ("no Sudo (governance-only)", "Sudo" not in pallets),
        ("Council present", "Council" in pallets),
        ("index at chain tip", abs(st.get("chain_tip", 0) - st.get("last_indexed_block", 0)) <= 3),
    ]
    for label, ok in positives:
        print(f"  {'PASS' if ok else 'FAIL'}  {label}")
        if not ok:
            failures.append(f"claim not provable: {label}")

    print("\n" + "=" * 70)
    if failures:
        print(f"NOT AUDIT-READY - {len(failures)} issue(s):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("ALL PUBLIC CLAIMS VERIFIED AGAINST THE CHAIN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
