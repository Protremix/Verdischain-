#!/usr/bin/env python3
"""Send security audit code to Kimi kimi-k3 for deep attack-vector analysis."""
import json, sys, os, requests

api_key = os.environ.get("KIMI_API_KEY")
if not api_key:
    with open("/app/.agents/.env") as f:
        for line in f:
            if line.startswith("KIMI_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"')
                break

if not api_key:
    print("ERROR: KIMI_API_KEY not found")
    sys.exit(1)

code_file = sys.argv[1]
model = sys.argv[2] if len(sys.argv) > 2 else "kimi-k3"
max_tokens = int(sys.argv[3]) if len(sys.argv) > 3 else 16000

with open(code_file) as f:
    code = f.read()

print(f"Sending {len(code)} chars to {model}...", flush=True)

req = {
    "model": model,
    "max_tokens": max_tokens,
    "temperature": 1,
    "messages": [
        {"role": "system", "content": "You are a world-class blockchain security auditor specializing in Substrate/Polkadot pallets. You find real exploitable vulnerabilities, not theoretical concerns. Be specific: cite line numbers, function names, and provide concrete attack scenarios. Rate each as CRITICAL/HIGH/MEDIUM/LOW with exploit steps and fixes."},
        {"role": "user", "content": code}
    ]
}

resp = requests.post(
    "https://api.moonshot.ai/v1/chat/completions",
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    },
    json=req,
    timeout=600
)

data = resp.json()
if "choices" in data:
    content = data["choices"][0]["message"]["content"]
    print(content)
else:
    print(f"ERROR: {json.dumps(data, indent=2)}")
