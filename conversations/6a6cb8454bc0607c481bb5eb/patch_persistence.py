#!/usr/bin/env python3
"""Patch persistence.js to convert contract state from plain objects to Maps."""

with open("/opt/verdis/app/dist/core/persistence.js", "r") as f:
    c = f.read()

# Find the contract restoration line and add Map conversion
old = """    // Restore contracts (Map)
    for (const contract of state.contracts) {
        contractManager.contracts.set(contract.id, contract);
    }"""

new = """    // Restore contracts (Map) — convert plain state objects to Maps for EVM-compatible VM
    for (const contract of state.contracts) {
        if (contract.state && !(contract.state instanceof Map)) {
            contract.state = new Map(Object.entries(contract.state));
        }
        contractManager.contracts.set(contract.id, contract);
    }"""

if old in c:
    c = c.replace(old, new)
    print("Patched contract state restoration to convert to Maps")
else:
    print("ERROR: Could not find contract restoration code")

# Also fix the export function to handle Maps properly
old_export = """    // Export contracts
    const contracts = contractManager.getContracts();
    const contractsData = contracts.map(c => {
        let stateSize = 0;
        let stateHolders = 0;
        if (c.state instanceof Map) {
            stateSize = c.state.size;
            for (const [key, value] of c.state.entries()) {
                if (typeof key === 'string' && key.startsWith('0x')) stateHolders++;
            }
        }"""

new_export = """    // Export contracts — serialize Maps to plain objects for JSON
    const contracts = contractManager.getContracts();
    const contractsData = contracts.map(c => {
        let stateSize = 0;
        let stateHolders = 0;
        let serializableState = {};
        if (c.state instanceof Map) {
            stateSize = c.state.size;
            for (const [key, value] of c.state.entries()) {
                if (typeof key === 'string' && key.startsWith('0x')) stateHolders++;
                // Convert BigInt to string for JSON serialization
                serializableState[key] = typeof value === 'bigint' ? value.toString() : value;
            }
        } else if (c.state && typeof c.state === 'object') {
            stateSize = Object.keys(c.state).length;
            serializableState = c.state;
        }"""

if old_export in c:
    c = c.replace(old_export, new_export)
    print("Patched contract export to handle Maps and BigInts")
else:
    print("WARNING: Could not find export code, but continuation may still work")

# Fix the return to use serializableState
old_return = """        return { id: c.id, name: c.name, owner: c.owner, deployedAt: c.deployedAt, stateSize, holderCount: stateHolders + 1 };
    }));"""

new_return = """        return { id: c.id, name: c.name, owner: c.owner, deployedAt: c.deployedAt, bytecode: c.bytecode, state: serializableState, stateSize, holderCount: stateHolders + 1 };
    }));"""

if old_return in c:
    c = c.replace(old_return, new_return)
    print("Patched contract export return to include serializable state")
else:
    print("NOTE: Return already patched or different format")

with open("/opt/verdis/app/dist/core/persistence.js", "w") as f:
    f.write(c)

print("Persistence patched!")
