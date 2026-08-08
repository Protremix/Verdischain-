from playwright.sync_api import sync_playwright
import json

def check_overlap():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
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
                '.tag-carbon'
            ];
            const found = [];
            selectors.forEach(sel => {
                const els = document.querySelectorAll(sel);
                els.forEach(el => {
                    const r = el.getBoundingClientRect();
                    found.push({
                        selector: sel,
                        class: String(el.className),
                        text: el.innerText.replace(/\\n/g, ' ').substring(0, 50),
                        rect: { x: r.x, y: r.y, width: r.width, height: r.height, top: r.top, bottom: r.bottom, left: r.left, right: r.right },
                        zIndex: getComputedStyle(el).zIndex
                    });
                });
            });
            return found;
        }""")
        
        print("FOUND FLOATING CARDS/MOCKUPS:")
        for c in cards:
            print(f"[{c['selector']}] class='{c['class']}' zIndex={c['zIndex']} rect=({c['rect']['left']:.1f}, {c['rect']['top']:.1f}, w={c['rect']['width']:.1f}, h={c['rect']['height']:.1f}) text='{c['text']}'")

        print("\nCHECKING OVERLAPS BETWEEN CARDS:")
        for i in range(len(cards)):
            for j in range(i+1, len(cards)):
                c1 = cards[i]
                c2 = cards[j]
                r1 = c1['rect']
                r2 = c2['rect']
                
                x_overlap = max(0, min(r1['right'], r2['right']) - max(r1['left'], r2['left']))
                y_overlap = max(0, min(r1['bottom'], r2['bottom']) - max(r1['top'], r2['top']))
                area = x_overlap * y_overlap
                if area > 0:
                    pct1 = (area / (r1['width'] * r1['height'])) * 100
                    pct2 = (area / (r2['width'] * r2['height'])) * 100
                    print(f"OVERLAP ({area:.1f} px^2): '{c1['selector']}' and '{c2['selector']}' -> {pct1:.1f}% of card1, {pct2:.1f}% of card2")

        browser.close()

check_overlap()
