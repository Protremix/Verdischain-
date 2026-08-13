const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');

async function main() {
  const api = await ApiPromise.create({ provider: new WsProvider('ws://localhost:9949') });
  const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  const alice = keyring.addFromUri('//Alice');

  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  console.log('Block:', (await api.rpc.chain.getHeader()).number.toNumber());
  console.log('Seeding eco data...');

  // 1. Mint carbon credits (id:Bytes, projectName:Bytes, tonsCo2:u64)
  const credits = [
    { id: 'CC-004', name: 'Amazon Reforestation 2024', tons: 5000 },
    { id: 'CC-005', name: 'Solar Farm Carbon Offset', tons: 3200 },
    { id: 'CC-006', name: 'Wind Energy Project', tons: 2100 },
  ];

  for (const c of credits) {
    try {
      const tx = api.tx.eco.mintCarbonCredit(c.id, c.name, c.tons);
      const hash = await tx.signAndSend(alice);
      console.log(`Minted ${c.id} (${c.tons}t): ${hash.toHex().slice(0,16)}...`);
      await sleep(3000);
    } catch(e) {
      console.log(`Failed ${c.id}: ${e.message}`);
    }
  }

  // 2. Create reforestation projects (id:Bytes, name:Bytes, treesPlanted:u32, location:Bytes)
  const projects = [
    { id: 'RP-004', name: 'Borneo Rainforest', trees: 15000, location: 'Borneo' },
    { id: 'RP-005', name: 'Costa Rica Reforest', trees: 8000, location: 'Costa Rica' },
    { id: 'RP-006', name: 'Ethiopian Green Legacy', trees: 24000, location: 'Ethiopia' },
  ];

  for (const p of projects) {
    try {
      const tx = api.tx.eco.createReforestProject(p.id, p.name, p.trees, p.location);
      await tx.signAndSend(alice);
      console.log(`Created ${p.id} (${p.trees} trees)`);
      await sleep(3000);
    } catch(e) {
      console.log(`Failed ${p.id}: ${e.message}`);
    }
  }

  // 3. Register green validators (energySource:Bytes, carbonOffset:u64, treesPlanted:u32, score:u8)
  const validators = [
    { source: 'Solar', co2: 1200, trees: 500, score: 94 },
    { source: 'Wind', co2: 980, trees: 300, score: 91 },
    { source: 'Hydro', co2: 1500, trees: 800, score: 96 },
  ];

  for (const v of validators) {
    try {
      const tx = api.tx.eco.registerGreenValidator(v.source, v.co2, v.trees, v.score);
      await tx.signAndSend(alice);
      console.log(`Registered validator (${v.source}, score: ${v.score})`);
      await sleep(3000);
    } catch(e) {
      console.log(`Failed validator: ${e.message}`);
    }
  }

  // Wait for finalization
  await sleep(5000);

  // Query results
  console.log('\n=== Eco Stats After Seeding ===');
  const co2 = await api.query.eco.totalCO2Offset();
  console.log('Total CO2 Offset:', co2.toString());
  const trees = await api.query.eco.totalTreesPlanted();
  console.log('Total Trees Planted:', trees.toString());
  const retired = await api.query.eco.totalCreditsRetired();
  console.log('Total Credits Retired:', retired.toString());

  // Also check via RPC
  console.log('\n=== Via Eco RPC ===');
  const rpcCo2 = await api.rpc.eco.getTotalCO2Offset();
  console.log('RPC CO2:', rpcCo2.toString());

  await api.disconnect();
  console.log('Done!');
}

main().catch(console.error);
