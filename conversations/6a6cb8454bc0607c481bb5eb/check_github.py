import urllib.request

url = 'https://github.com/Protremix/Verdischain-'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
res = urllib.request.urlopen(req)
print("Final URL:", res.geturl())
print("Status:", res.getcode())
