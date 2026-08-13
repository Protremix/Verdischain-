const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');
async function main() {
  const api = await ApiPromise.create({ provider: new WsProvider('ws://localhost:9949') });
  const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  const alice = keyring.addFromUri('//Alice');

  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  // 1. Mint additional carbon credits
  const credits = [
    { id: 'CC-NEW-001', name: 'Amazon Reforestation 2024', tons: 5000 },
    { id: 'CC-NEW-002', name: 'Solar Farm Carbon Offset', tons: 3200 },
    { id: 'CC-NEW-003', name: 'Wind Energy Project', tons: 2100 },
  ];

  for (const c of credits) {
    const tx = api.tx.eco.mintCarbonCredit(c.id, c.name, c.tons);
    await tx.signAndSend(alice);
    console.log('Minted', c.id, c.tons, 't');
    await sleep(2000);
  }

  // 2. Create reforestation projects
  const projects = [
    { id: 'RP-NEW-001', name: 'Borneo Rainforest', trees: 15000, location: 'Borneo' },
    { id: 'RP-NEW-002', name: 'Costa Rica Reforest', trees: 8000, location: 'Costa Rica' },
    { id: 'RP-NEW-003', name: 'Ethiopian Green Legacy', trees: 24000, location: 'Ethiopia' },
  ];

  for (const p of projects) {
    const tx = api.tx.eco.createReforestProject(p.id, p.name, p.trees, p.location);
    await tx.signAndSend(alice);
    console.log('Created', p.id, p.trees, 'trees');
    await sleep(2000);
  }

  // 3. Register green validators
  const validators = [
    { source: 'Solar', co2: 1200, trees: 500, score: 94 },
    { source: 'Wind', co2: 980, trees: 300, score: 91 },
    { source: 'Hydro', co2: 1500, trees: 800, score: 96 },
  ];

  for (const v of validators) {
    const tx = api.tx.eco.registerGreenValidator(v.source, v.co2, v.trees, v.score);
    await tx.signAndSend(alice);
    console.log('Registered', v.source, 'score', v.score);
    await sleep(2000);
  }

  // Wait for finalization
  await sleep(3000);

  // Final stats
  const co2 = await api.query.eco.totalCO2Offset();
  const trees = await api.query.eco.totalTreesPlanted();
  console.log('\n=== Final Eco Stats ===');
  console.log('Total CO2:', co2.toString());
  console.log('Total Trees:', trees.toString());

  await api.disconnect();
}
main().catch(console.error);
