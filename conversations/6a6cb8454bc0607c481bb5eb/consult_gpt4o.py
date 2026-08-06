#!/usr/bin/env python3
import json, urllib.request, os

api_key = os.environ.get("OPENAI_API_KEY_2", "")
if not api_key:
    with open("/opt/verdis-chain/.env") as f:
        for line in f:
            if line.startswith("OPENAI_API_KEY_2="):
                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

if not api_key:
    print("ERROR: No API key found")
    exit(1)

prompt = """You are the AI CTO for the Verdis Blockchain project. Review the current state and recommend the next phase.

CURRENT STATE (Phase 87 in progress):
- Substrate Node v2.0.0 functional with BABE/GRANDPA consensus
- 7 FRAME pallets deployed: DPoS, AmmDex, Eco, Tokenomics, Vesting, EVM, Storage
- 165/165 tests passing (25 AmmDex, 23 DPoS, 33 Eco, 34 Storage, 10 Tokenomics, 29 EVM, 9 Vesting, 2 Runtime)
- Benchmarking infrastructure COMPLETE: All 5 core pallets have benchmarking modules written and compiling
  - DPoS: 6 benchmarks (register_validator, unregister_validator, vote, unvote, slash_validator, update_green_score)
  - AmmDex: 5 benchmarks (create_pool, add_liquidity, remove_liquidity, swap, get_price)
  - Eco: 9 benchmarks (mint_carbon_credit, verify_carbon_credit, retire_carbon_credit, transfer_carbon_credit, create_reforest_project, update_reforest_project, verify_reforest_project, register_green_validator, update_green_score)
  - Tokenomics: 4 benchmarks (give_consent, purchase, update_presale_price, release_distribution)
  - Vesting: 3 benchmarks (assign_vesting, release_vested, check_transfer)
- define_benchmarks! macro registered in runtime
- frame-benchmarking-cli NOT integrated (core2 v0.4.0 yanked on crates.io, blocking CLI dependency)
- clippy: 75 warnings (0 errors), fmt: clean
- Native binary compiles, release build in progress
- Chain spec: "Verdis Development", 100B supply, 12B investor allocation
- RPC live on port 9944, blocks producing, GRANDPA finality working
- Production server: 62.238.61.145, 14 Docker containers

BLOCKING ISSUE:
- frame-benchmarking-cli v49.0.0 depends on core2 v0.4.0 which is yanked from crates.io
- The CLI tool to actually RUN benchmarks and generate measured weight files cannot be compiled
- Benchmarking modules are written but cannot be executed to produce real weight values
- All pallet weights currently use default WeightInfo (constant 10_000)

QUESTION: What should be the next phase? Consider:
1. How to work around the core2 yanked crate issue to get actual benchmark measurements
2. EVM pallet expansion (currently 101 opcodes planned, only basic ones implemented)
3. Storage pallet tests (currently 34 tests but may need expansion)
4. Any other critical production-readiness items

Provide a specific, actionable recommendation with a phase number and scope."""

data = json.dumps({
    "model": "gpt-4o",
    "messages": [
        {"role": "system", "content": "You are the AI CTO for Verdis Chain, a carbon-negative blockchain built on Rust + Substrate with BABE/GRANDPA consensus. Provide precise, actionable engineering recommendations."},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.3,
    "max_tokens": 2000
}).encode()

req = urllib.request.Request(
    "https://api.openai.com/v1/chat/completions",
    data=data,
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
)

resp = urllib.request.urlopen(req, timeout=60)
result = json.loads(resp.read())
print(result["choices"][0]["message"]["content"])
