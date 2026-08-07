const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');
async function main() {
  const api = await ApiPromise.create({ provider: new WsProvider('ws://localhost:9949') });
  const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  const alice = keyring.addFromUri('//Alice');

  const txs = [
    api.tx.eco.mintCarbonCredit('CC-NEW-001', 'Amazon Reforestation 2024', 5000),
    api.tx.eco.mintCarbonCredit('CC-NEW-002', 'Solar Farm Carbon Offset', 3200),
    api.tx.eco.mintCarbonCredit('CC-NEW-003', 'Wind Energy Project', 2100),
    api.tx.eco.createReforestProject('RP-NEW-001', 'Borneo Rainforest', 15000, 'Borneo'),
    api.tx.eco.createReforestProject('RP-NEW-002', 'Costa Rica Reforest', 8000, 'Costa Rica'),
    api.tx.eco.createReforestProject('RP-NEW-003', 'Ethiopian Green Legacy', 24000, 'Ethiopia'),
  ];

  console.log('Submitting', txs.length, 'eco txs...');
  const batch = api.tx.utility.batchAll(txs);
  await batch.signAndSend(alice);
  console.log('Batch submitted! Waiting for block...');
  await new Promise(r => setTimeout(r, 5000));

  const header = await api.rpc.chain.getHeader();
  console.log('Block:', header.number.toNumber());

  const co2 = await api.query.eco.totalCO2Offset();
  const trees = await api.query.eco.totalTreesPlanted();
  console.log('Total CO2:', co2.toString());
  console.log('Total Trees:', trees.toString());

  await api.disconnect();
}
main().catch(console.error);
