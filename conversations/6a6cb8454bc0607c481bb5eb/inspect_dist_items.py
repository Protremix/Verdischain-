import asyncio
from playwright.async_api import async_playwright

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://verdischain.com/whitepaper/', wait_until='networkidle')

        items = await page.evaluate("""
            () => {
                const distItems = document.querySelectorAll('.dist-item');
                return Array.from(distItems).map(item => {
                    const dot = item.querySelector('.dist-dot');
                    const name = item.querySelector('.dist-name')?.innerText;
                    const desc = item.querySelector('.dist-desc')?.innerText;
                    const pct = item.querySelector('.dist-pct')?.innerText;
                    const amt = item.querySelector('.dist-amt')?.innerText;
                    return {
                        name, desc, pct, amt,
                        dotColor: dot ? dot.style.background : null
                    };
                });
            }
        """)
        print("=== ALL DIST ITEMS ===")
        for i in items:
            print(f"Name: {i['name']} | Dot: {i['dotColor']} | Pct: {i['pct']} | Amt: {i['amt']} | Desc: {i['desc']}")

        await browser.close()

asyncio.run(audit())
