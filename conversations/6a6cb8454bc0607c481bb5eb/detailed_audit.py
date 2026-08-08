import asyncio
from playwright.async_api import async_playwright

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # ---------------- DESKTOP ----------------
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        await page.goto('https://verdischain.com/whitepaper/', wait_until='networkidle')

        print("=== 1. ALLOCATION TABLE / CARDS ANALYSIS ===")
        alloc_data = await page.evaluate("""
            () => {
                const items = document.querySelectorAll('.alloc-card, .distribution-card, .token-card, .distribution-item, [class*="alloc"], [class*="distribut"]');
                return Array.from(items).map(el => ({
                    text: el.innerText.replace(/\\n+/g, ' | '),
                    className: el.className
                }));
            }
        """)
        for d in alloc_data:
            print(d)

        print("\n=== 2. PIE CHART DETAILED ANALYSIS ===")
        pie_data = await page.evaluate("""
            () => {
                const svg = document.querySelector('.pie-svg');
                if (!svg) return 'No .pie-svg found';
                const segs = svg.querySelectorAll('.pie-seg');
                const segData = Array.from(segs).map(s => ({
                    stroke: s.getAttribute('stroke'),
                    dasharray: s.getAttribute('stroke-dasharray'),
                    dashoffset: s.getAttribute('stroke-dashoffset')
                }));
                const legend = Array.from(document.querySelectorAll('.pie-legend, .chart-legend, [class*="legend"]')).map(l => l.innerText);
                return { segData, legend, outerText: svg.parentElement.innerText };
            }
        """)
        print("Pie Chart Data:", pie_data)

        print("\n=== 3. ROADMAP DETAILED ANALYSIS ===")
        roadmap_data = await page.evaluate("""
            () => {
                const phases = document.querySelectorAll('.roadmap-card, .roadmap-phase, .timeline-phase, [class*="roadmap"]');
                return Array.from(phases).map(p => p.innerText.replace(/\\n+/g, ' | '));
            }
        """)
        for r in roadmap_data:
            print("ROADMAP ITEM:", r)

        print("\n=== 4. VESTING CARD DETAILED ANALYSIS ===")
        vesting_data = await page.evaluate("""
            () => {
                const cards = document.querySelectorAll('.vesting-card, [class*="vesting"]');
                return Array.from(cards).map(c => c.innerText.replace(/\\n+/g, ' | '));
            }
        """)
        for v in vesting_data:
            print("VESTING ITEM:", v)

        print("\n=== 5 & 6. STORY TIMELINE ANALYSIS ===")
        story_timeline = await page.evaluate("""
            () => {
                const items = document.querySelectorAll('.story-timeline .timeline-item, .history-item, .story-item, [class*="story"] .timeline-item, .timeline-node');
                if (items.length === 0) {
                    // find timeline nodes in general
                    const allTimeline = document.querySelectorAll('.timeline-item, .timeline-card, .timeline-step');
                    return Array.from(allTimeline).map(t => ({
                        text: t.innerText.replace(/\\n+/g, ' | '),
                        className: t.className,
                        classList: Array.from(t.classList),
                        innerHTML: t.innerHTML
                    }));
                }
                return Array.from(items).map(t => ({
                    text: t.innerText.replace(/\\n+/g, ' | '),
                    className: t.className,
                    classList: Array.from(t.classList),
                    innerHTML: t.innerHTML
                }));
            }
        """)
        print(f"Found {len(story_timeline)} timeline items:")
        for st in story_timeline:
            print("STORY TIMELINE ITEM:", st['text'])
            print("  Classes:", st['className'])
            print("  HTML snippet:", st['innerHTML'][:150])

        # Let's inspect specifically all timeline entries in the page
        all_timelines = await page.evaluate("""
            () => {
                const nodes = document.querySelectorAll('[class*="timeline"]');
                return Array.from(nodes).map(n => ({
                    class: n.className,
                    text: n.innerText.replace(/\\n+/g, ' | ')
                }));
            }
        """)
        print("\nALL TIMELINE ELEMENTS:")
        for t in all_timelines:
            print(t['class'], "-->", t['text'][:100])

        await browser.close()

asyncio.run(audit())
