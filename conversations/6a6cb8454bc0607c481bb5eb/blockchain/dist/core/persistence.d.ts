/**
 * Persistence Layer for Verdis Blockchain
 *
 * Saves and restores the full blockchain state to/from disk,
 * allowing the chain to survive restarts with all data intact.
 *
 * State file: blobs/verdis-state.json
 */
import { Blockchain } from './consensus';
import { WalletManager } from '../wallet/wallet';
import { EcoSystem } from './eco';
import { DEX } from './dex';
import { ContractManager } from './vm';
import { Block, Transaction } from '../types';
export interface VerdisState {
    version: number;
    timestamp: number;
    chain: Block[];
    balances: Record<string, number>;
    stakes: Record<string, number>;
    totalSupply: number;
    maxSupply: number;
    validators: Array<{
        publicKey: string;
        address: string;
        votes: number;
        isProducer: boolean;
        blocksProduced: number;
        totalRewards: number;
    }>;
    voteStakes: Array<{
        voter: string;
        validator: string;
        amount: number;
        timestamp: number;
    }>;
    roundTurn: number;
    mempool: Transaction[];
    wallets: Array<{
        privateKey: string;
        publicKey: string;
        address: string;
        balance: number;
        staked: number;
    }>;
    carbonCredits: any[];
    reforestationProjects: any[];
    greenScores: any[];
    pools: any[];
    contracts: any[];
    marketData: any;
}
/**
 * Exports the full blockchain state to a serializable object.
 */
export declare function exportState(blockchain: Blockchain, walletManager: WalletManager, ecoSystem: EcoSystem, dex: DEX, contractManager: ContractManager, marketTracker?: any): VerdisState;
/**
 * Saves the full blockchain state to disk.
 */
export declare function saveState(blockchain: Blockchain, walletManager: WalletManager, ecoSystem: EcoSystem, dex: DEX, contractManager: ContractManager, marketTracker?: any): boolean;
/**
 * Loads the blockchain state from disk and restores all systems.
 * Returns null if no state file exists.
 */
export declare function loadState(): VerdisState | null;
/**
 * Restores all blockchain systems from saved state.
 * Must be called before block production starts.
 */
export declare function restoreState(state: VerdisState, blockchain: Blockchain, walletManager: WalletManager, ecoSystem: EcoSystem, dex: DEX, contractManager: ContractManager): void;
/**
 * Periodically saves state at a given interval.
 */
export declare function startAutoSave(blockchain: Blockchain, walletManager: WalletManager, ecoSystem: EcoSystem, dex: DEX, contractManager: ContractManager, intervalMs?: number, marketTracker?: any): NodeJS.Timeout;
