import httpx
import json

client = httpx.Client(
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
    follow_redirects=True,
    timeout=10.0
)

# Extract all API URLs in page1
with open("page1_api.html", "r", encoding="utf-8") as f:
    text = f.read()

import re
urls = sorted(list(set(re.findall(r'https://verdischain\.com/api/v1[^\s"\'\`\<\>\\\]]+', text))))

print(f"Found {len(urls)} API URLs in Page 1:\n")

for url in urls:
    # Clean trailing characters like quotes or backslashes
    clean_url = url.rstrip('",;\\')
    try:
        r = client.get(clean_url)
        print(f"URL: {clean_url}")
        print(f"Status: {r.status_code}")
        try:
            data = r.json()
            print("Response Sample:", json.dumps(data, indent=2)[:300])
        except Exception:
            print("Response Text:", r.text[:200])
        print("-" * 50)
    except Exception as e:
        print(f"URL: {clean_url} -> EXCEPTION: {e}")
        print("-" * 50)

