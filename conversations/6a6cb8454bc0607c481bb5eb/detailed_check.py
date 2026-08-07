import re
import os
import subprocess

pages = ['referral', 'incentives', 'api', 'api/docs', 'contact']

for p in pages:
    path = f'/var/www/verdiscan/{p}/index.html'
    print(f"=== DETAILED CHECK FOR {p} ({path}) ===")
    if not os.path.exists(path):
        print("FILE DOES NOT EXIST")
        continue
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    
    # Check http code of page
    url = f"https://verdischain.com/{p}/"
    st_page = subprocess.getoutput(f"curl -sk -o /dev/null -w '%{{http_code}}' '{url}'")
    print(f"Page HTTP Code: {st_page}")

    # All srcs
    srcs = set(re.findall(r'src="([^"]+)"', html))
    print('SRCs found:', srcs)
    for s in sorted(srcs):
        if s.startswith('/'):
            st = subprocess.getoutput(f"curl -sk -o /dev/null -w '%{{http_code}}' 'https://verdischain.com{s}'")
            print(f'  SRC {s} -> {st}')
            
    # Check navigation block specifically
    nav_match = re.search(r'<nav[^>]*>(.*?)</nav>', html, re.DOTALL | re.IGNORECASE)
    if not nav_match:
        nav_match = re.search(r'<header[^>]*>(.*?)</header>', html, re.DOTALL | re.IGNORECASE)
    if nav_match:
        nav_html = nav_match.group(1)
        links_in_nav = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', nav_html, re.DOTALL | re.IGNORECASE)
        print('Nav links:', [(l[0], re.sub(r'<[^>]+>', '', l[1]).strip()) for l in links_in_nav])
    else:
        print('No nav or header tag found, listing first 15 <a> tags:')
        all_a = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL | re.IGNORECASE)[:15]
        print([(l[0], re.sub(r'<[^>]+>', '', l[1]).strip()) for l in all_a])
    print('\n' + '='*50 + '\n')
