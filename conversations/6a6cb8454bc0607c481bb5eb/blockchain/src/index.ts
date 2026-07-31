import fs from 'fs';
import path from 'path';
import { Blockchain } from './core/consensus';
import { ContractManager } from './core/vm';
import { BlockchainAPI } from './api/server';
import { WalletManager } from './wallet/wallet';
import { DEX } from './core/dex';
import { EcoSystem } from './core/eco';
import { loadState, restoreState, saveState, startAutoSave } from './core/persistence';

// === Initialize Core Systems ===
const blockchain = new Blockchain();
const contractManager = new ContractManager();
const walletManager = new WalletManager();
const dex = new DEX();
const ecoSystem = new EcoSystem();

// === Try to load persisted state ===
const savedState = loadState();

// === API Server ===
const PORT = 3200;
const apiServer = new BlockchainAPI(blockchain, walletManager, contractManager);
apiServer.setDEX(dex);
apiServer.setEco(ecoSystem);

// === Track validator wallets for auto-block production ===
const validatorWallets: Array<{ privateKey: string; publicKey: string; address: string }> = [];

if (savedState) {
  // === Restore from saved state ===
  console.log('📂 Restoring Verdis state from disk...\n');
  restoreState(savedState, blockchain, walletManager, ecoSystem, dex, contractManager);

  // Rebuild validatorWallets from restored wallets
  const consensus = blockchain.getConsensus();
  for (const val of consensus.getAllValidatorsList()) {
    const wallet = walletManager.getWallet(val.address);
    if (wallet) {
      validatorWallets.push({
        privateKey: wallet.privateKey,
        publicKey: wallet.publicKey,
        address: wallet.address,
      });
    }
  }

  console.log('\n╔══════════════════════════════════════════════════╗');
  console.log('║         🌿 Verdis Network Restored               ║');
  console.log('╠══════════════════════════════════════════════════╣');
  console.log(`║  Chain Height:   ${blockchain.getChainHeight()}`);
  console.log(`║  Total Supply:   ${blockchain.getTokenSystem().getTotalSupply().toLocaleString()} VRS`);
  console.log(`║  Validators:     ${consensus.getAllValidatorsList().length}`);
  console.log(`║  Wallets:        ${walletManager.getAllWallets().length}`);
  console.log(`║  DEX Pools:      ${dex.getAllPools().length}`);
  console.log(`║  Contracts:      ${contractManager.getContracts().length}`);
  console.log('╚══════════════════════════════════════════════════╝\n');
} else {
  // === Bootstrap fresh chain with 5 genesis validators ===
  console.log('⚡ Bootstrapping fresh Verdis network...');

  const consensus = blockchain.getConsensus();
  const tokenSystem = blockchain.getTokenSystem();

  const GENESIS_PER_VALIDATOR = 10_000_000_000; // 10 billion VRS each (50B total from 100B max)
  const STAKE_PER_VALIDATOR = 1_000_000_000;    // 1 billion VRS staked per validator

  const energySources = ['solar', 'wind', 'hydro', 'geothermal', 'solar'];

  for (let i = 1; i <= 5; i++) {
    const wallet = walletManager.createWallet();
    blockchain.addGenesisAllocation(wallet.address, GENESIS_PER_VALIDATOR);
    wallet.balance = GENESIS_PER_VALIDATOR;
    consensus.registerValidator(wallet.publicKey, wallet.address);
    tokenSystem.stake(wallet.address, STAKE_PER_VALIDATOR);
    wallet.staked = STAKE_PER_VALIDATOR;
    wallet.balance -= STAKE_PER_VALIDATOR;
    consensus.vote(wallet.address, wallet.address, STAKE_PER_VALIDATOR, tokenSystem);
    ecoSystem.registerGreenValidator(wallet.address, energySources[i - 1]);

    validatorWallets.push({
      privateKey: wallet.privateKey,
      publicKey: wallet.publicKey,
      address: wallet.address,
    });

    console.log(`  Validator #${i}: ${wallet.address.slice(0, 16)}... | Energy: ${energySources[i - 1]}`);
  }

  console.log('\n╔══════════════════════════════════════════════════╗');
  console.log('║         🌿 Verdis Network Bootstrapped            ║');
  console.log('╠══════════════════════════════════════════════════╣');
  console.log(`║  Total Supply:    ${tokenSystem.getTotalSupply().toLocaleString()} VRS`);
  console.log(`║  Max Supply:      ${tokenSystem.getMaxSupply().toLocaleString()} VRS`);
  console.log(`║  Validators:      ${consensus.getAllValidatorsList().length}`);
  console.log(`║  Green Validators: ${ecoSystem.getTopGreenValidators(5).length}`);
  console.log('╚══════════════════════════════════════════════════╝\n');

  // Save initial state
  saveState(blockchain, walletManager, ecoSystem, dex, contractManager);
}

// === Auto Block Production ===
const consensus = blockchain.getConsensus();
const BLOCK_INTERVAL_MS = 5000;
let autoBlockCount = 0;

function autoProduceBlock(): void {
  const producer = consensus.getCurrentProducer();
  if (!producer) return;

  const wallet = validatorWallets.find(w => w.address === producer.address);
  if (!wallet) return;

  const block = blockchain.produceBlock(wallet.privateKey, wallet.publicKey, wallet.address);
  if (block) {
    autoBlockCount++;
    const txCount = block.transactions.length;
    console.log(`📦 Block #${block.header.index} produced by ${producer.address.slice(0, 12)}... | ${txCount} txs | auto-block #${autoBlockCount}`);
    // Save state after each block
    saveState(blockchain, walletManager, ecoSystem, dex, contractManager);
  }
  consensus.rotateProducer();
}

console.log(`🤖 Auto-block production enabled (every ${BLOCK_INTERVAL_MS / 1000}s)`);
setInterval(autoProduceBlock, BLOCK_INTERVAL_MS);

// === Auto-save state every 30 seconds ===
startAutoSave(blockchain, walletManager, ecoSystem, dex, contractManager, 30000);

// === Serve Dashboard ===
const dashboardPath = path.resolve(__dirname, 'web/dashboard.html');
if (fs.existsSync(dashboardPath)) {
  apiServer.serveDashboard(dashboardPath);
} else {
  const altPath = path.resolve(__dirname, '../src/web/dashboard.html');
  if (fs.existsSync(altPath)) {
    apiServer.serveDashboard(altPath);
  }
}

// === Start the node ===
apiServer.start(PORT);

console.log('🚀 Verdis is running at http://localhost:3200');
console.log('📡 Trust Wallet RPC: http://localhost:3200/rpc (Chain ID 909)');
console.log('\n💡 Try these commands:');
console.log('   curl http://localhost:3200/api/blockchain/info');
console.log('   curl http://localhost:3200/api/validators');
console.log('   curl http://localhost:3200/api/eco/impact');
console.log('   curl -X POST http://localhost:3200/api/wallet/create');
console.log('   curl http://localhost:3200/api/dex/pools');
console.log('   curl -X POST http://localhost:3200/rpc -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}\'');
console.log('');

export { blockchain, contractManager, walletManager, dex, ecoSystem, apiServer };
