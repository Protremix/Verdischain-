import asyncio
from playwright.async_api import async_playwright

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://verdischain.com/whitepaper/', wait_until='networkidle')

        # Find section containing "Supply Distribution"
        tokenomics_html = await page.evaluate("""
            () => {
                const headers = Array.from(document.querySelectorAll('h2, h3'));
                const distHeader = headers.find(h => h.innerText.includes('Supply Distribution'));
                if (!distHeader) return 'Not found';
                const section = distHeader.closest('section') || distHeader.parentElement.parentElement;
                return section.innerHTML;
            }
        """)
        print("=== SUPPLY DISTRIBUTION SECTION HTML ===")
        print(tokenomics_html[:2000])

        await browser.close()

asyncio.run(audit())
