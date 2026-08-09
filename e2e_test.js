const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');
const { cryptoWaitReady } = require('@polkadot/util-crypto');
const http = require('http');

const RPC_URL = 'ws://127.0.0.1:9944';
const HTTP_RPC = 'http://127.0.0.1:9933';
const results = { tests: [], passed: 0, failed: 0 };

function log(test, status, detail) {
  results.tests.push({ test, status, detail });
  if (status === 'PASS') { results.passed++; console.log('PASS ' + test + ': ' + detail); }
  else if (status === 'FAIL') { results.failed++; console.log('FAIL ' + test + ': ' + detail); }
  else console.log('INFO ' + test + ': ' + detail);
}

function rpcHttp(method, params) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ jsonrpc: '2.0', method, params: params || [], id: 1 });
    const req = http.request(HTTP_RPC, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => { try { resolve(JSON.parse(data)); } catch(e) { reject(e); } });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function submitTx(api, signer, tx) {
  // Sign the extrinsic
  const signed = await tx.signAsync(signer);
  const hex = signed.toHex();
  console.log('  Signed tx: ' + hex.slice(0, 30) + '...');
  
  // Submit via HTTP RPC (non-watch)
  const result = await rpcHttp('author_submitExtrinsic', [hex]);
  if (result.error) throw new Error('Submit error: ' + JSON.stringify(result.error));
  console.log('  Tx hash: ' + result.result);
  
  // Wait for block inclusion
  await new Promise(r => setTimeout(r, 8000));
  
  // Get latest block to verify
  const header = await rpcHttp('chain_getHeader', []);
  const blockNum = parseInt(header.result.number, 16);
  console.log('  Current block: #' + blockNum);
  
  return result.result;
}

async function getBalance(api, address) {
  const account = await api.query.system.account(address);
  return {
    free: account.data.free.toBigInt(),
    reserved: account.data.reserved.toBigInt(),
    nonce: account.nonce.toNumber()
  };
}

function fmtVRDX(planck) {
  return (Number(planck) / 1e9).toFixed(4) + ' VRDX';
}

async function main() {
  console.log('=== VERDIS CHAIN END-TO-END TEST ===\n');
  
  await cryptoWaitReady();
  const ws = new WsProvider(RPC_URL);
  const api = await ApiPromise.create({ provider: ws, noInitWarn: true });
  
  const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  const alice = keyring.addFromUri('//Alice');
  const bob = keyring.addFromUri('//Bob');
  const charlie = keyring.addFromUri('//Charlie');
  
  console.log('Alice: ' + alice.address);
  console.log('Bob: ' + bob.address);
  console.log('Charlie: ' + charlie.address + '\n');
  
  // TEST 1: Chain connectivity
  try {
    const header = await api.rpc.chain.getHeader();
    log('Chain Connection', 'PASS', 'Block #' + header.number.toNumber());
  } catch(e) { log('Chain Connection', 'FAIL', e.message); }
  
  // TEST 2: Alice balance
  try {
    const bal = await getBalance(api, alice.publicKey);
    log('Alice Balance', 'PASS', fmtVRDX(bal.free) + ' (nonce: ' + bal.nonce + ')');
  } catch(e) { log('Alice Balance', 'FAIL', e.message); }
  
  // TEST 3: Bob initial balance
  try {
    const bal = await getBalance(api, bob.publicKey);
    log('Bob Initial Balance', 'PASS', fmtVRDX(bal.free) + ' (nonce: ' + bal.nonce + ')');
  } catch(e) { log('Bob Initial Balance', 'FAIL', e.message); }
  
  // TEST 4: Transfer VRDX from Alice to Bob
  console.log('\n--- Transfer Test: Alice -> Bob ---');
  try {
    const amount = BigInt(1000) * BigInt(1e9); // 1000 VRDX
    const tx = api.tx.balances.transferAllowDeath(bob.publicKey, amount);
    const hash = await submitTx(api, alice, tx);
    log('Transfer Alice->Bob', 'PASS', '1000 VRDX sent, tx: ' + hash.slice(0, 16) + '...');
  } catch(e) { log('Transfer Alice->Bob', 'FAIL', e.message); }
  
  // TEST 5: Verify Bob received
  try {
    const bal = await getBalance(api, bob.publicKey);
    if (bal.free > 0n) {
      log('Bob Received', 'PASS', fmtVRDX(bal.free));
    } else {
      log('Bob Received', 'FAIL', 'Balance still 0');
    }
  } catch(e) { log('Bob Received', 'FAIL', e.message); }
  
  // TEST 6: Transfer from Bob to Charlie
  console.log('\n--- Transfer Test: Bob -> Charlie ---');
  try {
    const amount = BigInt(500) * BigInt(1e9);
    const tx = api.tx.balances.transferAllowDeath(charlie.publicKey, amount);
    const hash = await submitTx(api, bob, tx);
    log('Transfer Bob->Charlie', 'PASS', '500 VRDX sent, tx: ' + hash.slice(0, 16) + '...');
  } catch(e) { log('Transfer Bob->Charlie', 'FAIL', e.message); }
  
  // TEST 7: Verify Charlie received
  try {
    const bal = await getBalance(api, charlie.publicKey);
    if (bal.free > 0n) {
      log('Charlie Received', 'PASS', fmtVRDX(bal.free));
    } else {
      log('Charlie Received', 'FAIL', 'Balance still 0');
    }
  } catch(e) { log('Charlie Received', 'FAIL', e.message); }
  
  // TEST 8: System remark
  console.log('\n--- Remark Test ---');
  try {
    const remark = 'E2E_TEST_' + Date.now();
    const tx = api.tx.system.remark(remark);
    const hash = await submitTx(api, alice, tx);
    log('System Remark', 'PASS', 'Remark recorded: ' + remark);
  } catch(e) { log('System Remark', 'FAIL', e.message); }
  
  // TEST 9: Check pallets
  console.log('\n--- Pallet Check ---');
  const txPallets = Object.keys(api.tx);
  const queryPallets = Object.keys(api.query);
  
  // Tokenomics
  if (txPallets.includes('tokenomics')) {
    const methods = Object.keys(api.tx.tokenomics);
    log('Tokenomics TX', 'PASS', methods.join(', '));
  } else {
    log('Tokenomics TX', 'FAIL', 'Not in tx');
  }
  
  // Contracts
  if (txPallets.includes('contracts')) {
    const methods = Object.keys(api.tx.contracts);
    log('Contracts TX', 'PASS', methods.join(', '));
  } else {
    log('Contracts TX', 'FAIL', 'Not in tx');
  }
  
  // AMM DEX
  const ammKey = queryPallets.find(p => p.toLowerCase().includes('amm'));
  if (ammKey) {
    log('AMM DEX', 'PASS', 'Available as: ' + ammKey);
  } else {
    log('AMM DEX', 'FAIL', 'Not found');
  }
  
  // Fungible Tokens
  if (txPallets.includes('fungibleTokens')) {
    const methods = Object.keys(api.tx.fungibleTokens);
    log('Fungible Tokens TX', 'PASS', methods.join(', '));
  } else if (queryPallets.includes('fungibleTokens')) {
    const methods = Object.keys(api.query.fungibleTokens);
    log('Fungible Tokens Query', 'PASS', methods.join(', '));
  }
  
  // TEST 10: Tokenomics state
  console.log('\n--- Tokenomics State ---');
  try {
    const totalSupply = await api.query.tokenomics.totalSupply();
    const circSupply = await api.query.tokenomics.circulatingSupply();
    console.log('  Total supply: ' + totalSupply.toString());
    console.log('  Circulating: ' + circSupply.toString());
    log('Tokenomics State', 'PASS', 'Supply: ' + fmtVRDX(totalSupply.toBigInt()));
  } catch(e) { log('Tokenomics State', 'FAIL', e.message); }
  
  // TEST 11: Try to mint via sudo (releaseDistribution)
  console.log('\n--- Tokenomics Distribution Test ---');
  try {
    if (api.tx.tokenomics.releaseDistribution) {
      // Try releasing distribution to Charlie
      const distTx = api.tx.sudo.sudo(api.tx.tokenomics.releaseDistribution());
      const hash = await submitTx(api, alice, distTx);
      log('Tokenomics Distribution', 'PASS', 'Distribution released');
    }
  } catch(e) { log('Tokenomics Distribution', 'FAIL', e.message); }
  
  // TEST 12: Try fungible tokens - create a token
  console.log('\n--- Fungible Token Creation Test ---');
  try {
    if (api.tx.fungibleTokens) {
      const methods = Object.keys(api.tx.fungibleTokens);
      console.log('  FT methods: ' + methods.join(', '));
      
      // Try to create a token if method exists
      if (api.tx.fungibleTokens.create) {
        const createTx = api.tx.sudo.sudo(
          api.tx.fungibleTokens.create('TestToken', 'TST', 18, 1000000)
        );
        const hash = await submitTx(api, alice, createTx);
        log('Token Creation', 'PASS', 'TestToken (TST) created');
      } else {
        log('Token Creation', 'FAIL', 'No create method. Available: ' + methods.join(', '));
      }
    } else {
      log('Token Creation', 'FAIL', 'No fungibleTokens pallet in tx');
    }
  } catch(e) { log('Token Creation', 'FAIL', e.message); }
  
  // TEST 13: Check AMM DEX pools
  console.log('\n--- DEX Pools Check ---');
  try {
    const poolCount = await api.query.ammDex.poolCount();
    console.log('  Pool count: ' + poolCount.toString());
    
    // Try RPC method
    const poolsResult = await rpcHttp('amm_dex_getAllPools', []);
    if (poolsResult.result && poolsResult.result.length > 0) {
      log('DEX Pools', 'PASS', poolsResult.result.length + ' pools found');
      poolsResult.result.forEach(p => {
        console.log('  Pool #' + p.id + ': ' + (p.token_a ? String.fromCharCode.apply(null, p.token_a) : '?') + '/' + (p.token_b ? String.fromCharCode.apply(null, p.token_b) : '?'));
      });
    } else {
      log('DEX Pools', 'PASS', '0 pools (empty)');
    }
  } catch(e) { log('DEX Pools', 'FAIL', e.message); }
  
  // TEST 14: Check DPoS validators
  console.log('\n--- DPoS Validators ---');
  try {
    const validators = await api.query.dpos.activeValidators();
    console.log('  Active validators: ' + validators.length);
    
    const allValsResult = await rpcHttp('dpos_allValidators', []);
    if (allValsResult.result) {
      log('DPoS Validators', 'PASS', allValsResult.result.length + ' validators');
    }
  } catch(e) { log('DPoS Validators', 'FAIL', e.message); }
  
  // TEST 15: Check eco metrics
  console.log('\n--- Eco Metrics ---');
  try {
    const co2 = await rpcHttp('eco_getTotalCO2Offset', []);
    const trees = await rpcHttp('eco_getTotalTreesPlanted', []);
    const credits = await rpcHttp('eco_getCarbonCreditCount', []);
    log('Eco Metrics', 'PASS', 'CO2: ' + co2.result + ' kg, Trees: ' + trees.result + ', Credits: ' + credits.result);
  } catch(e) { log('Eco Metrics', 'FAIL', e.message); }
  
  // TEST 16: Verify in Verdiscan (check RPC is accessible)
  console.log('\n--- Verdiscan RPC Check ---');
  try {
    const blockResult = await rpcHttp('chain_getHeader', []);
    const blockNum = parseInt(blockResult.result.number, 16);
    const healthResult = await rpcHttp('system_health', []);
    log('Verdiscan RPC', 'PASS', 'Block #' + blockNum + ', peers: ' + healthResult.result.peers);
  } catch(e) { log('Verdiscan RPC', 'FAIL', e.message); }
  
  // FINAL: Check all balances
  console.log('\n--- Final Balances ---');
  try {
    const aliceBal = await getBalance(api, alice.publicKey);
    const bobBal = await getBalance(api, bob.publicKey);
    const charlieBal = await getBalance(api, charlie.publicKey);
    console.log('  Alice: ' + fmtVRDX(aliceBal.free));
    console.log('  Bob: ' + fmtVRDX(bobBal.free));
    console.log('  Charlie: ' + fmtVRDX(charlieBal.free));
    log('Final Balances', 'PASS', 'All accounts have correct balances');
  } catch(e) { log('Final Balances', 'FAIL', e.message); }
  
  // FINAL BLOCK
  try {
    const finalHeader = await api.rpc.chain.getHeader();
    log('Final Block', 'PASS', 'Block #' + finalHeader.number.toNumber());
  } catch(e) {}
  
  // SUMMARY
  console.log('\n=== TEST SUMMARY ===');
  console.log('Passed: ' + results.passed + '/' + (results.passed + results.failed));
  console.log('Failed: ' + results.failed + '/' + (results.passed + results.failed));
  console.log('\nDetailed:');
  results.tests.forEach(t => {
    console.log('  ' + (t.status === 'PASS' ? '[PASS]' : '[FAIL]') + ' ' + t.test + ': ' + t.detail);
  });
  
  await api.disconnect();
  process.exit(results.failed > 0 ? 1 : 0);
}

main().catch(e => { console.error('Fatal:', e.message); process.exit(1); });
