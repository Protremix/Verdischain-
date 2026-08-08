from bs4 import BeautifulSoup
import json
import re

soup = BeautifulSoup(open("dumps/blog.html", "r", encoding="utf-8"), "html.parser")

print("=== BLOG ARTICLES & LINKS ===")
articles = soup.find_all(['article', 'div'], class_=re.compile(r'card|post|article|featured', re.I))
print(f"Found {len(articles)} potential article elements.")

for a in soup.find_all('a'):
    href = a.get('href')
    text = a.get_text(strip=True)
    print(f"A Tag: text='{text}' | href='{href}'")

for b in soup.find_all('button'):
    text = b.get_text(strip=True)
    onclick = b.get('onclick')
    print(f"BUTTON Tag: text='{text}' | onclick='{onclick}'")

# Check article dates, authors, categories, read buttons
print("\n=== ARTICLE DETAILS ===")
titles = soup.find_all(['h2', 'h3', 'h4'])
for t in titles:
    print(f"Heading: {t.get_text(strip=True)}")

ps = soup.find_all('p')
for p in ps:
    txt = p.get_text(strip=True)
    if any(k in txt for k in ['202', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Author', 'By']):
        print(f"Date/Author text: {txt}")

