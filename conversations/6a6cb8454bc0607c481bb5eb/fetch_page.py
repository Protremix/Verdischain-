import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        
        # Capture console messages and errors
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"CONSOLE {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: console_logs.append(f"PAGE ERROR: {err}"))

        response = await page.goto('https://verdischain.com/tokenomics/?nocache=50006', wait_until='networkidle')
        print(f"Status: {response.status}")
        
        content = await page.content()
        with open('page.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"HTML saved, length: {len(content)}")
        
        # Take screenshot
        await page.screenshot(path='desktop.png', full_page=True)
        print("Desktop screenshot saved.")
        
        # Mobile screenshot
        mobile_page = await browser.new_page(viewport={'width': 375, 'height': 812}, is_mobile=True)
        await mobile_page.goto('https://verdischain.com/tokenomics/?nocache=50006', wait_until='networkidle')
        await mobile_page.screenshot(path='mobile.png', full_page=True)
        print("Mobile screenshot saved.")
        
        with open('console.log', 'w', encoding='utf-8') as f:
            f.write('\n'.join(console_logs))

        await browser.close()

asyncio.run(main())
