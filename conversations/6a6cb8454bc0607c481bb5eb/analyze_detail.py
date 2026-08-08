import json
import urllib.request
from bs4 import BeautifulSoup

# Fetch raw HTML source
url = 'https://verdischain.com/validators/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

print("--- HTML LENGTH:", len(html))

soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script')
print(f"--- SCRIPTS FOUND: {len(scripts)}")
for i, s in enumerate(scripts):
    print(f"Script {i}: src={s.get('src')}, inline_len={len(s.string) if s.string else 0}")
    if s.string and len(s.string) < 3000:
        print(s.string[:1000])
        print("="*40)

# Check audit_results network details
with open('audit_results.json') as f:
    audit = json.load(f)

print("\n--- NETWORK RESPONSES FOR RPC ---")
for res in audit['network_responses']:
    if 'rpc' in res['url']:
        print("URL:", res['url'])
        print("Status:", res['status'])
        print("Body:", res['body'])

print("\n--- NETWORK REQUESTS FOR RPC ---")
for req in audit['network_requests']:
    if 'rpc' in req['url']:
        print("URL:", req['url'])
        print("Post data:", req['post_data'])

