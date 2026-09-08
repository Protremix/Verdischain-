#!/usr/bin/env bash
# The previous comparison was wrong: the on-chain `:code` blob is zstd-compressed with an
# 8-byte Substrate magic prefix (52bc537666db8e99), so regex-scanning it finds nothing and
# every import looked "new". Truncated matches like `ext_key30ext_storage_next_key_version_1`
# are the tell-tale of scanning compressed bytes.
#
# Decompress both blobs first, then compare import sets. Ground truth: the live runtime is
# what mainnet's binaries execute right now, so its imports are certainly available.
set -u
R=/root/audit-fix
NEW=$R/target/release/wbuild/verdis-runtime/verdis_runtime.wasm

echo "############ 1. fetch live :code ############"
rm -f /tmp/old_raw.bin /tmp/old_runtime.wasm
for P in 9944 9945 9946 9947 9948 9949 9960; do
  RES=$(curl -s -m 90 -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","id":1,"method":"state_getStorage","params":["0x3a636f6465"]}' \
        http://127.0.0.1:$P 2>/dev/null)
  echo "$RES" | grep -q '"result":"0x' || continue
  echo "$RES" | sed 's/.*"result":"0x//; s/".*//' | tr -d '\n' > /tmp/code.hex
  python3 -c "
h = open('/tmp/code.hex').read().strip()
open('/tmp/old_raw.bin','wb').write(bytes.fromhex(h))
print(f'  fetched from port $P: {len(h)//2:,} bytes')
" && break
done
[ -s /tmp/old_raw.bin ] || { echo "  FAILED"; exit 1; }

echo ""
echo "############ 2. decompress (Substrate zstd magic 52bc537666db8e99) ############"
pip list 2>/dev/null | grep -qi zstandard || /usr/bin/python3 -m pip install -q zstandard 2>/dev/null
python3 - <<'PY'
MAGIC = bytes.fromhex("52bc537646db8e05")   # sp_maybe_compressed_blob::ZSTD_PREFIX
raw = open("/tmp/old_raw.bin", "rb").read()
print(f"  first 8 bytes: {raw[:8].hex()}")
if raw[:8] == MAGIC:
    print("  -> Substrate-compressed, decompressing")
    try:
        import zstandard as zstd
        out = zstd.ZstdDecompressor().decompress(raw[8:], max_output_size=64 << 20)
    except ImportError:
        import subprocess
        open("/tmp/z.zst", "wb").write(raw[8:])
        subprocess.run(["zstd", "-d", "-f", "/tmp/z.zst", "-o", "/tmp/z.out"], check=True)
        out = open("/tmp/z.out", "rb").read()
    open("/tmp/old_runtime.wasm", "wb").write(out)
    print(f"  decompressed: {len(out):,} bytes, magic {out[:4].hex()} (expect 0061736d)")
elif raw[:4] == bytes.fromhex("0061736d"):
    open("/tmp/old_runtime.wasm", "wb").write(raw)
    print("  already plain wasm")
else:
    print(f"  UNKNOWN format: {raw[:8].hex()}")
PY
[ -s /tmp/old_runtime.wasm ] || { echo "  decompression failed"; exit 1; }

echo ""
echo "############ 3. compare host-function imports ############"
python3 - "$NEW" <<'PY'
import re, sys

def host_fns(path):
    data = open(path, 'rb').read()
    if data[:4] != bytes.fromhex('0061736d'):
        print(f"  WARNING: {path} is not plain wasm (magic {data[:4].hex()})")
    return {x.decode() for x in re.findall(rb'ext_[a-z0-9_]+_version_\d+', data)}

old = host_fns('/tmp/old_runtime.wasm')
new = host_fns(sys.argv[1])
print(f"  OLD runtime (live on mainnet, spec 16): {len(old)} host functions")
print(f"  NEW runtime (spec 17):                  {len(new)} host functions")
if not old:
    print("\n  ABORT: extracted 0 from the live runtime - comparison invalid")
    raise SystemExit(1)

added = sorted(new - old)
print(f"\n  host functions the NEW runtime needs but the OLD one never used: {len(added)}")
for a in added:
    print(f"    + {a}")
print(f"  dropped: {len(sorted(old - new))}")

print()
if not added:
    print("  VERDICT: SAFE. Every host function the new runtime imports is already in use by")
    print("  the runtime mainnet's binaries execute today. set_code cannot halt the chain on")
    print("  a missing host function, so no binary rollout is required beforehand.")
else:
    print("  VERDICT: roll binaries to all 21 validators BEFORE set_code.")
PY
