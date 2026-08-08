import urllib.request

url = 'https://verdischain.com/validators/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

style_start = html.find('<style>')
style_end = html.find('</style>')

print(html[style_start+7:style_end])

