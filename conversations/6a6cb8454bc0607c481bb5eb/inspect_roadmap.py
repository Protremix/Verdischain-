import asyncio
from playwright.async_api import async_playwright

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://verdischain.com/whitepaper/', wait_until='networkidle')

        phases = await page.evaluate("""
            () => {
                const roadmapSec = document.querySelector('#roadmap') || document.querySelector('.roadmap-timeline')?.closest('section') || document.querySelector('.roadmap-timeline')?.parentElement;
                const items = document.querySelectorAll('.rm-phase, .roadmap-card, .roadmap-step, .roadmap-phase, [class*="rm-"]');
                const phaseCards = document.querySelectorAll('.roadmap-timeline .timeline-item, .roadmap-timeline > div, .rm-card');
                
                // Let's get raw text of roadmap section
                return {
                    sectionHTML: roadmapSec ? roadmapSec.innerHTML : 'No section found',
                    sectionText: roadmapSec ? roadmapSec.innerText : ''
                };
            }
        """)
        print("=== ROADMAP TEXT ===")
        print(phases['sectionText'])

        await browser.close()

asyncio.run(audit())
