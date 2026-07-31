import { SmartContract } from '../types';

export enum OPCODES {
  PUSH = 0x01,
  ADD = 0x02,
  SUB = 0x03,
  MUL = 0x04,
  DIV = 0x05,
  LOG = 0x06,
  HALT = 0x00,
  STORE = 0x10,
  LOAD = 0x11,
  SSTORE = 0x12,
  SLOAD = 0x13,
  DUP = 0x14,
  SWAP = 0x15,
  LT = 0x20,
  GT = 0x21,
  EQ = 0x22,
  JUMP = 0x30,
  JUMPI = 0x31,
  LABEL = 0x40,
}

export interface VMResult {
  result: number;
  events: { type: string; data: any }[];
  state: Map<string, any>;
}

export class StackVM {
  private stack: number[] = [];
  private memory: Map<string, number> = new Map();
  private storage: Map<string, number> = new Map();
  private events: { type: string; data: any }[] = [];

  public run(bytecode: number[], initialState?: Map<string, any>): VMResult {
    this.stack = [];
    this.memory = new Map();
    this.storage = initialState ? new Map(initialState) : new Map();
    this.events = [];

    let pc = 0;
    const labels: Map<string, number> = new Map();

    // First pass: collect labels if encoded in bytecode structure
    // Bytecode format: opcodes and operands
    let step = 0;
    while (step < bytecode.length) {
      const op = bytecode[step];
      if (op === OPCODES.PUSH) {
        step += 2;
      } else if (op === OPCODES.STORE || op === OPCODES.LOAD || op === OPCODES.SSTORE || op === OPCODES.SLOAD) {
        step += 2;
      } else if (op === OPCODES.LABEL || op === OPCODES.JUMP || op === OPCODES.JUMPI) {
        step += 2;
      } else {
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
      } else if (op === OPCODES.PUSH) {
        const val = bytecode[pc + 1] ?? 0;
        this.stack.push(val);
        pc += 2;
      } else if (op === OPCODES.ADD) {
        const b = this.stack.pop() ?? 0;
        const a = this.stack.pop() ?? 0;
        this.stack.push(a + b);
        pc += 1;
      } else if (op === OPCODES.SUB) {
        const b = this.stack.pop() ?? 0;
        const a = this.stack.pop() ?? 0;
        this.stack.push(a - b);
        pc += 1;
      } else if (op === OPCODES.MUL) {
        const b = this.stack.pop() ?? 0;
        const a = this.stack.pop() ?? 0;
        this.stack.push(a * b);
        pc += 1;
      } else if (op === OPCODES.DIV) {
        const b = this.stack.pop() ?? 1;
        const a = this.stack.pop() ?? 0;
        this.stack.push(Math.floor(a / b));
        pc += 1;
      } else if (op === OPCODES.LT) {
        const b = this.stack.pop() ?? 0;
        const a = this.stack.pop() ?? 0;
        this.stack.push(a < b ? 1 : 0);
        pc += 1;
      } else if (op === OPCODES.GT) {
        const b = this.stack.pop() ?? 0;
        const a = this.stack.pop() ?? 0;
        this.stack.push(a > b ? 1 : 0);
        pc += 1;
      } else if (op === OPCODES.EQ) {
        const b = this.stack.pop() ?? 0;
        const a = this.stack.pop() ?? 0;
        this.stack.push(a === b ? 1 : 0);
        pc += 1;
      } else if (op === OPCODES.LOG) {
        const val = this.stack[this.stack.length - 1] ?? 0;
        this.events.push({ type: 'LOG', data: val });
        pc += 1;
      } else if (op === OPCODES.DUP) {
        const val = this.stack[this.stack.length - 1] ?? 0;
        this.stack.push(val);
        pc += 1;
      } else if (op === OPCODES.SWAP) {
        const a = this.stack.pop() ?? 0;
        const b = this.stack.pop() ?? 0;
        this.stack.push(a);
        this.stack.push(b);
        pc += 1;
      } else if (op === OPCODES.STORE) {
        const varIdx = bytecode[pc + 1] ?? 0;
        const val = this.stack.pop() ?? 0;
        this.memory.set(String(varIdx), val);
        pc += 2;
      } else if (op === OPCODES.LOAD) {
        const varIdx = bytecode[pc + 1] ?? 0;
        const val = this.memory.get(String(varIdx)) ?? 0;
        this.stack.push(val);
        pc += 2;
      } else if (op === OPCODES.SSTORE) {
        const varIdx = bytecode[pc + 1] ?? 0;
        const val = this.stack.pop() ?? 0;
        this.storage.set(String(varIdx), val);
        pc += 2;
      } else if (op === OPCODES.SLOAD) {
        const varIdx = bytecode[pc + 1] ?? 0;
        const val = this.storage.get(String(varIdx)) ?? 0;
        this.stack.push(val);
        pc += 2;
      } else if (op === OPCODES.JUMP) {
        const targetPc = bytecode[pc + 1] ?? 0;
        pc = targetPc;
      } else if (op === OPCODES.JUMPI) {
        const targetPc = bytecode[pc + 1] ?? 0;
        const cond = this.stack.pop() ?? 0;
        if (cond !== 0) {
          pc = targetPc;
        } else {
          pc += 2;
        }
      } else {
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

export function compileContract(source: string): number[] {
  const lines = source.split('\n');
  const bytecode: number[] = [];
  const labels: Map<string, number> = new Map();
  const symbolMap: Map<string, number> = new Map();
  let nextSymbolIdx = 1;

  function getSymbolIdx(sym: string): number {
    if (!symbolMap.has(sym)) {
      symbolMap.set(sym, nextSymbolIdx++);
    }
    return symbolMap.get(sym)!;
  }

  // Pass 1: Compute bytecode indices and record labels
  let currentByteIndex = 0;
  for (let line of lines) {
    line = line.trim();
    if (!line || line.startsWith('//')) continue;

    const parts = line.split(/\s+/);
    const cmd = parts[0].toUpperCase();

    if (cmd === 'LABEL') {
      labels.set(parts[1], currentByteIndex);
    } else if (cmd === 'PUSH') {
      currentByteIndex += 2;
    } else if (
      cmd === 'STORE' ||
      cmd === 'LOAD' ||
      cmd === 'SSTORE' ||
      cmd === 'SLOAD' ||
      cmd === 'JUMP' ||
      cmd === 'JUMPI'
    ) {
      currentByteIndex += 2;
    } else {
      currentByteIndex += 1;
    }
  }

  // Pass 2: Emit bytecode
  for (let line of lines) {
    line = line.trim();
    if (!line || line.startsWith('//')) continue;

    const parts = line.split(/\s+/);
    const cmd = parts[0].toUpperCase();

    if (cmd === 'PUSH') {
      bytecode.push(OPCODES.PUSH, parseInt(parts[1], 10) || 0);
    } else if (cmd === 'ADD') {
      bytecode.push(OPCODES.ADD);
    } else if (cmd === 'SUB') {
      bytecode.push(OPCODES.SUB);
    } else if (cmd === 'MUL') {
      bytecode.push(OPCODES.MUL);
    } else if (cmd === 'DIV') {
      bytecode.push(OPCODES.DIV);
    } else if (cmd === 'LOG') {
      bytecode.push(OPCODES.LOG);
    } else if (cmd === 'HALT') {
      bytecode.push(OPCODES.HALT);
    } else if (cmd === 'DUP') {
      bytecode.push(OPCODES.DUP);
    } else if (cmd === 'SWAP') {
      bytecode.push(OPCODES.SWAP);
    } else if (cmd === 'LT') {
      bytecode.push(OPCODES.LT);
    } else if (cmd === 'GT') {
      bytecode.push(OPCODES.GT);
    } else if (cmd === 'EQ') {
      bytecode.push(OPCODES.EQ);
    } else if (cmd === 'STORE') {
      bytecode.push(OPCODES.STORE, getSymbolIdx(parts[1]));
    } else if (cmd === 'LOAD') {
      bytecode.push(OPCODES.LOAD, getSymbolIdx(parts[1]));
    } else if (cmd === 'SSTORE') {
      bytecode.push(OPCODES.SSTORE, getSymbolIdx(parts[1]));
    } else if (cmd === 'SLOAD') {
      bytecode.push(OPCODES.SLOAD, getSymbolIdx(parts[1]));
    } else if (cmd === 'LABEL') {
      // Labels take no execution space
    } else if (cmd === 'JUMP') {
      const target = labels.get(parts[1]) ?? 0;
      bytecode.push(OPCODES.JUMP, target);
    } else if (cmd === 'JUMPI') {
      const target = labels.get(parts[1]) ?? 0;
      bytecode.push(OPCODES.JUMPI, target);
    }
  }

  return bytecode;
}

export class ContractManager {
  private contracts: Map<string, SmartContract> = new Map();

  public deploy(owner: string, name: string, bytecode: number[]): SmartContract {
    const id = 'contract_' + Date.now() + '_' + Math.floor(Math.random() * 1000);
    const contract: SmartContract = {
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

  public deployContract(name: string, owner: string, bytecode: number[]): SmartContract {
    return this.deploy(owner, name, bytecode);
  }

  public getContract(id: string): SmartContract | undefined {
    return this.contracts.get(id);
  }

  public getAllContracts(): SmartContract[] {
    return Array.from(this.contracts.values());
  }

  public execute(contractId: string, input: any): VMResult {
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
