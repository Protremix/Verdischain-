/**
 * MarketTracker Test Suite
 * 
 * Tests all MarketTracker functionality:
 * - Swap recording & history
 * - Price point tracking
 * - Market stats (price, volume, TVL, market cap, 24h change)
 * - Pool stats
 * - Data export/import (persistence)
 * - Edge cases
 * - Live API integration
 */

import { MarketTracker } from '../src/core/market';
import { DEX } from '../src/core/dex';

// Test framework
let passed = 0;
let failed = 0;
const failures: string[] = [];

function assert(condition: boolean, msg: string) {
  if (condition) {
    passed++;
    console.log(`  ✅ ${msg}`);
  } else {
    failed++;
    failures.push(msg);
    console.log(`  ❌ ${msg}`);
  }
}

function assertApprox(val: number, expected: number, tolerance: number, msg: string) {
  const diff = Math.abs(val - expected);
  assert(diff <= tolerance, `${msg} (got ${val}, expected ~${expected}, diff ${diff})`);
}

function section(name: string) {
  console.log(`\n── ${name} ──`);
}

async function main() {
  console.log('╔══════════════════════════════════════════╗');
  console.log('║  MarketTracker Test Suite                ║');
  console.log('╚══════════════════════════════════════════╝');

  // ── Setup ──
  section('Setup: Fresh DEX + MarketTracker');
  const dex = new DEX();
  const tracker = new MarketTracker(dex);
  assert(tracker !== null, 'MarketTracker instantiated');
  assert(tracker.getSwapHistory().length === 0, 'Empty swap history on init');
  assert(tracker.getPriceHistory('TEST').length === 0, 'Empty price history on init');

  // Create pools and mint tokens
  dex.depositToken('CARBON', '0xwallet1', 1_000_000);
  dex.depositToken('ECO', '0xwallet2', 2_000_000);
  dex.createPool('VRS', 'CARBON');
  dex.createPool('VRS', 'ECO');
  
  const liq1 = dex.addLiquidity('0xwallet1', 'VRS', 'CARBON', 100_000, 50_000);
  assert(liq1.lpTokens > 0, 'Liquidity added to VRS/CARBON pool');
  
  const liq2 = dex.addLiquidity('0xwallet2', 'VRS', 'ECO', 200_000, 400_000);
  assert(liq2.lpTokens > 0, 'Liquidity added to VRS/ECO pool');

  // ── Test 1: recordSwap ──
  section('Test 1: recordSwap');
  
  // Execute a real swap
  const swap1 = dex.swap('0xwallet1', 'CARBON', 'VRS', 10_000, 0);
  assert(swap1.amountOut > 0, 'Swap executed successfully');
  
  tracker.recordSwap(
    '0xwallet1', 'CARBON', 'VRS', 10_000, swap1.amountOut,
    swap1.fee, swap1.pool.id, 1
  );
  
  const history = tracker.getSwapHistory();
  assert(history.length === 1, 'Swap recorded in history');
  assert(history[0].trader === '0xwallet1', 'Swap trader recorded correctly');
  assert(history[0].tokenIn === 'CARBON', 'Swap tokenIn recorded correctly');
  assert(history[0].tokenOut === 'VRS', 'Swap tokenOut recorded correctly');
  assert(history[0].amountIn === 10_000, 'Swap amountIn recorded correctly');
  assertApprox(history[0].amountOut, swap1.amountOut, 0.01, 'Swap amountOut recorded correctly');
  assert(history[0].fee === swap1.fee, 'Swap fee recorded correctly');
  assert(history[0].poolId === swap1.pool.id, 'Swap poolId recorded correctly');
  assert(history[0].blockNumber === 1, 'Swap blockNumber recorded correctly');

  // ── Test 2: Multiple swaps ──
  section('Test 2: Multiple swaps & volume tracking');
  
  // Mint more CARBON for additional swaps
  dex.depositToken('CARBON', '0xwallet3', 100_000);
  
  for (let i = 2; i <= 5; i++) {
    const swap = dex.swap('0xwallet3', 'CARBON', 'VRS', 5_000, 0);
    tracker.recordSwap('0xwallet3', 'CARBON', 'VRS', 5_000, swap.amountOut, swap.fee, swap.pool.id, i);
  }
  
  assert(tracker.getSwapHistory().length === 5, '5 swaps recorded after multiple trades');
  
  const stats1 = tracker.getMarketStats('VRS', 50_000_000_000, 100_000_000_000);
  assert(stats1.totalSwaps === 5, 'Total swap count = 5');
  assert(stats1.totalVolume === 10_000 + 4 * 5_000, 'Total volume = 30,000');
  assert(stats1.volume24h === 30_000, '24h volume = 30,000 (all within 24h)');

  // ── Test 3: Price tracking ──
  section('Test 3: Price point tracking');
  
  const priceHistory = tracker.getPriceHistory(swap1.pool.id);
  assert(priceHistory.length > 0, 'Price history has entries after swaps');
  assert(priceHistory[0].price > 0, 'Price point is positive');
  assert(priceHistory[0].poolId === swap1.pool.id, 'Price point poolId correct');
  assert(priceHistory[0].pair.includes('VRS'), 'Price point pair contains VRS');

  // ── Test 4: Market stats calculation ──
  section('Test 4: Market stats calculation');
  
  const stats = tracker.getMarketStats('VRS', 50_000_000_000, 100_000_000_000);
  
  assert(stats.symbol === 'VRS', 'Stats symbol = VRS');
  assert(stats.priceUSD > 0, 'Price is positive');
  assert(stats.marketCap > 0, 'Market cap is positive');
  assertApprox(stats.marketCap, stats.priceUSD * 50_000_000_000, 1, 'Market cap = price * supply');
  assert(stats.circulatingSupply === 50_000_000_000, 'Circulating supply correct');
  assert(stats.totalVolume === 30_000, 'Total volume = 30,000');
  assert(stats.totalSwaps === 5, 'Total swaps = 5');
  assert(stats.liquidity > 0, 'Total liquidity is positive');
  assert(stats.pools.length === 2, '2 pools in stats');
  assert(stats.recentSwaps.length <= 20, 'Recent swaps capped at 20');

  // ── Test 5: Pool stats ──
  section('Test 5: Pool stats');
  
  const vrsCarbonPool = stats.pools.find(p => p.pair.includes('VRS') && p.pair.includes('CARBON'));
  assert(vrsCarbonPool !== undefined, 'VRS/CARBON pool found in stats');
  assert(vrsCarbonPool!.price > 0, 'Pool price is positive');
  assert(vrsCarbonPool!.tvl > 0, 'Pool TVL is positive');
  assert(vrsCarbonPool!.reserves.tokenA !== undefined, 'Pool reserves tokenA present');
  assert(vrsCarbonPool!.reserves.tokenB !== undefined, 'Pool reserves tokenB present');
  assert(vrsCarbonPool!.reserves.reserveA > 0, 'Pool reserveA > 0');
  assert(vrsCarbonPool!.reserves.reserveB > 0, 'Pool reserveB > 0');
  
  // Swaps in VRS/CARBON pool
  assert(vrsCarbonPool!.swaps24h === 5, 'VRS/CARBON pool has 5 swaps in 24h');
  assert(vrsCarbonPool!.volume24h === 30_000, 'VRS/CARBON pool volume = 30,000');

  // VRS/ECO pool should have 0 swaps
  const vrsEcoPool = stats.pools.find(p => p.pair.includes('VRS') && p.pair.includes('ECO'));
  assert(vrsEcoPool !== undefined, 'VRS/ECO pool found in stats');
  assert(vrsEcoPool!.swaps24h === 0, 'VRS/ECO pool has 0 swaps');
  assert(vrsEcoPool!.volume24h === 0, 'VRS/ECO pool volume = 0');

  // ── Test 6: Price change calculation ──
  section('Test 6: 24h price change');
  
  assert(typeof stats.priceChange24h === 'number', 'Price change is a number');
  assert(!isNaN(stats.priceChange24h), 'Price change is not NaN');
  assert(isFinite(stats.priceChange24h), 'Price change is finite');
  console.log(`    (priceChange24h = ${stats.priceChange24h.toFixed(4)}%)`);

  // ── Test 7: recordPrices (snapshot) ──
  section('Test 7: Price snapshot recording');
  
  const allPools = dex.getAllPools();
  tracker.recordPrices(10);
  
  for (const p of allPools) {
    const ph = tracker.getPriceHistory(p.id);
    assert(ph.length > 0, `Price snapshot exists for pool ${p.id}`);
  }

  // ── Test 8: Swap history limits ──
  section('Test 8: Swap history limits');
  
  // Record many swaps to test the 1000 limit
  for (let i = 0; i < 50; i++) {
    const w = i % 2 === 0 ? '0xwallet1' : '0xwallet3';
    try {
      const swap = dex.swap(w, 'CARBON', 'VRS', 100, 0);
      tracker.recordSwap(w, 'CARBON', 'VRS', 100, swap.amountOut, swap.fee, swap.pool.id, 100 + i);
    } catch (e) {
      break;
    }
  }
  
  const fullHistory = tracker.getSwapHistory();
  assert(fullHistory.length <= 1000, `Swap history capped at 1000 (got ${fullHistory.length})`);
  
  const limitedHistory = tracker.getSwapHistory(10);
  assert(limitedHistory.length === 10, 'getSwapHistory(10) returns 10 records');
  
  const allHistory = tracker.getSwapHistory(1000);
  assert(allHistory.length === fullHistory.length, 'getSwapHistory(1000) returns all');

  // ── Test 9: Data export/import ──
  section('Test 9: Data export/import (persistence)');
  
  const exported = tracker.exportData();
  assert(exported.swapHistory !== undefined, 'Export contains swapHistory');
  assert(exported.priceHistory !== undefined, 'Export contains priceHistory');
  assert(exported.totalVolumeAllTime !== undefined, 'Export contains totalVolumeAllTime');
  assert(exported.totalSwapCount !== undefined, 'Export contains totalSwapCount');
  assert(exported.swapHistory.length > 0, 'Exported swapHistory is non-empty');
  assert(exported.priceHistory.length > 0, 'Exported priceHistory is non-empty');
  
  const tracker2 = new MarketTracker(dex);
  assert(tracker2.getSwapHistory().length === 0, 'New tracker starts empty');
  
  tracker2.importData(exported);
  assert(tracker2.getSwapHistory().length > 0, 'Imported swap history');
  assert(tracker2.getSwapHistory().length === exported.swapHistory.length, 'Imported history matches export');
  
  const stats2 = tracker2.getMarketStats('VRS', 50_000_000_000, 100_000_000_000);
  assert(stats2.totalSwaps === exported.totalSwapCount, 'Imported totalSwapCount matches');
  assert(stats2.totalVolume === exported.totalVolumeAllTime, 'Imported totalVolume matches');

  // ── Test 10: Edge cases ──
  section('Test 10: Edge cases');
  
  const emptyDex = new DEX();
  const emptyTracker = new MarketTracker(emptyDex);
  const emptyStats = emptyTracker.getMarketStats('VRS', 50_000_000_000, 100_000_000_000);
  assert(emptyStats.priceUSD === 0, 'Empty tracker price = 0');
  assert(emptyStats.totalSwaps === 0, 'Empty tracker swaps = 0');
  assert(emptyStats.totalVolume === 0, 'Empty tracker volume = 0');
  assert(emptyStats.liquidity === 0, 'Empty tracker liquidity = 0');
  assert(emptyStats.pools.length === 0, 'Empty tracker pools = []');
  assert(emptyStats.recentSwaps.length === 0, 'Empty tracker recentSwaps = []');
  assert(emptyStats.priceHistory.length === 0, 'Empty tracker priceHistory = []');
  
  // Pool with zero reserves (created but no liquidity)
  emptyDex.createPool('VRS', 'CARBON');
  const zeroPoolStats = emptyTracker.getMarketStats('VRS', 1_000_000, 2_000_000);
  assert(zeroPoolStats.pools.length === 1, 'Pool with no liquidity still listed');
  assert(zeroPoolStats.pools[0].price === 0, 'Empty pool price = 0');
  assert(zeroPoolStats.pools[0].tvl === 0, 'Empty pool TVL = 0');

  // ── Test 11: Export trims to 200 records ──
  section('Test 11: Export trims to last 200 records');
  
  assert(exported.swapHistory.length <= 200, `Exported swapHistory trimmed to 200 (got ${exported.swapHistory.length})`);
  assert(exported.priceHistory.length <= 200, `Exported priceHistory trimmed to 200 (got ${exported.priceHistory.length})`);

  // ── Test 12: Price history filtering by pool ──
  section('Test 12: Price history filtering by pool');
  
  const pool1Id = allPools[0].id;
  const ph1 = tracker.getPriceHistory(pool1Id);
  
  for (const p of ph1) {
    assert(p.poolId === pool1Id, `Price history entry poolId matches (${pool1Id})`);
    break;
  }
  
  const phantomHistory = tracker.getPriceHistory('NONEXISTENT_POOL');
  assert(phantomHistory.length === 0, 'Non-existent pool price history is empty');

  // ── Live API Integration Tests ──
  section('Test 13: Live API integration');
  
  const API = 'http://localhost:3200';
  
  try {
    const marketRes = await fetch(`${API}/api/token/market`);
    assert(marketRes.ok, 'GET /api/token/market returns 200');
    const market = await marketRes.json();
    assert(market.symbol !== undefined, 'Market response has symbol');
    assert(typeof market.priceUSD === 'number', 'Market response has priceUSD');
    assert(typeof market.totalSwaps === 'number', 'Market response has totalSwaps');
    assert(typeof market.totalVolume === 'number', 'Market response has totalVolume');
    assert(Array.isArray(market.pools), 'Market response has pools array');
    assert(Array.isArray(market.recentSwaps), 'Market response has recentSwaps array');
    assert(Array.isArray(market.priceHistory), 'Market response has priceHistory array');
    assert(typeof market.marketCap === 'number', 'Market response has marketCap');
    assert(typeof market.liquidity === 'number', 'Market response has liquidity');
    assert(typeof market.priceChange24h === 'number', 'Market response has priceChange24h');
    assert(typeof market.volume24h === 'number', 'Market response has volume24h');
    assert(typeof market.circulatingSupply === 'number', 'Market response has circulatingSupply');
  } catch (e: any) {
    assert(false, `Live API /api/token/market failed: ${e.message}`);
  }
  
  try {
    const infoRes = await fetch(`${API}/api/token/info`);
    assert(infoRes.ok, 'GET /api/token/info returns 200');
    const info = await infoRes.json();
    assert(info.symbol === 'VRS', 'Token info symbol = VRS');
    assert(info.name === 'Verdis', 'Token info name = Verdis');
    assert(typeof info.totalSupply === 'number', 'Token info has totalSupply');
    assert(typeof info.maxSupply === 'number', 'Token info has maxSupply');
    assert(typeof info.price === 'number', 'Token info has price');
    assert(Array.isArray(info.pools), 'Token info has pools array');
  } catch (e: any) {
    assert(false, `Live API /api/token/info failed: ${e.message}`);
  }
  
  try {
    const swapsRes = await fetch(`${API}/api/token/swaps?limit=5`);
    assert(swapsRes.ok, 'GET /api/token/swaps returns 200');
    const swaps = await swapsRes.json();
    assert(Array.isArray(swaps), 'Swaps response is an array');
    assert(swaps.length <= 5, 'Swaps response respects limit=5');
    
    if (swaps.length > 0) {
      const s = swaps[0];
      assert(typeof s.trader === 'string', 'Swap record has trader');
      assert(typeof s.tokenIn === 'string', 'Swap record has tokenIn');
      assert(typeof s.tokenOut === 'string', 'Swap record has tokenOut');
      assert(typeof s.amountIn === 'number', 'Swap record has amountIn');
      assert(typeof s.amountOut === 'number', 'Swap record has amountOut');
      assert(typeof s.fee === 'number', 'Swap record has fee');
      assert(typeof s.blockNumber === 'number', 'Swap record has blockNumber');
      assert(typeof s.poolId === 'string', 'Swap record has poolId');
    }
  } catch (e: any) {
    assert(false, `Live API /api/token/swaps failed: ${e.message}`);
  }
  
  try {
    const poolsRes = await fetch(`${API}/api/dex/pools`);
    const pools = await poolsRes.json();
    if (pools.length > 0) {
      const poolId = pools[0].id;
      const priceRes = await fetch(`${API}/api/token/price-history/${poolId}`);
      assert(priceRes.ok, 'GET /api/token/price-history/:poolId returns 200');
      const priceHistory = await priceRes.json();
      assert(Array.isArray(priceHistory), 'Price history is an array');
      
      if (priceHistory.length > 0) {
        const p = priceHistory[0];
        assert(typeof p.price === 'number', 'Price point has price');
        assert(typeof p.blockNumber === 'number', 'Price point has blockNumber');
        assert(typeof p.pair === 'string', 'Price point has pair');
        assert(p.poolId === poolId, 'Price point poolId matches request');
      }
    }
  } catch (e: any) {
    assert(false, `Live API /api/token/price-history failed: ${e.message}`);
  }
  
  // Test: Execute swap via API and verify it shows up in market data
  try {
    const walletsRes = await fetch(`${API}/api/wallets`);
    const wallets = await walletsRes.json();
    const trader = wallets[0].address;
    
    await fetch(`${API}/api/dex/token/mint`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: 'CARBON', address: trader, amount: 100_000 })
    });
    
    const marketBefore = await (await fetch(`${API}/api/token/market`)).json();
    const swapsBefore = marketBefore.totalSwaps;
    
    const swapRes = await fetch(`${API}/api/dex/swap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ trader, tokenIn: 'CARBON', tokenOut: 'VRS', amountIn: 500, minAmountOut: 0 })
    });
    const swapResult = await swapRes.json();
    assert(swapResult.success !== false, 'API swap executed');
    
    await new Promise(r => setTimeout(r, 500));
    
    const marketAfter = await (await fetch(`${API}/api/token/market`)).json();
    const swapsAfter = marketAfter.totalSwaps;
    assert(swapsAfter > swapsBefore, `Swap count increased (${swapsBefore} -> ${swapsAfter})`);
    
    const recentSwaps = marketAfter.recentSwaps;
    const found = recentSwaps.some((s: any) => 
      s.trader === trader && s.tokenIn === 'CARBON' && s.amountIn === 500
    );
    assert(found, 'New swap appears in recent swaps');
    assert(marketAfter.totalVolume > marketBefore.totalVolume, 'Total volume increased after swap');
  } catch (e: any) {
    assert(false, `API swap + market tracking test failed: ${e.message}`);
  }

  // ── Results ──
  console.log('\n╔══════════════════════════════════════════╗');
  console.log('║  Test Results                            ║');
  console.log('╠══════════════════════════════════════════╣');
  console.log(`║  Passed: ${passed}`);
  console.log(`║  Failed: ${failed}`);
  console.log('╚══════════════════════════════════════════╝');
  
  if (failures.length > 0) {
    console.log('\n❌ Failures:');
    for (const f of failures) {
      console.log(`  - ${f}`);
    }
  } else {
    console.log('\n🎉 All tests passed!');
  }
  
  process.exit(failed > 0 ? 1 : 0);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
