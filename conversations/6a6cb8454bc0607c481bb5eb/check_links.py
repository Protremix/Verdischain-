import json
import urllib.request
import urllib.parse
import ssl
import sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = ["docs", "blog", "developers", "download", "status"]

checked_links = {}

def check_url(url, base_url):
    if not url:
        return "EMPTY_HREF"
    if url.startswith("#"):
        return "ANCHOR_ONLY"
    if url.startswith("javascript:"):
        return "JAVASCRIPT_SCHEME"
    
    full_url = urllib.parse.urljoin(base_url, url)
    if full_url in checked_links:
        return checked_links[full_url]
    
    req = urllib.request.Request(
        full_url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    )
    try:
        res = urllib.request.urlopen(req, timeout=10, context=ctx)
        result = {'status': res.status, 'final_url': res.geturl()}
    except urllib.error.HTTPError as e:
        result = {'status': e.code, 'error': str(e)}
    except Exception as e:
        result = {'status': 'ERROR', 'error': str(e)}
        
    checked_links[full_url] = result
    return result

for name in urls:
    with open(f"dumps/{name}_info.json") as f:
        data = json.load(f)
    
    page_url = data['url']
    print(f"\n=================== LINK AUDIT FOR {name.upper()} ({page_url}) ===================")
    
    links = data['links']
    for idx, link in enumerate(links):
        href = link.get('href')
        text = link.get('text')
        res = check_url(href, page_url)
        print(f"[{idx+1}] Text: '{text}' | href: '{href}' => Result: {res}")

