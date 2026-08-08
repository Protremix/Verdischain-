from playwright.sync_api import sync_playwright

def inspect_onchain():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.goto('https://verdischain.com/', wait_until='networkidle')
        page.wait_for_timeout(2000)
        
        section_html = page.evaluate("""() => {
            const heading = Array.from(document.querySelectorAll('*')).find(el => el.innerText && el.innerText.includes('ON-CHAIN METRICS'));
            if (!heading) return 'Not found';
            const parent = heading.parentElement;
            return parent ? parent.outerHTML : heading.outerHTML;
        }""")
        
        print("ON-CHAIN METRICS SECTION HTML:")
        print(section_html)

        browser.close()

inspect_onchain()
