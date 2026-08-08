import re

with open("/var/www/verdiscan/explorer/index.html", "r") as f:
    content = f.read()

# Find and replace the loadLatestBlocks function
# Use regex to match the function from "async function loadLatestBlocks" to the closing "}"
# followed by the loadLatestExtrinsics function

old_start = "async function loadLatestBlocks() {"
old_end = "  // Load latest extrinsics\n  loadLatestExtrinsics();\n}"

idx_start = content.find(old_start)
if idx_start == -1:
    print("ERROR: Could not find loadLatestBlocks function")
    exit(1)

# Find the end - look for the loadLatestExtrinsics call and closing brace
idx_end = content.find(old_end, idx_start)
if idx_end == -1:
    print("ERROR: Could not find end of function")
    exit(1)

idx_end += len(old_end)

new_func = '''async function loadLatestBlocks() {
  const tbody = document.getElementById('latestBlocks');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="4"><span class="skel" style="width:100%"></span></td></tr>';
  
  const header = await rpc('chain_getHeader', []);
  if (!header) { tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text-3)">Failed to load</td></tr>'; return; }
  
  const current = parseInt(header.number, 16);
  blockNum = current;
  document.getElementById('statBlock').textContent = '#'+current;
  document.getElementById('statBlockSub').textContent = 'Block time: 6s';
  document.getElementById('heroBlock').textContent = '#'+current;
  
  const finalHead = await rpc('chain_getFinalizedHead', []);
  if (finalHead) {
    const finalHeader = await rpc('chain_getHeader', [finalHead]);
    if (finalHeader) {
      finalNum = parseInt(finalHeader.number, 16);
      document.getElementById('statFinal').textContent = '#'+finalNum;
      document.getElementById('statFinalSub').textContent = Math.max(0, current - finalNum) + ' blocks behind';
    }
  }
  
  blocksData.length = 0;
  const blockNums = [];
  for (let i = 0; i < 6; i++) { if (current - i >= 0) blockNums.push(current - i); }
  
  const blockPromises = blockNums.map(function(bn) {
    return rpc('chain_getBlockHash', [bn]).then(function(h) {
      if (!h) return null;
      return rpc('chain_getBlock', [h]).then(function(b) {
        return {bn: bn, hash: h, block: b};
      });
    });
  });
  const results = await Promise.all(blockPromises);
  
  var html = '';
  for (var i = 0; i < results.length; i++) {
    var r = results[i];
    if (!r || !r.block) continue;
    var exts = (r.block.block && r.block.block.extrinsics) || [];
    html += '<tr onclick="showBlock(\\''+r.hash+'\\')"><td class="hash hash-accent">#'+r.bn+'</td><td>'+(i===0?'0s ago':(i*6)+'s ago')+'</td><td>'+exts.length+'</td><td class="hash">'+shortHash(r.hash)+'</td></tr>';
    blocksData.push({num:r.bn, hash:r.hash, exts:exts, time:Date.now()-i*6000});
  }
  tbody.innerHTML = html || '<tr><td colspan="4" style="text-align:center;color:var(--text-3)">No blocks</td></tr>';
  
  loadLatestExtrinsics();
}'''

content = content[:idx_start] + new_func + content[idx_end:]

with open("/var/www/verdiscan/explorer/index.html", "w") as f:
    f.write(content)

print("Fixed - parallel block loading!")
