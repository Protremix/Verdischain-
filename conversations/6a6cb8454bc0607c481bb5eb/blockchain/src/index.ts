import fs from 'fs';
import path from 'path';
import { Blockchain } from './core/consensus';
import { ContractManager } from './core/vm';
import { BlockchainAPI } from './api/server';
import { WalletManager } from './wallet/wallet';
import { DEX } from './core/dex';
import { EcoSystem } from './core/eco';
import { MarketTracker } from './core/market';
import { loadState, restoreState, saveState, startAutoSave } from './core/persistence';

// === Initialize Core Systems ===
const blockchain = new Blockchain();
const contractManager = new ContractManager();
const walletManager = new WalletManager();
const dex = new DEX();
const ecoSystem = new EcoSystem();
const marketTracker = new MarketTracker(dex);

// === Try to load persisted state ===
const savedState = loadState();

// === API Server ===
const PORT = 3200;
const apiServer = new BlockchainAPI(blockchain, walletManager, contractManager);
apiServer.setDEX(dex);
apiServer.setEco(ecoSystem);
apiServer.setMarketTracker(marketTracker);

// === Track validator wallets for auto-block production ===
const validatorWallets: Array<{ privateKey: string; publicKey: string; address: string }> = [];

if (savedState) {
  // === Restore from saved state ===
  console.log('📂 Restoring Verdis state from disk...\n');
  restoreState(savedState, blockchain, walletManager, ecoSystem, dex, contractManager);

  // Restore market data
  if (savedState.marketData) {
    marketTracker.importData(savedState.marketData);
  }

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
  console.log(`║  Total Supply:   ${blockchain.getTokenSystem().getTotalSupply().toLocaleString()} VCO`);
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

  const GENESIS_PER_VALIDATOR = 10_000_000_000; // 10 billion VCO each (50B total from 100B max)
  const STAKE_PER_VALIDATOR = 1_000_000_000;    // 1 billion VCO staked per validator

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
  console.log(`║  Total Supply:    ${tokenSystem.getTotalSupply().toLocaleString()} VCO`);
  console.log(`║  Max Supply:      ${tokenSystem.getMaxSupply().toLocaleString()} VCO`);
  console.log(`║  Validators:      ${consensus.getAllValidatorsList().length}`);
  console.log(`║  Green Validators: ${ecoSystem.getTopGreenValidators(5).length}`);
  console.log('╚══════════════════════════════════════════════════╝\n');

  // === Bootstrap DEX Liquidity Pools ===
  console.log('💱 Bootstrapping DEX liquidity pools...\n');

  const w1 = validatorWallets[0];
  const w2 = validatorWallets[1];
  const w3 = validatorWallets[2];

  // Mint CARBON tokens to wallets for liquidity
  dex.depositToken('CARBON', w1.address, 2_000_000);
  dex.depositToken('CARBON', w2.address, 2_000_000);
  console.log(`  Minted 4,000,000 CARBON tokens`);

  // Mint ECO tokens (governance/eco-rewards token)
  dex.depositToken('ECO', w2.address, 4_000_000);
  dex.depositToken('ECO', w3.address, 4_000_000);
  console.log(`  Minted 8,000,000 ECO tokens`);

  // Create VCO/CARBON pool — initial price: 1 VCO = 0.5 CARBON
  dex.createPool('VCO', 'CARBON');
  dex.addLiquidity(w1.address, 'VCO', 'CARBON', 2_000_000, 1_000_000);
  console.log(`  Pool VCO/CARBON: 2M VCO / 1M CARBON | Price: 1 VCO = 0.5 CARBON`);

  // Create VCO/ECO pool — initial price: 1 VCO = 2 ECO
  dex.createPool('VCO', 'ECO');
  dex.addLiquidity(w2.address, 'VCO', 'ECO', 1_000_000, 2_000_000);
  console.log(`  Pool VCO/ECO: 1M VCO / 2M ECO | Price: 1 VCO = 2 ECO`);

  // Create CARBON/ECO pool
  dex.createPool('CARBON', 'ECO');
  dex.addLiquidity(w3.address, 'CARBON', 'ECO', 500_000, 1_000_000);
  console.log(`  Pool CARBON/ECO: 500K CARBON / 1M ECO | Price: 1 CARBON = 2 ECO`);

  console.log(`\n  Total TVL: 3 pools | 5M+ tokens locked`);

  // === Execute initial trades to establish market ===
  console.log('\n📈 Executing initial market trades...\n');

  const trades = [
    { trader: w2.address, tokenIn: 'CARBON', tokenOut: 'VCO', amountIn: 50_000, label: '50K CARBON → VCO' },
    { trader: w1.address, tokenIn: 'CARBON', tokenOut: 'VCO', amountIn: 30_000, label: '30K CARBON → VCO' },
    { trader: w3.address, tokenIn: 'ECO', tokenOut: 'CARBON', amountIn: 100_000, label: '100K ECO → CARBON' },
    { trader: w2.address, tokenIn: 'ECO', tokenOut: 'VCO', amountIn: 80_000, label: '80K ECO → VCO' },
    { trader: w1.address, tokenIn: 'CARBON', tokenOut: 'VCO', amountIn: 20_000, label: '20K CARBON → VCO' },
    { trader: w3.address, tokenIn: 'ECO', tokenOut: 'CARBON', amountIn: 50_000, label: '50K ECO → CARBON' },
    { trader: w2.address, tokenIn: 'CARBON', tokenOut: 'VCO', amountIn: 10_000, label: '10K CARBON → VCO' },
    { trader: w1.address, tokenIn: 'CARBON', tokenOut: 'VCO', amountIn: 5_000, label: '5K CARBON → VCO' },
  ];

  for (let i = 0; i < trades.length; i++) {
    const t = trades[i];
    try {
      const result = dex.swap(t.trader, t.tokenIn, t.tokenOut, t.amountIn, 0);
      marketTracker.recordSwap(t.trader, t.tokenIn, t.tokenOut, t.amountIn, result.amountOut, result.fee, result.pool.id, 1);
      console.log(`  Trade #${i + 1}: ${t.label} → ${result.amountOut.toFixed(2)} ${t.tokenOut} | Fee: ${result.fee.toFixed(1)}`);
    } catch (e) {
      console.log(`  Trade #${i + 1}: ${t.label} → FAILED: ${(e as Error).message}`);
    }
  }

  // Record initial prices
  marketTracker.recordPrices(blockchain.getChainHeight());

  const allPools = dex.getAllPools();
  console.log(`\n  ✅ ${trades.length} trades executed | ${allPools.length} pools active`);
  console.log('  📊 Live Market Data:');
  for (const p of allPools) {
    const price = p.reserveA > 0 ? p.reserveB / p.reserveA : 0;
    console.log(`    ${p.tokenA}/${p.tokenB}: ${p.reserveA.toLocaleString()} / ${p.reserveB.toLocaleString()} | Price: ${price.toFixed(6)}`);
  }
  console.log('');

  // Save initial state
  saveState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker);
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
    saveState(blockchain, walletManager, ecoSystem, dex, contractManager, marketTracker);
    // Record prices every 5 blocks for market tracking
    if (autoBlockCount % 5 === 0) {
      marketTracker.recordPrices(block.header.index);
    }
  }
  consensus.rotateProducer();
}

console.log(`🤖 Auto-block production enabled (every ${BLOCK_INTERVAL_MS / 1000}s)`);
setInterval(autoProduceBlock, BLOCK_INTERVAL_MS);

// === Auto-save state every 30 seconds ===
startAutoSave(blockchain, walletManager, ecoSystem, dex, contractManager, 30000, marketTracker);

// === Auto-trade bot: keeps DEX active with periodic swaps ===
let tradeBotCount = 0;
function autoTradeBot(): void {
  if (validatorWallets.length < 3) return;
  const pools = dex.getAllPools();
  if (pools.length === 0) return;

  // Pick a random pool and trader
  const pool = pools[Math.floor(Math.random() * pools.length)];
  const trader = validatorWallets[Math.floor(Math.random() * validatorWallets.length)];

  // Small random swap (0.01% - 0.1% of pool reserve)
  const swapAmount = Math.floor(pool.reserveA * (0.0001 + Math.random() * 0.0009));
  if (swapAmount < 1) return;

  // Randomly pick direction
  const buyA = Math.random() > 0.5;
  const tokenIn = buyA ? pool.tokenB : pool.tokenA;
  const tokenOut = buyA ? pool.tokenA : pool.tokenB;
  const amountIn = Math.floor(swapAmount * (buyA ? (pool.reserveA / Math.max(pool.reserveB, 1)) : 1));

  if (amountIn < 1) return;

  try {
    const result = dex.swap(trader.address, tokenIn, tokenOut, amountIn, 0);
    marketTracker.recordSwap(trader.address, tokenIn, tokenOut, amountIn, result.amountOut, result.fee, result.pool.id, blockchain.getChainHeight());
    tradeBotCount++;
    console.log(`🤖 Auto-trade #${tradeBotCount}: ${amountIn} ${tokenIn} → ${result.amountOut.toFixed(2)} ${tokenOut}`);
  } catch (e) {
    // Swap failed (insufficient balance, etc) - skip silently
  }
}

// Run trade bot every 10 seconds
console.log('🤖 Auto-trade bot enabled (swaps every 10s)');
setInterval(autoTradeBot, 10000);

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
console.log('💱 Live DEX: VCO/CARBON, VCO/ECO, CARBON/ECO pools active');
console.log('📊 Token market data: http://localhost:3200/api/token/market');
console.log('\n💡 Try these commands:');
console.log('   curl http://localhost:3200/api/blockchain/info');
console.log('   curl http://localhost:3200/api/token/market');
console.log('   curl http://localhost:3200/api/dex/pools');
console.log('   curl http://localhost:3200/api/token/info');
console.log('');

export { blockchain, contractManager, walletManager, dex, ecoSystem, marketTracker, apiServer };
