#!/usr/bin/env python3
"""Extract nav links from all Verdis Chain pages."""
import re, os

pages = [
    "index.html", "explorer/index.html", "dex/index.html", "wallet/index.html",
    "sale/index.html", "faucet/index.html", "validators/index.html", "eco/index.html",
    "whitepaper/index.html", "docs/index.html", "contact/index.html",
    "incentives/index.html", "referral/index.html"
]

for p in pages:
    path = f"/var/www/verdiscan/{p}"
    try:
        with open(path) as f:
            c = f.read()
        # Find all <a href links in the header/nav area (first 200 lines usually)
        # Look for nav section
        nav_match = re.search(r'<nav[^>]*>(.*?)</nav>', c, re.DOTALL)
        if not nav_match:
            # Try header
            nav_match = re.search(r'<header[^>]*>(.*?)</header>', c, re.DOTALL)
        if nav_match:
            nav_text = nav_match.group(1)
        else:
            nav_text = c[:10000]  # First 10k chars
        
        links = re.findall(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', nav_text, re.DOTALL)
        labels = []
        for href, label in links:
            clean = re.sub(r'<[^>]+>', '', label).strip()
            if clean and len(clean) < 30:
                labels.append(f"{clean}({href})")
        print(f"\n=== {p} ===")
        print(f"  Nav links: {labels[:15]}")
    except Exception as e:
        print(f"\n=== {p} ===")
        print(f"  ERROR: {e}")
