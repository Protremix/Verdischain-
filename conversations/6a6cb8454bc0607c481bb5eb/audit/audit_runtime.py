import json, subprocess

def get_api_key():
    env = open("/app/.agents/.env").read()
    for line in env.split("\n"):
        if line.startswith("ANTHROPIC_API_KEY_2="):
            return line.split("=",1)[1].strip()
    return ""

def call_claude(code, label, max_tokens=16000):
    prompt = """You are a senior Substrate/Rust blockchain engineer doing a thorough code review of a Substrate runtime. Review for:
1. Pallet configuration issues (wrong types, missing constants)
2. Genesis config issues (wrong initial values, missing allocations)
3. construct_runtime! issues (wrong indices, missing pallets)
4. Security configuration (RPC methods exposed, unsafe calls)
5. Parameter tuning issues (epoch length, validator count, etc.)

For each finding provide:
- Severity: CRITICAL / HIGH / MEDIUM / LOW
- Location: section name
- Description
- The EXACT fixed code (before -> after)

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
    resp = json.loads(result.stdout)
    if "content" in resp:
        text = resp["content"][0]["text"]
        with open(label, "w") as f:
            f.write(text)
        print(f"OK: {label} - {len(text)} chars")
    else:
        print(f"ERROR: {result.stdout[:300]}")

code = open("runtime.rs").read()
mid = len(code) // 2
while mid < len(code) and code[mid] != '\n':
    mid += 1
call_claude(code[:mid], "audit_runtime_part1.md")
call_claude(code[mid:], "audit_runtime_part2.md")
