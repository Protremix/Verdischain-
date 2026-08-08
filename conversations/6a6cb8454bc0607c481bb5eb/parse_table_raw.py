from bs4 import BeautifulSoup

with open('page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

table = soup.find('table', class_='vesting-table')
for tr in table.find_all('tr'):
    if 'Community Rewards' in tr.get_text() or 'Eco Fund' in tr.get_text() or 'Treasury' in tr.get_text():
        print("RAW ROW:")
        print(tr.prettify())
