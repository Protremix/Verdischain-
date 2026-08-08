import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        for width, name in [(1920, 'Desktop-1920'), (1280, 'Desktop-1280'), (768, 'Tablet-768'), (375, 'Mobile-375')]:
            page = await browser.new_page(viewport={'width': width, 'height': 900})
            await page.goto('https://verdischain.com/whitepaper/?nocache=50008')
            await page.wait_for_timeout(1000)
            
            # Check overlap of cards in hero section
            hero_cards = await page.evaluate('''() => {
                const els = document.querySelectorAll('.hero-visual .wp-card, .hero-visual .wp-doc, .hero-visual .wp-team, .hero-visual .wp-roadmap, .hero-visual .wp-carbon, .hero-visual .float-tag');
                return Array.from(els).map(el => {
                    const rect = el.getBoundingClientRect();
                    return {
                        class: el.className,
                        text: el.innerText.replace(/\\n/g, ' '),
                        rect: {top: rect.top, bottom: rect.bottom, left: rect.left, right: rect.right, width: rect.width, height: rect.height}
                    };
                });
            }''')
            
            print(f"\n--- {name} Hero Visual Elements ({len(hero_cards)}) ---")
            for i, c in enumerate(hero_cards):
                print(f"[{i}] {c['class']} -> {c['rect']} -> text: '{c['text'][:40]}'")
                
            # Check if any elements overlap significantly
            overlaps = []
            for i in range(len(hero_cards)):
                for j in range(i + 1, len(hero_cards)):
                    r1 = hero_cards[i]['rect']
                    r2 = hero_cards[j]['rect']
                    
                    # Intersects?
                    if not (r1['right'] < r2['left'] or r1['left'] > r2['right'] or r1['bottom'] < r2['top'] or r1['top'] > r2['bottom']):
                        # calculate overlap area
                        overlap_w = max(0, min(r1['right'], r2['right']) - max(r1['left'], r2['left']))
                        overlap_h = max(0, min(r1['bottom'], r2['bottom']) - max(r1['top'], r2['top']))
                        area = overlap_w * overlap_h
                        if area > 10:
                            overlaps.append((i, j, area, hero_cards[i]['class'], hero_cards[j]['class']))
            
            print(f"Hero card overlaps found ({len(overlaps)}):")
            for o in overlaps:
                print(f"  Overlap between [{o[0]}] {o[3]} AND [{o[1]}] {o[4]} (Area: {o[2]:.1f}px²)")

            await page.close()
            
        await browser.close()

asyncio.run(main())
