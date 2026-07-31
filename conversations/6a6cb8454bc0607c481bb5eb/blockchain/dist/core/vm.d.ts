import { SmartContract } from '../types';
export declare function compileContract(source: string): number[];
export declare class ContractManager {
    private contracts;
    deployContract(owner: string, name: string, bytecode: number[]): SmartContract;
    executeContract(contractId: string, input: any): any;
    getContract(contractId: string): SmartContract | null;
    getAllContracts(): SmartContract[];
    getContractState(contractId: string): Map<string, any> | null;
}
