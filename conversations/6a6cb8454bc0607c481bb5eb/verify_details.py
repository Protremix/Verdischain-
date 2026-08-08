import urllib.request
import json

# Check image response
img_url = 'https://verdischain.com/assets/verdis-logo-black.png'
req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    res = urllib.request.urlopen(req)
    print("Logo image status:", res.status, "Content-Length:", len(res.read()))
except Exception as e:
    print("Logo image error:", e)

