import asyncio
from playwright.async_api import async_playwright
import json

async def run_analysis():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Test Viewports
        viewports = [
            ("desktop", 1280, 800),
            ("desktop_wide", 1920, 1080),
            ("tablet", 768, 1024),
            ("mobile", 375, 812)
        ]

        for name, w, h in viewports:
            context = await browser.new_context(viewport={'width': w, 'height': h})
            page = await context.new_page()
            await page.goto("https://verdischain.com/sale/?nocache=50005", wait_until="networkidle")

            # Check 4-column phase grid rendering
            phase_cards_rects = await page.evaluate("""() => {
                const grid = document.querySelector('.phases-grid');
                if (!grid) return null;
                const cards = Array.from(grid.querySelectorAll('.phase-card'));
                return cards.map((c, i) => {
                    const r = c.getBoundingClientRect();
                    return {
                        index: i,
                        title: c.querySelector('h3') ? c.querySelector('h3').innerText : '',
                        top: r.top,
                        bottom: r.bottom,
                        left: r.left,
                        right: r.right,
                        width: r.width,
                        height: r.height
                    };
                });
            }""")

            # Check floating cards bounding rects (desktop viewports)
            float_cards_rects = await page.evaluate("""() => {
                const cards = Array.from(document.querySelectorAll('.float-card'));
                return cards.map(c => {
                    const r = c.getBoundingClientRect();
                    return {
                        class: c.className,
                        text: c.innerText.replace(/\\n/g, ' '),
                        x: r.x, y: r.y, width: r.width, height: r.height, right: r.right, bottom: r.bottom
                    };
                });
            }""")

            # Screenshot specific sections
            if name == "desktop":
                # Hero screenshot
                hero = await page.query_selector('.hero')
                if hero:
                    await hero.screenshot(path="hero_desktop.png")
                
                # Phases section screenshot
                phases = await page.query_selector('.phases-section')
                if phases:
                    await phases.screenshot(path="phases_desktop.png")

                # Buy section screenshot
                buy = await page.query_selector('.buy-section')
                if buy:
                    await buy.screenshot(path="buy_desktop.png")

                # Vesting table screenshot
                vesting = await page.query_selector('.vesting-section')
                if vesting:
                    await vesting.screenshot(path="vesting_desktop.png")

            print(f"=== VIEWPORT {name} ({w}x{h}) ===")
            print("Phase Cards Rects:")
            print(json.dumps(phase_cards_rects, indent=2))
            if name.startswith("desktop"):
                print("Float Cards Rects:")
                print(json.dumps(float_cards_rects, indent=2))

        await browser.close()

asyncio.run(run_analysis())
