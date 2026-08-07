const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');

const RPC_URL = 'ws://localhost:9948';
const ACCOUNTS = ['//Alice', '//Bob', '//Charlie', '//Dave', '//Eve'];
const TRANSFER_AMOUNT = 1000000000000; // 1000 VRDX (12 decimals)
const MIN_AMOUNT = 100000000000;  // 100 VRDX
const MAX_AMOUNT = 5000000000000; // 5000 VRDX

let api, keyring;
let txCount = 0;
let running = true;

async function init() {
  const ws = new WsProvider(RPC_URL);
  api = await ApiPromise.create({ provider: ws });
  keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  console.log('Transfer bot connected to node');
  console.log('Chain:', (await api.rpc.system.chain()).toString());
  
  // Log balances
  for (const uri of ACCOUNTS) {
    const pair = keyring.addFromUri(uri);
    const account = await api.query.system.account(pair.address);
    const free = account.data.free.toString();
    console.log(`${uri.replace('//','')} balance: ${(parseInt(free)/1e12).toFixed(2)} VRDX`);
  }
}

async function sendTransfer(fromUri, toUri, amount) {
  try {
    const fromPair = keyring.addFromUri(fromUri);
    const toPair = keyring.addFromUri(toUri);
    
    const transfer = api.tx.balances.transfer(toPair.address, amount);
    const hash = await transfer.signAndSend(fromPair);
    txCount++;
    
    const header = await api.rpc.chain.getHeader();
    const blockNum = header.number.toNumber();
    const amountVRDX = (amount / 1e12).toFixed(2);
    
    console.log(`[${new Date().toISOString()}] TX #${txCount} | Block #${blockNum} | ${fromUri.replace('//','')} → ${toUri.replace('//','')} | ${amountVRDX} VRDX | hash: ${hash.toHex().substring(0, 18)}...`);
    return true;
  } catch (e) {
    console.log(`[${new Date().toISOString()}] Transfer failed: ${e.message}`);
    return false;
  }
}

async function runBot() {
  await init();
  console.log('Starting transfer bot...\n');
  
  while (running) {
    try {
      // Pick random sender and receiver
      const senderIdx = Math.floor(Math.random() * ACCOUNTS.length);
      let receiverIdx = Math.floor(Math.random() * ACCOUNTS.length);
      while (receiverIdx === senderIdx) {
        receiverIdx = Math.floor(Math.random() * ACCOUNTS.length);
      }
      
      const sender = ACCOUNTS[senderIdx];
      const receiver = ACCOUNTS[receiverIdx];
      const amount = MIN_AMOUNT + Math.floor(Math.random() * (MAX_AMOUNT - MIN_AMOUNT));
      
      await sendTransfer(sender, receiver, amount);
      
      // Wait 30-60 seconds between transfers
      const wait = 30000 + Math.random() * 30000;
      await new Promise(resolve => setTimeout(resolve, wait));
      
    } catch (e) {
      console.log('Error:', e.message);
      await new Promise(resolve => setTimeout(resolve, 30000));
    }
  }
}

process.on('SIGINT', () => {
  console.log(`\nStopping transfer bot. Total transfers: ${txCount}`);
  running = false;
  process.exit(0);
});

process.on('SIGTERM', () => {
  running = false;
  process.exit(0);
});

runBot().catch(console.error);
