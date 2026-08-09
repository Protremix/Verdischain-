const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');
const fs = require('fs');
const { execSync } = require('child_process');

const RPC_URL = 'ws://localhost:9948';
const TX_COUNT = parseInt(process.argv[2] || '1000');
const CONCURRENCY = parseInt(process.argv[3] || '10');
const AMOUNT = '1000000000'; // 1 VRS

function getMem() {
    try {
        const out = execSync('free -m | grep Mem').toString();
        return parseInt(out.split(/\s+/)[2]);
    } catch(e) { return 0; }
}

function getDb() {
    try {
        const out = execSync('du -s /opt/verdis-data/val-1').toString();
        return parseInt(out.split(/\s+/)[0]);
    } catch(e) { return 0; }
}

async function main() {
    const ws = new WsProvider(RPC_URL);
    const api = await ApiPromise.create({ provider: ws });
    const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
    
    const pairs = [
        keyring.addFromUri('//Alice'),
        keyring.addFromUri('//Bob'),
        keyring.addFromUri('//Charlie'),
        keyring.addFromUri('//Dave'),
        keyring.addFromUri('//Eve'),
    ];
    
    const nonces = [];
    for (const pair of pairs) {
        const account = await api.query.system.account(pair.publicKey);
        nonces.push(account.nonce.toNumber());
    }
    
    const memBefore = getMem();
    const dbBefore = getDb();
    
    console.log('=== Verdis Load Test ===');
    console.log('TX count:', TX_COUNT);
    console.log('Concurrency:', CONCURRENCY);
    console.log('Initial nonces:', nonces);
    console.log('Baseline memory (MB):', memBefore);
    console.log('Baseline DB (KB):', dbBefore);
    console.log('');
    
    let success = 0;
    let fail = 0;
    const latencies = [];
    const startTime = Date.now();
    let txIndex = 0;
    
    const workers = [];
    for (let w = 0; w < CONCURRENCY; w++) {
        workers.push((async () => {
            while (true) {
                const i = txIndex++;
                if (i >= TX_COUNT) break;
                
                const senderIdx = i % 5;
                const recipientIdx = (i + 1) % 5;
                const sender = pairs[senderIdx];
                const recipient = pairs[recipientIdx];
                
                const txStart = Date.now();
                try {
                    const nonce = nonces[senderIdx]++;
                    const tx = api.tx.balances.transferAllowDeath(recipient.publicKey, AMOUNT);
                    await tx.signAsync(sender, { nonce });
                    await api.rpc.author.submitExtrinsic(tx.toHex());
                    success++;
                    latencies.push(Date.now() - txStart);
                } catch (e) {
                    fail++;
                    try {
                        const account = await api.query.system.account(sender.publicKey);
                        nonces[senderIdx] = account.nonce.toNumber() + 1;
                    } catch (e2) {}
                }
                
                if ((i + 1) % 500 === 0) {
                    const elapsed = (Date.now() - startTime) / 1000;
                    const tps = (success / elapsed).toFixed(1);
                    console.log('TX ' + (i + 1) + '/' + TX_COUNT + ' | TPS: ' + tps + ' | OK: ' + success + ' | Fail: ' + fail);
                }
            }
        })());
    }
    
    await Promise.all(workers);
    
    const duration = (Date.now() - startTime) / 1000;
    const memAfter = getMem();
    const dbAfter = getDb();
    
    latencies.sort((a, b) => a - b);
    const avgLat = latencies.reduce((s, v) => s + v, 0) / (latencies.length || 1);
    const p50 = latencies[Math.floor(latencies.length * 0.5)] || 0;
    const p90 = latencies[Math.floor(latencies.length * 0.9)] || 0;
    const p99 = latencies[Math.floor(latencies.length * 0.99)] || 0;
    
    console.log('');
    console.log('=== Results ===');
    console.log('Total:', TX_COUNT, '| Success:', success, '| Fail:', fail);
    console.log('Duration:', duration.toFixed(2), 's');
    console.log('TPS:', (success / duration).toFixed(1));
    console.log('Latency (ms): min=' + latencies[0] + ' avg=' + avgLat.toFixed(0) + ' p50=' + p50 + ' p90=' + p90 + ' p99=' + p99 + ' max=' + latencies[latencies.length - 1]);
    console.log('Memory (MB): before=' + memBefore + ' after=' + memAfter + ' delta=' + (memAfter - memBefore));
    console.log('DB (KB): before=' + dbBefore + ' after=' + dbAfter + ' delta=' + (dbAfter - dbBefore));
    
    const results = {
        tx_count: TX_COUNT, success, fail, duration_s: duration, tps: success / duration,
        latency_ms: { min: latencies[0], avg: avgLat, p50, p90, p99, max: latencies[latencies.length - 1] },
        memory_mb: { before: memBefore, after: memAfter },
        db_kb: { before: dbBefore, after: dbAfter },
        timestamp: new Date().toISOString()
    };
    fs.writeFileSync('/tmp/load-test-results.json', JSON.stringify(results, null, 2));
    console.log('Saved to /tmp/load-test-results.json');
    process.exit(0);
}

main().catch(e => { console.error('Fatal:', e); process.exit(1); });
