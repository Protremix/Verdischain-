const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');

const RPC_URL = 'ws://localhost:9948';
const ACCOUNTS = ['//Alice', '//Bob', '//Charlie', '//Dave', '//Eve'];
const MIN_AMOUNT = 100000000000;  // 100 VRDX
const MAX_AMOUNT = 5000000000000; // 5000 VRDX

let api, keyring, txCount = 0, running = true;

async function init() {
  const ws = new WsProvider(RPC_URL);
  api = await ApiPromise.create({ provider: ws });
  keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  console.log('Transfer bot connected. Chain:', (await api.rpc.system.chain()).toString());
  for (const uri of ACCOUNTS) {
    const pair = keyring.addFromUri(uri);
    const account = await api.query.system.account(pair.address);
    console.log(`  ${uri.replace('//','')}: ${(parseInt(account.data.free)/1e12).toFixed(2)} VRDX`);
  }
}

async function sendTransfer(fromUri, toUri, amount) {
  try {
    const fromPair = keyring.addFromUri(fromUri);
    const toPair = keyring.addFromUri(toUri);
    // Use transferAllowDeath (Substrate v0.9.43+ naming)
    const transfer = api.tx.balances.transferAllowDeath(toPair.address, amount);
    const hash = await transfer.signAndSend(fromPair);
    txCount++;
    const header = await api.rpc.chain.getHeader();
    console.log(`[${new Date().toISOString()}] TX #${txCount} | Block #${header.number.toNumber()} | ${fromUri.replace('//','')} → ${toUri.replace('//','')} | ${(amount/1e12).toFixed(2)} VRDX | ${hash.toHex().substring(0,18)}...`);
  } catch (e) {
    console.log(`[${new Date().toISOString()}] Transfer failed: ${e.message}`);
  }
}

async function runBot() {
  await init();
  console.log('Starting real VRDX transfers...\n');
  while (running) {
    const si = Math.floor(Math.random() * ACCOUNTS.length);
    let ri = Math.floor(Math.random() * ACCOUNTS.length);
    while (ri === si) ri = Math.floor(Math.random() * ACCOUNTS.length);
    const amount = MIN_AMOUNT + Math.floor(Math.random() * (MAX_AMOUNT - MIN_AMOUNT));
    await sendTransfer(ACCOUNTS[si], ACCOUNTS[ri], amount);
    await new Promise(r => setTimeout(r, 30000 + Math.random() * 30000));
  }
}

process.on('SIGINT', () => { running = false; process.exit(0); });
process.on('SIGTERM', () => { running = false; process.exit(0); });
runBot().catch(console.error);
