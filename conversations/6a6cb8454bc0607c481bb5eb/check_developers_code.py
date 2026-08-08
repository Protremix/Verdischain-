from bs4 import BeautifulSoup

soup = BeautifulSoup(open("dumps/developers.html", "r", encoding="utf-8"), "html.parser")

pre_tags = soup.find_all('pre')
print(f"Total <pre> blocks in Developers page: {len(pre_tags)}")

for idx, pre in enumerate(pre_tags):
    txt = pre.get_text()
    print(f"\n--- CODE BLOCK [{idx+1}] ---")
    print(txt)

