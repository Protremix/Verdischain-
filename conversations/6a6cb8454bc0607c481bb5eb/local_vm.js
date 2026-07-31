'use strict';
Object.defineProperty(exports, '__esModule', { value: true });
exports.ContractManager = exports.StackVM = exports.OPCODES = void 0;
exports.compileContract = compileContract;

const crypto_1 = require('../crypto');
let keccak_256;
try {
    keccak_256 = require('@noble/hashes/sha3').keccak_256;
} catch (e) {
    // fallback if sha3 not found
}

exports.OPCODES = {
    STOP: 0x00,
    ADD: 0x01,
    MUL: 0x02,
    SUB: 0x03,
    DIV: 0x04,
    SDIV: 0x05,
    MOD: 0x06,
    SMOD: 0x07,
    ADDMOD: 0x08,
    MULMOD: 0x09,
    EXP: 0x0A,
    SIGNEXTEND: 0x0B,

    LT: 0x10,
    GT: 0x11,
    SLT: 0x12,
    SGT: 0x13,
    EQ: 0x14,
    ISZERO: 0x15,
    AND: 0x16,
    OR: 0x17,
    XOR: 0x18,
    NOT: 0x19,
    BYTE: 0x1A,
    SHL: 0x1B,
    SHR: 0x1C,
    SAR: 0x1D,

    KECCAK256: 0x20,
    SHA3: 0x20,
    ADDRESS: 0x30,
    BALANCE: 0x31,
    ORIGIN: 0x32,
    CALLER: 0x33,
    CALLVALUE: 0x34,
    CALLDATALOAD: 0x35,
    CALLDATASIZE: 0x36,
    CALLDATACOPY: 0x37,
    CODESIZE: 0x38,
    CODECOPY: 0x39,
    GASPRICE: 0x3A,
    EXTCODESIZE: 0x3B,
    EXTCODECOPY: 0x3C,
    RETURNDATASIZE: 0x3D,
    RETURNDATACOPY: 0x3E,
    EXTCODEHASH: 0x3F,

    BLOCKHASH: 0x40,
    COINBASE: 0x41,
    TIMESTAMP: 0x42,
    NUMBER: 0x43,
    PREVRANDAO: 0x44,
    DIFFICULTY: 0x44,
    GASLIMIT: 0x45,
    CHAINID: 0x46,
    SELFBALANCE: 0x47,
    BASEFEE: 0x48,

    POP: 0x50,
    MLOAD: 0x51,
    MSTORE: 0x52,
    MSTORE8: 0x53,
    SLOAD: 0x54,
    SSTORE: 0x55,
    JUMP: 0x56,
    JUMPI: 0x57,
    PC: 0x58,
    MSIZE: 0x59,
    GAS: 0x5A,
    JUMPDEST: 0x5B,
    TLOAD: 0x5C,
    TSTORE: 0x5D,
    PUSH0: 0x5F,

    PUSH1: 0x60, PUSH2: 0x61, PUSH3: 0x62, PUSH4: 0x63, PUSH5: 0x64, PUSH6: 0x65, PUSH7: 0x66, PUSH8: 0x67,
    PUSH9: 0x68, PUSH10: 0x69, PUSH11: 0x6A, PUSH12: 0x6B, PUSH13: 0x6C, PUSH14: 0x6D, PUSH15: 0x6E, PUSH16: 0x6F,
    PUSH17: 0x70, PUSH18: 0x71, PUSH19: 0x72, PUSH20: 0x73, PUSH21: 0x74, PUSH22: 0x75, PUSH23: 0x76, PUSH24: 0x77,
    PUSH25: 0x78, PUSH26: 0x79, PUSH27: 0x7A, PUSH28: 0x7B, PUSH29: 0x7C, PUSH30: 0x7D, PUSH31: 0x7E, PUSH32: 0x7F,
    PUSH: 0x60,

    DUP1: 0x80, DUP2: 0x81, DUP3: 0x82, DUP4: 0x83, DUP5: 0x84, DUP6: 0x85, DUP7: 0x86, DUP8: 0x87,
    DUP9: 0x88, DUP10: 0x89, DUP11: 0x8A, DUP12: 0x8B, DUP13: 0x8C, DUP14: 0x8D, DUP15: 0x8E, DUP16: 0x8F,

    SWAP1: 0x90, SWAP2: 0x91, SWAP3: 0x92, SWAP4: 0x93, SWAP5: 0x94, SWAP6: 0x95, SWAP7: 0x96, SWAP8: 0x97,
    SWAP9: 0x98, SWAP10: 0x99, SWAP11: 0x9A, SWAP12: 0x9B, SWAP13: 0x9C, SWAP14: 0x9D, SWAP15: 0x9E, SWAP16: 0x9F,

    LOG0: 0xA0, LOG1: 0xA1, LOG2: 0xA2, LOG3: 0xA3, LOG4: 0xA4,

    CREATE: 0xF0,
    CALL: 0xF1,
    CALLCODE: 0xF2,
    RETURN: 0xF3,
    DELEGATECALL: 0xF4,
    CREATE2: 0xF5,
    STATICCALL: 0xFA,
    REVERT: 0xFD,
    INVALID: 0xFE,
    SELFDESTRUCT: 0xFF,
    HALT: 0xFF,

    STORE: 0x55,
    LOAD: 0x54,
    LOG: 0x10,
    DUP: 0x80,
    SWAP: 0x90,
    EMIT: 0x15
};

const MASK_256 = (1n << 256n) - 1n;

function toBigInt(val) {
    if (val === undefined || val === null) return 0n;
    if (typeof val === 'bigint') return val;
    if (typeof val === 'number') return BigInt(Math.floor(val));
    if (typeof val === 'boolean') return val ? 1n : 0n;
    if (typeof val === 'string') {
        if (val.startsWith('0x') || val.startsWith('0X')) {
            try { return BigInt(val); } catch { return 0n; }
        }
        try { return BigInt(val); } catch { return 0n; }
    }
    if (Buffer.isBuffer(val) || val instanceof Uint8Array) {
        if (val.length === 0) return 0n;
        return BigInt('0x' + Buffer.from(val).toString('hex'));
    }
    return 0n;
}

function to256(val) {
    const b = toBigInt(val);
    return (b % (1n << 256n) + (1n << 256n)) % (1n << 256n);
}

function toSigned256(val) {
    const u = to256(val);
    if (u >= (1n << 255n)) {
        return u - (1n << 256n);
    }
    return u;
}

function formatStackValue(b) {
    if (typeof b === 'bigint') {
        if (b >= 0n && b <= BigInt(Number.MAX_SAFE_INTEGER)) {
            return Number(b);
        }
        return '0x' + b.toString(16);
    }
    return b;
}

function modExp(base, exp) {
    let b = to256(base);
    let e = toBigInt(exp);
    let result = 1n;
    while (e > 0n) {
        if (e & 1n) {
            result = (result * b) % (1n << 256n);
        }
        b = (b * b) % (1n << 256n);
        e >>= 1n;
    }
    return result;
}

function signExtend(b, x) {
    const byteIdx = toBigInt(b);
    let val = to256(x);
    if (byteIdx >= 31n) return val;
    const bitPos = byteIdx * 8n + 7n;
    const mask = (1n << (bitPos + 1n)) - 1n;
    const isNegative = (val & (1n << bitPos)) !== 0n;
    if (isNegative) {
        return val | (~mask & MASK_256);
    } else {
        return val & mask;
    }
}

function getByte(i, x) {
    const idx = toBigInt(i);
    const val = to256(x);
    if (idx >= 32n) return 0n;
    const shift = (31n - idx) * 8n;
    return (val >> shift) & 0xffn;
}

function getGasCost(opcode, vm, length = 0) {
    switch (opcode) {
        case 0x00: return 3;
        case 0x01: case 0x03: return 3;
        case 0x04: case 0x05: return 5;
        case 0x06: case 0x07: return 5;
        case 0x08: case 0x09: return 8;
        case 0x0A: return 10;
        case 0x0B: return 5;
        case 0x10: case 0x11: case 0x12: case 0x13: case 0x14: case 0x15:
        case 0x16: case 0x17: case 0x18: case 0x19: case 0x1A: case 0x1B: case 0x1C: case 0x1D:
            return 3;
        case 0x02: return 5;
        case 0x20: return 30 + 6 * Math.ceil(length / 32);
        case 0x30: case 0x32: case 0x33: case 0x34: case 0x36: case 0x38: case 0x3A: case 0x3D: case 0x40: case 0x41: case 0x42: case 0x43: case 0x44: case 0x45: case 0x46: case 0x48: case 0x58: case 0x59: case 0x5A: case 0x5F:
            return 2;
        case 0x31: return 700;
        case 0x35: case 0x37: case 0x39: case 0x3B: case 0x3C: case 0x3E: case 0x3F:
            return 3;
        case 0x47: return 5;
        case 0x50: return 2;
        case 0x51: case 0x52: case 0x53: return 3;
        case 0x54: case 0x0E: return 200;
        case 0x55: case 0x0D: return 2000;
        case 0x56: return 8;
        case 0x57: return 10;
        case 0x5B: return 1;
        case 0x5C: case 0x5D: return 100;
        case 0xF0: case 0xF5: return 32000;
        case 0xF1: case 0xF2: case 0xF4: case 0xFA: return 100;
        case 0xF3: case 0xFD: return 0;
        case 0xFE: return vm ? (vm.gasLimit - vm.gasUsed) : 0;
        case 0xFF: return 5000;
        default:
            if (opcode >= 0x60 && opcode <= 0x7F) return 3;
            if (opcode >= 0x80 && opcode <= 0x8F) return 3;
            if (opcode >= 0x90 && opcode <= 0x9F) return 3;
            if (opcode >= 0xA0 && opcode <= 0xA4) {
                const topics = opcode - 0xA0;
                return 375 + 375 * topics + 8 * length;
            }
            return 1;
    }
}

class StackVM {
    constructor(state, context = {}) {
        this.stack = [];
        this.state = state || new Map();
        this.events = [];
        this.pc = 0;
        this.halted = false;
        this.reverted = false;
        this.gasUsed = 0;
        this.gasLimit = context.gasLimit || 10000000;
        this.transientStorage = new Map();
        this.memory = Buffer.alloc(0);
        this.calldata = context.calldata ? (Buffer.isBuffer(context.calldata) ? context.calldata : Buffer.from(context.calldata)) : Buffer.alloc(0);
        this.returnData = Buffer.alloc(0);
        this.address = context.address || '0x0000000000000000000000000000000000000000';
        this.caller = context.caller || '0x0000000000000000000000000000000000000000';
        this.origin = context.origin || this.caller;
        this.callValue = context.callValue || 0;
        this.gasPrice = context.gasPrice || 1;
        this.blockNumber = context.blockNumber || 1;
        this.blockTimestamp = context.blockTimestamp || Math.floor(Date.now() / 1000);
        this.coinbase = context.coinbase || '0x0000000000000000000000000000000000000000';
        this.chainId = context.chainId || 1;
        this.baseFee = context.baseFee || 1;
        this.contractManager = context.contractManager || null;
    }

    push(value) {
        if (this.stack.length >= 1024) {
            throw new Error('Stack overflow');
        }
        this.stack.push(value);
    }

    pop() {
        if (this.stack.length === 0) {
            throw new Error('Stack underflow');
        }
        return this.stack.pop();
    }

    peek(index = 0) {
        if (index < 0 || index >= this.stack.length) {
            return undefined;
        }
        return this.stack[this.stack.length - 1 - index];
    }

    load(key) {
        const val = this.state.get(key);
        return val === undefined ? 0 : val;
    }

    store(key, value) {
        this.state.set(key, value);
    }

    emit(event, data) {
        this.events.push({ event, data });
    }

    getEvents() {
        return this.events;
    }

    getGasUsed() {
        return this.gasUsed;
    }

    readMemory(offset, length) {
        offset = Math.max(0, offset);
        length = Math.max(0, length);
        if (length === 0) return Buffer.alloc(0);
        this.ensureMemoryCapacity(offset + length);
        return this.memory.subarray(offset, offset + length);
    }

    writeMemory(offset, bytes) {
        offset = Math.max(0, offset);
        const buf = Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes);
        if (buf.length === 0) return;
        this.ensureMemoryCapacity(offset + buf.length);
        buf.copy(this.memory, offset);
    }

    ensureMemoryCapacity(size) {
        if (size > this.memory.length) {
            const newSize = Math.ceil(size / 32) * 32;
            const newBuf = Buffer.alloc(newSize);
            this.memory.copy(newBuf, 0);
            this.memory = newBuf;
        }
    }

    getMemorySize() {
        return Math.ceil(this.memory.length / 32) * 32;
    }

    run(bytecode, inputCalldata) {
        this.pc = 0;
        this.halted = false;
        this.reverted = false;
        this.gasUsed = 0;
        if (inputCalldata) {
            this.calldata = Buffer.isBuffer(inputCalldata) ? inputCalldata : Buffer.from(inputCalldata);
        }

        while (this.pc < bytecode.length && !this.halted) {
            const opcode = bytecode[this.pc];
            let gasCost = getGasCost(opcode, this);

            if (this.gasUsed + gasCost > this.gasLimit) {
                this.gasUsed += gasCost;
                return {
                    result: this.peek(),
                    events: this.events,
                    gasUsed: this.gasUsed,
                    error: 'Out of gas',
                };
            }
            this.gasUsed += gasCost;

            try {
                switch (opcode) {
                    case 0x00: { // STOP
                        this.halted = true;
                        break;
                    }
                    case 0x01: { // ADD or legacy PUSH
                        if (this.stack.length < 2 && this.pc + 1 < bytecode.length) {
                            this.pc++;
                            const val = bytecode[this.pc];
                            this.push(val);
                            this.pc++;
                        } else {
                            const b = toBigInt(this.pop());
                            const a = toBigInt(this.pop());
                            this.push(formatStackValue(to256(a + b)));
                            this.pc++;
                        }
                        break;
                    }
                    case 0x02: { // MUL or legacy POP
                        if (this.stack.length < 2) {
                            this.pop();
                            this.pc++;
                        } else {
                            const b = toBigInt(this.pop());
                            const a = toBigInt(this.pop());
                            this.push(formatStackValue(to256(a * b)));
                            this.pc++;
                        }
                        break;
                    }
                    case 0x03: { // SUB
                        const b = toBigInt(this.pop());
                        const a = toBigInt(this.pop());
                        this.push(formatStackValue(to256(a - b)));
                        this.pc++;
                        break;
                    }
                    case 0x04: { // DIV
                        const b = toBigInt(this.pop());
                        const a = toBigInt(this.pop());
                        if (b === 0n) this.push(0);
                        else this.push(formatStackValue(to256(a / b)));
                        this.pc++;
                        break;
                    }
                    case 0x05: { // SDIV
                        const b = toSigned256(this.pop());
                        const a = toSigned256(this.pop());
                        if (b === 0n) this.push(0);
                        else this.push(formatStackValue(to256(a / b)));
                        this.pc++;
                        break;
                    }
                    case 0x06: { // MOD
                        const b = toBigInt(this.pop());
                        const a = toBigInt(this.pop());
                        if (b === 0n) this.push(0);
                        else this.push(formatStackValue(to256(a % b)));
                        this.pc++;
                        break;
                    }
                    case 0x07: { // SMOD
                        const b = toSigned256(this.pop());
                        const a = toSigned256(this.pop());
                        if (b === 0n) this.push(0);
                        else this.push(formatStackValue(to256(a % b)));
                        this.pc++;
                        break;
                    }
                    case 0x08: { // ADDMOD
                        const N = toBigInt(this.pop());
                        const b = toBigInt(this.pop());
                        const a = toBigInt(this.pop());
                        if (N === 0n) this.push(0);
                        else this.push(formatStackValue(to256((a + b) % N)));
                        this.pc++;
                        break;
                    }
                    case 0x09: { // MULMOD
                        const N = toBigInt(this.pop());
                        const b = toBigInt(this.pop());
                        const a = toBigInt(this.pop());
                        if (N === 0n) this.push(0);
                        else this.push(formatStackValue(to256((a * b) % N)));
                        this.pc++;
                        break;
                    }
                    case 0x0A: { // EXP
                        const exp = this.pop();
                        const base = this.pop();
                        this.push(formatStackValue(modExp(base, exp)));
                        this.pc++;
                        break;
                    }
                    case 0x0B: { // SIGNEXTEND
                        const b = this.pop();
                        const x = this.pop();
                        this.push(formatStackValue(signExtend(b, x)));
                        this.pc++;
                        break;
                    }
                    case 0x10: { // LT or legacy LOG
                        if (this.stack.length >= 2) {
                            const b = toBigInt(this.pop());
                            const a = toBigInt(this.pop());
                            this.push(a < b ? 1 : 0);
                        } else {
                            const val = this.pop();
                            this.emit('LOG', val);
                        }
                        this.pc++;
                        break;
                    }
                    case 0x11: { // GT or legacy DUP
                        if (this.stack.length >= 2) {
                            const b = toBigInt(this.pop());
                            const a = toBigInt(this.pop());
                            this.push(a > b ? 1 : 0);
                        } else {
                            const val = this.peek();
                            this.push(val);
                        }
                        this.pc++;
                        break;
                    }
                    case 0x12: { // SLT or legacy SWAP
                        if (this.stack.length >= 2 && typeof this.peek(1) !== 'undefined') {
                            const b = toSigned256(this.pop());
                            const a = toSigned256(this.pop());
                            this.push(a < b ? 1 : 0);
                        } else if (this.stack.length >= 2) {
                            const top = this.pop();
                            const second = this.pop();
                            this.push(top);
                            this.push(second);
                        } else {
                            throw new Error('Stack underflow on SWAP');
                        }
                        this.pc++;
                        break;
                    }
                    case 0x13: { // SGT or legacy SSTORE
                        if (this.stack.length >= 2 && typeof this.peek(0) === 'number' && typeof this.peek(1) === 'number') {
                            const b = toSigned256(this.pop());
                            const a = toSigned256(this.pop());
                            this.push(a > b ? 1 : 0);
                        } else {
                            const key = this.pop();
                            const val = this.pop();
                            this.transientStorage.set(String(key), val);
                        }
                        this.pc++;
                        break;
                    }
                    case 0x14: { // EQ or legacy SLOAD
                        if (this.stack.length >= 2) {
                            const b = this.pop();
                            const a = this.pop();
                            this.push(toBigInt(a) === toBigInt(b) || a === b ? 1 : 0);
                        } else {
                            const key = this.pop();
                            const val = this.transientStorage.get(String(key));
                            this.push(val === undefined ? 0 : val);
                        }
                        this.pc++;
                        break;
                    }
                    case 0x15: { // ISZERO or legacy EMIT
                        if (this.stack.length >= 1 && (typeof this.peek(0) !== 'string' || !isNaN(Number(this.peek(0))))) {
                            const a = this.pop();
                            this.push((a === 0 || a === 0n || a === '0' || !a) ? 1 : 0);
                        } else {
                            const event = this.pop();
                            const data = this.pop();
                            this.emit(String(event), data);
                        }
                        this.pc++;
                        break;
                    }
                    case 0x16: { // AND
                        const b = toBigInt(this.pop());
                        const a = toBigInt(this.pop());
                        this.push(formatStackValue(to256(a & b)));
                        this.pc++;
                        break;
                    }
                    case 0x17: { // OR
                        const b = toBigInt(this.pop());
                        const a = toBigInt(this.pop());
                        this.push(formatStackValue(to256(a | b)));
                        this.pc++;
                        break;
                    }
                    case 0x18: { // XOR
                        const b = toBigInt(this.pop());
                        const a = toBigInt(this.pop());
                        this.push(formatStackValue(to256(a ^ b)));
                        this.pc++;
                        break;
                    }
                    case 0x19: { // NOT
                        const a = toBigInt(this.pop());
                        this.push(formatStackValue(to256(~a)));
                        this.pc++;
                        break;
                    }
                    case 0x1A: { // BYTE
                        const i = this.pop();
                        const x = this.pop();
                        this.push(formatStackValue(getByte(i, x)));
                        this.pc++;
                        break;
                    }
                    case 0x1B: { // SHL
                        const shift = toBigInt(this.pop());
                        const val = to256(this.pop());
                        if (shift >= 256n) this.push(0);
                        else this.push(formatStackValue(to256(val << shift)));
                        this.pc++;
                        break;
                    }
                    case 0x1C: { // SHR
                        const shift = toBigInt(this.pop());
                        const val = to256(this.pop());
                        if (shift >= 256n) this.push(0);
                        else this.push(formatStackValue(to256(val >> shift)));
                        this.pc++;
                        break;
                    }
                    case 0x1D: { // SAR
                        const shift = toBigInt(this.pop());
                        const val = toSigned256(this.pop());
                        if (shift >= 256n) {
                            this.push(val < 0n ? formatStackValue(MASK_256) : 0);
                        } else {
                            this.push(formatStackValue(to256(val >> shift)));
                        }
                        this.pc++;
                        break;
                    }
                    case 0x20: { // KECCAK256 / SHA3
                        const offset = Number(toBigInt(this.pop()));
                        const length = Number(toBigInt(this.pop()));
                        const bytes = this.readMemory(offset, length);
                        if (keccak_256) {
                            const hash = keccak_256(bytes);
                            this.push('0x' + Buffer.from(hash).toString('hex'));
                        } else {
                            this.push('0x' + (0, crypto_1.sha256)(bytes));
                        }
                        this.pc++;
                        break;
                    }
                    case 0x30: { // ADDRESS
                        this.push(this.address);
                        this.pc++;
                        break;
                    }
                    case 0x31: { // BALANCE
                        const addr = this.pop();
                        this.push(0);
                        this.pc++;
                        break;
                    }
                    case 0x32: { // ORIGIN
                        this.push(this.origin);
                        this.pc++;
                        break;
                    }
                    case 0x33: { // CALLER
                        this.push(this.caller);
                        this.pc++;
                        break;
                    }
                    case 0x34: { // CALLVALUE
                        this.push(this.callValue);
                        this.pc++;
                        break;
                    }
                    case 0x35: { // CALLDATALOAD
                        const offset = Number(toBigInt(this.pop()));
                        const bytes = Buffer.alloc(32);
                        if (offset < this.calldata.length) {
                            const slice = this.calldata.subarray(offset, Math.min(this.calldata.length, offset + 32));
                            slice.copy(bytes, 0);
                        }
                        const val = BigInt('0x' + (bytes.toString('hex') || '0'));
                        this.push(formatStackValue(val));
                        this.pc++;
                        break;
                    }
                    case 0x36: { // CALLDATASIZE
                        this.push(this.calldata.length);
                        this.pc++;
                        break;
                    }
                    case 0x37: { // CALLDATACOPY
                        const destOffset = Number(toBigInt(this.pop()));
                        const offset = Number(toBigInt(this.pop()));
                        const length = Number(toBigInt(this.pop()));
                        const bytes = Buffer.alloc(length);
                        if (offset < this.calldata.length) {
                            const slice = this.calldata.subarray(offset, Math.min(this.calldata.length, offset + length));
                            slice.copy(bytes, 0);
                        }
                        this.writeMemory(destOffset, bytes);
                        this.pc++;
                        break;
                    }
                    case 0x38: { // CODESIZE
                        this.push(bytecode.length);
                        this.pc++;
                        break;
                    }
                    case 0x39: { // CODECOPY
                        const destOffset = Number(toBigInt(this.pop()));
                        const offset = Number(toBigInt(this.pop()));
                        const length = Number(toBigInt(this.pop()));
                        const codeBuf = Buffer.from(bytecode.map(b => typeof b === 'number' ? b : 0));
                        const bytes = Buffer.alloc(length);
                        if (offset < codeBuf.length) {
                            const slice = codeBuf.subarray(offset, Math.min(codeBuf.length, offset + length));
                            slice.copy(bytes, 0);
                        }
                        this.writeMemory(destOffset, bytes);
                        this.pc++;
                        break;
                    }
                    case 0x3A: { // GASPRICE
                        this.push(this.gasPrice);
                        this.pc++;
                        break;
                    }
                    case 0x3B: { // EXTCODESIZE
                        const addr = this.pop();
                        if (this.contractManager && typeof addr === 'string' && this.contractManager.getContract(addr)) {
                            this.push(this.contractManager.getContract(addr).bytecode.length);
                        } else {
                            this.push(0);
                        }
                        this.pc++;
                        break;
                    }
                    case 0x3C: { // EXTCODECOPY
                        const addr = this.pop();
                        const destOffset = Number(toBigInt(this.pop()));
                        const offset = Number(toBigInt(this.pop()));
                        const length = Number(toBigInt(this.pop()));
                        let codeBuf = Buffer.alloc(0);
                        if (this.contractManager && typeof addr === 'string' && this.contractManager.getContract(addr)) {
                            codeBuf = Buffer.from(this.contractManager.getContract(addr).bytecode);
                        }
                        const bytes = Buffer.alloc(length);
                        if (offset < codeBuf.length) {
                            const slice = codeBuf.subarray(offset, Math.min(codeBuf.length, offset + length));
                            slice.copy(bytes, 0);
                        }
                        this.writeMemory(destOffset, bytes);
                        this.pc++;
                        break;
                    }
                    case 0x3D: { // RETURNDATASIZE
                        this.push(this.returnData.length);
                        this.pc++;
                        break;
                    }
                    case 0x3E: { // RETURNDATACOPY
                        const destOffset = Number(toBigInt(this.pop()));
                        const offset = Number(toBigInt(this.pop()));
                        const length = Number(toBigInt(this.pop()));
                        const bytes = Buffer.alloc(length);
                        if (offset < this.returnData.length) {
                            const slice = this.returnData.subarray(offset, Math.min(this.returnData.length, offset + length));
                            slice.copy(bytes, 0);
                        }
                        this.writeMemory(destOffset, bytes);
                        this.pc++;
                        break;
                    }
                    case 0x3F: { // EXTCODEHASH
                        const addr = this.pop();
                        if (this.contractManager && typeof addr === 'string' && this.contractManager.getContract(addr)) {
                            const code = Buffer.from(this.contractManager.getContract(addr).bytecode);
                            this.push('0x' + (keccak_256 ? Buffer.from(keccak_256(code)).toString('hex') : (0, crypto_1.sha256)(code)));
                        } else {
                            this.push('0x0000000000000000000000000000000000000000000000000000000000000000');
                        }
                        this.pc++;
                        break;
                    }
                    case 0x40: { // BLOCKHASH
                        const blockNum = this.pop();
                        this.push('0x0000000000000000000000000000000000000000000000000000000000000000');
                        this.pc++;
                        break;
                    }
                    case 0x41: { // COINBASE
                        this.push(this.coinbase);
                        this.pc++;
                        break;
                    }
                    case 0x42: { // TIMESTAMP
                        this.push(this.blockTimestamp);
                        this.pc++;
                        break;
                    }
                    case 0x43: { // NUMBER
                        this.push(this.blockNumber);
                        this.pc++;
                        break;
                    }
                    case 0x44: { // PREVRANDAO / DIFFICULTY
                        this.push(0);
                        this.pc++;
                        break;
                    }
                    case 0x45: { // GASLIMIT
                        this.push(this.gasLimit);
                        this.pc++;
                        break;
                    }
                    case 0x46: { // CHAINID
                        this.push(this.chainId);
                        this.pc++;
                        break;
                    }
                    case 0x47: { // SELFBALANCE
                        this.push(0);
                        this.pc++;
                        break;
                    }
                    case 0x48: { // BASEFEE
                        this.push(this.baseFee);
                        this.pc++;
                        break;
                    }
                    case 0x50: { // POP
                        this.pop();
                        this.pc++;
                        break;
                    }
                    case 0x51: { // MLOAD
                        const offset = Number(toBigInt(this.pop()));
                        const bytes = this.readMemory(offset, 32);
                        const val = BigInt('0x' + (bytes.toString('hex') || '0'));
                        this.push(formatStackValue(val));
                        this.pc++;
                        break;
                    }
                    case 0x52: { // MSTORE
                        const offset = Number(toBigInt(this.pop()));
                        const val = to256(this.pop());
                        const hex = val.toString(16).padStart(64, '0');
                        this.writeMemory(offset, Buffer.from(hex, 'hex'));
                        this.pc++;
                        break;
                    }
                    case 0x53: { // MSTORE8
                        const offset = Number(toBigInt(this.pop()));
                        const val = Number(toBigInt(this.pop()) & 0xffn);
                        this.writeMemory(offset, Buffer.from([val]));
                        this.pc++;
                        break;
                    }
                    case 0x54: { // SLOAD
                        const key = this.pop();
                        const val = this.load(String(key));
                        this.push(val);
                        this.pc++;
                        break;
                    }
                    case 0x55: { // SSTORE
                        const key = this.pop();
                        const val = this.pop();
                        this.store(String(key), val);
                        this.pc++;
                        break;
                    }
                    case 0x56: { // JUMP
                        let target;
                        if (this.stack.length > 0) {
                            target = this.pop();
                        } else if (this.pc + 1 < bytecode.length) {
                            this.pc++;
                            target = bytecode[this.pc];
                        } else {
                            return { result: this.peek(), events: this.events, gasUsed: this.gasUsed, error: 'Stack underflow on JUMP' };
                        }
                        if (typeof target !== 'number' || target < 0 || target >= bytecode.length) {
                            return { result: this.peek(), events: this.events, gasUsed: this.gasUsed, error: `Invalid JUMP target: ${target}` };
                        }
                        this.pc = target;
                        break;
                    }
                    case 0x57: { // JUMPI
                        let target;
                        let condition;
                        if (this.stack.length >= 2) {
                            target = this.pop();
                            condition = this.pop();
                        } else if (this.stack.length === 1 && this.pc + 1 < bytecode.length) {
                            condition = this.pop();
                            this.pc++;
                            target = bytecode[this.pc];
                        } else {
                            return { result: this.peek(), events: this.events, gasUsed: this.gasUsed, error: 'Stack underflow on JUMPI' };
                        }
                        if (condition) {
                            if (typeof target !== 'number' || target < 0 || target >= bytecode.length) {
                                return { result: this.peek(), events: this.events, gasUsed: this.gasUsed, error: `Invalid JUMPI target: ${target}` };
                            }
                            this.pc = target;
                        } else {
                            this.pc++;
                        }
                        break;
                    }
                    case 0x58: { // PC
                        this.push(this.pc);
                        this.pc++;
                        break;
                    }
                    case 0x59: { // MSIZE
                        this.push(this.getMemorySize());
                        this.pc++;
                        break;
                    }
                    case 0x5A: { // GAS
                        this.push(Math.max(0, this.gasLimit - this.gasUsed));
                        this.pc++;
                        break;
                    }
                    case 0x5B: { // JUMPDEST
                        this.pc++;
                        break;
                    }
                    case 0x5C: { // TLOAD
                        const key = this.pop();
                        const val = this.transientStorage.get(String(key));
                        this.push(val === undefined ? 0 : val);
                        this.pc++;
                        break;
                    }
                    case 0x5D: { // TSTORE
                        const key = this.pop();
                        const val = this.pop();
                        this.transientStorage.set(String(key), val);
                        this.pc++;
                        break;
                    }
                    case 0x5F: { // PUSH0
                        this.push(0);
                        this.pc++;
                        break;
                    }
                    case 0xA0: { // LOG0
                        const offset = Number(toBigInt(this.pop()));
                        const length = Number(toBigInt(this.pop()));
                        const data = this.readMemory(offset, length);
                        this.events.push({ event: 'LOG0', topics: [], data: '0x' + data.toString('hex') });
                        this.pc++;
                        break;
                    }
                    case 0xA1: { // LOG1
                        const offset = Number(toBigInt(this.pop()));
                        const length = Number(toBigInt(this.pop()));
                        const t1 = this.pop();
                        const data = this.readMemory(offset, length);
                        this.events.push({ event: 'LOG1', topics: [formatStackValue(to256(t1))], data: '0x' + data.toString('hex') });
                        this.pc++;
                        break;
                    }
                    case 0xA2: { // LOG2
                        const offset = Number(toBigInt(this.pop()));
                        const length = Number(toBigInt(this.pop()));
                        const t1 = this.pop();
                        const t2 = this.pop();
                        const data = this.readMemory(offset, length);
                        this.events.push({ event: 'LOG2', topics: [formatStackValue(to256(t1)), formatStackValue(to256(t2))], data: '0x' + data.toString('hex') });
                        this.pc++;
                        break;
                    }
                    case 0xA3: { // LOG3
                        const offset = Number(toBigInt(this.pop()));
                        const length = Number(toBigInt(this.pop()));
                        const t1 = this.pop();
                        const t2 = this.pop();
                        const t3 = this.pop();
                        const data = this.readMemory(offset, length);
                        this.events.push({ event: 'LOG3', topics: [formatStackValue(to256(t1)), formatStackValue(to256(t2)), formatStackValue(to256(t3))], data: '0x' + data.toString('hex') });
                        this.pc++;
                        break;
                    }
                    case 0xA4: { // LOG4
                        const offset = Number(toBigInt(this.pop()));
                        const length = Number(toBigInt(this.pop()));
                        const t1 = this.pop();
                        const t2 = this.pop();
                        const t3 = this.pop();
                        const t4 = this.pop();
                        const data = this.readMemory(offset, length);
                        this.events.push({ event: 'LOG4', topics: [formatStackValue(to256(t1)), formatStackValue(to256(t2)), formatStackValue(to256(t3)), formatStackValue(to256(t4))], data: '0x' + data.toString('hex') });
                        this.pc++;
                        break;
                    }
                    case 0xF0: { // CREATE
                        const val = this.pop();
                        const offset = Number(toBigInt(this.pop()));
                        const length = Number(toBigInt(this.pop()));
                        const initCode = this.readMemory(offset, length);
                        if (this.contractManager) {
                            const newContract = this.contractManager.deploy(this.address, 'Contract_' + Date.now(), Array.from(initCode));
                            this.push(newContract.id);
                        } else {
                            this.push('0x0000000000000000000000000000000000000000');
                        }
                        this.pc++;
                        break;
                    }
                    case 0xF1: { // CALL
                        if (this.stack.length >= 7) {
                            const gas = this.pop();
                            const addr = this.pop();
                            const value = this.pop();
                            const argsOffset = Number(toBigInt(this.pop()));
                            const argsLength = Number(toBigInt(this.pop()));
                            const retOffset = Number(toBigInt(this.pop()));
                            const retLength = Number(toBigInt(this.pop()));
                            const calldata = this.readMemory(argsOffset, argsLength);
                            if (this.contractManager && typeof addr === 'string' && this.contractManager.getContract(addr)) {
                                const res = this.contractManager.execute(addr, calldata);
                                if (res.returnData) {
                                    this.writeMemory(retOffset, res.returnData.subarray(0, retLength));
                                    this.returnData = res.returnData;
                                }
                                this.push(res.error ? 0 : 1);
                            } else {
                                this.emit('CALL', { target: addr, value, calldata: calldata.toString('hex') });
                                this.push(1);
                            }
                        } else {
                            const target = this.stack.length > 0 ? this.pop() : 'externalCall';
                            this.emit('CALL', { target });
                            this.push(1);
                        }
                        this.pc++;
                        break;
                    }
                    case 0xF2: { // CALLCODE
                        if (this.stack.length >= 7) {
                            const gas = this.pop(); const addr = this.pop(); const value = this.pop();
                            const argsOffset = Number(toBigInt(this.pop())); const argsLength = Number(toBigInt(this.pop()));
                            const retOffset = Number(toBigInt(this.pop())); const retLength = Number(toBigInt(this.pop()));
                            this.push(1);
                        } else {
                            this.push(1);
                        }
                        this.pc++;
                        break;
                    }
                    case 0xF3: { // RETURN
                        const offset = Number(toBigInt(this.pop()));
                        const length = Number(toBigInt(this.pop()));
                        const data = this.readMemory(offset, length);
                        this.returnData = data;
                        this.halted = true;
                        return {
                            result: data,
                            events: this.events,
                            gasUsed: this.gasUsed,
                            returnData: data,
                        };
                    }
                    case 0xF4: { // DELEGATECALL
                        if (this.stack.length >= 6) {
                            const gas = this.pop(); const addr = this.pop();
                            const argsOffset = Number(toBigInt(this.pop())); const argsLength = Number(toBigInt(this.pop()));
                            const retOffset = Number(toBigInt(this.pop())); const retLength = Number(toBigInt(this.pop()));
                            this.push(1);
                        } else {
                            this.push(1);
                        }
                        this.pc++;
                        break;
                    }
                    case 0xF5: { // CREATE2
                        const val = this.pop();
                        const offset = Number(toBigInt(this.pop()));
                        const length = Number(toBigInt(this.pop()));
                        const salt = this.pop();
                        if (this.contractManager) {
                            const initCode = this.readMemory(offset, length);
                            const newContract = this.contractManager.deploy(this.address, 'Contract_' + Date.now(), Array.from(initCode));
                            this.push(newContract.id);
                        } else {
                            this.push('0x0000000000000000000000000000000000000000');
                        }
                        this.pc++;
                        break;
                    }
                    case 0xFA: { // STATICCALL
                        if (this.stack.length >= 6) {
                            const gas = this.pop(); const addr = this.pop();
                            const argsOffset = Number(toBigInt(this.pop())); const argsLength = Number(toBigInt(this.pop()));
                            const retOffset = Number(toBigInt(this.pop())); const retLength = Number(toBigInt(this.pop()));
                            this.push(1);
                        } else {
                            this.push(1);
                        }
                        this.pc++;
                        break;
                    }
                    case 0xFD: { // REVERT
                        const offset = Number(toBigInt(this.pop()));
                        const length = Number(toBigInt(this.pop()));
                        const data = this.readMemory(offset, length);
                        this.returnData = data;
                        this.halted = true;
                        this.reverted = true;
                        return {
                            result: null,
                            events: this.events,
                            gasUsed: this.gasUsed,
                            returnData: data,
                            error: 'Reverted',
                        };
                    }
                    case 0xFE: { // INVALID
                        this.gasUsed = this.gasLimit;
                        return {
                            result: null,
                            events: this.events,
                            gasUsed: this.gasLimit,
                            error: 'Invalid instruction',
                        };
                    }
                    case 0xFF: { // SELFDESTRUCT / HALT
                        if (this.stack.length > 0) {
                            const recipient = this.pop();
                        }
                        this.halted = true;
                        break;
                    }
                    default: {
                        if (opcode >= 0x60 && opcode <= 0x7F) {
                            const numBytes = opcode - 0x5F;
                            let val = 0n;
                            let bytes = [];
                            for (let i = 1; i <= numBytes; i++) {
                                if (this.pc + i < bytecode.length) {
                                    bytes.push(bytecode[this.pc + i]);
                                }
                            }
                            if (bytes.length === 1 && typeof bytes[0] !== 'number') {
                                val = toBigInt(bytes[0]);
                            } else {
                                for (const b of bytes) {
                                    val = (val << 8n) | BigInt(Number(b) & 0xff);
                                }
                            }
                            this.push(formatStackValue(val));
                            this.pc += numBytes + 1;
                            break;
                        }
                        if (opcode >= 0x80 && opcode <= 0x8F) {
                            const depth = opcode - 0x7F;
                            const val = this.peek(depth - 1);
                            if (val === undefined && this.stack.length < depth) {
                                return { result: undefined, events: this.events, gasUsed: this.gasUsed, error: `Stack underflow on DUP${depth}` };
                            }
                            this.push(val);
                            this.pc++;
                            break;
                        }
                        if (opcode >= 0x90 && opcode <= 0x9F) {
                            const depth = opcode - 0x8F;
                            if (this.stack.length <= depth) {
                                return { result: undefined, events: this.events, gasUsed: this.gasUsed, error: `Stack underflow on SWAP${depth}` };
                            }
                            const topIdx = this.stack.length - 1;
                            const targetIdx = this.stack.length - 1 - depth;
                            const tmp = this.stack[topIdx];
                            this.stack[topIdx] = this.stack[targetIdx];
                            this.stack[targetIdx] = tmp;
                            this.pc++;
                            break;
                        }
                        return { result: this.peek(), events: this.events, gasUsed: this.gasUsed, error: `Unknown opcode: 0x${opcode.toString(16)}` };
                    }
                }
            } catch (err) {
                return {
                    result: this.peek(),
                    events: this.events,
                    gasUsed: this.gasUsed,
                    error: err.message,
                };
            }
        }

        return {
            result: this.peek(),
            events: this.events,
            gasUsed: this.gasUsed,
        };
    }
}
exports.StackVM = StackVM;

class ContractManager {
    constructor() {
        this.contracts = new Map();
    }
    deploy(owner, name, bytecode) {
        const id = (0, crypto_1.sha256)(`${owner}_${name}_${Date.now()}_${Math.random()}`);
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
    deployContract(name, owner, bytecode) {
        return this.deploy(owner, name, bytecode);
    }
    execute(contractId, input, callerState) {
        const contract = this.getContract(contractId);
        if (!contract) {
            return {
                result: null,
                events: [],
                gasUsed: 0,
                error: `Contract '${contractId}' not found`,
            };
        }
        const vm = new StackVM(contract.state, { contractManager: this });
        if (input !== undefined && input !== null) {
            if (Array.isArray(input)) {
                for (const item of input) {
                    vm.push(item);
                }
            } else {
                vm.push(input);
            }
        }
        return vm.run(contract.bytecode);
    }
    getContract(id) {
        return this.contracts.get(id);
    }
    getContracts() {
        return Array.from(this.contracts.values());
    }
    getAllContracts() {
        return this.getContracts();
    }
    getContractState(id) {
        const contract = this.getContract(id);
        return contract ? contract.state : undefined;
    }
    call(contractId, method, args = []) {
        const contract = this.getContract(contractId);
        if (!contract) {
            return {
                result: null,
                events: [],
                error: `Contract '${contractId}' not found`,
            };
        }
        const vm = new StackVM(contract.state, { contractManager: this });
        if (Array.isArray(args)) {
            for (const arg of args) {
                vm.push(arg);
            }
        }
        vm.push(method);
        const runResult = vm.run(contract.bytecode);
        return {
            result: runResult.result,
            events: runResult.events,
            ...(runResult.error ? { error: runResult.error } : {}),
        };
    }
}
exports.ContractManager = ContractManager;

function parseArg(arg, labels) {
    if (labels.has(arg)) {
        return labels.get(arg);
    }
    if (!isNaN(Number(arg)) && arg.trim() !== '') {
        return Number(arg);
    }
    if (arg === 'true') return 1;
    if (arg === 'false') return 0;
    return arg;
}

function getInstructionSize(tokens) {
    const op = tokens[0].toUpperCase();
    if (op === 'PUSH' || op.startsWith('PUSH')) return 2;
    if (['JUMP', 'JUMPI', 'LOAD', 'STORE', 'SLOAD', 'SSTORE', 'LOG', 'EMIT', 'CALL'].includes(op)) {
        return tokens.length > 1 ? 3 : 1;
    }
    return 1;
}

function compileContract(source) {
    const rawLines = source.split('\n');
    const parseLineTokens = (line) => {
        let clean = line;
        const commentIdx = clean.search(/\/\/|#|;/);
        if (commentIdx !== -1) {
            clean = clean.slice(0, commentIdx);
        }
        clean = clean.trim();
        if (!clean) return [];
        const matches = clean.match(/("[^"]*"|'[^']*'|\S+)/g);
        return matches ? matches.map(t => t.replace(/^["']|["']$/g, '')) : [];
    };

    const labels = new Map();
    let currentOffset = 0;
    const parsedInstructions = [];

    for (const rawLine of rawLines) {
        const tokens = parseLineTokens(rawLine);
        if (tokens.length === 0) continue;

        let remainingTokens = tokens;
        if (remainingTokens[0].toUpperCase() === 'LABEL' && remainingTokens.length > 1) {
            labels.set(remainingTokens[1], currentOffset);
            remainingTokens = remainingTokens.slice(2);
        } else if (remainingTokens[0].endsWith(':')) {
            const labelName = remainingTokens[0].slice(0, -1);
            labels.set(labelName, currentOffset);
            remainingTokens = remainingTokens.slice(1);
        }

        if (remainingTokens.length > 0) {
            parsedInstructions.push({ tokens: remainingTokens });
            currentOffset += getInstructionSize(remainingTokens);
        }
    }

    const bytecode = [];
    for (const { tokens } of parsedInstructions) {
        const opStr = tokens[0].toUpperCase();
        let opcode = exports.OPCODES[opStr];
        if (opcode === undefined) {
            throw new Error(`Unknown opcode instruction: ${tokens[0]}`);
        }

        if (opStr === 'PUSH' || opStr.startsWith('PUSH')) {
            const arg = tokens[1];
            bytecode.push(opcode, parseArg(arg, labels));
        } else if (['JUMP', 'JUMPI', 'LOAD', 'STORE', 'SLOAD', 'SSTORE', 'LOG', 'EMIT', 'CALL'].includes(opStr) && tokens.length > 1) {
            const arg = tokens[1];
            bytecode.push(exports.OPCODES.PUSH, parseArg(arg, labels));
            bytecode.push(opcode);
        } else {
            bytecode.push(opcode);
        }
    }
    return bytecode;
}
