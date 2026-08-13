import os
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

for name, filepath in pages:
    print(f"\n==================================================")
    print(f"PAGE: {name}")
    print(f"==================================================")
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    
    # Remove script and style tags
    for s in soup(["script", "style"]):
        s.decompose()
        
    for el in soup.find_all(True):
        direct_text = "".join([c for c in el.children if isinstance(c, str)]).strip()
        if direct_text:
            cid = el.get("id")
            ccls = el.get("class")
            id_str = f"#{cid}" if cid else ""
            cls_str = f".{'.'.join(ccls)}" if ccls else ""
            loc = f"{el.name}{id_str}{cls_str}"
            print(f"[{loc}] {direct_text}")
