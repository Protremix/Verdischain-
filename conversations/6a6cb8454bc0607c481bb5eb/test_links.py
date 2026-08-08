import urllib.request
import urllib.parse
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with open("links.json") as f:
    links = json.load(f)

print(f"Testing {len(links)} links...")

results = []
tested = set()

for item in links:
    href = item["href"]
    text = item["text"] or item["raw_href"]
    if href in tested:
        continue
    tested.add(href)
    
    req = urllib.request.Request(
        href, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        status = resp.status
        url = resp.geturl()
    except urllib.error.HTTPError as e:
        status = e.code
        url = href
    except Exception as e:
        status = f"ERR: {str(e)}"
        url = href
        
    print(f"[{status}] {text} -> {href} (final: {url})")
    results.append({
        "text": text,
        "href": href,
        "status": status,
        "final_url": url
    })

with open("link_results.json", "w") as f:
    json.dump(results, f, indent=2)

