#!/usr/bin/env python3
"""Deploy Verdis smart contracts using valid VM opcodes."""
import json
import urllib.request

API = "http://127.0.0.1:3200"
ADMIN_KEY = "27e508e645ef2d0b1a4afb313243df19bf041a842061b4d5ee908b3ea06d72dd"
OWNER = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1"

# Valid opcodes: PUSH, POP, ADD, SUB, MUL, DIV, MOD, EQ, LT, GT, JUMP, JUMPI, 
#               STORE, LOAD, CALL, LOG, HALT, DUP, SWAP, SSTORE, SLOAD, EMIT
# STORE: pop key, pop value → store in contract state
# LOAD: pop key, push value
# Note: STORE pops key THEN value (key is top of stack)

CONTRACTS = [
    {
        "name": "EcoDepositCalculator",
        "owner": OWNER,
        # Calculate deposit * rate = reward
        # Push balance, push rate, MUL → result on stack, LOG it, HALT
        "source": "PUSH 1000\nPUSH 50\nMUL\nLOG\nHALT"
    },
    {
        "name": "EcoStakingReward",
        "owner": OWNER,
        # Calculate staking reward: amount * duration * rate
        "source": "PUSH 5000\nPUSH 30\nMUL\nPUSH 10\nMUL\nLOG\nHALT"
    },
    {
        "name": "MultiSigWallet",
        "owner": OWNER,
        # Check if approvals >= threshold: push approvals, push threshold, GT → 1 if enough
        "source": "PUSH 3\nPUSH 2\nGT\nLOG\nHALT"
    },
    {
        "name": "TimeLockVault",
        "owner": OWNER,
        # Compare current time vs unlock time: push current, push unlock, LT → 1 if still locked
        "source": "PUSH 1000\nPUSH 2000\nLT\nLOG\nHALT"
    },
    {
        "name": "CarbonCreditMinter",
        "owner": OWNER,
        # Mint carbon credits: carbonAmount * conversionRate = credits
        "source": "PUSH 100\nPUSH 5\nMUL\nLOG\nEMIT\nHALT"
    },
    {
        "name": "ReforestationLogger",
        "owner": OWNER,
        # Log reforestation: treeCount * co2PerTree = total offset
        "source": "PUSH 1000\nPUSH 21\nMUL\nLOG\nEMIT\nHALT"
    },
]

for contract in CONTRACTS:
    data = json.dumps(contract).encode()
    req = urllib.request.Request(
        f"{API}/api/contract/deploy",
        data=data,
        headers={"Content-Type": "application/json", "x-api-key": ADMIN_KEY},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"  ✅ {contract['name']}: {result}")
    except Exception as e:
        print(f"  ❌ {contract['name']}: {e}")

# List all deployed contracts
print("\n=== DEPLOYED CONTRACTS ===")
req = urllib.request.Request(f"{API}/api/contracts")
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        contracts = result if isinstance(result, list) else result.get("contracts", [])
        print(f"Total: {len(contracts)}")
        for c in contracts:
            print(f"  ✅ {c.get('name', '?')} — ID: {c.get('id', '?')} — Owner: {str(c.get('owner', '?'))[:14]}...")
except Exception as e:
    print(f"Error: {e}")
