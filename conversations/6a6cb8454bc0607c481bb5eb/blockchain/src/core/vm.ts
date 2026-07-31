import { SmartContract } from '../types';

export class ContractManager {
  private contracts: Map<string, SmartContract> = new Map();

  public deployContract(name: string, owner: string, bytecode: number[]): SmartContract {
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

  public getContract(id: string): SmartContract | undefined {
    return this.contracts.get(id);
  }

  public getAllContracts(): SmartContract[] {
    return Array.from(this.contracts.values());
  }
}
