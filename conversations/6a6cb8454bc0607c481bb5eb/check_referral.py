import bs4, re

def search_referral_details():
    for fname in ['homepage.html', 'sale.html', 'tokenomics.html']:
        with open(fname) as f:
            html = f.read()
        soup = bs4.BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        print(f"=== REFERRAL SEARCH IN {fname} ===")
        # search for 'referral'
        matches = [m.start() for m in re.finditer(r'referral', text, re.IGNORECASE)]
        for m in matches:
            print("CONTEXT:", text[max(0, m-100):min(len(text), m+100)])

search_referral_details()
