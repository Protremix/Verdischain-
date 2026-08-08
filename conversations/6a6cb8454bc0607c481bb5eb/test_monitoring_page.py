import re

with open("monitoring_page.html", "r", encoding="utf-8") as f:
    html = f.read()

checks = []

# 1. File size check
checks.append(("File size > 10KB", len(html) > 10000, f"Size: {len(html)} bytes"))

# 2. CSS variables check
mandatory_vars = [
    "--bg:#f1f5f9;",
    "--bg-1:#f8fafc;",
    "--card:#ffffff;",
    "--border:#e2e8f0;",
    "--text:#0f172a;",
    "--text-2:#475569;",
    "--text-3:#94a3b8;",
    "--accent:#16a34a;",
    "--accent-2:#15803d;",
    "--accent-glow:rgba(22, 163, 74, 0.15);",
    "--success:#4ade80;",
    "--warning:#fbbf24;",
    "--error:#f87171;",
    "--radius:12px;",
    "--radius-sm:8px;",
    "--mono:'JetBrains Mono', monospace;",
    "--sans:'Inter', sans-serif;",
    "--display:'Space Grotesk', sans-serif;"
]

# Normalize whitespace in CSS
html_no_ws = re.sub(r'\s+', '', html)
for var in mandatory_vars:
    var_no_ws = re.sub(r'\s+', '', var)
    present = var_no_ws in html_no_ws
    checks.append((f"CSS Var: {var.split(':')[0]}", present, var if present else f"MISSING: {var}"))

# 3. Hero requirement
checks.append(("Dark Hero background #1a1a1a", "#1a1a1a" in html, "Found #1a1a1a"))
checks.append(("Hero title 'Validator Monitor'", "Validator" in html and "Monitor" in html, "Found Validator Monitor"))
checks.append(("Hero badge 'DPoS Network Health'", "DPoS Network Health" in html, "Found DPoS Network Health"))

# 4. Floating Cards
cards = ["Active Validators", "Total Staked", "Avg Green Score", "Block Producer"]
for card in cards:
    checks.append((f"Floating card: {card}", card in html, f"Found {card}"))

# 5. Stats Bar Cards
stats = ["Active / Total Validators", "Total Staked (VRDX)", "Green Validators", "Network Staking APY"]
for stat in stats:
    checks.append((f"Stats card: {stat}", stat in html, f"Found {stat}"))

# 6. Navigation links
nav_links = ["Verdiscan", "DEX", "Whitepaper", "Wallet", "Sale", "Tokenomics", "Faucet"]
for link in nav_links:
    checks.append((f"Nav link: {link}", link in html, f"Found {link}"))

# 7. RPC method calls in script
rpc_methods = [
    "dpos_allValidators",
    "dpos_activeValidators",
    "dpos_validatorStake",
    "eco_getGreenScore",
    "eco_getAllGreenValidators",
    "eco_getGreenValidatorCount",
    "system_health",
    "chain_getHeader"
]
for rpc in rpc_methods:
    checks.append((f"RPC method: {rpc}", rpc in html, f"Found {rpc}"))

# 8. Chart.js CDN
checks.append(("Chart.js CDN link", "cdn.jsdelivr.net/npm/chart.js" in html, "Found Chart.js CDN"))

# 9. Tabs check
tabs = ["Validator List", "Consensus Health", "Green Scores"]
for tab in tabs:
    checks.append((f"Tab: {tab}", tab in html, f"Found {tab}"))

# 10. SEO Meta & Favicon
checks.append(("og:title", "og:title" in html, "Found og:title"))
checks.append(("og:description", "og:description" in html, "Found og:description"))
checks.append(("canonical link", "canonical" in html, "Found canonical"))
checks.append(("Favicon link", "/assets/favicon.ico" in html, "Found /assets/favicon.ico"))

print("\n--- AUDIT RESULTS ---")
all_passed = True
for name, status, detail in checks:
    symbol = "✓" if status else "❌"
    if not status:
        all_passed = False
    print(f"{symbol} {name}: {detail}")

if all_passed:
    print("\nALL AUDIT CHECKS PASSED!")
else:
    print("\nSOME CHECKS FAILED! Please review above.")
