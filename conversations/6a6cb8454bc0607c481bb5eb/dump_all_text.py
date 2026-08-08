from bs4 import BeautifulSoup, NavigableString

with open('page_source.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

def walk_tree(el, section_name="Root"):
    if isinstance(el, NavigableString):
        text = str(el).strip()
        if text:
            print(f"[{section_name}] <{el.parent.name} class='{el.parent.get('class', '')}' id='{el.parent.get('id', '')}'> -> {text}")
    else:
        current_sec = section_name
        if el.name in ['section', 'nav', 'header', 'footer']:
            current_sec = f"{el.name}#{el.get('id', '')}.{'.'.join(el.get('class', []))}"
        for child in el.children:
            walk_tree(child, current_sec)

walk_tree(soup.body)
