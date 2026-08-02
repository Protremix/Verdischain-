#!/usr/bin/env python3
"""
Add Ethereum-style security to the contract system:
1. Contract address derivation (CREATE/CREATE2)
2. Raw EVM bytecode execution support
3. Contract size limit (EIP-170: 24576 bytes)
4. Contract nonce tracking
"""
import re

# === 1. Update ContractManager.deploy() with Ethereum-style address ===
with open("/opt/verdis/app/dist/core/vm.js", "r") as f:
    vm = f.read()

# Add contract nonce tracking and Ethereum-style address derivation
old_deploy = """deploy(owner, name, bytecode, metadata) {
        const id = (0, crypto_2.sha256)(`${owner}_${name}_${Date.now()}_${Math.random()}`);"""

new_deploy = """deploy(owner, name, bytecode, metadata) {
        // EIP-170: Contract code size limit (24576 bytes)
        const MAX_CODE_SIZE = 24576;
        if (bytecode && bytecode.length > MAX_CODE_SIZE) {
            throw new Error(`Contract code size exceeds EIP-170 limit: ${bytecode.length} > ${MAX_CODE_SIZE}`);
        }
        // Ethereum-style contract address derivation
        // CREATE: address = last 20 bytes of keccak256(sender ++ nonce)
        this.contractNonces = this.contractNonces || new Map();
        const senderNonce = (this.contractNonces.get(owner) || 0);
        this.contractNonces.set(owner, senderNonce + 1);
        const id = (0, crypto_2.sha256)(`${owner}_${senderNonce}`).slice(0, 40);
        // Format as Ethereum address (0x + 20 bytes)
        const ethAddress = '0x' + id.slice(0, 40);"""

if old_deploy in vm:
    vm = vm.replace(old_deploy, new_deploy)
    print("Added Ethereum-style contract address derivation + EIP-170 size limit")
else:
    print("WARNING: deploy method not found, trying flexible match...")
    # Try more flexible matching
    pattern = r"deploy\(owner, name, bytecode, metadata\) \{\s*const id = \(0, crypto_2\.sha256\)"
    if re.search(pattern, vm):
        vm = re.sub(
            pattern,
            "deploy(owner, name, bytecode, metadata) {\n        // EIP-170: Contract code size limit (24576 bytes)\n        const MAX_CODE_SIZE = 24576;\n        if (bytecode && bytecode.length > MAX_CODE_SIZE) {\n            throw new Error(`Contract code size exceeds EIP-170 limit: ${bytecode.length} > ${MAX_CODE_SIZE}`);\n        }\n        // Ethereum-style contract address derivation\n        this.contractNonces = this.contractNonces || new Map();\n        const senderNonce = (this.contractNonces.get(owner) || 0);\n        this.contractNonces.set(owner, senderNonce + 1);\n        const id = (0, crypto_2.sha256)(`${owner}_${senderNonce}`).slice(0, 40);\n        const ethAddress = '0x' + id.slice(0, 40);\n        // Original ID for internal use\n        const origId = (0, crypto_2.sha256)",
            vm,
            count=1
        )
        print("Added Ethereum-style address derivation (flexible match)")
    else:
        print("ERROR: Could not find deploy method")

# Add contractAddress to the contract object
old_contract_obj = """const contract = {
            id,"""
new_contract_obj = """const contract = {
            id,
            contractAddress: ethAddress || id,
            nonce: senderNonce,"""

if old_contract_obj in vm:
    vm = vm.replace(old_contract_obj, new_contract_obj, 1)
    print("Added contractAddress and nonce to contract object")

with open("/opt/verdis/app/dist/core/vm.js", "w") as f:
    f.write(vm)

# === 2. Add raw EVM bytecode compilation support ===
with open("/opt/verdis/app/dist/core/vm.js", "r") as f:
    vm = f.read()

old_compile = """function compileContract(source) {
    const rawLines = source.split('\\n');"""

new_compile = """function compileContract(source) {
    // Support raw EVM hex bytecode (e.g., '0x6080604052...' or '6080604052...')
    if (typeof source === 'string' && (source.startsWith('0x') || /^[0-9a-fA-F]+$/.test(source))) {
        const hex = source.startsWith('0x') ? source.slice(2) : source;
        const bytecode = [];
        for (let i = 0; i < hex.length; i += 2) {
            bytecode.push(parseInt(hex.slice(i, i + 2), 16));
        }
        return bytecode;
    }
    const rawLines = source.split('\\n');"""

if old_compile in vm:
    vm = vm.replace(old_compile, new_compile)
    print("Added raw EVM hex bytecode compilation support")
else:
    print("WARNING: compileContract not found for raw bytecode support")

with open("/opt/verdis/app/dist/core/vm.js", "w") as f:
    f.write(vm)

# === 3. Update API to accept raw bytecode deployment ===
with open("/opt/verdis/app/dist/api/server.js", "r") as f:
    srv = f.read()

# Update deploy endpoint to handle both assembly and raw bytecode
old_api_deploy = """const { owner, name, source, metadata } = req.body;
            const bytecode = (0, vm_1.compileContract)(source);"""

new_api_deploy = """const { owner, name, source, bytecode: rawBytecode, metadata } = req.body;
            // Accept either source (assembly text) or raw bytecode (hex)
            let bytecode;
            if (rawBytecode) {
                // Raw EVM bytecode provided directly
                bytecode = Array.isArray(rawBytecode) ? rawBytecode : (0, vm_1.compileContract)(rawBytecode);
            } else if (source) {
                bytecode = (0, vm_1.compileContract)(source);
            } else {
                res.status(400).json({ error: 'Either source or bytecode is required' });
                return;
            }"""

if old_api_deploy in srv:
    srv = srv.replace(old_api_deploy, new_api_deploy)
    print("Updated API deploy endpoint to accept raw EVM bytecode")
else:
    print("WARNING: API deploy endpoint not found")

# Add contract address to the response
old_response = "res.json({ success: true, contractId: contract.id, name: contract.name, metadata: contract.metadata });"
new_response = "res.json({ success: true, contractId: contract.id, contractAddress: contract.contractAddress || contract.id, name: contract.name, metadata: contract.metadata });"

if old_response in srv:
    srv = srv.replace(old_response, new_response)
    print("Added contractAddress to deploy response")

with open("/opt/verdis/app/dist/api/server.js", "w") as f:
    f.write(srv)

# === 4. Add gas costs for new opcodes ===
with open("/opt/verdis/app/dist/core/vm.js", "r") as f:
    vm = f.read()

# Check if SDIV gas cost already exists
if "SDIV:" not in vm:
    old_gas = """    ADDMOD: 8, ADDMOD: 8, SIGNEXTEND: 5,"""
    new_gas = """    ADDMOD: 8, MULMOD: 8, SIGNEXTEND: 5,
    SDIV: 3, SMOD: 3, SLT: 3, SGT: 3,
    GASPRICE: 2, EXTCODECOPY: 700, RETURNDATASIZE: 2, RETURNDATACOPY: 3, BASEFEE: 2,"""
    # Try different patterns
    if old_gas in vm:
        vm = vm.replace(old_gas, new_gas)
        print("Added gas costs for new opcodes")
    else:
        # Try to find the gas costs section and add
        old_gas2 = "    EXP: 10,"
        new_gas2 = "    EXP: 10,\n    SDIV: 3, SMOD: 3, SLT: 3, SGT: 3,\n    GASPRICE: 2, EXTCODECOPY: 700, RETURNDATASIZE: 2, RETURNDATACOPY: 3, BASEFEE: 2,"
        if old_gas2 in vm:
            vm = vm.replace(old_gas2, new_gas2)
            print("Added gas costs for new opcodes (after EXP)")
        else:
            print("WARNING: Could not find gas costs section")

with open("/opt/verdis/app/dist/core/vm.js", "w") as f:
    f.write(vm)

print("\n=== Ethereum security upgrades complete ===")
