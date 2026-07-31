import fs from 'fs';
import path from 'path';
import { Blockchain } from './core/consensus';
import { ContractManager } from './core/vm';
import { BlockchainAPI } from './api/server';
import { WalletManager } from './wallet/wallet';
import { DEX } from './core/dex';
import { EcoSystem } from './core/eco';

// === Initialize Core Systems ===
const blockchain = new Blockchain();
const contractManager = new ContractManager();
const walletManager = new WalletManager();
const dex = new DEX();
const ecoSystem = new EcoSystem();

// === API Server ===
const PORT = 3000;
const apiServer = new BlockchainAPI(blockchain, walletManager, contractManager);
apiServer.setDEX(dex);
apiServer.setEco(ecoSystem);

// === Bootstrap: Set up 5 genesis validators ===
console.log('⚡ Bootstrapping Verdis network...');

const consensus = blockchain.getConsensus();
const tokenSystem = blockchain.getTokenSystem();

const GENESIS_PER_VALIDATOR = 10_000_000_000; // 10 billion VRS each (50B total from 100B max)
const STAKE_PER_VALIDATOR = 1_000_000_000;    // 1 billion VRS staked per validator

const validatorsList: Array<{
  index: number;
  address: string;
  publicKey: string;
  balance: number;
  staked: number;
}> = [];

const energySources = ['solar', 'wind', 'hydro', 'geothermal', 'solar'];

for (let i = 1; i <= 5; i++) {
  // a. Create validator wallet
  const wallet = walletManager.createWallet();

  // b. Allocate genesis tokens
  blockchain.addGenesisAllocation(wallet.address, GENESIS_PER_VALIDATOR);
  wallet.balance = GENESIS_PER_VALIDATOR;

  // c. Register as validator
  consensus.registerValidator(wallet.publicKey, wallet.address);

  // d. Stake tokens and vote for self
  tokenSystem.stake(wallet.address, STAKE_PER_VALIDATOR);
  wallet.staked = STAKE_PER_VALIDATOR;
  wallet.balance -= STAKE_PER_VALIDATOR;
  consensus.vote(wallet.address, wallet.address, STAKE_PER_VALIDATOR, tokenSystem);

  // e. Register as green validator with eco system
  ecoSystem.registerGreenValidator(wallet.address, energySources[i - 1]);

  validatorsList.push({
    index: i,
    address: wallet.address,
    publicKey: wallet.publicKey,
    balance: wallet.balance,
    staked: wallet.staked,
  });
}

// === Log bootstrap info ===
console.log('\n╔══════════════════════════════════════════════════╗');
console.log('║         🌿 Verdis Network Bootstrapped            ║');
console.log('╠══════════════════════════════════════════════════╣');
validatorsList.forEach((v) => {
  console.log(`║  Validator #${v.index}: ${v.address.slice(0, 16)}...`);
  console.log(`║    Balance: ${v.balance.toLocaleString()} VRS`);
  console.log(`║    Staked:  ${v.staked.toLocaleString()} VRS`);
  console.log(`║    Energy:  ${energySources[v.index - 1]}`);
});
console.log('╠══════════════════════════════════════════════════╣');
console.log(`║  Total Supply:    ${tokenSystem.getTotalSupply().toLocaleString()} VRS`);
console.log(`║  Max Supply:      ${tokenSystem.getMaxSupply().toLocaleString()} VRS`);
console.log(`║  Validators:      ${consensus.getAllValidatorsList().length}`);
console.log(`║  Green Validators: ${ecoSystem.getTopGreenValidators(5).length}`);
console.log('╚══════════════════════════════════════════════════╝\n');

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

console.log('🚀 Verdis is running at http://localhost:3000');
console.log('\n💡 Try these commands:');
console.log('   curl http://localhost:3000/api/blockchain/info');
console.log('   curl http://localhost:3000/api/validators');
console.log('   curl http://localhost:3000/api/eco/impact');
console.log('   curl -X POST http://localhost:3000/api/wallet/create');
console.log('   curl http://localhost:3000/api/dex/pools');
console.log('');

export { blockchain, contractManager, walletManager, dex, ecoSystem, apiServer };
