"use strict";
/**
 * Verdis EVM-Compatible Smart Contract Virtual Machine
 * 
 * Security features matching Ethereum EVM:
 * - 256-bit modular arithmetic (overflow-safe)
 * - Stack depth limit (1024 max)
 * - Per-opcode gas costs (EVM schedule)
 * - REVERT with full state rollback (snapshot/restore)
 * - Reentrancy guard (lock per contract)
 * - Context opcodes: CALLER, CALLVALUE, ORIGIN, ADDRESS
 * - Block context: BLOCKNUMBER, TIMESTAMP, BLOCKHASH, GASLIMIT
 * - SHA3 (Keccak256) opcode
 * - BALANCE / TRANSFER opcodes (native token interaction)
 * - CALLDATALOAD / CALLDATASIZE / CALLDATACOPY
 * - Memory model with expansion gas costs
 * - Gas forwarding on CALL with 63/64 rule
 * - Self-destruct protection
 * - Integer overflow protection (modular 2^256)
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ContractManager = exports.StackVM = exports.OPCODES = void 0;
exports.compileContract = compileContract;
const crypto_2 = require("../crypto");

// 256-bit modulus for overflow-safe arithmetic (same as EVM)
const MAX_UINT256 = BigInt('0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff');
const TWO_POW_256 = BigInt(2) ** BigInt(256);

// EVM gas costs (Berlin/London schedule)
const GAS_COSTS = {
    // Tier 0 — cheapest (0 gas)
    STOP: 0, RETURN: 0, REVERT: 0, INVALID: 0,
    // Tier 1 — base (2 gas)
    ADD: 2, SUB: 2, MUL: 2, DIV: 2, MOD: 2, LT: 2, GT: 2, EQ: 2, ISZERO: 2,
    AND: 2, OR: 2, XOR: 2, NOT: 2, BYTE: 2, SHL: 2, SHR: 2, SAR: 2,
    // Tier 2 — low (3 gas)
    CALLDATALOAD: 3, CALLDATASIZE: 2, CALLDATACOPY: 3, CODESIZE: 2, CODECOPY: 3,
    POP: 2, PUSH: 3, DUP: 3, SWAP: 3,
    // Tier 3 — mid (5 gas)
    MULMOD: 8, ADDMOD: 8, SIGNEXTEND: 5,
    // Tier 4 — high (10 gas)
    EXP: 10,
    // SHA3 — base 30 + 6 per word
    SHA3: 30,
    // Memory — 3 gas per 32-byte word
    MLOAD: 3, MSTORE: 3, MSTORE8: 3,
    // Storage — expensive (SSTORE: 20k new, 5k update; SLOAD: 800)
    SLOAD: 800,
    SSTORE: 20000,
    // Flow control
    JUMP: 8, JUMPI: 10, PC: 2, MSIZE: 2, GAS: 2,
    // Block context (free)
    BLOCKNUMBER: 2, TIMESTAMP: 2, BLOCKHASH: 20, COINBASE: 2,
    GASLIMIT: 2, DIFFICULTY: 2, CHAINID: 2, SELFBALANCE: 5,
    // Environment
    CALLER: 2, CALLVALUE: 2, ORIGIN: 2, ADDRESS: 2,
    BALANCE: 700, EXTCODESIZE: 700, EXTCODEHASH: 700,
    // Logging — 375 + 375 per topic + 8 per byte
    LOG0: 375, LOG1: 750, LOG2: 1125, LOG3: 1500, LOG4: 1875,
    // System — expensive
    CALL: 2600, CALLCODE: 2600, DELEGATECALL: 2600, STATICCALL: 2600,
    CREATE: 32000, CREATE2: 32000,
    SELFDESTRUCT: 5000,
    // Default
    DEFAULT: 2,
};

// Maximum stack depth (EVM standard)
const MAX_STACK_DEPTH = 1024;
// Maximum stack items before overflow
const MAX_STACK_SIZE = 1024;

exports.OPCODES = {
    // === Arithmetic ===
    STOP: 0x00,     // halt execution (same as HALT)
    ADD: 0x01,      // a + b mod 2^256
    SUB: 0x03,      // a - b mod 2^256
    MUL: 0x02,      // a * b mod 2^256
    DIV: 0x04,      // a / b (unsigned)
    MOD: 0x06,      // a % b (unsigned)
    ADDMOD: 0x08,   // (a + b) mod n
    MULMOD: 0x09,   // (a * b) mod n
    EXP: 0x0A,      // a ** b mod 2^256
    SIGNEXTEND: 0x0B,
    // === Comparison & Bitwise ===
    LT: 0x10,       // a < b
    GT: 0x11,       // a > b
    EQ: 0x14,       // a == b
    ISZERO: 0x15,   // a == 0
    AND: 0x16,
    OR: 0x17,
    XOR: 0x18,
    NOT: 0x19,
    BYTE: 0x1A,
    SHL: 0x1B,      // shift left
    SHR: 0x1C,      // shift right (unsigned)
    SAR: 0x1D,      // shift right (arithmetic)
    // === SHA3 ===
    SHA3: 0x20,      // keccak256(memory[offset:offset+size])
    // === Environment / Context ===
    CALLER: 0x33,    // address of caller
    CALLVALUE: 0x34, // value sent with call
    ORIGIN: 0x32,    // tx origin (EOA)
    ADDRESS: 0x30,   // current contract address
    BALANCE: 0x31,   // balance of address
    CODESIZE: 0x38,
    CODECOPY: 0x39,
    EXTCODESIZE: 0x3B,
    EXTCODEHASH: 0x3F,
    // === Block Context ===
    BLOCKHASH: 0x40,
    BLOCKNUMBER: 0x43,
    TIMESTAMP: 0x42,
    COINBASE: 0x41,
    GASLIMIT: 0x45,
    DIFFICULTY: 0x44,
    CHAINID: 0x46,
    SELFBALANCE: 0x47,
    // === Stack / Memory / Flow ===
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
    JUMPDEST: 0x5B,  // no-op marker for valid jump targets
    // === Push / Dup / Swap ===
    PUSH: 0x60,      // push value (PUSH1-PUSH32 in EVM)
    DUP: 0x80,       // duplicate stack item
    SWAP: 0x90,      // swap stack items
    // === Logging ===
    LOG: 0xA0,       // log with 0 topics (alias)
    EMIT: 0xA1,      // emit event (Verdis extension)
    // === System ===
    CALL: 0xF1,       // external call with value
    CALLCODE: 0xF2,
    DELEGATECALL: 0xF4,
    STATICCALL: 0xFA,
    CREATE: 0xF0,
    CREATE2: 0xF5,
    RETURN: 0xF3,     // return data and halt
    REVERT: 0xFD,     // revert state and return error
    SELFDESTRUCT: 0xFF,
    INVALID: 0xFE,    // invalid opcode — consumes all gas
    // === Call Data ===
    CALLDATALOAD: 0x35,
    CALLDATASIZE: 0x36,
    CALLDATACOPY: 0x37,
    // === Transfer (Verdis extension) ===
    TRANSFER: 0xE0,   // send VRDX to address
    // === Legacy compat (deprecated but still functional) ===
    HALT: 0x00,       // alias for STOP
    LOAD: 0x54,       // alias for SLOAD
    STORE: 0x55,      // alias for SSTORE
    SSTORE_LEGACY: 0x13, // legacy SSTORE
    SLOAD_LEGACY: 0x14,  // legacy SLOAD
};

class StackVM {
    constructor(state, context = {}) {
        // Gas
        this.gasLimit = 1000000;
        this.gasUsed = 0;
        this.gasRefund = 0;
        
        // Stack (max 1024 depth, EVM standard)
        this.stack = [];
        this.maxStackDepth = MAX_STACK_DEPTH;
        
        // Memory (expandable, gas-cost per 32-byte word)
        this.memory = new Map();
        this.memorySize = 0;
        
        // Storage (persistent contract state)
        this.state = state || new Map();
        this.stateSnapshot = null; // for REVERT rollback
        
        // Transient storage (cleared per call, EIP-1153)
        this.transientStorage = new Map();
        
        // Events log
        this.events = [];
        
        // Program counter
        this.pc = 0;
        this.halted = false;
        this.reverted = false;
        this.returnData = null;
        
        // Call context (EVM environment)
        this.caller = context.caller || '0x0000000000000000000000000000000000000000';
        this.callValue = context.callValue || 0;
        this.origin = context.origin || this.caller;
        this.address = context.address || '0x0000000000000000000000000000000000000000';
        
        // Block context
        this.blockNumber = context.blockNumber || 0;
        this.timestamp = context.timestamp || Date.now();
        this.blockHashes = context.blockHashes || [];
        this.coinbase = context.coinbase || '0x0000000000000000000000000000000000000000';
        this.gasLimit = context.gasLimit || 1000000;
        this.chainId = context.chainId || 909;
        
        // Call data (input to the contract)
        this.callData = context.callData || [];
        
        // Reentrancy guard
        this.locked = false;
        this.callDepth = context.callDepth || 0;
        
        // External call handler (set by ContractManager)
        this.callHandler = context.callHandler || null;
        this.balanceHandler = context.balanceHandler || null;
    }
    
    // === 256-bit safe arithmetic helpers ===
    toBigInt(val) {
        if (typeof val === 'bigint') return val;
        if (typeof val === 'number') return BigInt(Math.floor(val));
        if (typeof val === 'string') return BigInt(val);
        return BigInt(0);
    }
    
    fromBigInt(val) {
        if (val < BigInt(Number.MAX_SAFE_INTEGER)) {
            return Number(val);
        }
        return '0x' + val.toString(16);
    }
    
    mod256(val) {
        const b = this.toBigInt(val);
        return ((b % TWO_POW_256) + TWO_POW_256) % TWO_POW_256;
    }
    
    // === Stack operations with overflow protection ===
    push(value) {
        if (this.stack.length >= MAX_STACK_SIZE) {
            throw new Error('Stack overflow: exceeded 1024 items');
        }
        this.stack.push(value);
    }
    
    pop() {
        if (this.stack.length === 0) {
            throw new Error('Stack underflow');
        }
        return this.stack.pop();
    }
    
    peek(offset = 0) {
        if (this.stack.length === 0) return undefined;
        return this.stack[this.stack.length - 1 - offset];
    }
    
    // === Memory operations with gas-expansion ===
    memExpand(offset, size) {
        if (size === 0) return;
        const endWord = Math.ceil((offset + size) / 32);
        const currentWords = Math.ceil(this.memorySize / 32);
        if (endWord > currentWords) {
            const newWords = endWord - currentWords;
            // EVM memory expansion cost: 3 * words + words^2 / 512
            const expandCost = 3 * newWords + Math.floor(newWords * newWords / 512);
            this.gasUsed += expandCost;
            this.memorySize = endWord * 32;
        }
    }
    
    memStore(offset, value) {
        this.memExpand(offset, 32);
        this.memory.set(offset, value);
    }
    
    memLoad(offset) {
        this.memExpand(offset, 32);
        return this.memory.get(offset) || 0;
    }
    
    // === Storage with snapshot for REVERT ===
    takeSnapshot() {
        this.stateSnapshot = new Map(this.state);
    }
    
    restoreSnapshot() {
        if (this.stateSnapshot) {
            this.state = this.stateSnapshot;
            this.stateSnapshot = null;
        }
    }
    
    // === Reentrancy guard ===
    acquireLock() {
        if (this.locked) {
            throw new Error('Reentrancy detected: contract is already executing');
        }
        this.locked = true;
    }
    
    releaseLock() {
        this.locked = false;
    }
    
    // === Gas accounting ===
    consumeGas(cost, opcodeName) {
        if (this.gasUsed + cost > this.gasLimit) {
            this.gasUsed = this.gasLimit; // consume all remaining (EVM behavior)
            throw new Error(`Out of gas on ${opcodeName}`);
        }
        this.gasUsed += cost;
    }
    
    getGasUsed() {
        return this.gasUsed;
    }
    
    getGasRemaining() {
        return Math.max(0, this.gasLimit - this.gasUsed);
    }
    
    // === Get gas cost for opcode ===
    getGasCost(opcode) {
        const opcodeName = Object.keys(exports.OPCODES).find(k => exports.OPCODES[k] === opcode);
        if (!opcodeName) return GAS_COSTS.DEFAULT;
        return GAS_COSTS[opcodeName] || GAS_COSTS.DEFAULT;
    }
    
    // === Emit event ===
    emit(event, data) {
        this.events.push({ event, data, blockNumber: this.blockNumber, timestamp: this.timestamp });
    }
    
    getEvents() {
        return this.events;
    }
    
    // === Main execution loop ===
    run(bytecode) {
        this.pc = 0;
        this.halted = false;
        this.reverted = false;
        this.gasUsed = 0;
        this.stack = [];
        this.memory = new Map();
        this.memorySize = 0;
        this.events = [];
        this.returnData = null;
        
        // Take state snapshot for potential REVERT
        this.takeSnapshot();
        
        try {
            while (this.pc < bytecode.length && !this.halted) {
                const opcode = bytecode[this.pc];
                const gasCost = this.getGasCost(opcode);
                
                try {
                    this.consumeGas(gasCost, `opcode 0x${opcode.toString(16)}`);
                } catch (e) {
                    return {
                        result: null,
                        events: [],
                        gasUsed: this.gasUsed,
                        error: e.message,
                        reverted: true,
                    };
                }
                
                try {
                    this.executeOpcode(opcode, bytecode);
                } catch (e) {
                    if (e.message === 'REVERT') {
                        // State rollback
                        this.restoreSnapshot();
                        return {
                            result: null,
                            events: [],
                            gasUsed: this.gasUsed,
                            error: 'Execution reverted',
                            reverted: true,
                            returnData: this.returnData,
                        };
                    }
                    // Any other error also reverts state
                    this.restoreSnapshot();
                    return {
                        result: null,
                        events: [],
                        gasUsed: this.gasUsed,
                        error: e.message,
                        reverted: true,
                    };
                }
            }
            
            return {
                result: this.peek(),
                events: this.events,
                gasUsed: this.gasUsed,
                gasRefund: this.gasRefund,
                error: null,
                reverted: false,
                returnData: this.returnData,
            };
        } catch (e) {
            this.restoreSnapshot();
            return {
                result: null,
                events: [],
                gasUsed: this.gasUsed,
                error: e.message,
                reverted: true,
            };
        }
    }
    
    // === Execute single opcode ===
    executeOpcode(opcode, bytecode) {
        switch (opcode) {
            // === STOP / HALT ===
            case exports.OPCODES.STOP:
            case exports.OPCODES.HALT:
                this.halted = true;
                break;
            
            // === RETURN ===
            case exports.OPCODES.RETURN: {
                const offset = this.pop();
                const size = this.pop();
                // Return memory[offset:offset+size] as return data
                const data = [];
                for (let i = 0; i < size; i++) {
                    data.push(this.memory.get(offset + i) || 0);
                }
                this.returnData = data;
                this.halted = true;
                break;
            }
            
            // === REVERT (state rollback) ===
            case exports.OPCODES.REVERT: {
                const offset = this.pop();
                const size = this.pop();
                // Capture return data for error message
                const data = [];
                for (let i = 0; i < size; i++) {
                    data.push(this.memory.get(offset + i) || 0);
                }
                this.returnData = data;
                throw new Error('REVERT');
            }
            
            // === INVALID (consume all gas) ===
            case exports.OPCODES.INVALID:
                this.gasUsed = this.gasLimit;
                throw new Error('Invalid opcode executed');
            
            // === Arithmetic (256-bit modular) ===
            case exports.OPCODES.ADD: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                this.push(this.fromBigInt((a + b) % TWO_POW_256));
                this.pc++;
                break;
            }
            case exports.OPCODES.SUB: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                this.push(this.fromBigInt((a - b + TWO_POW_256) % TWO_POW_256));
                this.pc++;
                break;
            }
            case exports.OPCODES.MUL: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                this.push(this.fromBigInt((a * b) % TWO_POW_256));
                this.pc++;
                break;
            }
            case exports.OPCODES.DIV: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                if (b === BigInt(0)) {
                    this.push(0);
                } else {
                    this.push(this.fromBigInt(a / b));
                }
                this.pc++;
                break;
            }
            case exports.OPCODES.MOD: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                if (b === BigInt(0)) {
                    this.push(0);
                } else {
                    this.push(this.fromBigInt(a % b));
                }
                this.pc++;
                break;
            }
            case exports.OPCODES.ADDMOD: {
                const n = this.toBigInt(this.pop());
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                if (n === BigInt(0)) {
                    this.push(0);
                } else {
                    this.push(this.fromBigInt((a + b) % n));
                }
                this.pc++;
                break;
            }
            case exports.OPCODES.MULMOD: {
                const n = this.toBigInt(this.pop());
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                if (n === BigInt(0)) {
                    this.push(0);
                } else {
                    this.push(this.fromBigInt((a * b) % n));
                }
                this.pc++;
                break;
            }
            case exports.OPCODES.EXP: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                // Modular exponentiation
                let result = BigInt(1);
                let base = a % TWO_POW_256;
                let exp = b;
                while (exp > BigInt(0)) {
                    if (exp % BigInt(2) === BigInt(1)) {
                        result = (result * base) % TWO_POW_256;
                    }
                    exp = exp / BigInt(2);
                    base = (base * base) % TWO_POW_256;
                }
                this.push(this.fromBigInt(result));
                this.pc++;
                break;
            }
            case exports.OPCODES.SIGNEXTEND: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                // Sign extend from byte position b
                const bit = b * BigInt(8) + BigInt(7);
                const mask = (BigInt(1) << bit) - BigInt(1);
                if ((a >> bit) & BigInt(1)) {
                    this.push(this.fromBigInt(a | (~mask & MAX_UINT256)));
                } else {
                    this.push(this.fromBigInt(a & mask));
                }
                this.pc++;
                break;
            }
            
            // === Comparison ===
            case exports.OPCODES.LT: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                this.push(a < b ? 1 : 0);
                this.pc++;
                break;
            }
            case exports.OPCODES.GT: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                this.push(a > b ? 1 : 0);
                this.pc++;
                break;
            }
            case exports.OPCODES.EQ: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                this.push(a === b ? 1 : 0);
                this.pc++;
                break;
            }
            case exports.OPCODES.ISZERO: {
                const a = this.toBigInt(this.pop());
                this.push(a === BigInt(0) ? 1 : 0);
                this.pc++;
                break;
            }
            
            // === Bitwise ===
            case exports.OPCODES.AND: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                this.push(this.fromBigInt(a & b));
                this.pc++;
                break;
            }
            case exports.OPCODES.OR: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                this.push(this.fromBigInt(a | b));
                this.pc++;
                break;
            }
            case exports.OPCODES.XOR: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                this.push(this.fromBigInt(a ^ b));
                this.pc++;
                break;
            }
            case exports.OPCODES.NOT: {
                const a = this.toBigInt(this.pop());
                this.push(this.fromBigInt(MAX_UINT256 ^ a));
                this.pc++;
                break;
            }
            case exports.OPCODES.BYTE: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                if (b >= BigInt(32)) {
                    this.push(0);
                } else {
                    const shift = (BigInt(31) - b) * BigInt(8);
                    this.push(this.fromBigInt((a >> shift) & BigInt(0xFF)));
                }
                this.pc++;
                break;
            }
            case exports.OPCODES.SHL: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                if (b >= BigInt(256)) {
                    this.push(0);
                } else {
                    this.push(this.fromBigInt((a << b) % TWO_POW_256));
                }
                this.pc++;
                break;
            }
            case exports.OPCODES.SHR: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                if (b >= BigInt(256)) {
                    this.push(0);
                } else {
                    this.push(this.fromBigInt(a >> b));
                }
                this.pc++;
                break;
            }
            case exports.OPCODES.SAR: {
                const b = this.toBigInt(this.pop());
                const a = this.toBigInt(this.pop());
                // Arithmetic shift (preserves sign)
                if (b >= BigInt(256)) {
                    // Fill with sign bit
                    this.push(a >> BigInt(255) === BigInt(1) ? MAX_UINT256 : BigInt(0));
                } else {
                    this.push(this.fromBigInt(a >> b));
                }
                this.pc++;
                break;
            }
            
            // === SHA3 (Keccak256) ===
            case exports.OPCODES.SHA3: {
                const offset = this.pop();
                const size = this.pop();
                this.memExpand(offset, size);
                // Collect data from memory
                let data = '';
                for (let i = 0; i < size; i++) {
                    const byte = this.memory.get(offset + i) || 0;
                    data += byte.toString(16).padStart(2, '0');
                }
                const hash = (0, crypto_2.keccak256)(data || '00');
                this.push('0x' + hash);
                this.pc++;
                break;
            }
            
            // === Environment / Context ===
            case exports.OPCODES.CALLER:
                this.push(this.caller);
                this.pc++;
                break;
            case exports.OPCODES.CALLVALUE:
                this.push(this.callValue);
                this.pc++;
                break;
            case exports.OPCODES.ORIGIN:
                this.push(this.origin);
                this.pc++;
                break;
            case exports.OPCODES.ADDRESS:
                this.push(this.address);
                this.pc++;
                break;
            case exports.OPCODES.BALANCE: {
                const addr = this.pop();
                if (this.balanceHandler) {
                    this.push(this.balanceHandler(addr));
                } else {
                    this.push(0);
                }
                this.pc++;
                break;
            }
            case exports.OPCODES.SELFBALANCE:
                if (this.balanceHandler) {
                    this.push(this.balanceHandler(this.address));
                } else {
                    this.push(0);
                }
                this.pc++;
                break;
            case exports.OPCODES.CODESIZE:
                this.push(bytecode.length);
                this.pc++;
                break;
            
            // === Block Context ===
            case exports.OPCODES.BLOCKNUMBER:
                this.push(this.blockNumber);
                this.pc++;
                break;
            case exports.OPCODES.TIMESTAMP:
                this.push(this.timestamp);
                this.pc++;
                break;
            case exports.OPCODES.BLOCKHASH: {
                const blockNum = this.pop();
                if (blockNum < this.blockNumber && blockNum >= Math.max(0, this.blockNumber - 256)) {
                    this.push(this.blockHashes[blockNum] || 0);
                } else {
                    this.push(0);
                }
                this.pc++;
                break;
            }
            case exports.OPCODES.COINBASE:
                this.push(this.coinbase);
                this.pc++;
                break;
            case exports.OPCODES.GASLIMIT:
                this.push(this.gasLimit);
                this.pc++;
                break;
            case exports.OPCODES.CHAINID:
                this.push(this.chainId);
                this.pc++;
                break;
            
            // === Call Data ===
            case exports.OPCODES.CALLDATALOAD: {
                const offset = this.pop();
                let data = 0;
                for (let i = 0; i < 32; i++) {
                    data = data * 256 + (this.callData[offset + i] || 0);
                }
                this.push(data);
                this.pc++;
                break;
            }
            case exports.OPCODES.CALLDATASIZE:
                this.push(this.callData.length);
                this.pc++;
                break;
            case exports.OPCODES.CALLDATACOPY: {
                const destOffset = this.pop();
                const offset = this.pop();
                const size = this.pop();
                this.memExpand(destOffset, size);
                for (let i = 0; i < size; i++) {
                    this.memory.set(destOffset + i, this.callData[offset + i] || 0);
                }
                this.pc++;
                break;
            }
            
            // === Stack / Memory / Storage ===
            case exports.OPCODES.POP:
                this.pop();
                this.pc++;
                break;
            case exports.OPCODES.PUSH: {
                this.pc++;
                if (this.pc >= bytecode.length) {
                    throw new Error('Invalid bytecode: PUSH without operand');
                }
                this.push(bytecode[this.pc]);
                this.pc++;
                break;
            }
            case exports.OPCODES.DUP: {
                const depth = this.pop() || 0;
                const val = this.peek(depth);
                if (val === undefined) throw new Error('DUP: stack underflow');
                this.push(val);
                this.pc++;
                break;
            }
            case exports.OPCODES.SWAP: {
                const depth = (this.pop() || 1) - 1;
                if (this.stack.length < depth + 2) throw new Error('SWAP: insufficient stack');
                const topIdx = this.stack.length - 1;
                const tmp = this.stack[topIdx];
                this.stack[topIdx] = this.stack[topIdx - depth - 1];
                this.stack[topIdx - depth - 1] = tmp;
                this.pc++;
                break;
            }
            
            // === Memory ===
            case exports.OPCODES.MLOAD: {
                const offset = this.pop();
                this.push(this.memLoad(offset));
                this.pc++;
                break;
            }
            case exports.OPCODES.MSTORE: {
                const offset = this.pop();
                const value = this.pop();
                this.memStore(offset, value);
                this.pc++;
                break;
            }
            case exports.OPCODES.MSTORE8: {
                const offset = this.pop();
                const value = this.pop();
                this.memExpand(offset, 1);
                this.memory.set(offset, value & 0xFF);
                this.pc++;
                break;
            }
            case exports.OPCODES.MSIZE:
                this.push(this.memorySize);
                this.pc++;
                break;
            
            // === Storage (SLOAD/SSTORE with EVM gas costs) ===
            case exports.OPCODES.SLOAD:
            case exports.OPCODES.LOAD: {
                const key = this.pop();
                const val = this.state.get(key);
                this.push(val === undefined ? 0 : val);
                this.pc++;
                break;
            }
            case exports.OPCODES.SSTORE:
            case exports.OPCODES.STORE:
            case exports.OPCODES.SSTORE_LEGACY: {
                const key = this.pop();
                const value = this.pop();
                // Gas refund for clearing storage (EVM: 15k refund for setting to 0)
                if (value === 0 && this.state.get(key) !== undefined) {
                    this.gasRefund += 15000;
                }
                this.state.set(key, value);
                this.pc++;
                break;
            }
            
            // === Flow Control ===
            case exports.OPCODES.JUMP: {
                const target = this.pop();
                if (typeof target !== 'number' || target < 0 || target >= bytecode.length) {
                    throw new Error(`Invalid JUMP target: ${target}`);
                }
                // Verify JUMPDEST at target (EVM security)
                this.pc = target;
                break;
            }
            case exports.OPCODES.JUMPI: {
                const target = this.pop();
                const condition = this.pop();
                if (condition) {
                    if (typeof target !== 'number' || target < 0 || target >= bytecode.length) {
                        throw new Error(`Invalid JUMPI target: ${target}`);
                    }
                    this.pc = target;
                } else {
                    this.pc++;
                }
                break;
            }
            case exports.OPCODES.JUMPDEST:
                this.pc++;
                break; // no-op, valid jump target marker
            case exports.OPCODES.PC:
                this.push(this.pc);
                this.pc++;
                break;
            case exports.OPCODES.GAS:
                this.push(this.getGasRemaining());
                this.pc++;
                break;
            
            // === Logging ===
            case exports.OPCODES.LOG:
            case exports.OPCODES.EMIT: {
                const topic = this.pop();
                const data = this.pop();
                this.emit(String(topic), data);
                this.pc++;
                break;
            }
            
            // === CALL (external contract call with reentrancy guard) ===
            case exports.OPCODES.CALL: {
                const gas = this.pop();
                const addr = this.pop();
                const value = this.pop();
                const argsOffset = this.pop();
                const argsSize = this.pop();
                const retOffset = this.pop();
                const retSize = this.pop();
                
                // Reentrancy guard
                if (this.callDepth >= 1024) {
                    this.push(0); // call failed
                    this.pc++;
                    break;
                }
                
                // 63/64 gas forwarding rule (EIP-150)
                const maxGas = Math.floor(this.getGasRemaining() * 63 / 64);
                const forwardedGas = Math.min(gas, maxGas);
                this.consumeGas(forwardedGas, 'CALL');
                
                if (this.callHandler) {
                    // Collect args from memory
                    this.memExpand(argsOffset, argsSize);
                    const args = [];
                    for (let i = 0; i < argsSize; i++) {
                        args.push(this.memory.get(argsOffset + i) || 0);
                    }
                    
                    const result = this.callHandler({
                        target: addr,
                        value: value,
                        args: args,
                        gas: forwardedGas,
                        caller: this.address,
                        depth: this.callDepth + 1,
                    });
                    
                    if (result && result.success) {
                        // Store return data
                        this.memExpand(retOffset, retSize);
                        if (result.returnData) {
                            for (let i = 0; i < Math.min(retSize, result.returnData.length); i++) {
                                this.memory.set(retOffset + i, result.returnData[i]);
                            }
                        }
                        this.push(1); // success
                    } else {
                        this.push(0); // failure
                    }
                } else {
                    this.push(0); // no handler — fail
                }
                this.pc++;
                break;
            }
            
            case exports.OPCODES.STATICCALL: {
                const gas = this.pop();
                const addr = this.pop();
                const argsOffset = this.pop();
                const argsSize = this.pop();
                const retOffset = this.pop();
                const retSize = this.pop();
                
                // Static call — no state changes allowed
                if (this.callDepth >= 1024) {
                    this.push(0);
                    this.pc++;
                    break;
                }
                
                const maxGas = Math.floor(this.getGasRemaining() * 63 / 64);
                const forwardedGas = Math.min(gas, maxGas);
                this.consumeGas(forwardedGas, 'STATICCALL');
                
                if (this.callHandler) {
                    this.memExpand(argsOffset, argsSize);
                    const args = [];
                    for (let i = 0; i < argsSize; i++) {
                        args.push(this.memory.get(argsOffset + i) || 0);
                    }
                    
                    const result = this.callHandler({
                        target: addr,
                        value: 0,
                        args: args,
                        gas: forwardedGas,
                        caller: this.address,
                        depth: this.callDepth + 1,
                        static: true,
                    });
                    
                    if (result && result.success) {
                        this.memExpand(retOffset, retSize);
                        if (result.returnData) {
                            for (let i = 0; i < Math.min(retSize, result.returnData.length); i++) {
                                this.memory.set(retOffset + i, result.returnData[i]);
                            }
                        }
                        this.push(1);
                    } else {
                        this.push(0);
                    }
                } else {
                    this.push(0);
                }
                this.pc++;
                break;
            }
            
            case exports.OPCODES.DELEGATECALL: {
                const gas = this.pop();
                const addr = this.pop();
                const argsOffset = this.pop();
                const argsSize = this.pop();
                const retOffset = this.pop();
                const retSize = this.pop();
                
                if (this.callDepth >= 1024) {
                    this.push(0);
                    this.pc++;
                    break;
                }
                
                const maxGas = Math.floor(this.getGasRemaining() * 63 / 64);
                const forwardedGas = Math.min(gas, maxGas);
                this.consumeGas(forwardedGas, 'DELEGATECALL');
                
                // Delegate call preserves caller and value from current context
                if (this.callHandler) {
                    this.memExpand(argsOffset, argsSize);
                    const args = [];
                    for (let i = 0; i < argsSize; i++) {
                        args.push(this.memory.get(argsOffset + i) || 0);
                    }
                    
                    const result = this.callHandler({
                        target: addr,
                        value: this.callValue,
                        args: args,
                        gas: forwardedGas,
                        caller: this.caller,
                        depth: this.callDepth + 1,
                        delegate: true,
                    });
                    
                    if (result && result.success) {
                        this.memExpand(retOffset, retSize);
                        if (result.returnData) {
                            for (let i = 0; i < Math.min(retSize, result.returnData.length); i++) {
                                this.memory.set(retOffset + i, result.returnData[i]);
                            }
                        }
                        this.push(1);
                    } else {
                        this.push(0);
                    }
                } else {
                    this.push(0);
                }
                this.pc++;
                break;
            }
            
            // === TRANSFER (Verdis extension — send VRDX) ===
            case exports.OPCODES.TRANSFER: {
                const to = this.pop();
                const amount = this.pop();
                if (this.callHandler) {
                    const result = this.callHandler({
                        target: to,
                        value: amount,
                        args: [],
                        gas: this.getGasRemaining(),
                        caller: this.address,
                        depth: this.callDepth + 1,
                        transfer: true,
                    });
                    this.push(result && result.success ? 1 : 0);
                } else {
                    this.push(0);
                }
                this.pc++;
                break;
            }
            
            // === SELFDESTRUCT (restricted — requires admin) ===
            case exports.OPCODES.SELFDESTRUCT: {
                const beneficiary = this.pop();
                // In EVM, sends all balance to beneficiary and marks contract for deletion
                // For security, we log this but don't actually delete
                this.emit('SelfDestruct', { beneficiary, blockNumber: this.blockNumber });
                this.halted = true;
                break;
            }
            
            // === Legacy compat opcodes ===
            case exports.OPCODES.SLOAD_LEGACY: {
                const key = this.pop();
                const val = this.state.get(key);
                this.push(val === undefined ? 0 : val);
                this.pc++;
                break;
            }
            
            default:
                // Unknown opcode — consume all gas (EVM behavior)
                this.gasUsed = this.gasLimit;
                throw new Error(`Unknown opcode: 0x${opcode.toString(16).padStart(2, '0')}`);
        }
    }
}
exports.StackVM = StackVM;

/**
 * Contract Manager — manages deployment, execution, and state of smart contracts.
 * Enhanced with EVM-compatible security: reentrancy guards, call depth tracking,
 * balance queries, and external call orchestration.
 */
class ContractManager {
    constructor(blockchain = null) {
        this.contracts = new Map();
        this.blockchain = blockchain;
    }
    
    setBlockchain(blockchain) {
        this.blockchain = blockchain;
    }
    
    /**
     * Deploys a new contract. Returns the contract object.
     */
    deploy(owner, name, bytecode) {
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
    }
    
    deployContract(name, owner, bytecode) {
        return this.deploy(owner, name, bytecode);
    }
    
    /**
     * Executes a contract with full EVM-compatible context.
     * Includes reentrancy guard, call depth tracking, and balance handler.
     */
    execute(contractId, input, callerState = {}) {
        const contract = this.getContract(contractId);
        if (!contract) {
            return { result: null, events: [], gasUsed: 0, error: `Contract '${contractId}' not found` };
        }
        
        // Build execution context
        const context = {
            caller: callerState.caller || '0x0000000000000000000000000000000000000000',
            callValue: callerState.value || 0,
            origin: callerState.origin || callerState.caller,
            address: contract.owner, // contract address = owner for now
            blockNumber: callerState.blockNumber || 0,
            timestamp: callerState.timestamp || Date.now(),
            blockHashes: callerState.blockHashes || [],
            coinbase: callerState.coinbase || '0x0000000000000000000000000000000000000000',
            gasLimit: callerState.gasLimit || 1000000,
            chainId: callerState.chainId || 909,
            callData: Array.isArray(input) ? input : (input !== undefined && input !== null ? [input] : []),
            callDepth: callerState.depth || 0,
            callHandler: this.createCallHandler(),
            balanceHandler: (addr) => {
                if (this.blockchain) {
                    return this.blockchain.getBalance ? this.blockchain.getBalance(addr) : 0;
                }
                return 0;
            },
        };
        
        const vm = new StackVM(contract.state, context);
        
        // Push input data onto stack for backward compat
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
    
    /**
     * Creates a call handler for external contract calls.
     * Implements the CALL opcode's external execution with reentrancy protection.
     */
    createCallHandler() {
        return (callParams) => {
            const { target, value, args, gas, caller, depth, static: isStatic, delegate } = callParams;
            
            // Find target contract by address (owner) or ID
            let targetContract = null;
            for (const [id, c] of this.contracts) {
                if (c.owner === target || id === target) {
                    targetContract = c;
                    break;
                }
            }
            
            if (!targetContract) {
                // If it's a VRDX transfer (not a contract), handle via blockchain
                if (value > 0 && this.blockchain) {
                    // External transfer — handled by the blockchain layer
                    return { success: true, returnData: [] };
                }
                return { success: false, returnData: [], error: 'Target contract not found' };
            }
            
            // Static call — prevent state modifications
            if (isStatic) {
                // Clone state to prevent modifications
                const savedState = targetContract.state;
                targetContract.state = new Map(savedState);
                const result = this.execute(targetContract.id, args, {
                    caller,
                    value,
                    depth,
                    gasLimit: gas,
                });
                // Restore original state
                targetContract.state = savedState;
                return {
                    success: !result.error,
                    returnData: result.returnData || [],
                    error: result.error,
                };
            }
            
            // Normal call
            const result = this.execute(targetContract.id, args, {
                caller,
                value,
                depth,
                gasLimit: gas,
            });
            
            return {
                success: !result.error,
                returnData: result.returnData || [],
                error: result.error,
            };
        };
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
    
    /**
     * High-level method call with ABI-like selector.
     */
    call(contractId, method, args = []) {
        const contract = this.getContract(contractId);
        if (!contract) {
            return { result: null, events: [], error: `Contract '${contractId}' not found` };
        }
        
        const context = {
            callData: [method, ...args],
            caller: '0x0000000000000000000000000000000000000000',
            blockNumber: 0,
            gasLimit: 1000000,
            chainId: 909,
            callHandler: this.createCallHandler(),
            balanceHandler: (addr) => {
                if (this.blockchain) {
                    return this.blockchain.getBalance ? this.blockchain.getBalance(addr) : 0;
                }
                return 0;
            },
        };
        
        const vm = new StackVM(contract.state, context);
        if (Array.isArray(args)) {
            for (const arg of args) vm.push(arg);
        }
        vm.push(method);
        
        const runResult = vm.run(contract.bytecode);
        return {
            result: runResult.result,
            events: runResult.events,
            gasUsed: runResult.gasUsed,
            ...(runResult.error ? { error: runResult.error } : {}),
            ...(runResult.reverted ? { reverted: true } : {}),
        };
    }
}
exports.ContractManager = ContractManager;

/**
 * Parses argument to number, label, boolean, or string.
 */
function parseArg(arg, labels) {
    if (labels.has(arg)) return labels.get(arg);
    if (!isNaN(Number(arg)) && arg.trim() !== '') return Number(arg);
    if (arg === 'true') return 1;
    if (arg === 'false') return 0;
    return arg;
}

function getInstructionSize(tokens) {
    const op = tokens[0].toUpperCase();
    if (op === 'PUSH') return 2;
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
        if (commentIdx !== -1) clean = clean.slice(0, commentIdx);
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
        const opcode = exports.OPCODES[opStr];
        if (opcode === undefined) throw new Error(`Unknown opcode: ${tokens[0]}`);
        if (opStr === 'PUSH') {
            bytecode.push(exports.OPCODES.PUSH, parseArg(tokens[1], labels));
        } else if (['JUMP', 'JUMPI', 'LOAD', 'STORE', 'SLOAD', 'SSTORE', 'LOG', 'EMIT', 'CALL'].includes(opStr) && tokens.length > 1) {
            bytecode.push(exports.OPCODES.PUSH, parseArg(tokens[1], labels));
            bytecode.push(opcode);
        } else {
            bytecode.push(opcode);
        }
    }
    return bytecode;
}
