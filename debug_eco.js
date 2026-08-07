const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');
async function main() {
  const api = await ApiPromise.create({ provider: new WsProvider('ws://localhost:9949') });
  const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  const alice = keyring.addFromUri('//Alice');

  // Check current block and events
  const header = await api.rpc.chain.getHeader();
  console.log('Current block:', header.number.toNumber());

  // Try a single mint carbon credit with event tracking
  console.log('\nSubmitting single mintCarbonCredit...');
  try {
    const tx = api.tx.eco.mintCarbonCredit('CC-TEST-001', 'Test Project', 1000);
    const result = await new Promise((resolve, reject) => {
      tx.signAndSend(alice, (status) => {
        console.log('Status:', status.type);
        if (status.isInBlock) {
          console.log('In block:', status.asInBlock.toHex().slice(0, 16));
        }
        if (status.isFinalized) {
          resolve(status);
        }
      }).catch(reject);
    });
    
    // Get events
    const events = await api.query.system.events.at(result.asFinalized);
    events.forEach((record) => {
      const { event } = record;
      if (event.section === 'eco' || event.method.includes('Carbon') || event.method.includes('Mint')) {
        console.log('Event:', event.section, event.method, event.meta.args.map(a => a.name).join(','));
      }
      if (event.method === 'ExtrinsicFailed') {
        console.log('FAILED:', event.toHuman());
      }
    });
  } catch(e) {
    console.log('Error:', e.message);
  }

  // Check new state
  const co2 = await api.query.eco.totalCO2Offset();
  const trees = await api.query.eco.totalTreesPlanted();
  const count = await api.query.eco.totalCreditsRetired();
  console.log('\nAfter single tx:');
  console.log('CO2:', co2.toString());
  console.log('Trees:', trees.toString());

  await api.disconnect();
}
main().catch(console.error);
