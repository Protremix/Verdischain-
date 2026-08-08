import urllib.request

url = "https://verdischain.com/whitepaper/?nocache=50008"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

with open("whitepaper.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Saved whitepaper.html, size:", len(html))
