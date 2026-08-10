#!/usr/bin/env bash
# CyberScan Security Scanner for Verdis Chain
# Uses Cyberscope CyberScan API for smart contract security analysis
# API Docs: https://docs.cyberscope.io/api/cyberscan

set -euo pipefail

API_KEY="${CYBERSCAN_API_KEY:-}"
if [[ -z "$API_KEY" ]]; then
  echo "ERROR: CYBERSCAN_API_KEY not set"
  exit 1
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

usage() {
  echo "CyberScan Security Scanner"
  echo ""
  echo "Usage: $0 <command> [options]"
  echo ""
  echo "Commands:"
  echo "  score <address> <network>          Get security score for an EVM contract"
  echo "  scan <address> <network>           Full Cyberscan audit (security, community, market scores)"
  echo "  upload <file>                       Upload a Solidity .sol file for scanning"
  echo "  batch <addresses_file> <network>   Batch scan multiple addresses"
  echo "  test                               Test API key validity"
  echo ""
  echo "Supported networks: ETH, BSC, MATIC, BASE, ARBITRUM, AVAX, OPTIMISM, etc."
  echo "API Key format: cs_live_..."
  echo ""
  echo "Note: Verdis Chain (Substrate) addresses are not directly supported."
  echo "Use 'upload' for Solidity contracts or 'scan' for EVM bridge contracts."
}

# Test API key
test_key() {
  echo -e "${CYAN}Testing CyberScan API key...${NC}"
  response=$(curl -s -w "\n%{http_code}" \
    'https://app.cyberscope.io/api/score?address=0xB8c77482e45F1F44dE1745F52C74426C631bDD52&network=ETH' \
    --header "x-api-key: $API_KEY" 2>/dev/null)
  http_code=$(echo "$response" | tail -1)
  body=$(echo "$response" | head -n -1)
  
  if echo "$body" | grep -q "Invalid API key"; then
    echo -e "${RED}FAIL: API key is invalid or not activated${NC}"
    echo "Response: $body"
    echo ""
    echo "To activate: Login at https://app.cyberscope.io > API Key Generation > Create API Key"
    return 1
  elif echo "$body" | grep -q '"success": true'; then
    score=$(echo "$body" | python3 -c "import json,sys; print(json.load(sys.stdin).get('score','?'))" 2>/dev/null)
    echo -e "${GREEN}PASS: API key valid. Test score for BNB token: $score${NC}"
    return 0
  else
    echo -e "${YELLOW}Unknown response (HTTP $http_code):${NC}"
    echo "$body"
    return 2
  fi
}

# Get security score
get_score() {
  local address="$1"
  local network="${2:-ETH}"
  
  echo -e "${CYAN}Fetching security score for $address on $network...${NC}"
  
  response=$(curl -s \
    "https://app.cyberscope.io/api/score?address=${address}&network=${network}" \
    --header "x-api-key: $API_KEY" 2>/dev/null)
  
  echo "$response" | python3 -c "
import json, sys
d = json.load(sys.stdin)
if d.get('success'):
    score = d.get('score')
    if score is not None:
        if score >= 80: status = 'GOOD'
        elif score >= 60: status = 'MODERATE'
        else: status = 'POOR'
        print(f'Security Score: {score}/100 ({status})')
    else:
        print(f'No score available: {d.get(\"message\",\"\")}')
else:
    print(f'Failed: {d.get(\"message\",\"\")}')
" 2>/dev/null
}

# Full Cyberscan audit
full_scan() {
  local address="$1"
  local network="${2:-ETH}"
  
  echo -e "${CYAN}Running full Cyberscan audit for $address on $network...${NC}"
  
  curl -s -X POST \
    'https://www.cyberscope.io/api/cyberscan' \
    --header "x-api-key: $API_KEY" \
    --header "Content-Type: application/json" \
    -d "{\"address\": \"${address}\", \"network\": \"${network}\"}" 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
if 'message' in d and 'Invalid' in str(d.get('message','')):
    print('ERROR: API key invalid')
    sys.exit(1)
print('=== CYBERSCAN AUDIT ===')
print(f\"Name: {d.get('name','?')}\")
scores = {
    'Security': d.get('securityScore'),
    'Community': d.get('communityScore'),
    'Market': d.get('marketScore'),
    'Fundamentals': d.get('fundamentalsScore'),
    'Decentralisation': d.get('decentralisationScore'),
}
print('--- SCORES ---')
for k, v in scores.items():
    if v is not None:
        print(f'  {k}: {float(v):.1f}/100')
    else:
        print(f'  {k}: N/A')
c = d.get('contract', {})
print('--- CONTRACT ---')
print(f\"  Name: {c.get('contractName','?')}\")
print(f\"  Renounced: {c.get('renounced','?')}\")
print(f\"  Proxy: {c.get('proxy','?')}\")
sa = d.get('smartAudit', {})
print('--- AUDIT FINDINGS ---')
for k in ['burn','mint','blacklist','setFees','maxTxAmount','pause']:
    v = sa.get(k, [])
    if v: print(f'  {k}: {len(v)} finding(s)')
print(f\"  SafeMath: {sa.get('safeMath',False)}\")
taxes = d.get('taxes',{})
if taxes:
    print('--- TAXES ---')
    print(f\"  Buy: {taxes.get('buyTax','?')}%  Sell: {taxes.get('sellTax','?')}%\")
print('=== END ===')
" 2>/dev/null
}

# Batch scan
batch_scan() {
  local file="$1"
  local network="${2:-ETH}"
  
  if [[ ! -f "$file" ]]; then
    echo -e "${RED}File not found: $file${NC}"
    return 1
  fi
  
  while IFS= read -r address; do
    [[ -z "$address" ]] && continue
    [[ "$address" == \#* ]] && continue
    echo "=== $address ==="
    get_score "$address" "$network"
    echo ""
    sleep 12
  done < "$file"
}

case "${1:-}" in
  test) test_key ;;
  score) get_score "${2:-}" "${3:-ETH}" ;;
  scan) full_scan "${2:-}" "${3:-ETH}" ;;
  batch) batch_scan "${2:-}" "${3:-ETH}" ;;
  *) usage; exit 1 ;;
esac
