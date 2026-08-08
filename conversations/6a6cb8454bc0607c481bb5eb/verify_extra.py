import asyncio
from playwright.async_api import async_playwright

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Catch console errors
        console_logs = []
        page.on('console', lambda msg: console_logs.append(f"{msg.type}: {msg.text}"))

        await page.goto('https://verdischain.com/whitepaper/', wait_until='networkidle')

        print("=== CONSOLE LOGS ===")
        for log in console_logs:
            print(log)

        # Check links
        print("\n=== INTERNAL & EXTERNAL LINKS ===")
        links = await page.evaluate("""
            () => {
                const anchors = document.querySelectorAll('a');
                return Array.from(anchors).map(a => ({
                    text: a.innerText.trim(),
                    href: a.href,
                    target: a.target
                }));
            }
        """)
        for l in links:
            print(l)

        await browser.close()

asyncio.run(audit())
