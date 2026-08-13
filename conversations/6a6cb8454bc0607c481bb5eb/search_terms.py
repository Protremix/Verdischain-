import bs4, re

def find_terms(fname, html_content):
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    
    keywords = ['referral', '10%', '5%', '2.5%', 'audit', 'mica', 'ai', 'evolvix', 'team', 'investor', 'partner', '18m', '4.5m', 'hard cap', 'net zero', 'carbon negative', 'green']
    print(f"=== KEYWORD SEARCH IN {fname} ===")
    for kw in keywords:
        matches = [m.start() for m in re.finditer(re.escape(kw), text, re.IGNORECASE)]
        if matches:
            print(f"Found '{kw}': {len(matches)} times")
            for m in matches[:5]: # show first 5 contexts
                start = max(0, m - 50)
                end = min(len(text), m + 50)
                snippet = text[start:end].replace('\n', ' ')
                print(f"   ...{snippet}...")

find_terms("homepage.html", open("homepage.html").read())
find_terms("sale.html", open("sale.html").read())
find_terms("tokenomics.html", open("tokenomics.html").read())
