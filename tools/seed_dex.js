const { ApiPromise, WsProvider, Keyring } = require("@polkadot/api");

async function main() {
  const api = await ApiPromise.create({
    provider: new WsProvider("ws://localhost:9933")
  });

  const keyring = new Keyring({ type: "sr25519", ss58Format: 909 });
  const alice = keyring.addFromUri("//Alice");

  const UNITS = 1_000_000_000; // 9 decimals

  // Create 3 DEX pools
  const pools = [
    { tokenA: "VRDX", tokenB: "CARBON", amountA: 500 * UNITS, amountB: 5000 * UNITS },
    { tokenA: "VRDX", tokenB: "ECO", amountA: 300 * UNITS, amountB: 3000 * UNITS },
    { tokenA: "VRDX", tokenB: "TREE", amountA: 200 * UNITS, amountB: 2000 * UNITS }
  ];

  const txs = pools.map(p =>
    api.tx.ammDex.createPool(
      Array.from(Buffer.from(p.tokenA, "utf8")),
      Array.from(Buffer.from(p.tokenB, "utf8")),
      p.amountA,
      p.amountB
    )
  );

  console.log("Submitting", txs.length, "pool creation txs...");

  const batch = api.tx.utility.batchAll(txs);

  await new Promise((resolve, reject) => {
    batch.signAndSend(alice, ({ status, dispatchError }) => {
      if (status.isInBlock) {
        console.log("Included in block:", status.asInBlock.toHex().substring(0, 16) + "...");
        if (dispatchError) {
          if (dispatchError.isModule) {
            const decoded = api.registry.findMetaError(dispatchError.asModule);
            console.error("Error:", decoded.section, decoded.name, decoded.docs);
          } else {
            console.error("Error:", dispatchError.toString());
          }
          reject(new Error("Pool creation failed"));
        }
      }
      if (status.isFinalized) {
        console.log("Finalized!");
        resolve();
      }
    });
  });

  await new Promise(r => setTimeout(r, 3000));

  // Check results
  const poolCount = await api.rpc.ammDex.getPoolCount();
  console.log("Pool count:", poolCount.toString());

  const allPools = await api.rpc.ammDex.getAllPools();
  for (const p of allPools) {
    console.log("Pool #" + p.id.toString() + ": " + 
      Buffer.from(p.tokenA).toString("utf8") + "/" + Buffer.from(p.tokenB).toString("utf8") +
      " reserves: " + (p.reserveA.toNumber() / UNITS) + " / " + (p.reserveB.toNumber() / UNITS));
  }

  await api.disconnect();
}

main().catch(e => { console.error(e.message); process.exit(1); });
