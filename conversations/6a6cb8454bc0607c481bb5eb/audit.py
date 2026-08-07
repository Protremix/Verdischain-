import re
import subprocess
import os
from html.parser import HTMLParser

pages = ["faucet", "validators", "docs"]
req_links = ["Home", "Verdiscan", "DEX", "Validators", "Eco", "Faucet", "Wallet", "Sale", "Contact", "API", "Docs"]

class NavAndTagParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = [] # list of (tag, attrs_dict, text)
        self.in_heading = None
        self.heading_text = ""
        self.in_nav = False
        self.nav_depth = 0
        self.nav_links = [] # list of (text, href)
        self.in_nav_a = False
        self.current_a_href = None
        self.current_a_text = ""
        self.img_logos = [] # list of (src, alt)
        self.all_hrefs = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            self.in_heading = tag
            self.heading_text = ""
            self.headings.append((tag, attr_dict))

        if tag == "nav" or (tag == "div" and "nav" in attr_dict.get("class", "").split()):
            self.in_nav = True
            self.nav_depth += 1
        elif self.in_nav and tag in ["div", "nav", "ul", "section"]:
            self.nav_depth += 1

        if tag == "a":
            href = attr_dict.get("href")
            if href:
                self.all_hrefs.append(href)
            if self.in_nav:
                self.in_nav_a = True
                self.current_a_href = href
                self.current_a_text = ""

        if tag == "img":
            src = attr_dict.get("src", "")
            if "logo" in src.lower():
                self.img_logos.append((src, attr_dict.get("alt", "")))

    def handle_endtag(self, tag):
        if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            self.in_heading = None

        if self.in_nav_a and tag == "a":
            self.in_nav_a = False
            self.nav_links.append((self.current_a_text.strip(), self.current_a_href))

        if self.in_nav:
            if tag in ["nav", "div", "ul", "section"]:
                self.nav_depth -= 1
                if self.nav_depth <= 0:
                    self.in_nav = False

    def handle_data(self, data):
        if self.in_nav_a:
            self.current_a_text += data

for p in pages:
    path = f"/var/www/verdiscan/{p}/index.html"
    print("=" * 60)
    print(f"AUDIT REPORT FOR PAGE: {p}")
    print("=" * 60)

    # 1. Page Curl HTTP status
    res = subprocess.run(["curl", "-sk", "-o", "/dev/null", "-w", "%{http_code}", f"https://verdischain.com/{p}/"], capture_output=True, text=True)
    status_code = res.stdout.strip()
    print(f"Page HTTP Status Code: {status_code}")

    if not os.path.exists(path):
        print(f"Error: {path} does not exist!")
        continue

    with open(path, "r", encoding="utf-8") as f:
        html_content = f.read()

    parser = NavAndTagParser()
    parser.feed(html_content)

    # 2. Unstyled Headings Check
    # Prompt check: grep -oP '<h[1-6][^>]*>' ... | grep -v 'class='
    raw_heading_tags = re.findall(r"<h[1-6][^>]*>", html_content)
    raw_no_class = [h for h in raw_heading_tags if "class=" not in h]
    print(f"\nUnstyled Headings Check (h1-h6 without 'class=' attribute):")
    print(f"  Total heading tags in HTML: {len(raw_heading_tags)}")
    print(f"  Headings without class= attribute: {len(raw_no_class)}")
    for h in raw_no_class[:10]:
        print(f"    {h}")

    # 3. Logo Check
    print(f"\nLogo Image Check:")
    logo_srcs = re.findall(r'src="[^"]*logo[^"]*"', html_content)
    print(f"  Logo image src matches in HTML: {len(logo_srcs)}")
    for ls in logo_srcs[:3]:
        print(f"    {ls}")
    
    if logo_srcs:
        first_logo_path = logo_srcs[0].replace('src="', '').replace('"', '')
        logo_url = f"https://verdischain.com{first_logo_path}" if first_logo_path.startswith("/") else first_logo_path
        res_logo = subprocess.run(["curl", "-sk", "-o", "/dev/null", "-w", "%{http_code}", logo_url], capture_output=True, text=True)
        print(f"  Logo Image HTTP Status: {res_logo.stdout.strip()} ({logo_url})")
        
        file_path_on_disk = f"/var/www/verdiscan{first_logo_path}" if first_logo_path.startswith("/") else first_logo_path
        exists_on_disk = os.path.exists(file_path_on_disk)
        print(f"  Logo File on Disk: {'EXISTS' if exists_on_disk else 'MISSING'} ({file_path_on_disk})")
    else:
        print("  NO logo image tag found in page HTML.")

    # 4. Nav Links Check (11 required links)
    # Prompt check: grep -oP '<a[^>]*href="/[^"]*"[^>]*>[^<]*</a>' ... | head -15
    print(f"\nNav Links Check:")
    nav_a_matches = re.findall(r'<a[^>]*href="/[^"]*"[^>]*>[^<]*</a>', html_content)
    print(f"  Top Nav Anchor Tags in HTML (first 15 shown):")
    for a_tag in nav_a_matches[:15]:
        print(f"    {a_tag}")

    # Parse link text vs required 11
    # Required: Home, Verdiscan, DEX, Validators, Eco, Faucet, Wallet, Sale, Contact, API, Docs
    # Find all top nav links
    found_nav_items = []
    for a_tag in nav_a_matches:
        m = re.search(r'href="(/[^"]*)"[^>]*>([^<]*)</a>', a_tag)
        if m:
            href, text = m.group(1), m.group(2).strip()
            found_nav_items.append((text, href))

    # Check 11 required links
    nav_texts_lower = [item[0].lower() for item in found_nav_items[:15]]
    missing_nav = []
    for req in req_links:
        if req.lower() not in nav_texts_lower:
            missing_nav.append(req)

    print(f"  11 Required Nav Links Status: {'PASS - All 11 present' if not missing_nav else 'FAIL - Missing: ' + ', '.join(missing_nav)}")

    # 5. Internal Links Check
    # Prompt check: grep -oP 'href="/[^"]*"' ... | sed 's/href="//;s/"//' | sort -u
    print(f"\nInternal Links Audit:")
    internal_hrefs = sorted(list(set(re.findall(r'href="(/[^"]*)"', html_content))))
    print(f"  Found {len(internal_hrefs)} unique internal link targets:")
    non_200 = []
    for href in internal_hrefs:
        url = f"https://verdischain.com{href}"
        res_link = subprocess.run(["curl", "-sk", "-o", "/dev/null", "-w", "%{http_code}", url], capture_output=True, text=True)
        code = res_link.stdout.strip()
        print(f"    {href} -> {code}")
        if code != "200":
            non_200.append((href, code))

    print(f"  Internal Links 200 Result: {'PASS (All return 200)' if not non_200 else 'FAIL (Non-200 links: ' + str(non_200) + ')'}")

    # 6. Huge text check
    # Prompt check: grep -oP 'font-size:\s*([3-9][0-9]|[1-9][0-9]{2})px' ...
    huge_matches = sorted(list(set(re.findall(r'font-size:\s*([3-9][0-9]|[1-9][0-9]{2})px', html_content))))
    print(f"\nHuge Text Check (font-size >= 30px):")
    print(f"  Matches found: {huge_matches if huge_matches else 'None'}")

    print("\n")
