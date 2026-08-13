const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');

async function main() {
    const ws = new WsProvider('ws://localhost:9948');
    const api = await ApiPromise.create({ provider: ws });
    const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
    const alice = keyring.addFromUri('//Alice');
    const bob = keyring.addFromUri('//Bob');
    
    console.log('Alice:', alice.address);
    console.log('Alice pubkey:', '0x' + Buffer.from(alice.publicKey).toString('hex'));
    console.log('Bob:', bob.address);
    
    // Get nonce via storage query (not RPC)
    const account = await api.query.system.account(alice.publicKey);
    console.log('Account nonce:', account.nonce.toString());
    const nonce = account.nonce.toNumber();
    
    // Create transfer
    const tx = api.tx.balances.transferAllowDeath(bob.publicKey, '1000000000000');
    console.log('TX created, method:', tx.method.toHex().slice(0, 40));
    
    // Sign manually
    console.log('Signing...');
    await tx.signAsync(alice, { nonce });
    console.log('Signed. Extrinsic:', tx.toHex().slice(0, 80));
    
    // Submit manually
    console.log('Submitting...');
    try {
        const result = await api.rpc.author.submitExtrinsic(tx.toHex());
        console.log('SUCCESS! Hash:', result.toHex());
    } catch (e) {
        console.error('SUBMIT ERROR:', e.message);
    }
    
    process.exit(0);
}

main().catch(e => { console.error('FATAL:', e); process.exit(1); });
