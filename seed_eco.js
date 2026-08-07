const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');

async function main() {
  const ws = new WsProvider('ws://localhost:9949');
  const api = await ApiPromise.create({ provider: ws });
  const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  const alice = keyring.addFromUri('//Alice');

  console.log('Connected to:', await api.rpc.system.chain());
  console.log('Block:', (await api.rpc.chain.getHeader()).number.toNumber());

  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  // 1. Mint carbon credits (one at a time with 7s delay)
  const credits = [
    { id: 'CC-001', name: 'Amazon Reforestation 2024', tons: 5000 },
    { id: 'CC-002', name: 'Solar Farm Carbon Offset', tons: 3200 },
    { id: 'CC-003', name: 'Wind Energy Project', tons: 2100 },
  ];

  for (const c of credits) {
    try {
      const tx = api.tx.eco.mintCarbonCredit(c.id, c.name, c.tons);
      const hash = await tx.signAndSend(alice);
      console.log(`Minted ${c.id} (${c.tons}t): ${hash.toHex().slice(0,16)}...`);
      await sleep(7000); // Wait for block
    } catch(e) {
      console.log(`Failed ${c.id}: ${e.message}`);
      await sleep(3000);
    }
  }

  // 2. Create reforestation projects (4 args: id, name, trees, location)
  const projects = [
    { id: 'RP-001', name: 'Borneo Rainforest', trees: 15000, location: 'Borneo' },
    { id: 'RP-002', name: 'Costa Rica Reforest', trees: 8000, location: 'Costa Rica' },
    { id: 'RP-003', name: 'Ethiopian Green Legacy', trees: 24000, location: 'Ethiopia' },
  ];

  for (const p of projects) {
    try {
      const tx = api.tx.eco.createReforestProject(p.id, p.name, p.trees, p.location);
      await tx.signAndSend(alice);
      console.log(`Created ${p.id} (${p.trees} trees)`);
      await sleep(7000);
    } catch(e) {
      console.log(`Failed ${p.id}: ${e.message}`);
      await sleep(3000);
    }
  }

  // 3. Register green validators (4 args: renewable, source, co2, trees)
  const bob = keyring.addFromUri('//Bob');
  const charlie = keyring.addFromUri('//Charlie');
  const dave = keyring.addFromUri('//Dave');
  
  const validators = [
    { acct: bob, name: 'Bob', renewable: true, source: 'Solar', co2: 1200, trees: 500 },
    { acct: charlie, name: 'Charlie', renewable: true, source: 'Wind', co2: 980, trees: 300 },
    { acct: dave, name: 'Dave', renewable: true, source: 'Hydro', co2: 1500, trees: 800 },
  ];

  for (const v of validators) {
    try {
      const tx = api.tx.eco.registerGreenValidator(v.renewable, v.source, v.co2, v.trees);
      await tx.signAndSend(v.acct);
      console.log(`Registered ${v.name} (${v.source}, ${v.co2}t CO2)`);
      await sleep(7000);
    } catch(e) {
      console.log(`Failed ${v.name}: ${e.message}`);
      await sleep(3000);
    }
  }

  // Wait for finalization
  await sleep(10000);

  // Query results
  console.log('\n=== Eco Stats ===');
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
