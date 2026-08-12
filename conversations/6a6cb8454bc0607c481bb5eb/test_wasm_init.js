global.window = global;
global.self = global;

const fs = require('fs');
const code = fs.readFileSync('/opt/verdis-wallet/mobile/assets/polkadot-crypto-bundle.js', 'utf8');

const start = Date.now();
try {
  eval(code);
} catch (e) {
  console.log('SYNC_LOAD_ERROR:', e.message);
  process.exit(1);
}

if (!global.PolkadotCrypto) {
  console.log('RESULT: PolkadotCrypto global not found after eval');
  process.exit(1);
}

console.log('Bundle loaded synchronously in', Date.now() - start, 'ms. Waiting for cryptoWaitReady()...');

global.PolkadotCrypto.cryptoWaitReady().then(() => {
  console.log('RESULT: READY in', Date.now() - start, 'ms total');
  process.exit(0);
}).catch((e) => {
  console.log('RESULT: INIT_FAILED after', Date.now() - start, 'ms —', e && e.message ? e.message : e);
  process.exit(1);
});

setTimeout(() => {
  console.log('RESULT: TIMEOUT after 30000ms — never resolved or rejected');
  process.exit(1);
}, 30000);
