import json, subprocess, os, time

def get_api_key():
    env = open("/app/.agents/.env").read()
    for line in env.split("\n"):
        if line.startswith("ANTHROPIC_API_KEY_2="):
            return line.split("=",1)[1].strip()
    return os.environ.get("ANTHROPIC_API_KEY_2","")

def call_claude(code, label, max_tokens=8000):
    prompt = """You are a senior Substrate/Rust blockchain engineer doing a thorough code review. Review this pallet code for:
1. Arithmetic overflow/underflow risks
2. Authorization issues (missing origin checks)
3. Storage issues (unbounded iterations, missing cleanup)
4. State consistency bugs
5. Any logic that could be exploited

For each finding, provide:
- Severity: CRITICAL / HIGH / MEDIUM / LOW
- Location: function name
- Description
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

# Infrastructure pallets + runtime
pallets = [
    ("pallets/pallets_ibc_src_lib.txt", "audit_ibc.md"),
    ("pallets/pallets_storage_src_lib.txt", "audit_storage.md"),
    ("pallets/pallets_poh_src_lib.txt", "audit_poh.md"),
    ("pallets/pallets_gulf-stream_src_lib.txt", "audit_gulf_stream.md"),
    ("pallets/pallets_sealevel_src_lib.txt", "audit_sealevel.md"),
    ("pallets/pallets_turbine_src_lib.txt", "audit_turbine.md"),
    ("pallets/pallets_zk-compression_src_lib.txt", "audit_zk_compression.md"),
    ("pallets/pallets_address-lookup-tables_src_lib.txt", "audit_alt.md"),
]

for filepath, label in pallets:
    code = open(filepath).read()
    call_claude(code, label)
    time.sleep(1)

# Runtime
code = open("runtime.rs").read()
# Split if too large
if len(code) > 50000:
    mid = len(code) // 2
    while mid < len(code) and code[mid] != '\n':
        mid += 1
    call_claude(code[:mid], "audit_runtime_part1.md")
    call_claude(code[mid:], "audit_runtime_part2.md")
else:
    call_claude(code, "audit_runtime.md")

