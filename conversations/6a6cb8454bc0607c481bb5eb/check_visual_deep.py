import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # Test on 1280 (Desktop)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('https://verdischain.com/whitepaper/?nocache=50008')
        
        # 1. Heading font sizes
        headings = await page.evaluate('''() => {
            const hs = Array.from(document.querySelectorAll('h1, h2, h3, h4, .section-title, .hero-title'));
            return hs.map(h => {
                const s = window.getComputedStyle(h);
                return {
                    tag: h.tagName,
                    class: h.className,
                    text: h.innerText.replace(/\\n/g, ' '),
                    fontSize: s.fontSize,
                    lineHeight: s.lineHeight
                };
            });
        }''')
        
        print("=== HEADINGS FONT SIZES ===")
        for h in headings:
            print(f"[{h['tag']}.{h['class']}] -> font-size: {h['fontSize']} | line-height: {h['lineHeight']} | text: '{h['text'][:40]}'")
            
        # 2. Check for button styling and text visibility
        buttons = await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('.btn-primary, .btn-secondary, button, a.btn'));
            return btns.map(b => {
                const rect = b.getBoundingClientRect();
                const s = window.getComputedStyle(b);
                return {
                    text: b.innerText,
                    fontSize: s.fontSize,
                    padding: s.padding,
                    bg: s.background,
                    color: s.color,
                    rect: {w: rect.width, h: rect.height}
                };
            });
        }''')
        print("\n=== BUTTON STYLES ===")
        for b in buttons:
            print(f"Btn: '{b['text']}' -> fs: {b['fontSize']}, pad: {b['padding']}, color: {b['color']}, rect: {b['rect']}")

        # 3. Check table visual / scroll responsiveness
        tables = await page.evaluate('''() => {
            const ts = Array.from(document.querySelectorAll('table'));
            return ts.map(t => {
                const rect = t.getBoundingClientRect();
                const parent = t.parentElement;
                const parentRect = parent.getBoundingClientRect();
                return {
                    tableWidth: rect.width,
                    parentWidth: parentRect.width,
                    overflows: rect.width > parentRect.width
                };
            });
        }''')
        print("\n=== TABLES RESPONSIVENESS ===")
        for t in tables:
            print(t)

        await browser.close()

asyncio.run(main())
