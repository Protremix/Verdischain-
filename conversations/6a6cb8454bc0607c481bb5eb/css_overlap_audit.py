import asyncio
from playwright.async_api import async_playwright

async def audit_layout():
    import os
    os.environ['PLAYWRIGHT_NODE_JS_PATH'] = '/usr/bin/node'

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        await page.goto('https://verdischain.com/?nocache=50001', wait_until='networkidle')

        # Run DOM & CSS inspection script inside browser
        analysis = await page.evaluate('''() => {
            const results = {
                textCutOff: [],
                overlaps: [],
                zindexIssues: [],
                computedStyles: []
            };

            // 1. Check for text truncation or overflow in buttons, cards, badges
            const textContainers = document.querySelectorAll('h1, h2, h3, h4, p, span, a, button, div.badge, div.card');
            textContainers.forEach(el => {
                if (el.children.length === 0 && el.innerText.trim().length > 0) {
                    if (el.scrollWidth > el.clientWidth + 2 && window.getComputedStyle(el).overflow === 'hidden') {
                        results.textCutOff.push({
                            tag: el.tagName,
                            class: el.className,
                            text: el.innerText,
                            scrollWidth: el.scrollWidth,
                            clientWidth: el.clientWidth
                        });
                    }
                }
            });

            // 2. Check overlap between major hero elements and nav
            const nav = document.querySelector('.std-nav');
            const hero = document.querySelector('.hero-section');
            if (nav && hero) {
                const navRect = nav.getBoundingClientRect();
                const heroRect = hero.getBoundingClientRect();
                results.navHeroRect = { navRect, heroRect };
            }

            // 3. Check for elements with negative margins or position absolute overlaying text
            const absEls = document.querySelectorAll('[style*="absolute"], [style*="fixed"]');
            absEls.forEach(el => {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                if (style.zIndex !== 'auto') {
                    results.zindexIssues.push({
                        tag: el.tagName,
                        class: el.className,
                        id: el.id,
                        zIndex: style.zIndex,
                        position: style.position,
                        rect: rect
                    });
                }
            });

            return results;
        }''')

        print("=== LAYOUT ANALYSIS ===")
        print("Text Cut Off:", len(analysis['textCutOff']), analysis['textCutOff'])
        print("Nav/Hero Rects:", analysis['navHeroRect'])
        print("Z-Index Elements:", len(analysis['zindexIssues']))
        for z in analysis['zindexIssues'][:10]:
            print(" ", z)

        await browser.close()

asyncio.run(audit_layout())
