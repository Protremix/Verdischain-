import asyncio
from playwright.async_api import async_playwright

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://verdischain.com/whitepaper/', wait_until='networkidle')

        # Check colors of alloc cards vs pie segments
        card_colors = await page.evaluate("""
            () => {
                const cards = document.querySelectorAll('.alloc-card');
                return Array.from(cards).map(c => {
                    const title = c.querySelector('.alloc-card-title')?.innerText;
                    const pct = c.querySelector('.alloc-pct')?.innerText;
                    const bar = c.querySelector('.alloc-pct-bar, [class*="bar"], [class*="color"], [class*="dot"]');
                    const style = window.getComputedStyle(c);
                    const beforeStyle = window.getComputedStyle(c, '::before');
                    const dotStyle = c.querySelector('.alloc-pct-badge') ? window.getComputedStyle(c.querySelector('.alloc-pct-badge')) : null;
                    return {
                        title, pct,
                        borderColor: style.borderColor,
                        borderLeftColor: style.borderLeftColor,
                        badgeBg: dotStyle ? dotStyle.backgroundColor : null,
                        outerHTML: c.outerHTML
                    };
                });
            }
        """)
        print("=== ALLOC CARD COLORS ===")
        for cc in card_colors:
            print(f"Title: {cc['title']} | Pct: {cc['pct']} | BorderLeft: {cc['borderLeftColor']} | BadgeBg: {cc['badgeBg']}")
            print("  HTML:", cc['outerHTML'][:150])

        await browser.close()

asyncio.run(audit())
