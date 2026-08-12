const { ApiPromise, WsProvider } = require('@polkadot/api');
const { Keyring } = require('@polkadot/keyring');
const { cryptoWaitReady } = require('@polkadot/util-crypto');

async function main() {
    await cryptoWaitReady();
    
    // Connect to local node
    const ws = new WsProvider('ws://127.0.0.1:9944');
    const api = await ApiPromise.create({ provider: ws });
    
    // Alice's mnemonic (well-known test account)
    const mnemonic = 'bottom drive obey lake curtain smoke basket hold race lonely fit walk';
    const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
    const alice = keyring.addFromMnemonic(mnemonic);
    
    console.log('Signer address:', alice.address);
    
    // Get nonce
    const nonce = (await api.rpc.system.accountNextIndex(alice.address)).toNumber();
    console.log('Nonce:', nonce);
    
    // Get genesis hash
    const genesisHash = api.genesisHash.toString();
    console.log('Genesis hash:', genesisHash);
    
    // Get spec version
    const runtimeVersion = await api.rpc.state.getRuntimeVersion();
    const specVersion = runtimeVersion.specVersion.toNumber();
    console.log('Spec version:', specVersion);
    
    // Current block hash
    const blockHash = (await api.rpc.chain.getBlockHash()).toString();
    console.log('Block hash:', blockHash);
    
    // Create transfer: 1 VRDX to Bob
    const bob = keyring.addFromUri('//Bob');
    console.log('Recipient (Bob):', bob.address);
    
    const amount = 1 * 1e9; // 1 VRDX in atoms (9 decimals)
    
    // Create signed extrinsic
    const tx = api.tx.balances.transfer(bob.address, amount);
    
    // Sign it
    await tx.signAsync(alice, { nonce, era: { period: 0 }, blockHash: genesisHash });
    
    // Get the signed extrinsic hex
    const signedHex = tx.toHex();
    console.log('Signed extrinsic:', signedHex);
    console.log('Extrinsic length:', signedHex.length, 'chars');
    
    // Also log the call data for comparison
    const callData = tx.method.toHex();
    console.log('Call data:', callData);
    
    // Submit via TX Relay v3
    const http = require('http');
    const data = JSON.stringify({
        action: 'submit-extrinsic',
        extrinsic: signedHex
    });
    
    const options = {
        hostname: '127.0.0.1',
        port: 5001,
        path: '/',
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    };
    
    const req = http.request(options, (res) => {
        let body = '';
        res.on('data', (chunk) => body += chunk);
        res.on('end', () => {
            console.log('TX Relay response:', body);
            process.exit(0);
        });
    });
    req.on('error', (e) => {
        console.error('Error:', e.message);
        process.exit(1);
    });
    req.write(data);
    req.end();
}

main().catch(e => { console.error(e); process.exit(1); });
