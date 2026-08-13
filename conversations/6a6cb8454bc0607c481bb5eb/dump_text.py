import bs4

def analyze_page(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = bs4.BeautifulSoup(html, 'html.parser')
    
    print("==================================================")
    print(f"FILE: {file_path}")
    print("==================================================")
    
    # Print all text content structured
    for elem in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'td', 'th', 'span', 'div']):
        # If element has no children elements with text (i.e. leaf node or direct text wrapper)
        if not elem.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'td', 'th']):
            text = elem.get_text(strip=True)
            if text and len(text) > 1:
                # Get class / id if available
                classes = ".".join(elem.get('class', []))
                elem_id = elem.get('id', '')
                location_info = f"<{elem.name}" + (f" id='{elem_id}'" if elem_id else "") + (f" class='{classes}'" if classes else "") + ">"
                # Avoid printing duplicated text from parent nodes
                # We'll just print text with context
                
# Actually, let's write a cleaner extractor that walks the DOM and extracts key blocks/sections and text

with open("homepage_text.txt", "w") as out:
    soup = bs4.BeautifulSoup(open("homepage.html").read(), 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    out.write(soup.get_text(separator="\n"))

with open("sale_text.txt", "w") as out:
    soup = bs4.BeautifulSoup(open("sale.html").read(), 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    out.write(soup.get_text(separator="\n"))

with open("tokenomics_text.txt", "w") as out:
    soup = bs4.BeautifulSoup(open("tokenomics.html").read(), 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    out.write(soup.get_text(separator="\n"))

print("Text files written successfully.")
