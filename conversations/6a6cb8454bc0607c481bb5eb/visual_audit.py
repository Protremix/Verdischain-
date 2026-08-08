import asyncio
from playwright.async_api import async_playwright
import json

async def audit_visuals():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # 1. DESKTOP VIEW AUDIT (1440x900)
        page_desk = await browser.new_page(viewport={'width': 1440, 'height': 900})
        await page_desk.goto('https://verdischain.com/tokenomics/?nocache=50006', wait_until='networkidle')
        
        # Check IDO grid elements desktop
        ido_grid_desk = await page_desk.eval_on_selector('#ido-grid', '''el => {
            const rect = el.getBoundingClientRect();
            const children = Array.from(el.children).map(c => {
                const r = c.getBoundingClientRect();
                return { width: r.width, height: r.height, left: r.left, right: r.right, top: r.top, bottom: r.bottom };
            });
            return { gridWidth: rect.width, children };
        }''')
        print("DESKTOP IDO GRID:", json.dumps(ido_grid_desk, indent=2))
        
        # Check Hero floating cards bounding boxes and potential overlap
        hero_float = await page_desk.eval_on_selector_all('.float-card', '''cards => {
            return cards.map(c => {
                const r = c.getBoundingClientRect();
                return { class: c.className, left: r.left, top: r.top, width: r.width, height: r.height, right: r.right, bottom: r.bottom };
            });
        }''')
        print("DESKTOP HERO FLOATING CARDS:", json.dumps(hero_float, indent=2))
        
        # Check Donut Chart canvas bounding box and visibility
        chart_info = await page_desk.eval_on_selector('#tokenomicsChart', '''c => {
            const r = c.getBoundingClientRect();
            return { width: r.width, height: r.height, left: r.left, top: r.top };
        }''')
        print("DESKTOP CHART:", json.dumps(chart_info, indent=2))

        # Check for any overflowing elements (horizontal scrollbar)
        overflow_desk = await page_desk.evaluate('''() => {
            return {
                scrollWidth: document.documentElement.scrollWidth,
                clientWidth: document.documentElement.clientWidth,
                hasHorizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth
            };
        }''')
        print("DESKTOP OVERFLOW:", overflow_desk)

        # 2. MOBILE VIEW AUDIT (375x812)
        page_mob = await browser.new_page(viewport={'width': 375, 'height': 812}, is_mobile=True)
        await page_mob.goto('https://verdischain.com/tokenomics/?nocache=50006', wait_until='networkidle')
        
        ido_grid_mob = await page_mob.eval_on_selector('#ido-grid', '''el => {
            const rect = el.getBoundingClientRect();
            const children = Array.from(el.children).map((c, i) => {
                const r = c.getBoundingClientRect();
                return { index: i, width: r.width, height: r.height, left: r.left, right: r.right, top: r.top, bottom: r.bottom, scrollWidth: c.scrollWidth };
            });
            return { gridWidth: rect.width, children };
        }''')
        print("MOBILE IDO GRID:", json.dumps(ido_grid_mob, indent=2))
        
        overflow_mob = await page_mob.evaluate('''() => {
            return {
                scrollWidth: document.documentElement.scrollWidth,
                clientWidth: document.documentElement.clientWidth,
                hasHorizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth
            };
        }''')
        print("MOBILE OVERFLOW:", overflow_mob)
        
        # Find which elements cause overflow on mobile if any
        wide_els_mob = await page_mob.evaluate('''() => {
            const wide = [];
            document.querySelectorAll('*').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.right > window.innerWidth + 1) {
                    wide.append || wide.push({ tag: el.tagName, id: el.id, class: el.className, right: r.right, width: r.width });
                }
            });
            return wide;
        }''')
        print("MOBILE ELEMENTS OVERFLOWING VIEWPORT:", json.dumps(wide_els_mob[:10], indent=2))

        await browser.close()

asyncio.run(audit_visuals())
