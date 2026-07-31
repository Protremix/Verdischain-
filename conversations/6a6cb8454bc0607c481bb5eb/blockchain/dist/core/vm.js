"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ContractManager = void 0;
exports.compileContract = compileContract;
const sha256_1 = require("@noble/hashes/sha256");
function compileContract(source) {
    if (!source || typeof source !== 'string') {
        throw new Error('Contract source code must be a non-empty string');
    }
    // Simple bytecode compiler stub converting source string to ASCII byte array
    return Array.from(Buffer.from(source, 'utf-8'));
}
class ContractManager {
    constructor() {
        this.contracts = new Map();
    }
    deployContract(owner, name, bytecode) {
        if (!owner)
            throw new Error('Contract owner is required');
        if (!name)
            throw new Error('Contract name is required');
        if (!bytecode || bytecode.length === 0)
            throw new Error('Contract bytecode cannot be empty');
        const id = `contract_${Buffer.from((0, sha256_1.sha256)(Buffer.from(`${owner}:${name}:${Date.now()}`))).toString('hex').slice(0, 16)}`;
        const contract = {
            id,
            owner,
            name,
            bytecode,
            state: new Map(),
            deployedAt: Date.now(),
        };
        this.contracts.set(id, contract);
        return contract;
    }
    executeContract(contractId, input) {
        const contract = this.contracts.get(contractId);
        if (!contract) {
            throw new Error(`Contract with ID '${contractId}' not found`);
        }
        // Execute input and update state
        const executionKey = `exec_${Date.now()}`;
        contract.state.set(executionKey, input);
        return {
            success: true,
            contractId,
            input,
            executedAt: Date.now(),
            stateKeysCount: contract.state.size,
        };
    }
    getContract(contractId) {
        return this.contracts.get(contractId) || null;
    }
    getAllContracts() {
        return Array.from(this.contracts.values());
    }
    getContractState(contractId) {
        const contract = this.contracts.get(contractId);
        if (!contract)
            return null;
        return contract.state;
    }
}
exports.ContractManager = ContractManager;
//# sourceMappingURL=vm.js.map