#!/usr/bin/env bash
# Fast Kimi AI consultation - kimi-k2.7-code-highspeed (30-60s response)
# Usage: quick-ask.sh "Your question here"

QUESTION="${1:-No question provided}"
MAX_TOKENS="${2:-8000}"

if [ -z "$KIMI_API_KEY" ]; then
  source /app/.agents/.env 2>/dev/null
fi

python3 -c "
import json, sys
req = {
    'model': 'kimi-k2.7-code-highspeed',
    'max_tokens': int(sys.argv[1]),
    'temperature': 1,
    'messages': [
        {'role': 'system', 'content': 'You are a Substrate/blockchain architect. Answer directly and concisely. No reasoning, just actionable advice.'},
        {'role': 'user', 'content': sys.argv[2]}
    ]
}
print(json.dumps(req))
" "$MAX_TOKENS" "$QUESTION" > /tmp/kimi_req.json

curl -s --max-time 90 \
  -X POST "https://api.moonshot.ai/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KIMI_API_KEY" \
  -d @/tmp/kimi_req.json 2>/dev/null | python3 -c "
import sys, json
data = sys.stdin.read()
if not data:
    print('ERROR: Empty response from Kimi')
    sys.exit(1)
try:
    r = json.loads(data)
    if 'error' in r:
        print(f'KIMI ERROR: {r[\"error\"][\"message\"]}')
        sys.exit(1)
    msg = r['choices'][0]['message']
    content = msg.get('content', '')
    reasoning = msg.get('reasoning_content', '')
    if content:
        print(content)
    elif reasoning:
        print('NOTE: Kimi returned reasoning only. Key points:')
        print(reasoning[:3000])
    else:
        print('ERROR: No content in response')
    fr = r['choices'][0].get('finish_reason', '')
    if fr == 'length':
        print(f'\n[Truncated at {r[\"usage\"][\"completion_tokens\"]} tokens]')
except Exception as e:
    print(f'ERROR: {e}')
    print(data[:500])
"
