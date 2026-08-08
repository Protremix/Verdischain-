import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('https://verdischain.com/whitepaper/?nocache=50008')
        await page.wait_for_timeout(1000)
        
        # Check nav brand logo
        brand_logo = await page.evaluate('''() => {
            const img = document.querySelector('.brand-logo-img');
            return img ? {src: img.src, naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight} : null;
        }''')
        print("Nav Brand Logo:", brand_logo)
        
        # Check hero title rendering & CSS
        hero_title = await page.evaluate('''() => {
            const h1 = document.querySelector('.hero-title');
            const style = window.getComputedStyle(h1);
            return {
                text: h1.innerText,
                fontSize: style.fontSize,
                lineHeight: style.lineHeight,
                color: style.color
            };
        }''')
        print("Hero Title Style:", hero_title)
        
        # Check team section social icons / links
        team_links = await page.evaluate('''() => {
            const teamSec = document.querySelector('#team');
            if (!teamSec) return [];
            const links = teamSec.querySelectorAll('a');
            return Array.from(links).map(a => ({
                text: a.innerText,
                href: a.getAttribute('href'),
                class: a.className,
                outer: a.outerHTML
            }));
        }''')
        print("\nTeam Section Links:", team_links)
        
        # Check calculators or dynamic elements on page
        calc_status = await page.evaluate('''() => {
            const calcInput = document.querySelector('#calc-input') || document.querySelector('input');
            const calcResult = document.querySelector('#calc-daily') || document.querySelector('.calc-result') || document.querySelector('#calc-yearly');
            return {
                hasInput: !!calcInput,
                inputVal: calcInput ? calcInput.value : null,
                hasResult: !!calcResult
            };
        }''')
        print("\nCalculator check:", calc_status)

        # Check all images on page
        images = await page.evaluate('''() => {
            const imgs = Array.from(document.querySelectorAll('img'));
            return imgs.map(img => ({
                src: img.src,
                alt: img.alt,
                naturalWidth: img.naturalWidth,
                naturalHeight: img.naturalHeight,
                complete: img.complete
            }));
        }''')
        print(f"\nImages on page ({len(images)}):")
        for img in images:
            print(" ", img)

        await browser.close()

asyncio.run(main())
