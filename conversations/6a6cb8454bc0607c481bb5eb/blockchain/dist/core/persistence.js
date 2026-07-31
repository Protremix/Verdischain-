"use strict";
/**
 * Persistence Layer for Verdis Blockchain
 *
 * Saves and restores the full blockchain state to/from disk,
 * allowing the chain to survive restarts with all data intact.
 *
 * State file: blobs/verdis-state.json
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.exportState = exportState;
exports.saveState = saveState;
exports.loadState = loadState;
exports.restoreState = restoreState;
exports.startAutoSave = startAutoSave;
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const STATE_FILE = path_1.default.join(process.cwd(), '..', 'blobs', 'verdis-state.json');
const STATE_DIR = path_1.default.dirname(STATE_FILE);
/**
 * Exports the full blockchain state to a serializable object.
 */
function exportState(blockchain, walletManager, ecoSystem, dex, contractManager) {
    const tokenSystem = blockchain.getTokenSystem();
    const consensus = blockchain.getConsensus();
    const mempool = blockchain.getMempool();
    // Export balances
    const balances = {};
    for (const [addr, bal] of tokenSystem.getBalancesMap()) {
        balances[addr] = bal;
    }
    // Export stakes (staking positions)
    const stakes = {};
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
        roundTurn: consensus.roundTurn || 0,
        mempool: mempoolTxs,
        wallets,
        carbonCredits,
        reforestationProjects,
        greenScores,
        pools,
        contracts,
    };
}
/**
 * Saves the full blockchain state to disk.
 */
function saveState(blockchain, walletManager, ecoSystem, dex, contractManager) {
    try {
        // Ensure directory exists
        if (!fs_1.default.existsSync(STATE_DIR)) {
            fs_1.default.mkdirSync(STATE_DIR, { recursive: true });
        }
        const state = exportState(blockchain, walletManager, ecoSystem, dex, contractManager);
        const json = JSON.stringify(state, null, 2);
        fs_1.default.writeFileSync(STATE_FILE, json);
        console.log(`💾 State saved: ${state.chain.length} blocks, ${Object.keys(state.balances).length} balances, ${state.wallets.length} wallets, ${state.contracts.length} contracts`);
        return true;
    }
    catch (error) {
        console.error('❌ Failed to save state:', error);
        return false;
    }
}
/**
 * Loads the blockchain state from disk and restores all systems.
 * Returns null if no state file exists.
 */
function loadState() {
    try {
        if (!fs_1.default.existsSync(STATE_FILE)) {
            return null;
        }
        const json = fs_1.default.readFileSync(STATE_FILE, 'utf-8');
        if (!json || json.trim() === '')
            return null;
        const state = JSON.parse(json);
        console.log(`📂 State file found: v${state.version}, saved ${new Date(state.timestamp).toISOString()}`);
        return state;
    }
    catch (error) {
        console.error('❌ Failed to load state:', error);
        return null;
    }
}
/**
 * Restores all blockchain systems from saved state.
 * Must be called before block production starts.
 */
function restoreState(state, blockchain, walletManager, ecoSystem, dex, contractManager) {
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
    tokenSystem.maxSupply = state.maxSupply;
    // Restore consensus (validators and votes)
    const consensus = blockchain.getConsensus();
    // Clear existing validators and re-register from state
    consensus.validators.clear();
    consensus.stakes = [];
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
        consensus.stakes.push(vs);
    }
    // Restore round turn
    consensus.roundTurn = state.roundTurn || 0;
    // Restore mempool (need balances for validation)
    const mempool = blockchain.getMempool();
    const balances = tokenSystem.getBalancesMap();
    for (const tx of state.mempool) {
        mempool.addTransaction(tx, balances);
    }
    // Restore eco data (these are Maps)
    for (const cc of state.carbonCredits) {
        ecoSystem.carbonCredits.set(cc.id, cc);
    }
    for (const rp of state.reforestationProjects) {
        ecoSystem.reforestationProjects.set(rp.projectId, rp);
    }
    for (const gs of state.greenScores) {
        ecoSystem.greenScores.set(gs.address, gs);
    }
    // Restore DEX pools (Map)
    for (const pool of state.pools) {
        dex.pools.set(pool.id || pool.poolId, pool);
    }
    // Restore contracts (Map)
    for (const contract of state.contracts) {
        contractManager.contracts.set(contract.id, contract);
    }
    console.log(`✅ State restored: ${state.chain.length} blocks, ${Object.keys(state.balances).length} balances, ${state.wallets.length} wallets, ${state.validators.length} validators, ${state.pools.length} DEX pools, ${state.contracts.length} contracts`);
}
/**
 * Periodically saves state at a given interval.
 */
function startAutoSave(blockchain, walletManager, ecoSystem, dex, contractManager, intervalMs = 30000) {
    console.log(`💾 Auto-save enabled (every ${intervalMs / 1000}s)`);
    return setInterval(() => {
        saveState(blockchain, walletManager, ecoSystem, dex, contractManager);
    }, intervalMs);
}
//# sourceMappingURL=persistence.js.map