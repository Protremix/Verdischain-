import json, subprocess, os, time

def get_api_key():
    env = open("/app/.agents/.env").read()
    for line in env.split("\n"):
        if line.startswith("ANTHROPIC_API_KEY_2="):
            return line.split("=",1)[1].strip()
    return os.environ.get("ANTHROPIC_API_KEY_2","")

def call_claude(code, label, max_tokens=16000):
    prompt = """You are a senior Substrate/Rust blockchain engineer doing a thorough code review. Review this pallet code for:
1. Arithmetic overflow/underflow risks (use checked/saturating math)
2. Authorization issues (missing origin checks)
3. Storage issues (unbounded iterations, missing cleanup)
4. Economic logic errors (reward distribution, slashing, staking, DEX math)
5. State consistency bugs (storage not updated atomically)
6. Missing event emission
7. Any logic that could be exploited

For each finding, provide:
- Severity: CRITICAL / HIGH / MEDIUM / LOW
- Location: function name + approximate line
- Description of the issue
- The EXACT fixed code snippet (before -> after)

Code to review:
"""
    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt + code}]
    }
    result = subprocess.run(
        ["curl", "-s", "https://api.anthropic.com/v1/messages",
         "-H", "x-api-key: " + get_api_key(),
         "-H", "anthropic-version: 2023-06-01",
         "-H", "content-type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=180
    )
    try:
        resp = json.loads(result.stdout)
        if "content" in resp:
            text = resp["content"][0]["text"]
            with open(label, "w") as f:
                f.write(text)
            print(f"OK: {label} - {len(text)} chars")
        else:
            print(f"ERROR: {label} - {result.stdout[:300]}")
    except Exception as e:
        print(f"ERROR: {label} - {e}")

# Remaining pallets
pallets = [
    ("pallets/pallets_presale_src_lib.txt", "audit_presale.md"),
    ("pallets/pallets_vesting_src_lib.txt", "audit_vesting.md"),
    ("pallets/pallets_tokenomics_src_lib.txt", "audit_tokenomics.md"),
]

for filepath, label in pallets:
    code = open(filepath).read()
    call_claude(code, label)
    time.sleep(1)

