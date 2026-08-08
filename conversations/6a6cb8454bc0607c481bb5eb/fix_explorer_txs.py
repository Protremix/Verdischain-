#!/usr/bin/env python3
"""Fix Verdiscan explorer to show signed transactions prominently."""

WEB_ROOT = "/var/www/verdiscan"
path = WEB_ROOT + "/explorer/index.html"
content = open(path).read()

# 1. Fix loadLatestExtrinsics to only show SIGNED extrinsics
old_func = """// Load latest extrinsics
async function loadLatestExtrinsics() {
  const tbody = document.getElementById('latestExts');
  if (!tbody) return;
  let html = '';
  let count = 0;
  for (let i = 0; i < blocksData.length && count < 6; i++) {
    const b = blocksData[i];
    const exts = b.exts || [];
    for (let j = 0; j < exts.length && count < 6; j++) {
      const ext = decodeExtrinsic(exts[j], b.hash, b.num);
      if (!ext) continue;
      html += '<tr onclick="showBlock(\\''+b.hash+'\\')">' +
        '<td><span class="badge '+ext.badge+'">'+ext.type+'</span></td>' +
        '<td class="hash">'+ext.hash+'</td>' +
        '<td class="hash hash-accent">#'+b.num+'</td>' +
        '</tr>';
      count++;
    }
  }
  tbody.innerHTML = html || '<tr><td colspan="3" style="text-align:center;color:var(--text-3)">No extrinsics</td></tr>';
}"""

new_func = """// Load latest extrinsics (SIGNED only - real transactions)
async function loadLatestExtrinsics() {
  const tbody = document.getElementById('latestExts');
  if (!tbody) return;
  let html = '';
  let count = 0;
  for (let i = 0; i < blocksData.length && count < 8; i++) {
    const b = blocksData[i];
    const exts = b.exts || [];
    for (let j = 0; j < exts.length && count < 8; j++) {
      const ext = decodeExtrinsic(exts[j], b.hash, b.num);
      if (!ext) continue;
      if (ext.type !== 'Signed') continue; // Skip inherent/timestamp
      const remarkShort = ext.remark ? ext.remark.substring(0, 35) : '';
      html += '<tr onclick="showBlock(\\''+b.hash+'\\')" style="cursor:pointer">' +
        '<td><span class="badge '+ext.badge+'">'+ext.type+'</span></td>' +
        '<td>' + ext.method + (remarkShort ? '<br><span style="font-size:11px;color:var(--text-3)">'+remarkShort+'</span>' : '') + '</td>' +
        '<td class="hash">'+ext.hash+'</td>' +
        '<td class="hash hash-accent">#'+b.num+'</td>' +
        '</tr>';
      count++;
    }
  }
  // If no signed extrinsics found, show message
  if (count === 0) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text-3);padding:24px">Waiting for signed transactions...</td></tr>';
  } else {
    tbody.innerHTML = html;
  }
}"""

if old_func in content:
    content = content.replace(old_func, new_func)
    print("OK: loadLatestExtrinsics updated to show SIGNED only")
else:
    print("SKIP: loadLatestExtrinsics not found - trying alternate match")
    # Try a more relaxed match
    import re
    pattern = re.compile(r"// Load latest extrinsics\nasync function loadLatestExtrinsics\(\).*?\n\}", re.DOTALL)
    match = pattern.search(content)
    if match:
        content = content[:match.start()] + new_func + content[match.end():]
        print("OK: loadLatestExtrinsics updated (regex match)")
    else:
        print("FAIL: could not find loadLatestExtrinsics function")

# 2. Update the table headers for latestExts to include METHOD/DATA column
old_header = '<table class="tbl"><thead><tr><th>TYPE</th><th>EXTRINSIC HASH</th><th>BLOCK</th></tr></thead><tbody id="latestExts"></tbody></table>'
new_header = '<table class="tbl"><thead><tr><th>TYPE</th><th>METHOD / DATA</th><th>HASH</th><th>BLOCK</th></tr></thead><tbody id="latestExts"></tbody></table>'

if old_header in content:
    content = content.replace(old_header, new_header)
    print("OK: latestExts table headers updated")
else:
    print("SKIP: latestExts table header not found")

# 3. Also update loadExtrinsics to fetch more blocks if needed for more signed txs
# Currently it only uses blocksData (10 blocks from overview). Let's make it fetch 30 blocks.
old_load_ext = """// Load all extrinsics
async function loadExtrinsics() {
  const tbody = document.getElementById('allExts');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="6"><span class="skel" style="width:100%"></span></td></tr>';
  let html = '';
  for (let i = 0; i < blocksData.length; i++) {"""

new_load_ext = """// Load all extrinsics (fetch more blocks for signed txs)
async function loadExtrinsics() {
  const tbody = document.getElementById('allExts');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="6"><span class="skel" style="width:100%"></span></td></tr>';
  // Fetch 30 blocks worth of extrinsics
  const hdr = await rpc('chain_getHeader', []);
  const currentBlock = hdr ? parseInt(hdr.number, 16) : blockNum;
  let allExts = [];
  if (currentBlock > 0) {
    const fetchCount = 30;
    const promises = [];
    for (let i = 0; i < fetchCount; i++) {
      const bn = currentBlock - i;
      if (bn < 0) break;
      promises.push(rpc('chain_getBlockHash', [bn]).then(function(h) {
        if (!h) return null;
        return rpc('chain_getBlock', [h]).then(function(b) {
          return {num: bn, hash: h, exts: (b && b.block && b.block.extrinsics) || []};
        });
      }));
    }
    const results = await Promise.all(promises);
    for (const r of results) {
      if (r && r.exts.length > 0) allExts.push(r);
    }
  }
  let html = '';
  for (let i = 0; i < allExts.length; i++) {
    const b = allExts[i];
    const exts = b.exts || [];"""

if old_load_ext in content:
    content = content.replace(old_load_ext, new_load_ext)
    # Also fix the closing part of loadExtrinsics
    old_close = """  tbody.innerHTML = html || '<tr><td colspan="6" style="text-align:center;color:var(--text-3)">No extrinsics</td></tr>';
}

// Load validators"""

    new_close = """  tbody.innerHTML = html || '<tr><td colspan="6" style="text-align:center;color:var(--text-3)">No extrinsics</td></tr>';
}

// Load validators"""
    
    if old_close in content:
        content = content.replace(old_close, new_close)
        print("OK: loadExtrinsics updated to fetch 30 blocks")
    else:
        print("SKIP: loadExtrinsics closing not found")
else:
    print("SKIP: loadExtrinsics not found")

open(path, "w").write(content)
print(f"\nFile size: {len(content)} bytes")
print("Done!")
