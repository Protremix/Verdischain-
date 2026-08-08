import re

# Check referral share links
content = open("/var/www/verdiscan/referral/index.html").read()
print("=== REFERRAL SHARE LINKS ===")
shares = re.findall(r'(?:twitter|x\.com|t\.me|discord|linkedin|facebook|reddit)[^\"]*[^\"]*', content)
for s in shares[:15]:
    print("  " + s[:150])

# Check contact page social section
print("\n=== CONTACT PAGE SOCIAL SECTION ===")
ccontent = open("/var/www/verdiscan/contact/index.html").read()
idx = ccontent.find("Community Support")
if idx > 0:
    print(ccontent[idx:idx+800])

# Check footer CSS vars on light vs dark pages
print("\n=== CSS VARS ===")
for page in ["index", "explorer", "dex", "cookies"]:
    path = "/var/www/verdiscan/{}/index.html".format(page) if page != "index" else "/var/www/verdiscan/index.html"
    c = open(path).read()
    hero_bg = re.findall(r'--hero-bg:\s*([^;]+)', c)
    accent = re.findall(r'--accent:\s*([^;]+)', c)
    text_white = re.findall(r'--text-white:\s*([^;]+)', c)
    text_muted = re.findall(r'--text-muted:\s*([^;]+)', c)
    text_dim = re.findall(r'--text-dim:\s*([^;]+)', c)
    print("  {}: hero_bg={} accent={} text_white={} text_muted={} text_dim={}".format(
        page,
        hero_bg[0] if hero_bg else "N/A",
        accent[0] if accent else "N/A",
        text_white[0] if text_white else "N/A",
        text_muted[0] if text_muted else "N/A",
        text_dim[0] if text_dim else "N/A"
    ))
