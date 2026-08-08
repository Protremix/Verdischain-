import asyncio
from playwright.async_api import async_playwright
import json

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Desktop 1920x1080
        page_desktop = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        await page_desktop.goto('https://verdischain.com/validators/', wait_until='networkidle')
        await asyncio.sleep(1)
        await page_desktop.screenshot(path='desktop_1920.png', full_page=True)
        
        # Desktop 1280x800
        page_d1280 = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page_d1280.goto('https://verdischain.com/validators/', wait_until='networkidle')
        await asyncio.sleep(1)
        await page_d1280.screenshot(path='desktop_1280.png', full_page=True)

        # Mobile 375x812 (iPhone 12/13/14 mini)
        page_mobile = await browser.new_page(viewport={'width': 375, 'height': 812})
        await page_mobile.goto('https://verdischain.com/validators/', wait_until='networkidle')
        await asyncio.sleep(1)
        await page_mobile.screenshot(path='mobile_375.png', full_page=True)
        
        # Let's inspect layout & CSS properties
        desktop_layout = await page_d1280.evaluate('''() => {
            const list = document.getElementById('validatorList');
            const rows = document.querySelectorAll('.validator-row');
            const header = document.querySelector('.validators-header');
            
            return {
                rowCount: rows.length,
                rowsData: Array.from(rows).map(r => r.innerText.replace(/\\n/g, ' | ')),
                listWidth: list ? list.offsetWidth : null,
                containerWidth: document.querySelector('.container') ? document.querySelector('.container').offsetWidth : null
            };
        }''')
        
        mobile_layout = await page_mobile.evaluate('''() => {
            const list = document.getElementById('validatorList');
            const rows = document.querySelectorAll('.validator-row');
            const hamburger = document.getElementById('navHamburger');
            const navLinks = document.querySelector('.nav-links');
            
            // Check overflow per element
            const overflow = [];
            document.querySelectorAll('*').forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.right > window.innerWidth + 1) {
                    overflow.push({
                        tag: el.tagName,
                        cls: el.className,
                        id: el.id,
                        right: rect.right,
                        width: rect.width
                    });
                }
            });
            
            // Click hamburger
            let navStateBefore = navLinks ? window.getComputedStyle(navLinks).display : null;
            if (hamburger) hamburger.click();
            let navStateAfter = navLinks ? window.getComputedStyle(navLinks).display : null;
            
            return {
                rowCount: rows.length,
                rowsData: Array.from(rows).map(r => r.innerText.replace(/\\n/g, ' | ')),
                overflow,
                navStateBefore,
                navStateAfter
            };
        }''')
        
        print("Desktop Layout:", json.dumps(desktop_layout, indent=2))
        print("Mobile Layout:", json.dumps(mobile_layout, indent=2))

        await browser.close()

asyncio.run(run())
