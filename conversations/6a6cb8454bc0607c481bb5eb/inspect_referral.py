from bs4 import BeautifulSoup
import re

with open("audit_data/referral.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
for s in soup.find_all("script"):
    if s.string:
        print("SCRIPT IN REFERRAL:")
        print(s.string)
