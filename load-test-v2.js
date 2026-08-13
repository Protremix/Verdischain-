const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');
const fs = require('fs');
const { execSync } = require('child_process');

const RPC_URL = 'ws://localhost:9948';
const TX_COUNT = parseInt(process.argv[2] || '100000');
const AMOUNT = '100000000'; // 0.1 VRS (low amount to preserve balance)

function getMem() { try { return parseInt(execSync('free -m | grep Mem').toString().split(/\s+/)[2]); } catch(e) { return 0; } }
function getDb() { try { return parseInt(execSync('du -s /opt/verdis-data/val-1').toString().split(/\s+/)[0]); } catch(e) { return 0; } }

async function main() {
    const ws = new WsProvider(RPC_URL);
    const api = await ApiPromise.create({ provider: ws });
    const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
    
    const names = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve'];
    const pairs = names.map(n => keyring.addFromUri('//' + n));
    
    // Each account sends to the next, forming a ring
    // Alice->Bob, Bob->Charlie, Charlie->Dave, Dave->Eve, Eve->Alice
    
    // Get initial nonces
    const nonces = [];
    for (const pair of pairs) {
        const account = await api.query.system.account(pair.publicKey);
        nonces.push(account.nonce.toNumber());
    }
    
    const memBefore = getMem();
    const dbBefore = getDb();
    const txPerAccount = Math.ceil(TX_COUNT / 5);
    
    console.log('=== Verdis Load Test v2 ===');
    console.log('TX count:', TX_COUNT, '(' + txPerAccount + ' per account)');
    console.log('Workers: 5 (one per account, sequential)');
    console.log('Initial nonces:', nonces);
    console.log('Baseline memory (MB):', memBefore);
    console.log('Baseline DB (KB):', dbBefore);
    console.log('');
    
    let success = 0;
    let fail = 0;
    const latencies = [];
    const startTime = Date.now();
    let txIndex = 0;
    
    // 5 sequential workers, one per account
    const workers = pairs.map((sender, i) => {
        return (async () => {
            const recipient = pairs[(i + 1) % 5];
            let nonce = nonces[i];
            
            for (let j = 0; j < txPerAccount; j++) {
                const globalIdx = txIndex++;
                const txStart = Date.now();
                let retries = 0;
                
                while (retries < 3) {
                    try {
                        const tx = api.tx.balances.transferAllowDeath(recipient.publicKey, AMOUNT);
                        await tx.signAsync(sender, { nonce });
                        await api.rpc.author.submitExtrinsic(tx.toHex());
                        success++;
                        latencies.push(Date.now() - txStart);
                        nonce++;
                        break;
                    } catch (e) {
                        retries++;
                        if (retries >= 3) {
                            fail++;
                            break;
                        }
                        // Refresh nonce from chain
                        try {
                            const account = await api.query.system.account(sender.publicKey);
                            nonce = account.nonce.toNumber();
                        } catch(e2) {}
                        await new Promise(r => setTimeout(r, 1000));
                    }
                }
                
                if ((j + 1) % 1000 === 0) {
                    const elapsed = (Date.now() - startTime) / 1000;
                    const tps = (success / elapsed).toFixed(1);
                    console.log(names[i] + ': ' + (j + 1) + '/' + txPerAccount + ' | Global TPS: ' + tps + ' | OK: ' + success + ' | Fail: ' + fail);
                }
            }
        })();
    });
    
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
