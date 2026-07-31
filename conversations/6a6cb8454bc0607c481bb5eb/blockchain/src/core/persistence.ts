/**
 * Persistence Layer for Verdis Blockchain
 * 
 * Saves and restores the full blockchain state to/from disk,
 * allowing the chain to survive restarts with all data intact.
 * 
 * State file: blobs/verdis-state.json
 */

import fs from 'fs';
import path from 'path';
import { Blockchain, TokenSystem, DPoSConsensus } from './consensus';
import { Mempool } from './transaction';
import { WalletManager } from '../wallet/wallet';
import { EcoSystem } from './eco';
import { DEX } from './dex';
import { ContractManager } from './vm';
import { Block, Transaction } from '../types';

const STATE_FILE = path.join(process.cwd(), '..', 'blobs', 'verdis-state.json');
const STATE_DIR = path.dirname(STATE_FILE);

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
export function exportState(
  blockchain: Blockchain,
  walletManager: WalletManager,
  ecoSystem: EcoSystem,
  dex: DEX,
  contractManager: ContractManager,
  marketTracker?: any
): VerdisState {
  const tokenSystem = blockchain.getTokenSystem();
  const consensus = blockchain.getConsensus();
  const mempool = blockchain.getMempool();

  // Export balances
  const balances: Record<string, number> = {};
  for (const [addr, bal] of tokenSystem.getBalancesMap()) {
    balances[addr] = bal;
  }

  // Export stakes (staking positions)
  const stakes: Record<string, number> = {};
  // TokenSystem doesn't expose stakes map directly, but we can get them from wallets
  for (const w of walletManager.getAllWallets()) {
    stakes[w.address] = tokenSystem.getStaked(w.address);
  }

  // Export validators
  const validators = consensus.getAllValidatorsList().map(v => ({
    publicKey: v.publicKey,
    address: v.address,
    votes: v.votes,
    isProducer: v.isProducer,
    blocksProduced: v.blocksProduced,
    totalRewards: v.totalRewards,
  }));

  // Export vote stakes
  const voteStakes = consensus.getStakes();

  // Export mempool
  const mempoolTxs = mempool.getPendingTransactions(10000);

  // Export wallets
  const wallets = walletManager.getAllWallets().map(w => ({
    privateKey: w.privateKey,
    publicKey: w.publicKey,
    address: w.address,
    balance: w.balance,
    staked: w.staked,
  }));

  // Export eco data
  const carbonCredits = ecoSystem.getCarbonCredits();
  const reforestationProjects = ecoSystem.getReforestationProjects();
  const greenScores = ecoSystem.getAllGreenScores();

  // Export DEX pools
  const pools = dex.getAllPools();

  // Export contracts
  const contracts = contractManager.getContracts();

  return {
    version: 1,
    timestamp: Date.now(),
    chain: blockchain.getChain(),
    balances,
    stakes,
    totalSupply: tokenSystem.getTotalSupply(),
    maxSupply: tokenSystem.getMaxSupply(),
    validators,
    voteStakes,
    roundTurn: (consensus as any).roundTurn || 0,
    mempool: mempoolTxs,
    wallets,
    carbonCredits,
    reforestationProjects,
    greenScores,
    pools,
    contracts,
    marketData: marketTracker ? marketTracker.exportData() : null,
  };
}

/**
 * Saves the full blockchain state to disk.
 */
export function saveState(
  blockchain: Blockchain,
  walletManager: WalletManager,
  ecoSystem: EcoSystem,
  dex: DEX,
  contractManager: ContractManager,
  marketTracker?: any
): boolean {
  try {
    // Ensure directory exists
    if (!fs.existsSync(STATE_DIR)) {
      fs.mkdirSync(STATE_DIR, { recursive: true });
    }

    const state = exportState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker);
    const json = JSON.stringify(state, null, 2);
    fs.writeFileSync(STATE_FILE, json);

    console.log(`💾 State saved: ${state.chain.length} blocks, ${Object.keys(state.balances).length} balances, ${state.wallets.length} wallets, ${state.contracts.length} contracts, ${state.pools.length} pools`);
    return true;
  } catch (error) {
    console.error('❌ Failed to save state:', error);
    return false;
  }
}

/**
 * Loads the blockchain state from disk and restores all systems.
 * Returns null if no state file exists.
 */
export function loadState(): VerdisState | null {
  try {
    if (!fs.existsSync(STATE_FILE)) {
      return null;
    }

    const json = fs.readFileSync(STATE_FILE, 'utf-8');
    if (!json || json.trim() === '') return null;

    const state: VerdisState = JSON.parse(json);
    console.log(`📂 State file found: v${state.version}, saved ${new Date(state.timestamp).toISOString()}`);
    return state;
  } catch (error) {
    console.error('❌ Failed to load state:', error);
    return null;
  }
}

/**
 * Restores all blockchain systems from saved state.
 * Must be called before block production starts.
 */
export function restoreState(
  state: VerdisState,
  blockchain: Blockchain,
  walletManager: WalletManager,
  ecoSystem: EcoSystem,
  dex: DEX,
  contractManager: ContractManager
): void {
  // Restore wallets first (needed for validator addresses)
  for (const w of state.wallets) {
    const wallet = walletManager.importWallet(w.privateKey);
    wallet.balance = w.balance;
    wallet.staked = w.staked;
  }

  // Restore chain (replace genesis-only chain with saved chain)
  const chainField = blockchain.getChain();
  if (chainField.length > 0) {
    chainField.length = 0; // Clear the genesis-only chain
    for (const block of state.chain) {
      chainField.push(block);
    }
  }

  // Restore token system
  const tokenSystem = blockchain.getTokenSystem();
  tokenSystem.setTotalSupply(state.totalSupply);
  for (const [addr, bal] of Object.entries(state.balances)) {
    tokenSystem.setBalance(addr, bal);
  }
  // Restore max supply
  (tokenSystem as any).maxSupply = state.maxSupply;

  // Restore consensus (validators and votes)
  const consensus = blockchain.getConsensus();
  // Clear existing validators and re-register from state
  (consensus as any).validators.clear();
  (consensus as any).stakes = [];
  for (const v of state.validators) {
    consensus.registerValidator(v.publicKey, v.address);
    const validator = consensus.getValidators().get(v.address);
    if (validator) {
      validator.votes = v.votes;
      validator.isProducer = v.isProducer;
      validator.blocksProduced = v.blocksProduced;
      validator.totalRewards = v.totalRewards;
    }
  }
  // Restore vote stakes
  for (const vs of state.voteStakes) {
    (consensus as any).stakes.push(vs);
  }
  // Restore round turn
  (consensus as any).roundTurn = state.roundTurn || 0;

  // Restore mempool (need balances for validation)
  const mempool = blockchain.getMempool();
  const balances = tokenSystem.getBalancesMap();
  for (const tx of state.mempool) {
    mempool.addTransaction(tx, balances);
  }

  // Restore eco data (these are Maps)
  for (const cc of state.carbonCredits) {
    (ecoSystem as any).carbonCredits.set(cc.id, cc);
  }
  for (const rp of state.reforestationProjects) {
    (ecoSystem as any).reforestationProjects.set(rp.projectId, rp);
  }
  for (const gs of state.greenScores) {
    (ecoSystem as any).greenScores.set(gs.address, gs);
  }

  // Restore DEX pools (Map)
  for (const pool of state.pools) {
    (dex as any).pools.set(pool.id || pool.poolId, pool);
  }

  // Restore contracts (Map)
  for (const contract of state.contracts) {
    (contractManager as any).contracts.set(contract.id, contract);
  }

  console.log(`✅ State restored: ${state.chain.length} blocks, ${Object.keys(state.balances).length} balances, ${state.wallets.length} wallets, ${state.validators.length} validators, ${state.pools.length} DEX pools, ${state.contracts.length} contracts`);
}

/**
 * Periodically saves state at a given interval.
 */
export function startAutoSave(
  blockchain: Blockchain,
  walletManager: WalletManager,
  ecoSystem: EcoSystem,
  dex: DEX,
  contractManager: ContractManager,
  intervalMs: number = 30000,
  marketTracker?: any
): NodeJS.Timeout {
  console.log(`💾 Auto-save enabled (every ${intervalMs / 1000}s)`);
  return setInterval(() => {
    saveState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker);
  }, intervalMs);
}
