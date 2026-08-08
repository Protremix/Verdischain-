import asyncio
from playwright.async_api import async_playwright

async def run_visual_deep():
    import os
    os.environ['PLAYWRIGHT_NODE_JS_PATH'] = '/usr/bin/node'

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for w in [1440, 1024, 768, 375]:
            page = await browser.new_page(viewport={'width': w, 'height': 900})
            await page.goto('https://verdischain.com/?nocache=50001', wait_until='networkidle')
            await page.wait_for_timeout(1000)

            print(f"\n================ VIEWPORT {w}px ================")
            
            # Check hero visual visibility
            hero_vis_display = await page.evaluate('''() => {
                const el = document.querySelector('.hero-visual');
                if (!el) return 'NOT FOUND';
                const style = window.getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                return {
                    display: style.display,
                    visibility: style.visibility,
                    width: rect.width,
                    height: rect.height,
                    top: rect.top,
                    left: rect.left
                };
            }''')
            print("Hero Visual:", hero_vis_display)

            # Check if elements overlap each other in hero visual
            hero_cards = await page.evaluate('''() => {
                const cards = document.querySelectorAll('.hero-visual > *');
                return Array.from(cards).map(c => {
                    const rect = c.getBoundingClientRect();
                    return {
                        class: c.className,
                        id: c.id,
                        display: window.getComputedStyle(c).display,
                        rect: { x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height) }
                    };
                });
            }''')
            print(f"Hero Sub-elements ({len(hero_cards)}):")
            for c in hero_cards:
                print(" ", c)

            await page.screenshot(path=f'screenshot_{w}.png')
            await page.close()

        await browser.close()

asyncio.run(run_visual_deep())
