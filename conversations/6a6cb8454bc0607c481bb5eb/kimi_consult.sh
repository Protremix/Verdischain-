#!/bin/bash
# Consult Kimi for next direction

KIMI_API_KEY=$(grep KIMI /opt/verdis-chain-rust/.env 2>/dev/null | head -1 | cut -d= -f2)
if [ -z "$KIMI_API_KEY" ]; then
    echo "KIMI_API_KEY not found"
    exit 1
fi

PAYLOAD=$(cat <<'ENDPAYLOAD'
{
  "model": "kimi-k2.7-code-highspeed",
  "temperature": 1,
  "max_tokens": 8000,
  "messages": [
    {
      "role": "system",
      "content": "You are a blockchain security architect. Provide concise, actionable next steps."
    },
    {
      "role": "user",
      "content": "Verdis Chain (Substrate-based DPoS blockchain) status:\n\nCOMPLETED:\n- 17-component security audit (Claude + Kimi dual audit)\n- 127/127 CRITICAL vulnerabilities fixed\n- 10 HIGH vulnerabilities fixed (presale whitelist, refund, IBC timeout, GulfStream, ALT limits, vesting caps, DEX guards, storage limits)\n- 249 tests pass, 0 failures, clippy 0 errors\n- Node rebuilt, chain re-genesis, Block #575, 3 nodes, 2 peers, 7 validators, 8 services, 15 web pages 200\n- Pushed GitHub acd5625\n\nREMAINING:\n- MEDIUM severity findings\n- DEX pools need re-seeding\n- Separate testnet/mainnet chain specs\n- CI/CD pipeline (fmt/check/test/clippy/release/WASM)\n\nWhat are the next 3 priorities? Be specific and technical."
    }
  ]
}
ENDPAYLOAD
)

curl -s https://api.moonshot.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KIMI_API_KEY" \
  -d "$PAYLOAD" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['choices'][0]['message']['content'])"
