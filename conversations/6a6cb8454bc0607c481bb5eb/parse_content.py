import re
from bs4 import BeautifulSoup

with open("whitepaper.html", "r", encoding="utf-8") as f:
    html = f.read()

# Let's extract all sections and text
# Also let's search for specific keywords: DPoS, AMM, carbon, VRDX, supply, TPS, benchmark, test, speed, validator, 100B, 10B, 1B, 100M, etc.

print("=== SEARCHING FOR TOKEN SUPPLY & VRDX MENTIONS ===")
matches = re.findall(r'.{0,100}(?:VRDX|supply|100B|100[ ,]000[ ,]000[ ,]000|billion|million|tokenomics).{0,100}', html, re.IGNORECASE)
for m in matches[:30]:
    print("MATCH:", m.strip().replace('\n', ' '))

