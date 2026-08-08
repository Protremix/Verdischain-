from playwright.sync_api import sync_playwright

def inspect_stats():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.goto('https://verdischain.com/', wait_until='networkidle')
        page.wait_for_timeout(3000)
        
        # Scroll down to ensure IntersectionObserver triggers if any
        page.evaluate("window.scrollTo(0, 1000)")
        page.wait_for_timeout(2000)
        page.evaluate("window.scrollTo(0, 2000)")
        page.wait_for_timeout(2000)
        
        stats_info = page.evaluate("""() => {
            // Find stat containers
            const cards = Array.from(document.querySelectorAll('*')).filter(el => {
                const text = el.innerText || '';
                return text.includes('TOTAL TOKEN SUPPLY') || text.includes('EVM OPCODES') || text.includes('TESTS PASSING') || text.includes('PRODUCTION PALLETS');
            });
            
            return cards.map(c => ({
                outerHTML: c.outerHTML,
                innerText: c.innerText
            }));
        }""")
        
        print("=== STAT CARDS HTML & TEXT ===")
        for s in stats_info[:5]:
            print("--- Card ---")
            print("Text:", repr(s['innerText']))
            print("HTML:", s['outerHTML'][:300])

        browser.close()

inspect_stats()
