#!/usr/bin/env python3
"""Fix the loadTransactions function to handle byte arrays in timestamp extraction."""

TX_PATH = "/var/www/verdiscan/transactions/index.html"

with open(TX_PATH, "r") as f:
    html = f.read()

# Find the timestamp extraction code in loadTransactions and replace it
old_ts_code = '''        if (decoded.section === "timestamp") {
          // Extract timestamp value from hex
          var hex = ext.startsWith("0x") ? ext.slice(2) : ext;
          // timestamp.set has: section(1) + method(1) + compact u64 timestamp
          // For inherent: first 2 bytes are call index, then compact encoded value
          var tsHex = hex.slice(4, 20);
          if (tsHex.length >= 16) {
            // Compact u64: if first byte has high bits, need special decoding
            // Simple case: if first two bits are 00, it's a single-byte mode
            var firstByte = parseInt(tsHex.slice(0, 2), 16);
            if (firstByte < 64) {
              blockTime = firstByte;
            } else if (firstByte < 128) {
              blockTime = parseInt(tsHex.slice(0, 4), 16) >> 2;
            } else {
              // 4-byte mode
              blockTime = parseInt(tsHex.slice(0, 8), 16) >> 2;
            }
            blockTime = blockTime * 1000; // ms
          }
          continue; // Skip timestamp extrinsic in display
        }'''

new_ts_code = '''        if (decoded.section === "timestamp") {
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
          }
          continue;
        }'''

if old_ts_code in html:
    html = html.replace(old_ts_code, new_ts_code)
    print("Timestamp extraction fixed")
else:
    print("Timestamp code not found - trying alternate approach")
    # Try to find it by a shorter marker
    marker = "ext.startsWith(\"0x\") ? ext.slice(2) : ext"
    idx = html.find(marker)
    if idx != -1:
        # Find the broader context
        start = html.rfind("if (decoded.section === \"timestamp\")", max(0, idx-200), idx+10)
        if start != -1:
            end = html.find("continue;", idx)
            if end != -1:
                end = html.find("}", end) + 1
                old_block = html[start:end]
                print(f"Found block at {start}-{end}: {old_block[:100]}...")
                html = html[:start] + new_ts_code + html[end:]
                print("Fixed via alternate approach")

with open(TX_PATH, "w") as f:
    f.write(html)
print(f"Done ({len(html)} bytes)")
