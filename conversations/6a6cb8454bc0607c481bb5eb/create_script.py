import subprocess
import os
import json

remote_script = """
import os
import subprocess
import glob

pages = ["referral", "incentives", "api", "api/docs", "contact"]

results = {}

for page in pages:
    p_info = {}
    url_path = f"/{page}/"
    full_url = f"https://verdischain.com{url_path}"
    
    # 1. HTTP Code
    cmd_code = f"curl -sk -o /dev/null -w '%{{http_code}}' {full_url}"
    p_info['http_code'] = subprocess.getoutput(cmd_code)
    
    file_path = f"/var/www/verdiscan/{page}/index.html"
    p_info['file_exists'] = os.path.exists(file_path)
    
    if p_info['file_exists']:
        # Read content for custom checks as well
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # 2. Unstyled headings
        cmd_headings = f"grep -oP '<h[1-6][^>]*>' {file_path} 2>/dev/null | grep -v 'class=' | head -10"
        p_info['unstyled_headings'] = [h for h in subprocess.getoutput(cmd_headings).splitlines() if h.strip()]
        
        # 3. Internal links
        cmd_links = f"grep -oP 'href=\"/[^\"]*\"' {file_path} 2>/dev/null | sed 's/href=\"//;s/\"//' | sort -u"
        links = [l.strip() for l in subprocess.getoutput(cmd_links).splitlines() if l.strip()]
        link_statuses = {}
        for link in links:
            link_url = f"https://verdischain.com{link}"
            st = subprocess.getoutput(f"curl -sk -o /dev/null -w '%{{http_code}}' '{link_url}'")
            link_statuses[link] = st
        p_info['internal_links'] = link_statuses
        
        # 4. Huge text
        cmd_huge = f"grep -oP 'font-size:\\s*([3-9][0-9]|[1-9][0-9]{{2}})px' {file_path} 2>/dev/null | sort -u"
        p_info['huge_text'] = [ht for ht in subprocess.getoutput(cmd_huge).splitlines() if ht.strip()]
        
        # 5. Logo
        cmd_logo = f"grep -oP 'src=\"[^\"]*logo[^\"]*\"' {file_path} 2>/dev/null | head -3"
        p_info['logo_matches'] = [lg for lg in subprocess.getoutput(cmd_logo).splitlines() if lg.strip()]
        
        # 6. Nav links (raw grep)
        cmd_nav = f"grep -oP '<a[^>]*href=\"/[^\"]*\"[^>]*>[^<]*</a>' {file_path} 2>/dev/null | head -15"
        p_info['nav_matches'] = [n for n in subprocess.getoutput(cmd_nav).splitlines() if n.strip()]

    results[page] = p_info

import json
print(json.dumps(results, indent=2))
"""

with open("remote_audit.py", "w") as f:
    f.write(remote_script)

print("Created remote_audit.py")
