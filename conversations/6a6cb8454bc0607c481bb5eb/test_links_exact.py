import re
import subprocess
import json

files = [
    ('/developers/', 'html_dumps/developers.html'),
    ('/download/', 'html_dumps/download.html'),
    ('/referral/', 'html_dumps/referral.html'),
    ('/incentives/', 'html_dumps/incentives.html'),
    ('/api/', 'html_dumps/api.html'),
    ('/status/', 'html_dumps/status.html'),
    ('/privacy/', 'html_dumps/privacy.html'),
    ('/terms/', 'html_dumps/terms.html')
]

for path, filepath in files:
    with open(filepath, 'r') as f:
        html = f.read()
    
    # find all href, src
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html)
    srcs = re.findall(r'src=["\']([^"\']+)["\']', html)
    
    links = set(hrefs + srcs)
    print(f"\n=== PAGE: {path} ===")
    
    broken_list = []
    for link in sorted(list(links)):
        link_s = link.strip()
        if not link_s or link_s == '#' or link_s.startswith(('javascript:', 'mailto:', 'tel:', 'data:')):
            if not link_s or link_s == '#':
                broken_list.append(f"Empty/hash anchor ('{link_s}')")
            continue
        
        # Resolve URL
        if link_s.startswith('/'):
            target_url = f"https://verdischain.com{link_s}"
        elif link_s.startswith('http://') or link_s.startswith('https://'):
            target_url = link_s
        else:
            target_url = f"https://verdischain.com{path}{link_s}"
        
        # run curl
        cmd = f'curl -s -L -o /dev/null -w "%{{http_code}}" -A "Mozilla/5.0" "{target_url}"'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        status = res.stdout.strip()
        
        if status != '200':
            broken_list.append(f"{link_s} -> HTTP {status}")

    if broken_list:
        print(f"Broken links/resources found ({len(broken_list)}):")
        for b in broken_list:
            print(f"  - {b}")
    else:
        print("No broken links found!")

