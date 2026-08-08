import asyncio
from playwright.async_api import async_playwright
import json

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # 1. Desktop Check
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        await page.goto('https://verdischain.com/tokenomics/?nocache=50006', wait_until='networkidle')
        
        # Check Hero 3D float cards detailed positions and z-indexes
        cards_desk = await page.evaluate('''() => {
            const cards = Array.from(document.querySelectorAll('.hero-right .float-card'));
            return cards.map(c => {
                const r = c.getBoundingClientRect();
                const style = window.getComputedStyle(c);
                return {
                    class: c.className,
                    text: c.innerText.replace(/\\n/g, ' '),
                    top: r.top, left: r.left, width: r.width, height: r.height, right: r.right, bottom: r.bottom,
                    zIndex: style.zIndex
                };
            });
        }''')
        print("DESKTOP HERO CARDS:", json.dumps(cards_desk, indent=2))
        
        # Check Donut Chart rendering
        chart_details = await page.evaluate('''() => {
            const chartCanvas = document.getElementById('tokenomicsChart');
            if (!chartCanvas) return "Canvas missing";
            const r = chartCanvas.getBoundingClientRect();
            const parentR = chartCanvas.parentElement.getBoundingClientRect();
            return {
                canvasWidth: chartCanvas.width,
                canvasHeight: chartCanvas.height,
                styleWidth: chartCanvas.style.width,
                styleHeight: chartCanvas.style.height,
                rectWidth: r.width,
                rectHeight: r.height,
                parentWidth: parentR.width,
                parentHeight: parentR.height
            };
        }''')
        print("CHART DETAILS:", json.dumps(chart_details, indent=2))

        # Check Mobile View (375px) Hero section behavior
        page_mob = await browser.new_page(viewport={'width': 375, 'height': 812}, is_mobile=True)
        await page_mob.goto('https://verdischain.com/tokenomics/?nocache=50006', wait_until='networkidle')
        
        hero_mob = await page_mob.evaluate('''() => {
            const hr = document.querySelector('.hero-right');
            if (!hr) return "no hero right";
            const r = hr.getBoundingClientRect();
            const cards = Array.from(hr.querySelectorAll('.float-card')).map(c => {
                const cr = c.getBoundingClientRect();
                return {
                    class: c.className,
                    left: cr.left, top: cr.top, width: cr.width, height: cr.height, right: cr.right, bottom: cr.bottom
                };
            });
            return { heroRightRect: { left: r.left, top: r.top, width: r.width, height: r.height }, cards };
        }''')
        print("MOBILE HERO RIGHT:", json.dumps(hero_mob, indent=2))

        # Check table responsiveness on mobile (Vesting table, Category table)
        tables_mob = await page_mob.evaluate('''() => {
            const tables = Array.from(document.querySelectorAll('table')).map(t => {
                const r = t.getBoundingClientRect();
                return {
                    class: t.className,
                    width: r.width,
                    scrollWidth: t.scrollWidth,
                    right: r.right,
                    parentWidth: t.parentElement.clientWidth,
                    parentScrollWidth: t.parentElement.scrollWidth
                };
            });
            return tables;
        }''')
        print("MOBILE TABLES:", json.dumps(tables_mob, indent=2))

        await browser.close()

asyncio.run(check())
