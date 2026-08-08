from bs4 import BeautifulSoup

with open('page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

table = soup.find('table', class_='dist-table')
if table:
    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        if tds:
            cat_dot = tds[0].find('span', class_='cat-dot')
            color = cat_dot.get('style') if cat_dot else None
            cat_name = tds[0].get_text(strip=True)
            pct = tds[1].get_text(strip=True)
            amount = tds[2].get_text(strip=True)
            print(f"Cat: {cat_name} | Pct: {pct} | Amount: {amount} | Dot Style: {color}")
