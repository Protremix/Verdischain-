import re

with open("whitepaper.html", "r", encoding="utf-8") as f:
    html = f.read()

# Search for @media blocks
media_blocks = re.findall(r'@media[^{]+\{([\s\S]+?\})\s*\}', html)
print(f"Found {len(media_blocks)} @media rules:")
for i, m in enumerate(media_blocks, 1):
    print(f"--- Media Query {i} ---")
    print(m[:500])

