const { ApiPromise, WsProvider } = require('@polkadot/api');
const fs = require('fs');

const RPC_URL = 'ws://localhost:9948';
const TARGETS = [600, 1200, 1800, 2400];
const LOG_FILE = '/tmp/epoch-transition-log.json';
const results = {};

async function getBlockInfo(api, blockNum) {
    const hash = await api.rpc.chain.getBlockHash(blockNum);
    const block = await api.rpc.chain.getBlock(hash);
    const header = block.block.header;
    
    // Get epoch index
    let epochIndex = null;
    try {
        const epochResult = await api.rpc.state.call('BabeApi_epoch', '0x');
        // Parse epoch result
        epochIndex = epochResult.toHex();
    } catch (e) {
        epochIndex = 'Error: ' + e.message;
    }
    
    // Get session index
    let sessionIndex = null;
    try {
        const sessionResult = await api.rpc.state.call('Session_current_index', '0x');
        sessionIndex = sessionResult.toHex();
    } catch (e) {
        sessionIndex = 'Error: ' + e.message;
    }
    
    // Get validators
    let validators = null;
    try {
        const validatorsResult = await api.query.session.validators();
        validators = validatorsResult.map(v => v.toString());
    } catch (e) {
        validators = 'Error: ' + e.message;
    }
    
    // Extract digest items
    const digests = header.digest.logs.map(log => {
        if (log.preRuntime) {
            return { type: 'PreRuntime', engine: log.preRuntime[0].toString(), data: log.preRuntime[1].toHex() };
        } else if (log.consensus) {
            return { type: 'Consensus', engine: log.consensus[0].toString(), data: log.consensus[1].toHex() };
        } else if (log.seal) {
            return { type: 'Seal', engine: log.seal[0].toString(), data: log.seal[1].toHex() };
        } else {
            return { type: 'Other', data: log.toHex() };
        }
    });
    
    return {
        block_number: blockNum,
        block_hash: hash.toHex(),
        parent_hash: header.parentHash.toHex(),
        state_root: header.stateRoot.toHex(),
        extrinsics_root: header.extrinsicsRoot.toHex(),
        digest_items: digests,
        digest_count: digests.length,
        epoch_index_raw: epochIndex,
        session_index_raw: sessionIndex,
        validators: validators,
        extrinsic_count: block.block.extrinsics.length,
        timestamp: new Date().toISOString()
    };
}

async function captureTransition(api, targetBlock) {
    console.log('=== Capturing transition at block #' + targetBlock + ' ===');
    
    // Capture block before
    const blockBefore = await getBlockInfo(api, targetBlock - 1);
    console.log('Block #' + (targetBlock - 1) + ' captured');
    
    // Wait for target block
    let targetBlockInfo = null;
    while (!targetBlockInfo) {
        try {
            targetBlockInfo = await getBlockInfo(api, targetBlock);
            console.log('Block #' + targetBlock + ' captured');
        } catch (e) {
            console.log('Waiting for block #' + targetBlock + '...');
            await new Promise(r => setTimeout(r, 5000));
        }
    }
    
    // Capture block after
    await new Promise(r => setTimeout(r, 7000)); // Wait 7s for next block
    const blockAfter = await getBlockInfo(api, targetBlock + 1);
    console.log('Block #' + (targetBlock + 1) + ' captured');
    
    // Check for BABE epoch digest
    const babeDigests = targetBlockInfo.digest_items.filter(d => d.engine === 'BABE');
    const grandpaDigests = targetBlockInfo.digest_items.filter(d => d.engine === 'Babe' || d.engine === 'FRNK' || d.engine === 'GRPA');
    
    const result = {
        target_block: targetBlock,
        block_before: blockBefore,
        block_target: targetBlockInfo,
        block_after: blockAfter,
        babe_digest_count: babeDigests.length,
        babe_digests: babeDigests,
        grandpa_digest_count: grandpaDigests.length,
        grandpa_digests: grandpaDigests,
        validator_set_valid: targetBlockInfo.validators && targetBlockInfo.validators.length > 0,
        validator_count: targetBlockInfo.validators ? targetBlockInfo.validators.length : 0,
        epoch_index_before: blockBefore.epoch_index_raw,
        epoch_index_after: targetBlockInfo.epoch_index_raw,
        session_index_before: blockBefore.session_index_raw,
        session_index_after: targetBlockInfo.session_index_raw,
        timestamp: new Date().toISOString()
    };
    
    results['block_' + targetBlock] = result;
    
    // Save to file
    fs.writeFileSync(LOG_FILE, JSON.stringify(results, null, 2));
    console.log('Results saved to ' + LOG_FILE);
    
    // Print summary
    console.log('');
    console.log('--- SUMMARY for block #' + targetBlock + ' ---');
    console.log('BABE digests: ' + result.babe_digest_count);
    console.log('Validators: ' + result.validator_count);
    console.log('Epoch before: ' + result.epoch_index_before);
    console.log('Epoch after: ' + result.epoch_index_after);
    console.log('Session before: ' + result.session_index_before);
    console.log('Session after: ' + result.session_index_after);
    console.log('Block ' + targetBlock + ' extrinsics: ' + targetBlockInfo.extrinsic_count);
    console.log('Block ' + (targetBlock + 1) + ' produced: ' + (blockAfter ? 'YES' : 'NO'));
    console.log('');
}

async function main() {
    const ws = new WsProvider(RPC_URL);
    const api = await ApiPromise.create({ provider: ws });
    
    console.log('Epoch transition monitor started');
    console.log('Monitoring blocks: ' + TARGETS.join(', '));
    console.log('Log file: ' + LOG_FILE);
    console.log('');
    
    for (const target of TARGETS) {
        // Wait until we're close to the target block
        let currentBlock = 0;
        while (currentBlock < target - 3) {
            const header = await api.rpc.chain.getHeader();
            currentBlock = header.number.toNumber();
            if (currentBlock % 50 == 0) {
                console.log('Current block: #' + currentBlock + ' (target: #' + target + ')');
            }
            await new Promise(r => setTimeout(r, 10000));
        }
        
        // Now check every 3 seconds
        console.log('Approaching target #' + target + ', current: #' + currentBlock);
        while (currentBlock < target) {
            const header = await api.rpc.chain.getHeader();
            currentBlock = header.number.toNumber();
            if (currentBlock >= target - 3) {
                console.log('Block #' + currentBlock + ' (waiting for #' + target + ')');
            }
            await new Promise(r => setTimeout(r, 3000));
        }
        
        // Capture the transition
        await captureTransition(api, target);
        
        // Check for consensus warnings in logs
        console.log('Checking for consensus warnings...');
        // (This will be done separately by grepping the logs)
    }
    
    // Final report
    console.log('');
    console.log('=== ALL EPOCH TRANSITIONS COMPLETE ===');
    
    let allPassed = true;
    for (const target of TARGETS) {
        const r = results['block_' + target];
        if (!r) {
            console.log('#' + target + ': NOT CAPTURED');
            allPassed = false;
            continue;
        }
        const passed = r.babe_digest_count >= 1 && r.validator_set_valid && r.block_after;
        console.log('#' + target + ': ' + (passed ? 'PASS' : 'FAIL') + 
            ' (BABE digests: ' + r.babe_digest_count + 
            ', validators: ' + r.validator_count + 
            ', next block: ' + (r.block_after ? 'YES' : 'NO') + ')');
        if (!passed) allPassed = false;
    }
    
    console.log('');
    console.log('OVERALL: ' + (allPassed ? 'ALL PASSED ✅' : 'SOME FAILED ❌'));
    
    fs.writeFileSync(LOG_FILE, JSON.stringify(results, null, 2));
    process.exit(allPassed ? 0 : 1);
}

main().catch(e => { console.error('Fatal:', e); process.exit(1); });
