#!/usr/bin/env bash
# Point the WebSocket path at the mainnet too.
#
# Chain of hops today:
#   browser -> nginx /ws -> 127.0.0.1:9944 (ws_filter_proxy.py) -> 127.0.0.1:9933
#   and :9933 is the TESTNET node. So wallet/explorer live-subscriptions still read
#   the testnet even though JSON-RPC now reads mainnet.
#
# ws_filter_proxy.py hardcodes BACKEND_PORT = 9933. Make it configurable via the
# environment, default unchanged, and set VERDIS_WS_BACKEND_PORT=9960 on the service
# so it forwards to the mainnet tunnel. Editing one constant keeps the method
# filtering intact.

set -uo pipefail
KEY=$HOME/.ssh/id_ed25519
MAIN_GEN=0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e

ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i "$KEY" \
    root@91.98.160.145 'bash -s' <<'REMOTE' 2>&1
set -uo pipefail
P=/opt/verdis-chain-rust/ws_filter_proxy.py
cp -a "$P" "$P.bak-$(date -u +%Y%m%d-%H%M%S)"
echo "  backup: $(ls -1t $P.bak-* | head -1)"

echo "  --- before ---"
sed -n '22,26p' "$P" | sed 's/^/    /'

python3 - "$P" <<'PY'
import sys, re
p = sys.argv[1]
s = open(p).read()
if 'VERDIS_WS_BACKEND_PORT' in s:
    print("    already parameterised"); sys.exit(0)
if 'import os' not in s.split('\n\n')[0] and not re.search(r'^import os$', s, re.M):
    s = re.sub(r'^(import .*)$', r'import os\n\1', s, count=1, flags=re.M)
s2 = re.sub(r'^BACKEND_PORT\s*=\s*9933.*$',
            'BACKEND_PORT = int(os.environ.get("VERDIS_WS_BACKEND_PORT", "9933"))',
            s, count=1, flags=re.M)
if s2 == s:
    print("    ERROR: BACKEND_PORT line not found"); sys.exit(1)
open(p, 'w').write(s2)
print("    BACKEND_PORT now reads VERDIS_WS_BACKEND_PORT (default 9933)")
PY

python3 -c "import ast,sys; ast.parse(open('$P').read())" && echo "    syntax OK" || { echo "    SYNTAX ERROR - restoring"; cp -a "$(ls -1t $P.bak-* | head -1)" "$P"; exit 1; }

echo "  --- after ---"
grep -n 'BACKEND_PORT\|^import os' "$P" | head -4 | sed 's/^/    /'

# tell the service to use the mainnet tunnel
D=/etc/systemd/system/verdis-ws-filter.service.d
mkdir -p "$D"
printf '[Service]\nEnvironment=VERDIS_WS_BACKEND_PORT=9960\n' > "$D/10-mainnet.conf"
systemctl daemon-reload
systemctl restart verdis-ws-filter
sleep 8
echo "  ws-filter: $(systemctl is-active verdis-ws-filter)"
if [ "$(systemctl is-active verdis-ws-filter)" != "active" ]; then
  journalctl -u verdis-ws-filter -n 8 --no-pager | tail -8 | cut -c1-160
  cp -a "$(ls -1t $P.bak-* | head -1)" "$P"
  rm -f "$D/10-mainnet.conf"; systemctl daemon-reload; systemctl restart verdis-ws-filter
  echo "  REVERTED"; exit 1
fi
journalctl -u verdis-ws-filter -n 3 --no-pager | tail -3 | cut -c1-150 | sed 's/^/    /'
REMOTE

echo
echo "=== verify WS through the public URL ==="
python - <<'PY'
import json, socket, ssl, base64, os, struct
# minimal WS client: handshake then one JSON-RPC call
host, path = "verdischain.com", "/ws"
key = base64.b64encode(os.urandom(16)).decode()
req = (f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUpgrade: websocket\r\n"
       f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
       f"Sec-WebSocket-Version: 13\r\n\r\n")
try:
    raw = socket.create_connection((host, 443), timeout=20)
    s = ssl.create_default_context().wrap_socket(raw, server_hostname=host)
    s.sendall(req.encode())
    resp = s.recv(4096).decode(errors="replace")
    print("  handshake:", resp.split("\r\n")[0])
    if "101" not in resp:
        print("  WS upgrade failed"); raise SystemExit
    payload = json.dumps({"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}).encode()
    mask = os.urandom(4)
    frame = bytearray([0x81])
    n = len(payload)
    frame += bytes([0x80 | n]) if n < 126 else b"\xfe" + struct.pack(">H", n)
    frame += mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    s.sendall(bytes(frame))
    data = s.recv(8192)
    i = 2
    ln = data[1] & 0x7F
    if ln == 126: i, ln = 4, struct.unpack(">H", data[2:4])[0]
    body = data[i:i+ln].decode(errors="replace")
    print("  response:", body[:150])
    if "2284393d" in body: print("  *** WS now serves MAINNET ***")
    elif "f72f1241" in body: print("  !! WS still serves TESTNET")
    s.close()
except Exception as e:
    print("  WS test failed:", type(e).__name__, e)
PY
