import { SmartContract } from '../types';
/**
 * Bytecode Instruction Set Opcodes for RojsChain Smart Contract Virtual Machine.
 */
export declare const OPCODES: {
    readonly PUSH: 1;
    readonly POP: 2;
    readonly ADD: 3;
    readonly SUB: 4;
    readonly MUL: 5;
    readonly DIV: 6;
    readonly MOD: 7;
    readonly EQ: 8;
    readonly LT: 9;
    readonly GT: 10;
    readonly JUMP: 11;
    readonly JUMPI: 12;
    readonly STORE: 13;
    readonly LOAD: 14;
    readonly CALL: 15;
    readonly LOG: 16;
    readonly HALT: 255;
    readonly DUP: 17;
    readonly SWAP: 18;
    readonly SSTORE: 19;
    readonly SLOAD: 20;
    readonly EMIT: 21;
};
/**
 * Real stack-based virtual machine executing bytecode instructions.
 */
export declare class StackVM {
    private stack;
    private state;
    private events;
    private pc;
    private halted;
    private gasUsed;
    private gasLimit;
    private transientStorage;
    constructor(state?: Map<string, any>);
    /**
     * Pushes a value onto the stack.
     */
    push(value: any): void;
    /**
     * Pops top value from the stack.
     */
    pop(): any;
    /**
     * Peeks top value on the stack without popping.
     */
    peek(): any;
    /**
     * Loads value from contract persistent state.
     */
    load(key: string): any;
    /**
     * Stores value in contract persistent state.
     */
    store(key: string, value: any): void;
    /**
     * Emits an event with event name and data payload.
     */
    emit(event: string, data: any): void;
    /**
     * Returns all recorded events.
     */
    getEvents(): {
        event: string;
        data: any;
    }[];
    /**
     * Returns total gas consumed by execution.
     */
    getGasUsed(): number;
    /**
     * Executes bytecode instruction by instruction.
     * Costs 1 gas per opcode, 3 gas for storage operations, 5 gas for CALL.
     * Halts on HALT opcode, out of gas, or execution error.
     */
    run(bytecode: number[]): {
        result: any;
        events: {
            event: string;
            data: any;
        }[];
        gasUsed: number;
        error?: string;
    };
}
/**
 * Manages deployment, retrieval, state, and execution of smart contracts.
 */
export declare class ContractManager {
    private contracts;
    /**
     * Creates and stores a new contract, returns it.
     */
    deploy(owner: string, name: string, bytecode: number[]): SmartContract;
    /**
     * Alias for deploy to maintain backward compatibility.
     */
    deployContract(name: string, owner: string, bytecode: number[]): SmartContract;
    /**
     * Runs the contract bytecode in a new StackVM with the contract state.
     */
    execute(contractId: string, input: any, callerState?: Map<string, any>): {
        result: any;
        events: any[];
        gasUsed: number;
        error?: string;
    };
    /**
     * Retrieves smart contract by ID.
     */
    getContract(id: string): SmartContract | undefined;
    /**
     * Returns array of all deployed contracts.
     */
    getContracts(): SmartContract[];
    /**
     * Alias for getContracts.
     */
    getAllContracts(): SmartContract[];
    /**
     * Returns persistent state map for contract with given ID.
     */
    getContractState(id: string): Map<string, any> | undefined;
    /**
     * Higher-level method call that wraps bytecode execution with a method selector.
     */
    call(contractId: string, method: string, args?: any[]): {
        result: any;
        events: any[];
        error?: string;
    };
}
/**
 * Compiles human-readable assembly source code into bytecode.
 */
export declare function compileContract(source: string): number[];
