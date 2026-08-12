#!/usr/bin/env python3
"""Replace the sequential loadTransactions with parallel batch version."""

with open('/var/www/verdiscan/transactions/index.html', 'r') as f:
    content = f.read()

old_func = """async function loadTransactions(isRefresh) {
  var tbody = document.getElementById("txTable");
  var countEl = document.getElementById("tableCount");

  if (isRefresh) {
    document.getElementById("refreshBtn").classList.add("spinning");
  }

  countEl.textContent = "Scanning chain...";

  try {
    var hdr = await rpc("chain_getHeader", []);
    var latestBlock = parseInt(hdr.number, 16);
    document.getElementById("heroBlock").textContent = "#" + latestBlock;
    document.getElementById("navBlock").textContent = "#" + latestBlock;

    // Collect transactions from last N blocks
    var blocksToScan = 50;
    var txs = [];

    for (var b = latestBlock; b >= 0 && b > latestBlock - blocksToScan; b--) {
      var hash = await rpc("chain_getBlockHash", [b]);
      if (!hash || hash === "0x" + "0".repeat(64)) continue;

      var block = await rpc("chain_getBlock", [hash]);
      if (!block || !block.block) continue;

      var blockTime = 0;
      var exts = block.block.extrinsics || [];
      var multiCount = exts.length;

      // Get timestamp from first extrinsic (timestamp.set)
      for (var i = 0; i < exts.length; i++) {
        var ext = exts[i];
        var decoded = decodeExtrinsic(ext, b, hash, blockTime);
        if (decoded.section === "timestamp") {
          // Extract timestamp value from byte array or hex string
          var tsBytes;
          if (Array.isArray(ext)) {
            tsBytes = ext;
          } else {
            var hex = ext.startsWith("0x") ? ext.slice(2) : ext;
            tsBytes = [];
            for (var bi = 0; bi < hex.length; bi += 2) { tsBytes.push(parseInt(hex.substr(bi, 2), 16)); }
          }
          // With 2-byte prefix: [prefix2] [section=1] [method=0] [compact_u64_timestamp]
          // Call index at offset 2-3, timestamp starts at offset 4
          var tsOffset = 4;
          if (tsOffset < tsBytes.length) {
            var first = tsBytes[tsOffset];
            var mode = first & 0x03;
            if (mode === 0) { blockTime = (first >> 2) * 1000; }
            else if (mode === 1 && tsOffset + 1 < tsBytes.length) { blockTime = ((first | (tsBytes[tsOffset+1] << 8)) >> 2) * 1000; }
            else if (mode === 2 && tsOffset + 3 < tsBytes.length) { blockTime = ((first | (tsBytes[tsOffset+1] << 8) | (tsBytes[tsOffset+2] << 16) | (tsBytes[tsOffset+3] << 24)) >>> 2) * 1000; } 
          else if (mode === 3) { var bigLen = (first >> 2) + 4; var val = 0; for (var bi = 1; bi <= bigLen && tsOffset + bi < tsBytes.length; bi++) { val += tsBytes[tsOffset + bi] * Math.pow(256, bi - 1); } blockTime = val; }
          }
          continue;
        }

        // Skip inherent/timestamp entries
        if (decoded.section === "inherent" || decoded.fullType === "unknown") {
          continue;
        }

        // Apply remark filter
        if (excludeRemarks && decoded.fullType === "system.remark") continue;

        // Set block time for all txs in this block
        decoded.time = blockTime;
        decoded.multiInstr = multiCount > 3;

        txs.push(decoded);
      }
    }

    allTransactions = txs;
    txCount += txs.length;
    document.getElementById("heroTxCount").textContent = txCount;

    // Calculate TPS
    if (txs.length > 0) {
      var tps = (txs.length / blocksToScan).toFixed(1);
      document.getElementById("heroTps").textContent = tps;
    }

    renderTable();
    document.getElementById("refreshBtn").classList.remove("spinning");
  } catch(e) {
    console.error("Load error:", e);
    tbody.innerHTML = '<tr class="empty-state"><td colspan="9">Error loading transactions: ' + e.message + '</td></tr>';
    document.getElementById("refreshBtn").classList.remove("spinning");
  }
}"""

new_func = """async function loadTransactions(isRefresh) {
  var tbody = document.getElementById("txTable");
  var countEl = document.getElementById("tableCount");

  if (isRefresh) {
    document.getElementById("refreshBtn").classList.add("spinning");
  }

  countEl.textContent = "Scanning chain...";

  try {
    var hdr = await rpc("chain_getHeader", []);
    var latestBlock = parseInt(hdr.number, 16);
    document.getElementById("heroBlock").textContent = "#" + latestBlock;
    document.getElementById("navBlock").textContent = "#" + latestBlock;

    var blocksToScan = 50;
    var batchSize = 10;
    var txs = [];

    // Build list of block numbers to scan
    var blockNums = [];
    for (var b = latestBlock; b >= 0 && b > latestBlock - blocksToScan; b--) {
      blockNums.push(b);
    }

    // Fetch block hashes in parallel batches
    for (var i = 0; i < blockNums.length; i += batchSize) {
      var batch = blockNums.slice(i, i + batchSize);
      var hashPromises = batch.map(function(bn) { return rpc("chain_getBlockHash", [bn]); });
      var hashes = await Promise.all(hashPromises);

      // Fetch block data in parallel
      var blockPromises = [];
      for (var j = 0; j < batch.length; j++) {
        if (!hashes[j] || hashes[j] === "0x" + "0".repeat(64)) {
          blockPromises.push(Promise.resolve(null));
        } else {
          blockPromises.push(rpc("chain_getBlock", [hashes[j]]));
        }
      }
      var blocks = await Promise.all(blockPromises);

      // Process each block
      for (var k = 0; k < blocks.length; k++) {
        var block = blocks[k];
        if (!block || !block.block) continue;

        var bn = batch[k];
        var bh = hashes[k];
        var blockTime = 0;
        var exts = block.block.extrinsics || [];
        var multiCount = exts.length;

        // Get timestamp from first extrinsic (timestamp.set)
        for (var xi = 0; xi < exts.length; xi++) {
          var ext = exts[xi];
          var decoded = decodeExtrinsic(ext, bn, bh, blockTime);
          if (decoded.section === "timestamp") {
            // Extract timestamp value
            var tsBytes;
            if (Array.isArray(ext)) {
              tsBytes = ext;
            } else {
              var hex = ext.startsWith("0x") ? ext.slice(2) : ext;
              tsBytes = [];
              for (var bi = 0; bi < hex.length; bi += 2) { tsBytes.push(parseInt(hex.substr(bi, 2), 16)); }
            }
            var tsOffset = 4;
            if (tsOffset < tsBytes.length) {
              var first = tsBytes[tsOffset];
              var mode = first & 0x03;
              if (mode === 0) { blockTime = (first >> 2) * 1000; }
              else if (mode === 1 && tsOffset + 1 < tsBytes.length) { blockTime = ((first | (tsBytes[tsOffset+1] << 8)) >> 2) * 1000; }
              else if (mode === 2 && tsOffset + 3 < tsBytes.length) { blockTime = ((first | (tsBytes[tsOffset+1] << 8) | (tsBytes[tsOffset+2] << 16) | (tsBytes[tsOffset+3] << 24)) >>> 2) * 1000; }
              else if (mode === 3) { var bigLen = (first >> 2) + 4; var val = 0; for (var bi = 1; bi <= bigLen && tsOffset + bi < tsBytes.length; bi++) { val += tsBytes[tsOffset + bi] * Math.pow(256, bi - 1); } blockTime = val; }
            }
            continue;
          }

          // Skip inherent/timestamp entries
          if (decoded.section === "inherent" || decoded.fullType === "unknown") {
            continue;
          }

          // Apply remark filter
          if (excludeRemarks && decoded.fullType === "system.remark") continue;

          // Set block time for all txs in this block
          decoded.time = blockTime;
          decoded.multiInstr = multiCount > 3;

          txs.push(decoded);
        }
      }
    }

    allTransactions = txs;
    txCount = txs.length;
    document.getElementById("heroTxCount").textContent = txCount;

    // Calculate TPS
    if (txs.length > 0) {
      var tps = (txs.length / blocksToScan).toFixed(1);
      document.getElementById("heroTps").textContent = tps;
    } else {
      document.getElementById("heroTps").textContent = "0.0";
    }

    renderTable();
    document.getElementById("refreshBtn").classList.remove("spinning");
  } catch(e) {
    console.error("Load error:", e);
    tbody.innerHTML = '<tr class="empty-state"><td colspan="9">Error loading transactions: ' + e.message + '</td></tr>';
    document.getElementById("refreshBtn").classList.remove("spinning");
  }
}"""

if old_func in content:
    content = content.replace(old_func, new_func, 1)
    with open('/var/www/verdiscan/transactions/index.html', 'w') as f:
        f.write(content)
    print("PATCHED: loadTransactions now uses parallel batch fetching")
else:
    print("NOT FOUND")
