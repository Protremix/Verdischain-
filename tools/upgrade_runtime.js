const { ApiPromise, WsProvider, Keyring } = require("@polkadot/api");
const fs = require("fs");

async function main() {
  const ws = new WsProvider("ws://127.0.0.1:9944");
  const api = await ApiPromise.create({ provider: ws, noDataEvent: true });
  
  const keyring = new Keyring({ type: "sr25519" });
  const alice = keyring.addFromUri("//Alice");
  
  const wasm = fs.readFileSync("target/release/wbuild/verdis-runtime/verdis_runtime.compact.compressed.wasm");
  const wasmHex = "0x" + wasm.toString("hex");
  console.log("WASM:", wasm.length, "bytes");
  
  const setCode = api.tx.system.setCode(wasmHex);
  const sudoCall = api.tx.sudo.sudo(setCode);
  
  const account = await api.query.system.account(alice.publicKey);
  const nonce = account.nonce.toNumber();
  console.log("Nonce:", nonce);
  
  const signed = await sudoCall.signAsync(alice, { nonce });
  const hex = signed.toHex();
  console.log("Extrinsic length:", hex.length);
  
  try {
    const txHash = await api.rpc.author.submitExtrinsic(hex);
    console.log("Tx hash:", txHash.toHex());
  } catch(e) {
    console.log("Submit error:", e.message);
  }
  
  console.log("Waiting 60s...");
  await new Promise(r => setTimeout(r, 60000));
  
  const ver = await api.rpc.state.getRuntimeVersion();
  console.log("spec_version:", ver.specVersion.toNumber());
  
  const header = await api.rpc.chain.getHeader();
  console.log("Block:", header.number.toString());
  
  process.exit(0);
}

main().catch(e => { console.error("ERROR:", e.message); process.exit(1); });
