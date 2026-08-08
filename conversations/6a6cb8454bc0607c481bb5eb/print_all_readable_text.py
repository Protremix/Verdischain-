from bs4 import BeautifulSoup

with open("whitepaper.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

sections = soup.find_all(['section', 'div'])
seen = set()

for sec in soup.find_all('section'):
    sec_id = sec.get('id', 'NO_ID')
    print(f"\n================ SECTION [{sec_id}] ================")
    for elem in sec.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'td', 'th', '.card', '.box']):
        txt = elem.get_text().strip()
        if txt and txt not in seen and len(txt) > 2:
            seen.add(txt)
            print(f"[{elem.name}] {txt}")

