#!/usr/bin/env python3
"""Fix XSS in explorer - targeted replacements based on actual code patterns."""

PATH = "/var/www/verdiscan/explorer/index.html"

with open(PATH, "r") as f:
    html = f.read()

r = 0

# Line 1833: ext.method and remarkText not escaped
old = "'<td>' + (ext.method || 'unknown') + (remarkText ? '<br><span style=\"font-size:11px;color:var(--text-3)\">'+remarkText+'</span>' : '') + '</td>' +"
new = "'<td>' + escapeHtml(ext.method || 'unknown') + (remarkText ? '<br><span style=\"font-size:11px;color:var(--text-3)\">'+escapeHtml(remarkText)+'</span>' : '') + '</td>' +"
if old in html:
    html = html.replace(old, new)
    r += 1
    print("Fixed line ~1833: ext.method + remarkText")

# Line 1926: ext.method in badge
old = "'<td><span class=\"badge badge-signed\">' + (ext.method || 'unknown') + '</span></td>' +"
new = "'<td><span class=\"badge badge-signed\">' + escapeHtml(ext.method || 'unknown') + '</span></td>' +"
if old in html:
    html = html.replace(old, new)
    r += 1
    print("Fixed line ~1926: ext.method badge")

# Line 1927: signerDisplay
old = "'<td class=\"hash\">' + signerDisplay + '</td>' +"
new = "'<td class=\"hash\">' + escapeHtml(signerDisplay) + '</td>' +"
if old in html:
    html = html.replace(old, new)
    r += 1
    print("Fixed line ~1927: signerDisplay")

# Line 2025: ext.method + remarkDisplay
old = "'<td>'+ext.method+(remarkDisplay ? '<br>'+remarkDisplay : '')+'</td>'"
new = "'<td>'+escapeHtml(ext.method)+(remarkDisplay ? '<br>'+escapeHtml(remarkDisplay) : '')+'</td>'"
if old in html:
    html = html.replace(old, new)
    r += 1
    print("Fixed line ~2025: ext.method + remarkDisplay")

# Line 2209: ext.method in span
old = "'<span style=\"color:var(--text-2);font-size:13px\">'+ext.method+'</span>'"
new = "'<span style=\"color:var(--text-2);font-size:13px\">'+escapeHtml(ext.method)+'</span>'"
if old in html:
    html = html.replace(old, new)
    r += 1
    print("Fixed line ~2209: ext.method in span")

# Fix onclick handlers - signerDisplay not escaped in attributes
# Line 1831: onclick="showExtrinsic(\''+escapeAttr(safeMethod)+'\', '+b.num+', \''+signerDisplay+'\', \''+safeRemark+'\')"
old = "', '+b.num+', '+signerDisplay+'"
new = "', '+b.num+', '+escapeAttr(signerDisplay)+'"
# Actually these are in onclick attributes, need escapeAttr
old2 = "'+signerDisplay+'"
# This is too broad - let's be more specific
# Find the onclick patterns
import re
# Pattern: showExtrinsic(..., signerDisplay, ...)
# Replace signerDisplay with escapeAttr(signerDisplay) in onclick contexts
for pattern in [
    # Line 1831
    ("+signerDisplay+'\", '", "+escapeAttr(signerDisplay)+'\", '"),
    # Line 1923
    ("+signerDisplay+'\", '", "+escapeAttr(signerDisplay)+'\", '"),
]:
    if pattern[0] in html and pattern[1] not in html:
        html = html.replace(pattern[0], pattern[1])
        r += 1
        print(f"Fixed onclick: signerDisplay escaped in attribute")

# Line 2193: parent hash
old = "html += '<dt>Parent Hash</dt><dd>'+(h.parentHash||'\u2014')+'</dd>';"
new = "html += '<dt>Parent Hash</dt><dd>'+escapeHtml(h.parentHash||'\u2014')+'</dd>';"
if old in html:
    html = html.replace(old, new)
    r += 1
    print("Fixed line ~2193: parent hash")

# Check for block hash in modal
old = "html += '<dt>Block Hash</dt><dd class=\"hash\">'+(h.hash||'\u2014')+'</dd>';"
new = "html += '<dt>Block Hash</dt><dd class=\"hash\">'+escapeHtml(h.hash||'\u2014')+'</dd>';"
if old in html:
    html = html.replace(old, new)
    r += 1
    print("Fixed: block hash in modal")
else:
    # Try alternate pattern
    old2 = "html += '<dt>Block Hash</dt><dd class=\"hash\">' + header.hash + '</dd>';"
    new2 = "html += '<dt>Block Hash</dt><dd class=\"hash\">' + escapeHtml(header.hash) + '</dd>';"
    if old2 in html:
        html = html.replace(old2, new2)
        r += 1
        print("Fixed: block hash in modal (header.hash)")

# Fix block detail modal - other fields
for old, new in [
    ("+(h.hash||'\u2014')+", "+escapeHtml(h.hash||'\u2014')+"),
    ("+(h.parentHash||'\u2014')+", "+escapeHtml(h.parentHash||'\u2014')+"),
    ("+(h.stateRoot||'\u2014')+", "+escapeHtml(h.stateRoot||'\u2014')+"),
    ("+(h.extrinsicsRoot||'\u2014')+", "+escapeHtml(h.extrinsicsRoot||'\u2014')+"),
]:
    if old in html and new not in html:
        html = html.replace(old, new)
        r += 1
        print(f"Fixed: {old[:30]}...")

# Fix extrinsic detail modal fields
for pattern in [
    ("+(ext.signer||'\u2014')+", "+escapeHtml(ext.signer||'\u2014')+"),
    ("+(ext.hash||'\u2014')+", "+escapeHtml(ext.hash||'\u2014')+"),
    ("+(ext.blockHash||'\u2014')+", "+escapeHtml(ext.blockHash||'\u2014')+"),
    ("+(ext.nonce||'\u2014')+", "+escapeHtml(ext.nonce||'\u2014')+"),
    ("+(ext.args||'\u2014')+", "+escapeHtml(ext.args||'\u2014')+"),
    ("+(ext.era||'\u2014')+", "+escapeHtml(ext.era||'\u2014')+"),
    ("+(ext.tip||'0')+", "+escapeHtml(ext.tip||'0')+"),
]:
    if pattern[0] in html and pattern[1] not in html:
        html = html.replace(pattern[0], pattern[1])
        r += 1
        print(f"Fixed: ext field {pattern[0][:25]}...")

# Fix validator metrics modal
for pattern in [
    ("+(v.name||", "+escapeHtml(v.name||"),
    ("+(v.address||", "+escapeHtml(v.address||"),
    ("+(v.controller||", "+escapeHtml(v.controller||"),
    ("+(v.stake||", "+escapeHtml(v.stake||"),
    ("+(v.greenScore||", "+escapeHtml(v.greenScore||"),
    ("+(v.energySource||", "+escapeHtml(v.energySource||"),
]:
    if pattern[0] in html and pattern[1] not in html:
        html = html.replace(pattern[0], pattern[1])
        r += 1
        print(f"Fixed: validator field {pattern[0][:20]}...")

# Fix DEX pool rendering
for pattern in [
    ("+(pool.token0||pool.asset0||'Unknown')+", "+escapeHtml(pool.token0||pool.asset0||'Unknown')+"),
    ("+(pool.token1||pool.asset1||'Unknown')+", "+escapeHtml(pool.token1||pool.asset1||'Unknown')+"),
    ("+(pool.token0||'Unknown')+", "+escapeHtml(pool.token0||'Unknown')+"),
    ("+(pool.token1||'Unknown')+", "+escapeHtml(pool.token1||'Unknown')+"),
    ("+(pool.asset0||'Unknown')+", "+escapeHtml(pool.asset0||'Unknown')+"),
    ("+(pool.asset1||'Unknown')+", "+escapeHtml(pool.asset1||'Unknown')+"),
]:
    if pattern[0] in html and pattern[1] not in html:
        html = html.replace(pattern[0], pattern[1])
        r += 1
        print(f"Fixed: DEX field {pattern[0][:25]}...")

# Fix any remaining raw signerDisplay in innerHTML (not just in td)
count = html.count("+signerDisplay+'")
if count > 0:
    # Replace only in innerHTML contexts (not in variable assignments)
    html = html.replace("+signerDisplay+'", "+escapeHtml(signerDisplay)+'")
    r += 1
    print(f"Fixed: {count} remaining signerDisplay occurrences")

# Fix shortHash results (block hashes are hex, but escape anyway)
for pattern in [
    ("+shortHash(b.hash)+", "+escapeHtml(shortHash(b.hash))+"),
    ("+shortHash(ext.hash)+", "+escapeHtml(shortHash(ext.hash))+"),
    ("+shortHash(h.hash)+", "+escapeHtml(shortHash(h.hash))+"),
]:
    if pattern[0] in html and pattern[1] not in html:
        html = html.replace(pattern[0], pattern[1])
        r += 1
        print(f"Fixed: shortHash {pattern[0][:25]}...")

with open(PATH, "w") as f:
    f.write(html)

print(f"\nTotal: {r} replacements")
