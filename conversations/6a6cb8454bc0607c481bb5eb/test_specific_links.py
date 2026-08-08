import urllib.request
import urllib.parse
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls_to_test = [
    "https://verdischain.com/chain-spec.json",
    "https://verdischain.com/verdis-wallet-release.apk",
    "https://github.com/Protremix/Verdischain-",
    "https://github.com/verdischain/verdis-js-sdk",
    "https://github.com/verdischain/verdis-subxt",
    "https://github.com/verdischain/verdis-py",
    "https://evolvixos.com",
    "https://verdischain.com/api/",
    "https://verdischain.com/faucet/",
    "https://verdischain.com/explorer/",
    "https://verdischain.com/dex/",
    "https://verdischain.com/whitepaper/",
    "https://verdischain.com/wallet/",
    "https://verdischain.com/sale/",
    "https://verdischain.com/tokenomics/",
    "https://verdischain.com/validators/",
    "https://verdischain.com/eco/",
    "https://verdischain.com/referral/",
    "https://verdischain.com/incentives/",
    "https://verdischain.com/contact/"
]

for url in urls_to_test:
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    )
    try:
        res = urllib.request.urlopen(req, timeout=10, context=ctx)
        content_type = res.headers.get('Content-Type', '')
        length = len(res.read())
        print(f"URL: {url}\n  => Status: {res.status}, Type: {content_type}, Length: {length} bytes, Final: {res.geturl()}")
    except urllib.error.HTTPError as e:
        print(f"URL: {url}\n  => HTTP ERROR: {e.code} ({e.reason})")
    except Exception as e:
        print(f"URL: {url}\n  => ERROR: {e}")

