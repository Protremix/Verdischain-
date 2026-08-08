from bs4 import BeautifulSoup

with open('page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

table = soup.find('table', class_='vesting-table')
if table:
    headers = [th.get_text(strip=True) for th in table.find_all('th')]
    print("HEADERS:", headers)
    
    for tr in table.find_all('tr'):
        tds = [td.get_text(strip=True) for td in tr.find_all('td')]
        if tds:
            print("ROW (len={}):".format(len(tds)), tds)

