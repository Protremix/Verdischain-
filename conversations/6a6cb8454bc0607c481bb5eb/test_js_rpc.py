import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        console_logs = []
        page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        await page.goto('https://verdischain.com/whitepaper/?nocache=50008')
        await page.wait_for_timeout(5000) # wait 5 seconds for JS / RPC
        
        stat_text = await page.evaluate('''() => {
            return {
                statBlock: document.querySelector('#stat-block') ? document.querySelector('#stat-block').innerText : null,
                statBlockSub: document.querySelector('#stat-block-sub') ? document.querySelector('#stat-block-sub').innerText : null,
                statValidators: document.querySelector('#stat-validators') ? document.querySelector('#stat-validators').innerText : null,
                statPeers: document.querySelector('#stat-peers') ? document.querySelector('#stat-peers').innerText : null,
            };
        }''')
        
        print("Stat Block Values after 5s:", stat_text)
        print("Console logs during execution:")
        for log in console_logs:
            print(" ", log)
            
        await browser.close()

asyncio.run(main())
