const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');

async function main() {
  const ws = new WsProvider('ws://localhost:9949');
  const api = await ApiPromise.create({ provider: ws });
  const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  const alice = keyring.addFromUri('//Alice');

  console.log('Block:', (await api.rpc.chain.getHeader()).number.toNumber());

  // Get Alice's nonce
  let nonce = (await api.query.system.account(alice.address)).nonce.toNumber();
  console.log('Alice nonce:', nonce);
  console.log('Alice balance:', (await api.query.system.account(alice.address)).data.free.toHuman());

  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  // Submit all txs with increasing nonces
  const txs = [
    // Carbon credits
    api.tx.eco.mintCarbonCredit('CC-001', 'Amazon Reforestation 2024', 5000),
    api.tx.eco.mintCarbonCredit('CC-002', 'Solar Farm Carbon Offset', 3200),
    api.tx.eco.mintCarbonCredit('CC-003', 'Wind Energy Project', 2100),
    // Reforestation projects
    api.tx.eco.createReforestProject('RP-001', 'Borneo Rainforest', 15000, 'Borneo'),
    api.tx.eco.createReforestProject('RP-002', 'Costa Rica Reforest', 8000, 'Costa Rica'),
    api.tx.eco.createReforestProject('RP-003', 'Ethiopian Green Legacy', 24000, 'Ethiopia'),
    // Green validators (already registered Alice, do Bob and Charlie via Alice as proxy? No, must be self-registration)
    // Use updateGreenScore instead for Alice
  ];

  console.log(`\nSubmitting ${txs.length} transactions with nonce ${nonce}...`);

  for (let i = 0; i < txs.length; i++) {
    try {
      await txs[i].signAndSend(alice, { nonce: nonce + i }, (result) => {
        if (result.status.isInBlock) {
          console.log(`Tx ${i+1} included in block #${result.status.asInBlock.toNumber()}`);
        } else if (result.status.isFinalized) {
          console.log(`Tx ${i+1} finalized`);
        }
      });
      console.log(`Tx ${i+1} submitted (nonce ${nonce + i})`);
    } catch(e) {
      console.log(`Tx ${i+1} failed: ${e.message}`);
    }
  }

  // Wait for all txs to finalize
  console.log('\nWaiting 20s for finalization...');
  await sleep(20000);

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
