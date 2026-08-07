const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');
const fs = require('fs');

// Configuration
const RPC_URL = 'ws://localhost:9948';
const ACCOUNTS = ['//Alice', '//Bob', '//Charlie', '//Dave', '//Eve'];
const REMARKS = [
  'Verdis Chain testnet live',
  'Green blockchain for a sustainable future',
  'Carbon-negative consensus',
  'DPoS validator network active',
  'VRDX token transfer',
  'AMM DEX pool update',
  'Reforestation credit logged',
  'Eco-friendly block production',
  'Validator rotation complete',
  'Network healthy and synced',
];

let api, keyring;
let txCount = 0;
let running = true;

async function init() {
  const ws = new WsProvider(RPC_URL);
  api = await ApiPromise.create({ provider: ws });
  keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  console.log('Connected to node:', await api.rpc.system.chain());
  console.log('Starting transaction bot...\n');
}

async function sendRemark(accountUri, remark) {
  try {
    const pair = keyring.addFromUri(accountUri);
    const tx = api.tx.system.remark(remark);
    
    const hash = await tx.signAndSend(pair);
    txCount++;
    const height = await api.rpc.chain.getHeader();
    const blockNum = height.number.toNumber();
    console.log(`[${new Date().toISOString()}] TX #${txCount} | Block #${blockNum} | ${accountUri.replace('//', '')} | "${remark}" | hash: ${hash.toHex().substring(0, 18)}...`);
    return true;
  } catch (e) {
    console.log(`[${new Date().toISOString()}] TX failed: ${e.message}`);
    return false;
  }
}

async function runBot() {
  await init();
  
  while (running) {
    try {
      // Pick random account and remark
      const account = ACCOUNTS[Math.floor(Math.random() * ACCOUNTS.length)];
      const remark = REMARKS[Math.floor(Math.random() * REMARKS.length)];
      
      await sendRemark(account, remark);
      
      // Wait 10-25 seconds between transactions
      const wait = 10000 + Math.random() * 15000;
      await new Promise(resolve => setTimeout(resolve, wait));
      
    } catch (e) {
      console.log('Error:', e.message);
      await new Promise(resolve => setTimeout(resolve, 30000));
    }
  }
}

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nStopping transaction bot...');
  console.log(`Total transactions sent: ${txCount}`);
  running = false;
  process.exit(0);
});

process.on('SIGTERM', () => {
  running = false;
  process.exit(0);
});

runBot().catch(console.error);
