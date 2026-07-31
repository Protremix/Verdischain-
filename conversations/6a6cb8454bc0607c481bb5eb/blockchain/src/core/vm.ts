import { SmartContract, Transaction } from '../types';
import { sha256 } from '../crypto';

/**
 * Bytecode Instruction Set Opcodes for RojsChain Smart Contract Virtual Machine.
 */
export const OPCODES = {
  PUSH: 0x01,   // push value onto stack
  POP: 0x02,    // pop from stack
  ADD: 0x03,    // pop two, push sum
  SUB: 0x04,    // pop two, push difference
  MUL: 0x05,    // pop two, push product
  DIV: 0x06,    // pop two, push quotient
  MOD: 0x07,    // pop two, push modulo
  EQ: 0x08,     // pop two, push 1 if equal
  LT: 0x09,     // pop two, push 1 if first < second
  GT: 0x0A,     // pop two, push 1 if first > second
  JUMP: 0x0B,   // jump to instruction index
  JUMPI: 0x0C,  // conditional jump (pop condition, if true jump)
  STORE: 0x0D,  // store value in contract state (pop key, pop value)
  LOAD: 0x0E,   // load value from contract state (pop key, push value)
  CALL: 0x0F,   // call external function (log the call)
  LOG: 0x10,    // log a value
  HALT: 0xFF,   // stop execution
  DUP: 0x11,    // duplicate top of stack
  SWAP: 0x12,   // swap top two stack items
  SSTORE: 0x13, // store in transient storage
  SLOAD: 0x14,  // load from transient storage
  EMIT: 0x15,   // emit an event
} as const;

/**
 * Real stack-based virtual machine executing bytecode instructions.
 */
export class StackVM {
  private stack: any[];
  private state: Map<string, any>;
  private events: { event: string; data: any }[];
  private pc: number;
  private halted: boolean;
  private gasUsed: number;
  private gasLimit: number = 1000000;
  private transientStorage: Map<string, any>;

  constructor(state?: Map<string, any>) {
    this.stack = [];
    this.state = state || new Map<string, any>();
    this.events = [];
    this.pc = 0;
    this.halted = false;
    this.gasUsed = 0;
    this.gasLimit = 1000000;
    this.transientStorage = new Map<string, any>();
  }

  /**
   * Pushes a value onto the stack.
   */
  public push(value: any): void {
    this.stack.push(value);
  }

  /**
   * Pops top value from the stack.
   */
  public pop(): any {
    if (this.stack.length === 0) {
      throw new Error('Stack underflow');
    }
    return this.stack.pop();
  }

  /**
   * Peeks top value on the stack without popping.
   */
  public peek(): any {
    if (this.stack.length === 0) {
      return undefined;
    }
    return this.stack[this.stack.length - 1];
  }

  /**
   * Loads value from contract persistent state.
   */
  public load(key: string): any {
    return this.state.get(key);
  }

  /**
   * Stores value in contract persistent state.
   */
  public store(key: string, value: any): void {
    this.state.set(key, value);
  }

  /**
   * Emits an event with event name and data payload.
   */
  public emit(event: string, data: any): void {
    this.events.push({ event, data });
  }

  /**
   * Returns all recorded events.
   */
  public getEvents(): { event: string; data: any }[] {
    return this.events;
  }

  /**
   * Returns total gas consumed by execution.
   */
  public getGasUsed(): number {
    return this.gasUsed;
  }

  /**
   * Executes bytecode instruction by instruction.
   * Costs 1 gas per opcode, 3 gas for storage operations, 5 gas for CALL.
   * Halts on HALT opcode, out of gas, or execution error.
   */
  public run(bytecode: number[]): {
    result: any;
    events: { event: string; data: any }[];
    gasUsed: number;
    error?: string;
  } {
    this.pc = 0;
    this.halted = false;
    this.gasUsed = 0;

    while (this.pc < bytecode.length && !this.halted) {
      const opcode = bytecode[this.pc];

      // Calculate gas cost per instruction
      let gasCost = 1;
      if (
        opcode === OPCODES.STORE ||
        opcode === OPCODES.LOAD ||
        opcode === OPCODES.SSTORE ||
        opcode === OPCODES.SLOAD
      ) {
        gasCost = 3;
      } else if (opcode === OPCODES.CALL) {
        gasCost = 5;
      }

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
          case OPCODES.PUSH: {
            this.pc++;
            if (this.pc >= bytecode.length) {
              return {
                result: this.peek(),
                events: this.events,
                gasUsed: this.gasUsed,
                error: 'Invalid bytecode: PUSH without operand',
              };
            }
            const val = bytecode[this.pc];
            this.push(val);
            this.pc++;
            break;
          }

          case OPCODES.POP: {
            this.pop();
            this.pc++;
            break;
          }

          case OPCODES.ADD: {
            const b = this.pop();
            const a = this.pop();
            this.push(a + b);
            this.pc++;
            break;
          }

          case OPCODES.SUB: {
            const b = this.pop();
            const a = this.pop();
            this.push(a - b);
            this.pc++;
            break;
          }

          case OPCODES.MUL: {
            const b = this.pop();
            const a = this.pop();
            this.push(a * b);
            this.pc++;
            break;
          }

          case OPCODES.DIV: {
            const b = this.pop();
            const a = this.pop();
            if (b === 0) {
              return {
                result: this.peek(),
                events: this.events,
                gasUsed: this.gasUsed,
                error: 'Division by zero',
              };
            }
            this.push(typeof a === 'number' && typeof b === 'number' ? Math.floor(a / b) : a / b);
            this.pc++;
            break;
          }

          case OPCODES.MOD: {
            const b = this.pop();
            const a = this.pop();
            if (b === 0) {
              return {
                result: this.peek(),
                events: this.events,
                gasUsed: this.gasUsed,
                error: 'Modulo by zero',
              };
            }
            this.push(a % b);
            this.pc++;
            break;
          }

          case OPCODES.EQ: {
            const b = this.pop();
            const a = this.pop();
            this.push(a === b ? 1 : 0);
            this.pc++;
            break;
          }

          case OPCODES.LT: {
            const b = this.pop();
            const a = this.pop();
            this.push(a < b ? 1 : 0);
            this.pc++;
            break;
          }

          case OPCODES.GT: {
            const b = this.pop();
            const a = this.pop();
            this.push(a > b ? 1 : 0);
            this.pc++;
            break;
          }

          case OPCODES.JUMP: {
            let target: number;
            if (this.stack.length > 0) {
              target = this.pop();
            } else if (this.pc + 1 < bytecode.length) {
              this.pc++;
              target = bytecode[this.pc];
            } else {
              return {
                result: this.peek(),
                events: this.events,
                gasUsed: this.gasUsed,
                error: 'Stack underflow on JUMP',
              };
            }

            if (typeof target !== 'number' || target < 0 || target >= bytecode.length) {
              return {
                result: this.peek(),
                events: this.events,
                gasUsed: this.gasUsed,
                error: `Invalid JUMP target: ${target}`,
              };
            }
            this.pc = target;
            break;
          }

          case OPCODES.JUMPI: {
            let target: number;
            let condition: any;

            if (this.stack.length >= 2) {
              target = this.pop();
              condition = this.pop();
            } else if (this.stack.length === 1 && this.pc + 1 < bytecode.length) {
              condition = this.pop();
              this.pc++;
              target = bytecode[this.pc];
            } else {
              return {
                result: this.peek(),
                events: this.events,
                gasUsed: this.gasUsed,
                error: 'Stack underflow on JUMPI',
              };
            }

            if (condition) {
              if (typeof target !== 'number' || target < 0 || target >= bytecode.length) {
                return {
                  result: this.peek(),
                  events: this.events,
                  gasUsed: this.gasUsed,
                  error: `Invalid JUMPI target: ${target}`,
                };
              }
              this.pc = target;
            } else {
              this.pc++;
            }
            break;
          }

          case OPCODES.STORE: {
            const key = this.pop();
            const value = this.pop();
            this.store(String(key), value);
            this.pc++;
            break;
          }

          case OPCODES.LOAD: {
            const key = this.pop();
            const value = this.load(String(key));
            this.push(value);
            this.pc++;
            break;
          }

          case OPCODES.CALL: {
            const target = this.stack.length > 0 ? this.pop() : 'externalCall';
            this.emit('CALL', { target });
            this.pc++;
            break;
          }

          case OPCODES.LOG: {
            const val = this.pop();
            this.emit('LOG', val);
            this.pc++;
            break;
          }

          case OPCODES.DUP: {
            const val = this.peek();
            if (val === undefined && this.stack.length === 0) {
              return {
                result: undefined,
                events: this.events,
                gasUsed: this.gasUsed,
                error: 'Stack underflow on DUP',
              };
            }
            this.push(val);
            this.pc++;
            break;
          }

          case OPCODES.SWAP: {
            if (this.stack.length < 2) {
              return {
                result: this.peek(),
                events: this.events,
                gasUsed: this.gasUsed,
                error: 'Stack underflow on SWAP',
              };
            }
            const a = this.pop();
            const b = this.pop();
            this.push(a);
            this.push(b);
            this.pc++;
            break;
          }

          case OPCODES.SSTORE: {
            const key = this.pop();
            const value = this.pop();
            this.transientStorage.set(String(key), value);
            this.pc++;
            break;
          }

          case OPCODES.SLOAD: {
            const key = this.pop();
            const value = this.transientStorage.get(String(key));
            this.push(value);
            this.pc++;
            break;
          }

          case OPCODES.EMIT: {
            if (this.stack.length >= 2) {
              const data = this.pop();
              const eventName = this.pop();
              this.emit(String(eventName), data);
            } else if (this.stack.length === 1) {
              const data = this.pop();
              this.emit('EVENT', data);
            } else {
              this.emit('EVENT', null);
            }
            this.pc++;
            break;
          }

          case OPCODES.HALT: {
            this.halted = true;
            this.pc++;
            break;
          }

          default: {
            return {
              result: this.peek(),
              events: this.events,
              gasUsed: this.gasUsed,
              error: `Invalid opcode: 0x${opcode.toString(16)} at index ${this.pc}`,
            };
          }
        }
      } catch (err: any) {
        return {
          result: this.peek(),
          events: this.events,
          gasUsed: this.gasUsed,
          error: err?.message || String(err),
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

/**
 * Manages deployment, retrieval, state, and execution of smart contracts.
 */
export class ContractManager {
  private contracts: Map<string, SmartContract> = new Map();

  /**
   * Creates and stores a new contract, returns it.
   */
  public deploy(owner: string, name: string, bytecode: number[]): SmartContract {
    const id = sha256(`${owner}_${name}_${Date.now()}_${Math.random()}`);
    const contract: SmartContract = {
      id,
      owner,
      name,
      bytecode,
      state: new Map<string, any>(),
      deployedAt: Date.now(),
    };
    this.contracts.set(id, contract);
    return contract;
  }

  /**
   * Alias for deploy to maintain backward compatibility.
   */
  public deployContract(name: string, owner: string, bytecode: number[]): SmartContract {
    return this.deploy(owner, name, bytecode);
  }

  /**
   * Runs the contract bytecode in a new StackVM with the contract state.
   */
  public execute(
    contractId: string,
    input: any,
    callerState?: Map<string, any>
  ): { result: any; events: any[]; gasUsed: number; error?: string } {
    const contract = this.getContract(contractId);
    if (!contract) {
      return {
        result: null,
        events: [],
        gasUsed: 0,
        error: `Contract '${contractId}' not found`,
      };
    }

    const vm = new StackVM(contract.state);

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
   * Retrieves smart contract by ID.
   */
  public getContract(id: string): SmartContract | undefined {
    return this.contracts.get(id);
  }

  /**
   * Returns array of all deployed contracts.
   */
  public getContracts(): SmartContract[] {
    return Array.from(this.contracts.values());
  }

  /**
   * Alias for getContracts.
   */
  public getAllContracts(): SmartContract[] {
    return this.getContracts();
  }

  /**
   * Returns persistent state map for contract with given ID.
   */
  public getContractState(id: string): Map<string, any> | undefined {
    const contract = this.getContract(id);
    return contract ? contract.state : undefined;
  }

  /**
   * Higher-level method call that wraps bytecode execution with a method selector.
   */
  public call(
    contractId: string,
    method: string,
    args: any[] = []
  ): { result: any; events: any[]; error?: string } {
    const contract = this.getContract(contractId);
    if (!contract) {
      return {
        result: null,
        events: [],
        error: `Contract '${contractId}' not found`,
      };
    }

    const vm = new StackVM(contract.state);

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

/**
 * Parses single token into number, label address, boolean, or string value.
 */
function parseArg(arg: string, labels: Map<string, number>): any {
  if (labels.has(arg)) {
    return labels.get(arg)!;
  }
  if (!isNaN(Number(arg)) && arg.trim() !== '') {
    return Number(arg);
  }
  if (arg === 'true') return 1;
  if (arg === 'false') return 0;
  return arg;
}

/**
 * Calculates byte size of instruction line for label offset resolution.
 */
function getInstructionSize(tokens: string[]): number {
  const op = tokens[0].toUpperCase();
  if (op === 'PUSH') return 2;
  if (['JUMP', 'JUMPI', 'LOAD', 'STORE', 'SLOAD', 'SSTORE', 'LOG', 'EMIT', 'CALL'].includes(op)) {
    return tokens.length > 1 ? 3 : 1;
  }
  return 1;
}

/**
 * Compiles human-readable assembly source code into bytecode.
 */
export function compileContract(source: string): number[] {
  const rawLines = source.split('\n');

  const parseLineTokens = (line: string): string[] => {
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

  const labels = new Map<string, number>();
  let currentOffset = 0;
  const parsedInstructions: { tokens: string[] }[] = [];

  // Pass 1: Resolve labels and calculate instruction byte offsets
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

  // Pass 2: Generate bytecode array
  const bytecode: number[] = [];

  for (const { tokens } of parsedInstructions) {
    const opStr = tokens[0].toUpperCase();
    const opcode = (OPCODES as Record<string, number>)[opStr];

    if (opcode === undefined) {
      throw new Error(`Unknown opcode instruction: ${tokens[0]}`);
    }

    if (opStr === 'PUSH') {
      const arg = tokens[1];
      bytecode.push(OPCODES.PUSH, parseArg(arg, labels));
    } else if (
      ['JUMP', 'JUMPI', 'LOAD', 'STORE', 'SLOAD', 'SSTORE', 'LOG', 'EMIT', 'CALL'].includes(opStr) &&
      tokens.length > 1
    ) {
      const arg = tokens[1];
      bytecode.push(OPCODES.PUSH, parseArg(arg, labels));
      bytecode.push(opcode);
    } else {
      bytecode.push(opcode);
    }
  }

  return bytecode;
}
