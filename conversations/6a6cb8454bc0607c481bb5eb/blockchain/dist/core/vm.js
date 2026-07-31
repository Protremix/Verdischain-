"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ContractManager = exports.StackVM = exports.OPCODES = void 0;
exports.compileContract = compileContract;
var OPCODES;
(function (OPCODES) {
    OPCODES[OPCODES["PUSH"] = 1] = "PUSH";
    OPCODES[OPCODES["ADD"] = 2] = "ADD";
    OPCODES[OPCODES["SUB"] = 3] = "SUB";
    OPCODES[OPCODES["MUL"] = 4] = "MUL";
    OPCODES[OPCODES["DIV"] = 5] = "DIV";
    OPCODES[OPCODES["LOG"] = 6] = "LOG";
    OPCODES[OPCODES["HALT"] = 0] = "HALT";
    OPCODES[OPCODES["STORE"] = 16] = "STORE";
    OPCODES[OPCODES["LOAD"] = 17] = "LOAD";
    OPCODES[OPCODES["SSTORE"] = 18] = "SSTORE";
    OPCODES[OPCODES["SLOAD"] = 19] = "SLOAD";
    OPCODES[OPCODES["DUP"] = 20] = "DUP";
    OPCODES[OPCODES["SWAP"] = 21] = "SWAP";
    OPCODES[OPCODES["LT"] = 32] = "LT";
    OPCODES[OPCODES["GT"] = 33] = "GT";
    OPCODES[OPCODES["EQ"] = 34] = "EQ";
    OPCODES[OPCODES["JUMP"] = 48] = "JUMP";
    OPCODES[OPCODES["JUMPI"] = 49] = "JUMPI";
    OPCODES[OPCODES["LABEL"] = 64] = "LABEL";
})(OPCODES || (exports.OPCODES = OPCODES = {}));
class StackVM {
    constructor() {
        this.stack = [];
        this.memory = new Map();
        this.storage = new Map();
        this.events = [];
    }
    run(bytecode, initialState) {
        this.stack = [];
        this.memory = new Map();
        this.storage = initialState ? new Map(initialState) : new Map();
        this.events = [];
        let pc = 0;
        const labels = new Map();
        // First pass: collect labels if encoded in bytecode structure
        // Bytecode format: opcodes and operands
        let step = 0;
        while (step < bytecode.length) {
            const op = bytecode[step];
            if (op === OPCODES.PUSH) {
                step += 2;
            }
            else if (op === OPCODES.STORE || op === OPCODES.LOAD || op === OPCODES.SSTORE || op === OPCODES.SLOAD) {
                step += 2;
            }
            else if (op === OPCODES.LABEL || op === OPCODES.JUMP || op === OPCODES.JUMPI) {
                step += 2;
            }
            else {
                step += 1;
            }
        }
        // Execute VM
        let result = 0;
        let cycles = 0;
        const maxCycles = 10000;
        while (pc < bytecode.length && cycles < maxCycles) {
            cycles++;
            const op = bytecode[pc];
            if (op === OPCODES.HALT) {
                if (this.stack.length > 0) {
                    result = this.stack[this.stack.length - 1];
                }
                break;
            }
            else if (op === OPCODES.PUSH) {
                const val = bytecode[pc + 1] ?? 0;
                this.stack.push(val);
                pc += 2;
            }
            else if (op === OPCODES.ADD) {
                const b = this.stack.pop() ?? 0;
                const a = this.stack.pop() ?? 0;
                this.stack.push(a + b);
                pc += 1;
            }
            else if (op === OPCODES.SUB) {
                const b = this.stack.pop() ?? 0;
                const a = this.stack.pop() ?? 0;
                this.stack.push(a - b);
                pc += 1;
            }
            else if (op === OPCODES.MUL) {
                const b = this.stack.pop() ?? 0;
                const a = this.stack.pop() ?? 0;
                this.stack.push(a * b);
                pc += 1;
            }
            else if (op === OPCODES.DIV) {
                const b = this.stack.pop() ?? 1;
                const a = this.stack.pop() ?? 0;
                this.stack.push(Math.floor(a / b));
                pc += 1;
            }
            else if (op === OPCODES.LT) {
                const b = this.stack.pop() ?? 0;
                const a = this.stack.pop() ?? 0;
                this.stack.push(a < b ? 1 : 0);
                pc += 1;
            }
            else if (op === OPCODES.GT) {
                const b = this.stack.pop() ?? 0;
                const a = this.stack.pop() ?? 0;
                this.stack.push(a > b ? 1 : 0);
                pc += 1;
            }
            else if (op === OPCODES.EQ) {
                const b = this.stack.pop() ?? 0;
                const a = this.stack.pop() ?? 0;
                this.stack.push(a === b ? 1 : 0);
                pc += 1;
            }
            else if (op === OPCODES.LOG) {
                const val = this.stack[this.stack.length - 1] ?? 0;
                this.events.push({ type: 'LOG', data: val });
                pc += 1;
            }
            else if (op === OPCODES.DUP) {
                const val = this.stack[this.stack.length - 1] ?? 0;
                this.stack.push(val);
                pc += 1;
            }
            else if (op === OPCODES.SWAP) {
                const a = this.stack.pop() ?? 0;
                const b = this.stack.pop() ?? 0;
                this.stack.push(a);
                this.stack.push(b);
                pc += 1;
            }
            else if (op === OPCODES.STORE) {
                const varIdx = bytecode[pc + 1] ?? 0;
                const val = this.stack.pop() ?? 0;
                this.memory.set(String(varIdx), val);
                pc += 2;
            }
            else if (op === OPCODES.LOAD) {
                const varIdx = bytecode[pc + 1] ?? 0;
                const val = this.memory.get(String(varIdx)) ?? 0;
                this.stack.push(val);
                pc += 2;
            }
            else if (op === OPCODES.SSTORE) {
                const varIdx = bytecode[pc + 1] ?? 0;
                const val = this.stack.pop() ?? 0;
                this.storage.set(String(varIdx), val);
                pc += 2;
            }
            else if (op === OPCODES.SLOAD) {
                const varIdx = bytecode[pc + 1] ?? 0;
                const val = this.storage.get(String(varIdx)) ?? 0;
                this.stack.push(val);
                pc += 2;
            }
            else if (op === OPCODES.JUMP) {
                const targetPc = bytecode[pc + 1] ?? 0;
                pc = targetPc;
            }
            else if (op === OPCODES.JUMPI) {
                const targetPc = bytecode[pc + 1] ?? 0;
                const cond = this.stack.pop() ?? 0;
                if (cond !== 0) {
                    pc = targetPc;
                }
                else {
                    pc += 2;
                }
            }
            else {
                pc += 1;
            }
        }
        if (this.stack.length > 0) {
            result = this.stack[this.stack.length - 1];
        }
        return {
            result,
            events: this.events,
            state: this.storage,
        };
    }
}
exports.StackVM = StackVM;
function compileContract(source) {
    const lines = source.split('\n');
    const bytecode = [];
    const labels = new Map();
    const symbolMap = new Map();
    let nextSymbolIdx = 1;
    function getSymbolIdx(sym) {
        if (!symbolMap.has(sym)) {
            symbolMap.set(sym, nextSymbolIdx++);
        }
        return symbolMap.get(sym);
    }
    // Pass 1: Compute bytecode indices and record labels
    let currentByteIndex = 0;
    for (let line of lines) {
        line = line.trim();
        if (!line || line.startsWith('//'))
            continue;
        const parts = line.split(/\s+/);
        const cmd = parts[0].toUpperCase();
        if (cmd === 'LABEL') {
            labels.set(parts[1], currentByteIndex);
        }
        else if (cmd === 'PUSH') {
            currentByteIndex += 2;
        }
        else if (cmd === 'STORE' ||
            cmd === 'LOAD' ||
            cmd === 'SSTORE' ||
            cmd === 'SLOAD' ||
            cmd === 'JUMP' ||
            cmd === 'JUMPI') {
            currentByteIndex += 2;
        }
        else {
            currentByteIndex += 1;
        }
    }
    // Pass 2: Emit bytecode
    for (let line of lines) {
        line = line.trim();
        if (!line || line.startsWith('//'))
            continue;
        const parts = line.split(/\s+/);
        const cmd = parts[0].toUpperCase();
        if (cmd === 'PUSH') {
            bytecode.push(OPCODES.PUSH, parseInt(parts[1], 10) || 0);
        }
        else if (cmd === 'ADD') {
            bytecode.push(OPCODES.ADD);
        }
        else if (cmd === 'SUB') {
            bytecode.push(OPCODES.SUB);
        }
        else if (cmd === 'MUL') {
            bytecode.push(OPCODES.MUL);
        }
        else if (cmd === 'DIV') {
            bytecode.push(OPCODES.DIV);
        }
        else if (cmd === 'LOG') {
            bytecode.push(OPCODES.LOG);
        }
        else if (cmd === 'HALT') {
            bytecode.push(OPCODES.HALT);
        }
        else if (cmd === 'DUP') {
            bytecode.push(OPCODES.DUP);
        }
        else if (cmd === 'SWAP') {
            bytecode.push(OPCODES.SWAP);
        }
        else if (cmd === 'LT') {
            bytecode.push(OPCODES.LT);
        }
        else if (cmd === 'GT') {
            bytecode.push(OPCODES.GT);
        }
        else if (cmd === 'EQ') {
            bytecode.push(OPCODES.EQ);
        }
        else if (cmd === 'STORE') {
            bytecode.push(OPCODES.STORE, getSymbolIdx(parts[1]));
        }
        else if (cmd === 'LOAD') {
            bytecode.push(OPCODES.LOAD, getSymbolIdx(parts[1]));
        }
        else if (cmd === 'SSTORE') {
            bytecode.push(OPCODES.SSTORE, getSymbolIdx(parts[1]));
        }
        else if (cmd === 'SLOAD') {
            bytecode.push(OPCODES.SLOAD, getSymbolIdx(parts[1]));
        }
        else if (cmd === 'LABEL') {
            // Labels take no execution space
        }
        else if (cmd === 'JUMP') {
            const target = labels.get(parts[1]) ?? 0;
            bytecode.push(OPCODES.JUMP, target);
        }
        else if (cmd === 'JUMPI') {
            const target = labels.get(parts[1]) ?? 0;
            bytecode.push(OPCODES.JUMPI, target);
        }
    }
    return bytecode;
}
class ContractManager {
    constructor() {
        this.contracts = new Map();
    }
    deploy(owner, name, bytecode) {
        const id = 'contract_' + Date.now() + '_' + Math.floor(Math.random() * 1000);
        const contract = {
            id,
            name,
            owner,
            bytecode,
            state: new Map(),
            deployedAt: Date.now(),
        };
        this.contracts.set(id, contract);
        return contract;
    }
    deployContract(name, owner, bytecode) {
        return this.deploy(owner, name, bytecode);
    }
    getContract(id) {
        return this.contracts.get(id);
    }
    getAllContracts() {
        return Array.from(this.contracts.values());
    }
    execute(contractId, input) {
        const contract = this.contracts.get(contractId);
        if (!contract) {
            throw new Error(`Contract ${contractId} not found`);
        }
        const vm = new StackVM();
        const res = vm.run(contract.bytecode, contract.state);
        contract.state = res.state;
        return res;
    }
}
exports.ContractManager = ContractManager;
//# sourceMappingURL=vm.js.map