from bs4 import BeautifulSoup

with open("whitepaper.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

sections = soup.find_all('section')

for i in range(7, len(sections)):
    sec = sections[i]
    sec_id = sec.get('id', 'NO_ID')
    sec_class = ' '.join(sec.get('class', []))
    print(f"\n==================== SECTION {i+1}: id='{sec_id}' class='{sec_class}' ====================")
    text = sec.get_text(separator=' ', strip=True)
    print(text)

