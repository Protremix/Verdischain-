from bs4 import BeautifulSoup
import urllib.request
import urllib.error
import urllib.parse

with open('page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

base_url = 'https://verdischain.com/tokenomics/'

links = []
for a in soup.find_all('a', href=True):
    href = a['href']
    text = a.get_text(strip=True)
    parent_class = a.parent.get('class', [])
    grandparent_class = a.parent.parent.get('class', []) if a.parent and a.parent.parent else []
    
    # Determine section
    section = "Body"
    if 'nav-links' in parent_class or 'nav-brand' in parent_class or a.find_parent('nav'):
        section = "Nav"
    elif 'footer-links' in parent_class or a.find_parent('footer') or 'footer' in str(parent_class):
        section = "Footer"
        
    full_url = urllib.parse.urljoin(base_url, href)
    links.append({'text': text, 'href': href, 'full_url': full_url, 'section': section})

print(f"Total links found: {len(links)}")
for l in links:
    print(f"[{l['section']}] '{l['text']}' -> href: {l['href']} (full: {l['full_url']})")

print("\n--- TESTING LINK STATUS CODES ---")
tested = {}
for l in links:
    url = l['full_url']
    if url in tested:
        l['status'] = tested[url]
        continue
    
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    )
    try:
        res = urllib.request.urlopen(req, timeout=10)
        status = res.getcode()
        tested[url] = f"HTTP {status}"
    except urllib.error.HTTPError as e:
        tested[url] = f"HTTP {e.code}"
    except urllib.error.URLError as e:
        tested[url] = f"ERROR: {e.reason}"
    except Exception as e:
        tested[url] = f"ERROR: {str(e)}"
    
    l['status'] = tested[url]
    print(f"{url} -> {tested[url]}")

