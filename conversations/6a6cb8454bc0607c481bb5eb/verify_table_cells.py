import asyncio
from playwright.async_api import async_playwright
import json

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        await page.goto('https://verdischain.com/tokenomics/?nocache=50006', wait_until='networkidle')
        
        rows = await page.eval_on_selector_all('.vesting-table tr', '''rows => {
            return rows.map(r => {
                const cells = Array.from(r.children).map(c => {
                    const rect = c.getBoundingClientRect();
                    return { tag: c.tagName, text: c.innerText.trim(), left: rect.left, width: rect.width, right: rect.right };
                });
                return cells;
            });
        }''')
        print(json.dumps(rows, indent=2))
        await browser.close()

asyncio.run(check())
