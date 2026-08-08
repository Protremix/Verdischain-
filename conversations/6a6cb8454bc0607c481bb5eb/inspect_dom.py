import urllib.request
from bs4 import BeautifulSoup

url = 'https://verdischain.com/validators/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')

print("--- IMAGES ---")
for img in soup.find_all('img'):
    print(img.get('src'), img.get('alt'))

print("\n--- NAV LINKS ---")
for a in soup.find_all('a'):
    print(a.get('href'), a.text.strip())

print("\n--- INPUTS & SELECTS ---")
for inp in soup.find_all(['input', 'select', 'button']):
    print(inp.name, inp.get('id'), inp.get('type'), inp.get('value'))

