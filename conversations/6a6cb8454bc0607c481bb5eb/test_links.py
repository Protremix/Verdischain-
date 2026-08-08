import urllib.request
import urllib.error
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

links = [
    ("Nav logo", "https://verdischain.com/"),
    ("Nav Verdiscan", "https://verdischain.com/explorer/"),
    ("Nav DEX", "https://verdischain.com/dex/"),
    ("Nav Whitepaper", "https://verdischain.com/whitepaper/"),
    ("Nav Wallet", "https://verdischain.com/wallet/"),
    ("Nav Sale", "https://verdischain.com/sale/"),
    ("Nav Tokenomics", "https://verdischain.com/tokenomics/"),
    ("Nav Faucet", "https://verdischain.com/faucet/"),
    ("FAQ Verdis Wallet link", "https://verdischain.com/wallet/"),
    ("Footer Home", "https://verdischain.com/"),
    ("Footer Verdiscan", "https://verdischain.com/explorer/"),
    ("Footer DEX", "https://verdischain.com/dex/"),
    ("Footer Whitepaper", "https://verdischain.com/whitepaper/"),
    ("Footer Wallet", "https://verdischain.com/wallet/"),
    ("Footer Sale", "https://verdischain.com/sale/"),
    ("Footer Tokenomics", "https://verdischain.com/tokenomics/"),
    ("Footer Faucet", "https://verdischain.com/faucet/"),
    ("Footer Validators", "https://verdischain.com/validators/"),
    ("Footer Eco", "https://verdischain.com/eco/"),
    ("Footer Referral", "https://verdischain.com/referral/"),
    ("Footer Incentives", "https://verdischain.com/incentives/"),
    ("Footer Contact", "https://verdischain.com/contact/"),
    ("Footer API", "https://verdischain.com/api/"),
    ("Footer Docs", "https://verdischain.com/docs/"),
    ("Footer GitHub", "https://github.com/Protremix/Verdischain-"),
]

for label, url in links:
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        print(f"[{resp.status}] SUCCESS: {label} -> {url}")
    except urllib.error.HTTPError as e:
        print(f"[{e.code}] BROKEN LINK: {label} -> {url}")
    except Exception as e:
        print(f"[ERR] FAILED: {label} -> {url} ({e})")
