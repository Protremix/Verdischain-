import re
from bs4 import BeautifulSoup

with open("whitepaper.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
text = soup.get_text()

# 1. Check supply math & numbers
print("=== SUPPLY DISTRIBUTION MATH CHECK ===")
# 40% + 20% + 15% + 12% + 8% + 5%
# 40B + 20B + 15B + 12B + 8B + 5B = 100B
# 40 + 20 = 60 + 15 = 75 + 12 = 87 + 8 = 95 + 5 = 100%. Total = 100B VRDX.

allocations = [
    ("Community & Ecosystem Grants", "40%", "40,000,000,000 VRDX"),
    ("Validator Staking Rewards", "20%", "20,000,000,000 VRDX"),
    ("Core Team & Contributors", "15%", "15,000,000,000 VRDX"),
    ("Strategic Investors", "12%", "12,000,000,000 VRDX"),
    ("Protocol Treasury", "8%", "8,000,000,000 VRDX"),
    ("Green Eco Fund", "5%", "5,000,000,000 VRDX")
]
total_pct = 40 + 20 + 15 + 12 + 8 + 5
total_tokens = 40 + 20 + 15 + 12 + 8 + 5
print(f"Total % = {total_pct}%, Total Tokens = {total_tokens}B VRDX")

# 2. Check Vesting Math & Claims
print("\n=== VESTING MATH CHECK ===")
# Core Team: 15B VRDX. 12-Month Cliff (0% unlocked). Linear release of 312,500,000 VRDX per month over 36 months (4 years total).
# 312,500,000 * 36 = 11,250,000,000 VRDX (11.25B) -> WAIT! 11.25B != 15B!
# Let's check: 15,000,000,000 / 36 = 416,666,666.67 per month! Or if 48 months: 15,000,000,000 / 48 = 312,500,000 per month!
# BUT the text says: "linear release of 312,500,000 VRDX per month over 36 months (4 years total)"!
# 312,500,000 * 36 = 11,250,000,000! That leaves 3.75 Billion tokens UNACCOUNTED FOR!
# Or if it's over 48 months, 312.5M * 48 = 15B, but text says 36 months!
# AND if month 12 cliff (1 year) + 36 months = 48 months (4 years total). BUT 312.5M * 36 months = 11.25B, NOT 15B!

# Let's check Strategic Investors: 12B VRDX. 6-Month Cliff (10% TGE = 1.2B).
# Remaining: 12B - 1.2B = 10.8B VRDX.
# Text says: "18-month linear monthly unlock ( 600,000,000 VRDX / mo )".
# 600,000,000 * 18 = 10,800,000,000 VRDX (10.8B).
# 10.8B + 1.2B = 12B. This calculation matches.

# Let's check Community & Eco Fund: 45B VRDX.
# Text says: "Community & Eco Fund 45B VRDX Linear Release 10% unlocked at TGE. Remaining 90% released linearly over 60 months... Linear active: 4,500,000,000 VRDX circulating"
# Wait! In section 2 Distribution:
# Community & Ecosystem Grants = 40B VRDX (40%)
# Green Eco Fund = 5B VRDX (5%)
# Total = 45B VRDX.
# But in section 3 Vesting Schedule: It groups them together as "Community & Eco Fund 45B VRDX".

# Let's check Phase 1 Roadmap: "24.5B VRDX initial circulating supply."
# Where does 24.5B come from at TGE?
# TGE unlocks mentioned:
# - Strategic Investors: 10% of 12B = 1.2B VRDX
# - Community & Eco Fund: 10% of 45B = 4.5B VRDX
# - Core Team: 0% TGE
# - Validator Staking / Treasury: Unstated TGE %
# If TGE circulating is 24.5B, that's 24.5% of total supply, but only 1.2B + 4.5B = 5.7B is accounted for by the TGE unlock rules stated in Section 3!

