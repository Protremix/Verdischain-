import json
import httpx
from urllib.parse import urljoin, urlparse

client = httpx.Client(
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
    follow_redirects=True,
    timeout=10.0
)

for page_key in ["page1_api", "page2_api_docs", "page3_validators"]:
    with open(f"{page_key}_parsed.json", "r") as f:
        data = json.load(f)
    
    base_url = data['url']
    print(f"\n=================== CHECKING LINKS FOR {page_key} ({base_url}) ===================")
    
    links = data['links']
    tested = set()
    
    for l in links:
        href = l['href']
        text = l['text']
        
        # Resolve URL
        full_url = urljoin(base_url, href)
        if full_url in tested:
            continue
        tested.add(full_url)
        
        # Check fragment if present
        parsed = urlparse(full_url)
        
        try:
            r = client.get(full_url)
            status = r.status_code
            final_url = str(r.url)
            
            # Check if anchor exists in page if there's a fragment
            anchor_ok = True
            if parsed.fragment and status == 200:
                if "#" in href or parsed.fragment:
                    # check if element with id exists in response text
                    soup_html = r.text
                    if f'id="{parsed.fragment}"' not in soup_html and f"id='{parsed.fragment}'" not in soup_html and f'name="{parsed.fragment}"' not in soup_html:
                        anchor_ok = False
            
            print(f"[{status}] '{text}' -> {href} (Full: {full_url}) | Final: {final_url} | Anchor OK: {anchor_ok}")
        except Exception as e:
            print(f"[ERROR] '{text}' -> {href} (Full: {full_url}) | Exception: {e}")

