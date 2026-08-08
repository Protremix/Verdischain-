import re
from bs4 import BeautifulSoup

with open("whitepaper.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=== CHECKING ALL TECHNICAL CLAIMS AND NUMBERS ===")

# Extract all text
text = soup.get_text()

# Search for validator counts
validators = re.findall(r'.{0,50}\b(?:validator|validators|node|nodes)\b.{0,50}', text, re.IGNORECASE)
print("\n--- VALIDATOR CLAIMS ---")
for v in set(validators):
    print(" ", v.strip().replace('\n', ' '))

# Search for DPoS, Consensus claims
consensus = re.findall(r'.{0,50}\b(?:DPoS|BABE|GRANDPA|consensus|PoH|Solana|Substrate)\b.{0,50}', text, re.IGNORECASE)
print("\n--- CONSENSUS / ARCHITECTURE CLAIMS ---")
for c in set(consensus)[:20]:
    print(" ", c.strip().replace('\n', ' '))

# Search for Token Supply numbers across text
supplies = re.findall(r'.{0,50}\b(?:supply|total supply|100B|100,000,000,000|VRDX|billion|million|B|M)\b.{0,50}', text, re.IGNORECASE)
print("\n--- SUPPLY CLAIMS ---")
for s in set(supplies)[:30]:
    print(" ", s.strip().replace('\n', ' '))

