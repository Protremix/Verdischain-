const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');
const RPC_URL = 'ws://localhost:9944';
let api, keyring, txCount = 0, running = true;

async function init() {
  api = await ApiPromise.create({ provider: new WsProvider(RPC_URL) });
  keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  console.log('Connected. TX bot running...');
}

async function loop() {
  while (running) {
    try {
      const alice = keyring.addFromUri('//Alice');
      const remarks = [
        'Verdis Chain testnet live',
        'Green blockchain for sustainability',
        'Carbon-negative consensus',
        'DPoS validator network active',
        'VRDX token transfer',
        'AMM DEX pool update',
        'Reforestation credit logged',
        'Eco-friendly block production',
      ];
      const remark = remarks[Math.floor(Math.random() * remarks.length)];
      const tx = api.tx.system.remark(remark);
      await tx.signAndSend(alice);
      txCount++;
      console.log(`TX #${txCount}: ${remark}`);
    } catch(e) {
      console.log('Error:', e.message);
    }
    await new Promise(r => setTimeout(r, 10000 + Math.random() * 15000));
  }
}

process.on('SIGTERM', () => { running = false; });
init().then(loop).catch(console.error);
