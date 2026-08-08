import asyncio
from playwright.async_api import async_playwright

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://verdischain.com/whitepaper/', wait_until='networkidle')

        vest_cards = await page.evaluate("""
            () => {
                const sec = document.querySelector('#vesting') || document.querySelectorAll('section')[2];
                const cards = document.querySelectorAll('.vest-card, .vesting-card, [class*="vest-"]');
                return Array.from(cards).map(c => ({
                    title: c.querySelector('.vest-title, h3, h4, [class*="title"]')?.innerText,
                    text: c.innerText,
                    html: c.innerHTML
                }));
            }
        """)
        print("=== VESTING CARDS ===")
        for i, c in enumerate(vest_cards):
            print(f"Card {i}: Title={c['title']}")
            print("  Text:", c['text'].replace('\n', ' | '))
            print("  HTML:", c['html'][:200])

        await browser.close()

asyncio.run(audit())
