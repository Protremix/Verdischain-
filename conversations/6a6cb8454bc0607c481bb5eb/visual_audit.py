import asyncio
import json
from playwright.async_api import async_playwright

async def check_visuals():
    import os
    os.environ['PLAYWRIGHT_NODE_JS_PATH'] = '/usr/bin/node'

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Test Desktop (1440x900)
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        await page.goto('https://verdischain.com/?nocache=50001', wait_until='networkidle')
        await page.wait_for_timeout(3000)

        # 1. Check Image status
        images = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('img')).map(img => ({
                src: img.src,
                naturalWidth: img.naturalWidth,
                naturalHeight: img.naturalHeight,
                complete: img.complete,
                alt: img.alt,
                outer: img.outerHTML
            }));
        }''')
        print("=== IMAGES (Desktop) ===")
        for img in images:
            print(img)

        # 2. Check for Horizontal Overflow (X-scrollbar)
        overflow_x = await page.evaluate('''() => {
            return {
                scrollWidth: document.documentElement.scrollWidth,
                clientWidth: document.documentElement.clientWidth,
                hasOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth
            };
        }''')
        print("\n=== OVERFLOW X (Desktop) ===")
        print(overflow_x)

        # 3. Check for elements extending beyond viewport
        offscreen_elements = await page.evaluate('''() => {
            const width = window.innerWidth;
            const elements = document.querySelectorAll('*');
            const bad = [];
            elements.forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.right > width + 5 && rect.width > 0) {
                    bad.append || bad.push({
                        tag: el.tagName,
                        id: el.id,
                        className: el.className,
                        right: rect.right,
                        width: rect.width,
                        text: el.innerText ? el.innerText.substring(0, 30) : ''
                    });
                }
            });
            return bad;
        }''')
        print(f"\n=== OFFSCREEN/OVERFLOWING ELEMENTS (Desktop: {len(offscreen_elements)}) ===")
        for el in offscreen_elements[:10]:
            print(el)

        # 4. Check Mobile (375x812)
        mobile_page = await browser.new_page(viewport={'width': 375, 'height': 812})
        await mobile_page.goto('https://verdischain.com/?nocache=50001', wait_until='networkidle')
        await mobile_page.wait_for_timeout(3000)

        mobile_overflow_x = await mobile_page.evaluate('''() => {
            return {
                scrollWidth: document.documentElement.scrollWidth,
                clientWidth: document.documentElement.clientWidth,
                hasOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth
            };
        }''')
        print("\n=== OVERFLOW X (Mobile) ===")
        print(mobile_overflow_x)

        mobile_offscreen = await mobile_page.evaluate('''() => {
            const width = window.innerWidth;
            const elements = document.querySelectorAll('*');
            const bad = [];
            elements.forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.right > width + 5 && rect.width > 0) {
                    bad.push({
                        tag: el.tagName,
                        id: el.id,
                        className: el.className,
                        right: rect.right,
                        width: rect.width,
                        text: el.innerText ? el.innerText.substring(0, 30) : ''
                    });
                }
            });
            return bad;
        }''')
        print(f"\n=== OFFSCREEN/OVERFLOWING ELEMENTS (Mobile: {len(mobile_offscreen)}) ===")
        for el in mobile_offscreen[:10]:
            print(el)

        # 5. Check Mobile Nav Menu interaction
        mobile_nav_state = await mobile_page.evaluate('''() => {
            const hamburger = document.getElementById('navHamburger');
            const navLinks = document.querySelector('.nav-links');
            return {
                hamburgerExists: !!hamburger,
                hamburgerDisplay: hamburger ? window.getComputedStyle(hamburger).display : null,
                navLinksDisplay: navLinks ? window.getComputedStyle(navLinks).display : null,
                navLinksClass: navLinks ? navLinks.className : null
            };
        }''')
        print("\n=== MOBILE NAV MENU STATE ===")
        print(mobile_nav_state)

        # Click hamburger and check menu display
        await mobile_page.click('#navHamburger')
        await mobile_page.wait_for_timeout(500)
        mobile_nav_after_click = await mobile_page.evaluate('''() => {
            const navLinks = document.querySelector('.nav-links');
            const rect = navLinks ? navLinks.getBoundingClientRect() : null;
            return {
                navLinksClass: navLinks ? navLinks.className : null,
                visible: rect ? (rect.width > 0 && rect.height > 0) : false,
                rect: rect
            };
        }''')
        print("\n=== MOBILE NAV AFTER CLICK ===")
        print(mobile_nav_after_click)
        await mobile_page.screenshot(path='mobile_nav_open.png')

        await browser.close()

asyncio.run(check_visuals())
