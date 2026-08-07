const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');
async function main() {
  const api = await ApiPromise.create({ provider: new WsProvider('ws://localhost:9949') });
  const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  const alice = keyring.addFromUri('//Alice');

  // Submit single tx
  console.log('Submitting mintCarbonCredit...');
  const tx = api.tx.eco.mintCarbonCredit('CC-TEST-001', 'Test Project', 1000);
  const hash = await tx.signAndSend(alice);
  console.log('Hash:', hash.toHex());

  // Wait for block
  await new Promise(r => setTimeout(r, 5000));

  // Check block and state
  const header = await api.rpc.chain.getHeader();
  console.log('Block:', header.number.toNumber());

  // Check events from latest block
  const blockHash = await api.rpc.chain.getBlockHash();
  const events = await api.query.system.events.at(blockHash);
  console.log('Events in latest block:');
  events.forEach((e, i) => {
    const { event } = e;
    console.log(`  [${i}] ${event.section}.${event.method}`);
    if (event.method === 'ExtrinsicFailed' || event.section === 'eco') {
      console.log('    ', JSON.stringify(event.toHuman()));
    }
  });

  // Check eco state
  const co2 = await api.query.eco.totalCO2Offset();
  console.log('Total CO2:', co2.toString());

  await api.disconnect();
}
main().catch(console.error);
