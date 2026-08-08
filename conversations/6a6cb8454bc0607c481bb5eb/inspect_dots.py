import asyncio
from playwright.async_api import async_playwright

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://verdischain.com/whitepaper/', wait_until='networkidle')

        dots_data = await page.evaluate("""
            () => {
                const items = document.querySelectorAll('.story-tl-item');
                return Array.from(items).map(item => {
                    const date = item.querySelector('.story-tl-date')?.innerText;
                    const title = item.querySelector('.story-tl-title')?.innerText;
                    const dot = item.querySelector('.story-tl-dot');
                    const dotStyle = dot ? window.getComputedStyle(dot) : null;
                    const pseudoBefore = dot ? window.getComputedStyle(dot, '::before') : null;
                    const pseudoAfter = dot ? window.getComputedStyle(dot, '::after') : null;
                    return {
                        date, title,
                        dotClass: dot ? dot.className : null,
                        dotBg: dotStyle ? dotStyle.backgroundColor : null,
                        dotBorder: dotStyle ? dotStyle.borderColor : null,
                        beforeContent: pseudoBefore ? pseudoBefore.content : null,
                        afterContent: pseudoAfter ? pseudoAfter.content : null
                    };
                });
            }
        """)
        print("=== STORY TIMELINE DOTS ===")
        for d in dots_data:
            print(d)

        await browser.close()

asyncio.run(audit())
