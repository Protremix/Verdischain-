import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # Test across multiple viewports
        viewports = [
            {'name': 'Desktop-1920', 'width': 1920, 'height': 1080},
            {'name': 'Desktop-1280', 'width': 1280, 'height': 800},
            {'name': 'Tablet-768', 'width': 768, 'height': 1024},
            {'name': 'Mobile-375', 'width': 375, 'height': 812},
        ]
        
        for vp in viewports:
            page = await browser.new_page(viewport={'width': vp['width'], 'height': vp['height']})
            
            console_logs = []
            page_errors = []
            failed_requests = []
            
            page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
            page.on('pageerror', lambda err: page_errors.append(str(err)))
            page.on('requestfailed', lambda req: failed_requests.append(f"{req.url} - {req.failure}"))
            
            await page.goto('https://verdischain.com/whitepaper/?nocache=50008', wait_until='networkidle')
            
            print(f"\n=================== VIEWPORT: {vp['name']} ({vp['width']}x{vp['height']}) ===================")
            print("Console logs:", len(console_logs))
            for log in console_logs:
                print("  LOG:", log)
            print("Page errors:", len(page_errors))
            for err in page_errors:
                print("  ERROR:", err)
            print("Failed requests:", len(failed_requests))
            for freq in failed_requests:
                print("  FAILED REQ:", freq)
                
            # Check overflow x
            has_overflow_x = await page.evaluate('''() => {
                return document.documentElement.scrollWidth > document.documentElement.clientWidth;
            }''')
            print(f"Horizontal scroll overflow? {has_overflow_x}")
            
            # Take screenshot for visual check
            shot_name = f"screenshot_{vp['name']}.png"
            await page.screenshot(path=shot_name, full_page=True)
            print(f"Saved screenshot: {shot_name}")
            
            await page.close()
            
        await browser.close()

asyncio.run(main())
