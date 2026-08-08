import asyncio
from playwright.async_api import async_playwright

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://verdischain.com/whitepaper/', wait_until='networkidle')

        story_html = await page.eval_on_selector('.story-timeline', 'el => el.outerHTML')
        print("=== STORY TIMELINE HTML ===")
        print(story_html)

        # Inspect classes and styles of items in story-timeline
        items = await page.evaluate("""
            () => {
                const el = document.querySelector('.story-timeline');
                if (!el) return [];
                const children = el.children;
                return Array.from(children).map(c => ({
                    tag: c.tagName,
                    class: c.className,
                    text: c.innerText,
                    html: c.innerHTML
                }));
            }
        """)
        print("\n=== STORY TIMELINE CHILDREN ===")
        for i, item in enumerate(items):
            print(f"Child {i}: Tag={item['tag']}, Class={item['class']}")
            print(f"  Text: {item['text']}")
            print(f"  HTML: {item['html'][:200]}")

        await browser.close()

asyncio.run(audit())
