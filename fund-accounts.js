const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');

async function main() {
    const ws = new WsProvider('ws://localhost:9948');
    const api = await ApiPromise.create({ provider: ws });
    const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
    
    const names = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve'];
    const pairs = names.map(n => keyring.addFromUri('//' + n));
    
    // Print addresses
    console.log('=== Account Addresses ===');
    for (let i = 0; i < pairs.length; i++) {
        const account = await api.query.system.account(pairs[i].publicKey);
        const bal = account.data.free.toString();
        console.log(names[i] + ': ' + pairs[i].address + ' | Balance: ' + (parseInt(bal) / 1e9).toFixed(0) + ' VRS | Nonce: ' + account.nonce.toString());
    }
    
    // Fund Bob, Charlie, Dave, Eve with 10B VRS each from Alice
    console.log('');
    console.log('=== Funding accounts ===');
    
    const FUND_AMOUNT = '10000000000000'; // 10B VRS (10,000,000,000 * 1e9)
    
    // Get Alice's nonce
    const aliceAccount = await api.query.system.account(pairs[0].publicKey);
    let nonce = aliceAccount.nonce.toNumber();
    
    for (let i = 1; i < 5; i++) {
        const tx = api.tx.balances.transferAllowDeath(pairs[i].publicKey, FUND_AMOUNT);
        await tx.signAsync(pairs[0], { nonce: nonce++ });
        const result = await api.rpc.author.submitExtrinsic(tx.toHex());
        console.log('Funded ' + names[i] + ': ' + result.toHex());
        await new Promise(r => setTimeout(r, 2000));
    }
    
    // Wait for transactions to be included
    console.log('');
    console.log('Waiting 10s for transactions...');
    await new Promise(r => setTimeout(r, 10000));
    
    // Check balances
    console.log('');
    console.log('=== Updated Balances ===');
    for (let i = 0; i < pairs.length; i++) {
        const account = await api.query.system.account(pairs[i].publicKey);
        const bal = account.data.free.toString();
        console.log(names[i] + ': ' + (parseInt(bal) / 1e9).toFixed(0) + ' VRS | Nonce: ' + account.nonce.toString());
    }
    
    process.exit(0);
}

main().catch(e => { console.error('Fatal:', e); process.exit(1); });
