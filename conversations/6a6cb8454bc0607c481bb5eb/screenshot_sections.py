import asyncio
from playwright.async_api import async_playwright

async def snap():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # Desktop
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        await page.goto('https://verdischain.com/tokenomics/?nocache=50006', wait_until='networkidle')
        
        # Hero section screenshot
        hero = await page.query_selector('.hero')
        if hero:
            await hero.screenshot(path='snap_hero_desk.png')
            
        # Chart section screenshot
        dist = await page.query_selector('.dist-grid')
        if dist:
            await dist.screenshot(path='snap_chart_desk.png')

        # IDO grid screenshot
        ido = await page.query_selector('#ido-grid')
        if ido:
            await ido.screenshot(path='snap_ido_desk.png')

        # Vesting table screenshot
        vest = await page.query_selector('.vesting-table')
        if vest:
            await vest.screenshot(path='snap_vesting_desk.png')

        # Mobile
        page_mob = await browser.new_page(viewport={'width': 375, 'height': 812}, is_mobile=True)
        await page_mob.goto('https://verdischain.com/tokenomics/?nocache=50006', wait_until='networkidle')

        hero_m = await page_mob.query_selector('.hero')
        if hero_m:
            await hero_m.screenshot(path='snap_hero_mob.png')

        ido_m = await page_mob.query_selector('#ido-grid')
        if ido_m:
            await ido_m.screenshot(path='snap_ido_mob.png')

        vest_m = await page_mob.query_selector('.vesting-table')
        if vest_m:
            await vest_m.screenshot(path='snap_vesting_mob.png')

        await browser.close()

asyncio.run(snap())
