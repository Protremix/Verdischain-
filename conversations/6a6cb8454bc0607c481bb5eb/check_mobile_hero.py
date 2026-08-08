from playwright.sync_api import sync_playwright

def check_mobile_hero():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 375, 'height': 812}, is_mobile=True)
        page.goto('https://verdischain.com/', wait_until='networkidle')
        page.wait_for_timeout(2000)
        
        cards = page.evaluate("""() => {
            const selectors = [
                '.dex-chart-card',
                '.monitor-frame',
                '.mobile-phone-mockup',
                '[class*="stat-pills"]',
                '.tag-staking',
                '.tag-swap',
                '.tag-vrdx',
                '.tag-carbon',
                '#hero-canvas',
                'canvas'
            ];
            const found = [];
            selectors.forEach(sel => {
                const els = document.querySelectorAll(sel);
                els.forEach(el => {
                    const r = el.getBoundingClientRect();
                    const style = getComputedStyle(el);
                    found.push({
                        selector: sel,
                        class: String(el.className),
                        text: el.innerText.replace(/\\n/g, ' ').substring(0, 50),
                        rect: { x: r.x, y: r.y, width: r.width, height: r.height, top: r.top, bottom: r.bottom, left: r.left, right: r.right },
                        display: style.display,
                        visibility: style.visibility
                    });
                });
            });
            return found;
        }""")
        
        print("MOBILE FLOATING CARDS & CANVAS:")
        for c in cards:
            print(f"[{c['selector']}] rect=(x={c['rect']['x']:.1f}, y={c['rect']['y']:.1f}, w={c['rect']['width']:.1f}, h={c['rect']['height']:.1f}) disp={c['display']} text='{c['text']}'")

        browser.close()

check_mobile_hero()
