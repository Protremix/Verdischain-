import urllib.request
from bs4 import BeautifulSoup

url = 'https://verdischain.com/validators/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script')

for i, s in enumerate(scripts):
    print(f"=== SCRIPT {i} ===")
    if s.string:
        print(s.string)
    elif s.get('src'):
        print(f"External script: {s.get('src')}")

