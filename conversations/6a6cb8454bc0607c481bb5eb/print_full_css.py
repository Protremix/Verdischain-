import urllib.request
from bs4 import BeautifulSoup

url = 'https://verdischain.com/validators/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

soup = BeautifulSoup(html, 'html.parser')
for i, st in enumerate(soup.find_all('style')):
    print(f"--- STYLE TAG {i} ---")
    print(st.string)

