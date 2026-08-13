import os, re
from bs4 import BeautifulSoup

pages = [
    ("Explorer", "/tmp/verdis_pages/explorer.html"),
    ("Validators", "/tmp/verdis_pages/validators.html"),
    ("DEX", "/tmp/verdis_pages/dex.html"),
    ("Governance", "/tmp/verdis_pages/governance.html"),
    ("Faucet", "/tmp/verdis_pages/faucet.html"),
    ("Analytics", "/tmp/verdis_pages/analytics.html"),
    ("Monitoring", "/tmp/verdis_pages/monitoring.html"),
    ("Transactions", "/tmp/verdis_pages/transactions.html"),
]

for page_name, filepath in pages:
    print("=" * 80)
    print(f"PAGE: {page_name}")
    print("=" * 80)
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Page title
    title = soup.title.string.strip() if soup.title else ""
    print(f"[Title] {title}")
    
    # 2. Extract badges, stat cards, headings, labels, buttons, footers
    # Let us find all tags with text
    for el in soup.find_all(["h1", "h2", "h3", "h4", "p", "span", "div", "button", "a", "td", "th", "li"]):
        # skip if contains nested tags that have text (to avoid duplicates), unless it is a card or badge
        text = el.get_text(strip=True)
        if not text:
            continue
            
        # check if el has direct text
        children = [c for c in el.children if isinstance(c, str) and c.strip()]
        cid = el.get("id", "")
        ccls = ".".join(el.get("class", []))
        
        # We want to catch specific keywords or metrics
        keywords = [
            "live", "mainnet", "testnet", "production", "tps", "supply", "stake", "epoch",
            "tvl", "volume", "pool", "liquidity", "fee", "swap", "finality", "amm",
            "validator", "dpos", "babe", "grandpa", "apy", "reward", "yield", "slashing",
            "green", "carbon", "co2", "credit", "tree", "offset", "reforest",
            "vrdx", "cvrdx", "$", "budget", "recipient", "propose", "referendum", "council", "treasury",
            "participant", "security", "audited", "referral", "bonus", "commission", "tier"
        ]
        
        if any(k in text.lower() for k in keywords):
            # Print location context
            loc = f"<{el.name}"
            if cid: loc += f" id='{cid}'"
            if ccls: loc += f" class='{ccls}'"
            loc += ">"
            print(f"  {loc}: {text}")

