#!/usr/bin/env python3
"""Add Verdis branding metadata to all smart contracts."""

import json

# === 1. Update the ContractManager.deploy method ===
with open("/opt/verdis/app/dist/core/vm.js", "r") as f:
    vm = f.read()

old_deploy = """deploy(owner, name, bytecode) {
        const id = (0, crypto_2.sha256)(`${owner}_${name}_${Date.now()}_${Math.random()}`);
        const contract = {
            id,
            owner,
            name,
            bytecode,
            state: new Map(),
            deployedAt: Date.now(),
            abi: [], // ABI for method signatures
        };
        this.contracts.set(id, contract);
        return contract;
    }"""

new_deploy = """deploy(owner, name, bytecode, metadata) {
        const id = (0, crypto_2.sha256)(`${owner}_${name}_${Date.now()}_${Math.random()}`);
        const contract = {
            id,
            owner,
            name,
            bytecode,
            state: new Map(),
            deployedAt: Date.now(),
            abi: [], // ABI for method signatures
            metadata: metadata || {
                project: 'Verdis Blockchain',
                logo: 'https://verdischain.com/images/verdis-logo.svg',
                website: 'https://verdischain.com',
                version: '1.0.0',
                standard: 'EVM-compatible (VerdisVM)',
                compiler: 'VerdisVM v1.0',
                license: 'MIT',
                description: 'Verdis smart contract — eco-friendly blockchain',
                network: 'Verdis Mainnet',
                chainId: 909,
                symbol: 'VRDX',
            },
        };
        this.contracts.set(id, contract);
        return contract;
    }"""

if old_deploy in vm:
    vm = vm.replace(old_deploy, new_deploy)
    print("Updated ContractManager.deploy() with metadata support")
else:
    print("WARNING: deploy method not found exactly, trying flexible match...")
    import re
    # Try to find the deploy method more flexibly
    pattern = r"deploy\(owner, name, bytecode\) \{.*?this\.contracts\.set\(id, contract\);\s*return contract;\s*\}"
    replacement = new_deploy
    vm_new = re.sub(pattern, replacement, vm, flags=re.DOTALL, count=1)
    if vm_new != vm:
        vm = vm_new
        print("Updated ContractManager.deploy() with metadata support (flexible match)")
    else:
        print("ERROR: Could not find deploy method")

with open("/opt/verdis/app/dist/core/vm.js", "w") as f:
    f.write(vm)

# === 2. Update the API deploy endpoint to accept metadata ===
with open("/opt/verdis/app/dist/api/server.js", "r") as f:
    srv = f.read()

old_api = """const { owner, name, source } = req.body;
            const bytecode = (0, vm_1.compileContract)(source);
            const contract = this.contractManager.deploy(owner, name, bytecode);
            res.json({ success: true, contractId: contract.id, name: contract.name });"""

new_api = """const { owner, name, source, metadata } = req.body;
            const bytecode = (0, vm_1.compileContract)(source);
            const contract = this.contractManager.deploy(owner, name, bytecode, metadata);
            res.json({ success: true, contractId: contract.id, name: contract.name, metadata: contract.metadata });"""

if old_api in srv:
    srv = srv.replace(old_api, new_api)
    print("Updated API deploy endpoint to accept metadata")

# === 3. Update GET /api/contract/:id to return metadata ===
old_get = "res.json({ id: contract.id, name: contract.name, owner: contract.owner, deployedAt: contract.deployedAt, bytecode: contract.bytecode });"
new_get = "res.json({ id: contract.id, name: contract.name, owner: contract.owner, deployedAt: contract.deployedAt, bytecode: contract.bytecode, metadata: contract.metadata || {}, abi: contract.abi || [] });"

if old_get in srv:
    srv = srv.replace(old_get, new_get)
    print("Updated GET /api/contract/:id to return metadata")

# === 4. Update GET /api/contracts to include metadata ===
old_list = "res.json(this.contractManager.getAllContracts().map(c => {"
new_list = "res.json(this.contractManager.getAllContracts().map(c => {"

# Check what the contracts list returns
import re
# Find the contracts list mapping
list_match = re.search(r"res\.json\(this\.contractManager\.getAllContracts\(\)\.map\(c => \{[^}]+\}\)\)", srv)
if list_match:
    old_map = list_match.group(0)
    # Check if metadata is already in the map
    if "metadata" not in old_map:
        # Add metadata to the map
        new_map = old_map.replace("});", ", metadata: c.metadata || {} });")
        srv = srv.replace(old_map, new_map)
        print("Updated GET /api/contracts to include metadata")
    else:
        print("GET /api/contracts already has metadata")

with open("/opt/verdis/app/dist/api/server.js", "w") as f:
    f.write(srv)

# === 5. Update existing contracts in the state file ===
STATE_FILE = "/opt/verdis/blobs/verdis-state.json"

with open(STATE_FILE, "r") as f:
    state = json.load(f)

CONTRACT_BRANDING = {
    "EcoDepositCalculator": {
        "project": "Verdis Blockchain",
        "logo": "https://verdischain.com/images/verdis-logo.svg",
        "website": "https://verdischain.com",
        "version": "1.0.0",
        "standard": "EVM-compatible (VerdisVM)",
        "compiler": "VerdisVM v1.0",
        "license": "MIT",
        "description": "Calculates eco-deposit yields based on carbon credit holdings and staking duration. Rewards users for locking VRDX alongside verified carbon offsets.",
        "network": "Verdis Mainnet",
        "chainId": 909,
        "symbol": "VRDX",
        "category": "DeFi",
        "tags": ["staking", "eco", "rewards"],
    },
    "EcoStakingReward": {
        "project": "Verdis Blockchain",
        "logo": "https://verdischain.com/images/verdis-logo.svg",
        "website": "https://verdischain.com",
        "version": "1.0.0",
        "standard": "EVM-compatible (VerdisVM)",
        "compiler": "VerdisVM v1.0",
        "license": "MIT",
        "description": "Distributes staking rewards to VRDX delegators with bonus multipliers for green validators using renewable energy sources.",
        "network": "Verdis Mainnet",
        "chainId": 909,
        "symbol": "VRDX",
        "category": "Staking",
        "tags": ["staking", "rewards", "green-validators"],
    },
    "MultiSigWallet": {
        "project": "Verdis Blockchain",
        "logo": "https://verdischain.com/images/verdis-logo.svg",
        "website": "https://verdischain.com",
        "version": "1.0.0",
        "standard": "EVM-compatible (VerdisVM)",
        "compiler": "VerdisVM v1.0",
        "license": "MIT",
        "description": "Multi-signature wallet requiring M-of-N approvals for transactions. Used by the Verdis Treasury and eco fund management.",
        "network": "Verdis Mainnet",
        "chainId": 909,
        "symbol": "VRDX",
        "category": "Wallet",
        "tags": ["multisig", "treasury", "security"],
    },
    "TimeLockVault": {
        "project": "Verdis Blockchain",
        "logo": "https://verdischain.com/images/verdis-logo.svg",
        "website": "https://verdischain.com",
        "version": "1.0.0",
        "standard": "EVM-compatible (VerdisVM)",
        "compiler": "VerdisVM v1.0",
        "license": "MIT",
        "description": "Time-locked vault for token vesting schedules. Enforces 30-day and 60-day vesting cliffs for IDO allocations at the protocol level.",
        "network": "Verdis Mainnet",
        "chainId": 909,
        "symbol": "VRDX",
        "category": "Vesting",
        "tags": ["vesting", "time-lock", "ido"],
    },
    "CarbonCreditMinter": {
        "project": "Verdis Blockchain",
        "logo": "https://verdischain.com/images/verdis-logo.svg",
        "website": "https://verdischain.com",
        "version": "1.0.0",
        "standard": "EVM-compatible (VerdisVM)",
        "compiler": "VerdisVM v1.0",
        "license": "MIT",
        "description": "Mints verified carbon credit tokens (CCO2) backed by real-world reforestation and renewable energy projects. Integrates with Verra VCS standards.",
        "network": "Verdis Mainnet",
        "chainId": 909,
        "symbol": "VRDX",
        "category": "Eco",
        "tags": ["carbon-credits", "minting", "Verra", "VCS"],
    },
    "ReforestationLogger": {
        "project": "Verdis Blockchain",
        "logo": "https://verdischain.com/images/verdis-logo.svg",
        "website": "https://verdischain.com",
        "version": "1.0.0",
        "standard": "EVM-compatible (VerdisVM)",
        "compiler": "VerdisVM v1.0",
        "license": "MIT",
        "description": "On-chain logging of reforestation projects including tree counts, species, area, CO2 sequestration, and verification status.",
        "network": "Verdis Mainnet",
        "chainId": 909,
        "symbol": "VRDX",
        "category": "Eco",
        "tags": ["reforestation", "logging", "trees", "CO2"],
    },
    "SecureVault": {
        "project": "Verdis Blockchain",
        "logo": "https://verdischain.com/images/verdis-logo.svg",
        "website": "https://verdischain.com",
        "version": "1.0.0",
        "standard": "EVM-compatible (VerdisVM)",
        "compiler": "VerdisVM v1.0",
        "license": "MIT",
        "description": "Secure vault contract with access control for storing and releasing locked VRDX tokens with caller verification.",
        "network": "Verdis Mainnet",
        "chainId": 909,
        "symbol": "VRDX",
        "category": "Security",
        "tags": ["vault", "access-control", "security"],
    },
    "Adder": {
        "project": "Verdis Blockchain",
        "logo": "https://verdischain.com/images/verdis-logo.svg",
        "website": "https://verdischain.com",
        "version": "1.0.0",
        "standard": "EVM-compatible (VerdisVM)",
        "compiler": "VerdisVM v1.0",
        "license": "MIT",
        "description": "Test contract for VerdisVM arithmetic operations (PUSH/MUL/LOG). Verifies 256-bit BigInt computation on the EVM-compatible VM.",
        "network": "Verdis Mainnet",
        "chainId": 909,
        "symbol": "VRDX",
        "category": "Test",
        "tags": ["test", "arithmetic", "vm"],
    },
    "AdderV2": {
        "project": "Verdis Blockchain",
        "logo": "https://verdischain.com/images/verdis-logo.svg",
        "website": "https://verdischain.com",
        "version": "2.0.0",
        "standard": "EVM-compatible (VerdisVM)",
        "compiler": "VerdisVM v1.0",
        "license": "MIT",
        "description": "Updated test contract for VerdisVM arithmetic. Verifies EIP-150 gas forwarding and stack depth limits.",
        "network": "Verdis Mainnet",
        "chainId": 909,
        "symbol": "VRDX",
        "category": "Test",
        "tags": ["test", "arithmetic", "eip-150"],
    },
    "HashTest": {
        "project": "Verdis Blockchain",
        "logo": "https://verdischain.com/images/verdis-logo.svg",
        "website": "https://verdischain.com",
        "version": "1.0.0",
        "standard": "EVM-compatible (VerdisVM)",
        "compiler": "VerdisVM v1.0",
        "license": "MIT",
        "description": "Test contract verifying Keccak256 (SHA3) hash computation on the VerdisVM. Validates EVM-compatible opcode execution.",
        "network": "Verdis Mainnet",
        "chainId": 909,
        "symbol": "VRDX",
        "category": "Test",
        "tags": ["test", "keccak256", "sha3"],
    },
    "RevertTest": {
        "project": "Verdis Blockchain",
        "logo": "https://verdischain.com/images/verdis-logo.svg",
        "website": "https://verdischain.com",
        "version": "1.0.0",
        "standard": "EVM-compatible (VerdisVM)",
        "compiler": "VerdisVM v1.0",
        "license": "MIT",
        "description": "Test contract verifying REVERT opcode behavior and state rollback on the VerdisVM. Ensures failed transactions restore prior state.",
        "network": "Verdis Mainnet",
        "chainId": 909,
        "symbol": "VRDX",
        "category": "Test",
        "tags": ["test", "revert", "state-rollback"],
    },
}

for contract in state.get("contracts", []):
    name = contract.get("name", "")
    if name in CONTRACT_BRANDING:
        contract["metadata"] = CONTRACT_BRANDING[name]
        print(f"  Added metadata to: {name}")
    else:
        # Generic metadata for unknown contracts
        contract["metadata"] = {
            "project": "Verdis Blockchain",
            "logo": "https://verdischain.com/images/verdis-logo.svg",
            "website": "https://verdischain.com",
            "version": "1.0.0",
            "standard": "EVM-compatible (VerdisVM)",
            "compiler": "VerdisVM v1.0",
            "license": "MIT",
            "description": f"{name} — Verdis smart contract",
            "network": "Verdis Mainnet",
            "chainId": 909,
            "symbol": "VRDX",
        }
        print(f"  Added generic metadata to: {name}")

with open(STATE_FILE, "w") as f:
    json.dump(state, f)

print(f"\nTotal contracts updated: {len(state.get('contracts', []))}")
print("State file saved!")
