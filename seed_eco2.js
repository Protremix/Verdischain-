const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');

async function main() {
  const ws = new WsProvider('ws://localhost:9949');
  const api = await ApiPromise.create({ provider: ws });
  const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  
  // Use multiple accounts to avoid priority conflicts
  const alice = keyring.addFromUri('//Alice');
  const bob = keyring.addFromUri('//Bob');
  const charlie = keyring.addFromUri('//Charlie');
  const dave = keyring.addFromUri('//Dave');
  const eve = keyring.addFromUri('//Eve');
  const ferdie = keyring.addFromUri('//Ferdie');

  console.log('Block:', (await api.rpc.chain.getHeader()).number.toNumber());
  console.log('Starting eco seeding...\n');

  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  // 1. Mint carbon credits using different accounts
  const credits = [
    { sender: alice, id: 'CC-001', name: 'Amazon Reforestation 2024', tons: 5000 },
    { sender: bob, id: 'CC-002', name: 'Solar Farm Carbon Offset', tons: 3200 },
    { sender: charlie, id: 'CC-003', name: 'Wind Energy Project', tons: 2100 },
  ];

  for (const c of credits) {
    try {
      const tx = api.tx.eco.mintCarbonCredit(c.id, c.name, c.tons);
      const hash = await tx.signAndSend(c.sender);
      console.log(`Minted ${c.id} (${c.tons}t) by ${c.sender.address.slice(0,8)}: ${hash.toHex().slice(0,16)}...`);
    } catch(e) {
      console.log(`Failed ${c.id}: ${e.message}`);
    }
    await sleep(1000);
  }

  // 2. Create reforestation projects
  const projects = [
    { sender: dave, id: 'RP-001', name: 'Borneo Rainforest', trees: 15000, location: 'Borneo' },
    { sender: eve, id: 'RP-002', name: 'Costa Rica Reforest', trees: 8000, location: 'Costa Rica' },
    { sender: ferdie, id: 'RP-003', name: 'Ethiopian Green Legacy', trees: 24000, location: 'Ethiopia' },
  ];

  for (const p of projects) {
    try {
      const tx = api.tx.eco.createReforestProject(p.id, p.name, p.trees, p.location);
      await tx.signAndSend(p.sender);
      console.log(`Created ${p.id} (${p.trees} trees) by ${p.sender.address.slice(0,8)}`);
    } catch(e) {
      console.log(`Failed ${p.id}: ${e.message}`);
    }
    await sleep(1000);
  }

  // 3. Register green validators (energySource, carbonOffset, treesPlanted, score)
  const validators = [
    { sender: alice, source: 'Solar', co2: 1200, trees: 500, score: 94 },
    { sender: bob, source: 'Wind', co2: 980, trees: 300, score: 91 },
    { sender: charlie, source: 'Hydro', co2: 1500, trees: 800, score: 96 },
  ];

  for (const v of validators) {
    try {
      const tx = api.tx.eco.registerGreenValidator(v.source, v.co2, v.trees, v.score);
      await tx.signAndSend(v.sender);
      console.log(`Registered validator (${v.source}, ${v.co2}t, score: ${v.score})`);
    } catch(e) {
      console.log(`Failed validator: ${e.message}`);
    }
    await sleep(1000);
  }

  // Wait for finalization
  console.log('\nWaiting for blocks...');
  await sleep(15000);

  // Query results
  console.log('\n=== Eco Stats After Seeding ===');
  try {
    const co2 = await api.query.eco.totalCO2Offset();
    console.log('Total CO2 Offset:', co2.toString());
    const trees = await api.query.eco.totalTreesPlanted();
    console.log('Total Trees Planted:', trees.toString());
    const retired = await api.query.eco.totalCreditsRetired();
    console.log('Total Credits Retired:', retired.toString());
  } catch(e) {
    console.log('Query error:', e.message);
  }

  await api.disconnect();
  console.log('Done!');
}

main().catch(console.error);
