import { SmartContract } from '../types';
export declare enum OPCODES {
    PUSH = 1,
    ADD = 2,
    SUB = 3,
    MUL = 4,
    DIV = 5,
    LOG = 6,
    HALT = 0,
    STORE = 16,
    LOAD = 17,
    SSTORE = 18,
    SLOAD = 19,
    DUP = 20,
    SWAP = 21,
    LT = 32,
    GT = 33,
    EQ = 34,
    JUMP = 48,
    JUMPI = 49,
    LABEL = 64
}
export interface VMResult {
    result: number;
    events: {
        type: string;
        data: any;
    }[];
    state: Map<string, any>;
}
export declare class StackVM {
    private stack;
    private memory;
    private storage;
    private events;
    run(bytecode: number[], initialState?: Map<string, any>): VMResult;
}
export declare function compileContract(source: string): number[];
export declare class ContractManager {
    private contracts;
    deploy(owner: string, name: string, bytecode: number[]): SmartContract;
    deployContract(name: string, owner: string, bytecode: number[]): SmartContract;
    getContract(id: string): SmartContract | undefined;
    getAllContracts(): SmartContract[];
    execute(contractId: string, input: any): VMResult;
}
