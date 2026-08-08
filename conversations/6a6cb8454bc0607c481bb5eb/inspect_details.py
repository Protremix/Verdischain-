import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        await page.goto('https://verdischain.com/whitepaper/', wait_until='networkidle')

        # 1. Allocation table / cards
        print("=== 1. ALLOCATION TABLE / CARDS ===")
        alloc_cards = await page.eval_on_selector_all('.token-card, [class*="alloc"], [class*="tokenom"], tr, .distribution-item', """
            elements => elements.map(el => ({
                text: el.innerText,
                className: el.className
            }))
        """)
        for c in alloc_cards:
            if any(k in c['text'] for k in ['Community', 'Eco', 'Team', 'DEX', 'Treasury', 'Investors', '25%', '18%', '15%', '12%']):
                print("---")
                print(c['text'])

        # Let's get full text of Tokenomics section
        print("\n=== TOKENOMICS SECTION FULL TEXT ===")
        tok_section = await page.eval_on_selector('#tokenomics, [id*="token"]', "el => el ? el.innerText : 'NOT FOUND'")
        print(tok_section if tok_section != 'NOT FOUND' else "No #tokenomics element")

        # Check all text containing percentages or token allocations
        print("\n=== ALL PERCENTAGES ON PAGE ===")
        percentages = await page.evaluate("""
            () => {
                const nodes = [];
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                let node;
                while (node = walker.nextNode()) {
                    if (node.nodeValue.includes('%')) {
                        nodes.push(node.parentElement.innerText);
                    }
                }
                return [...new Set(nodes)];
            }
        """)
        for p_text in percentages:
            print("PCT:", p_text.replace('\n', ' | '))

        # 2. Pie chart
        print("\n=== 2. PIE CHART / CANVAS / SVG ===")
        charts = await page.eval_on_selector_all('canvas, svg, chart, .pie-chart, #chart, [id*="chart"]', """
            elements => elements.map(el => ({
                tag: el.tagName,
                id: el.id,
                className: el.className,
                outerHTML: el.outerHTML.substring(0, 300)
            }))
        """)
        print("Chart elements found:", len(charts))
        for ch in charts:
            print(ch)

        # Let's check chart data or canvas script
        chart_scripts = await page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script'));
                return scripts.map(s => s.innerText).filter(t => t.includes('Chart') || t.includes('pie') || t.includes('25') || t.includes('Community'));
            }
        """)
        print("Chart scripts found:", len(chart_scripts))
        for s in chart_scripts:
            print("SCRIPT SNIPPET:", s[:500])

        # 3. Roadmap section
        print("\n=== 3. ROADMAP SECTION ===")
        roadmap = await page.evaluate("""
            () => {
                const el = document.querySelector('#roadmap, [id*="roadmap"]') || document.body;
                return el.innerText;
            }
        """)
        # Search roadmap text for Phase 3, Q3 2026, 6-month cliff
        print("Roadmap text snippet:")
        for line in roadmap.split('\n'):
            if any(k in line.lower() for k in ['phase', 'q1', 'q2', 'q3', 'q4', 'cliff', '2026', 'roadmap']):
                print("RM:", line)

        # 4. Vesting card
        print("\n=== 4. VESTING CARD ===")
        vesting = await page.evaluate("""
            () => {
                const el = document.querySelector('#vesting, [id*="vesting"]') || document.body;
                return el.innerText;
            }
        """)
        for line in vesting.split('\n'):
            if any(k in line.lower() for k in ['vesting', 'ido', 'phase', 'cliff', 'month', 'investor']):
                print("VEST:", line)

        # 5 & 6. Story timeline / Q1/Q2/Q3 2026
        print("\n=== 5 & 6. STORY TIMELINE / TIMELINE SECTIONS ===")
        timeline = await page.evaluate("""
            () => {
                const els = Array.from(document.querySelectorAll('.timeline, [class*="timeline"], [class*="story"], #timeline, #story, .history'));
                return els.map(e => e.innerText);
            }
        """)
        print("Timeline elements found:", len(timeline))
        for t in timeline:
            print("TIMELINE ITEM:\n", t)

        await browser.close()

asyncio.run(inspect())
