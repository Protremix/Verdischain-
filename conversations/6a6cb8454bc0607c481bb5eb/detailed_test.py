import asyncio
import json
from playwright.async_api import async_playwright

async def detailed_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 1. Desktop Detailed Test
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        
        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
        
        page_errors = []
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        # Catch alerts
        dialog_text = []
        page.on("dialog", lambda dialog: (dialog_text.append(dialog.message), asyncio.create_task(dialog.accept())))

        await page.goto("https://verdischain.com/explorer/", wait_until="networkidle")
        await asyncio.sleep(2)

        # Test tabs on desktop
        tabs = ["overview", "blocks", "extrinsics", "validators", "dex", "eco"]
        tab_screenshots = {}
        for tab in tabs:
            tab_selector = f".tab[data-t='{tab}']"
            if await page.query_selector(tab_selector):
                await page.click(tab_selector)
                await asyncio.sleep(1)
                await page.screenshot(path=f"desktop_tab_{tab}.png", full_page=True)
                tab_screenshots[tab] = f"desktop_tab_{tab}.png"

        # Test block modal by searching block 1
        await page.fill("#searchInput", "1")
        await page.keyboard.press("Enter")
        await asyncio.sleep(2)
        await page.screenshot(path="desktop_modal_block1.png")

        # Check modal visibility and content
        modal_visible = await page.is_visible("#modal.show")
        modal_content = await page.inner_text("#modalBody") if modal_visible else None

        # Close modal
        if modal_visible:
            await page.click(".modal-close")
            await asyncio.sleep(0.5)

        # Test search with non-existent hash / address
        await page.fill("#searchInput", "5D4y11111111111111111111111111111111111111111111")
        await page.keyboard.press("Enter")
        await asyncio.sleep(1)

        # 2. Mobile Detailed Test (375px)
        mobile_page = await browser.new_page(viewport={"width": 375, "height": 812}, is_mobile=True)
        mobile_page.on("console", lambda msg: console_msgs.append(f"[Mobile-{msg.type}] {msg.text}"))
        
        await mobile_page.goto("https://verdischain.com/explorer/", wait_until="networkidle")
        await asyncio.sleep(2)
        await mobile_page.screenshot(path="mobile_overview.png", full_page=True)

        for tab in ["overview", "blocks", "validators", "dex", "eco"]:
            tab_selector = f".tab[data-t='{tab}']"
            if await mobile_page.query_selector(tab_selector):
                await mobile_page.click(tab_selector)
                await asyncio.sleep(1)
                await mobile_page.screenshot(path=f"mobile_tab_{tab}.png", full_page=True)

        # Check mobile elements layout & bounding boxes / horizontal scroll
        mobile_layout_issues = await mobile_page.evaluate("""() => {
            const issues = [];
            const vw = window.innerWidth;
            document.querySelectorAll('*').forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.right > vw + 2) {
                    issues.push({
                        tag: el.tagName,
                        class: el.className,
                        id: el.id,
                        width: rect.width,
                        right: rect.right,
                        text: el.innerText ? el.innerText.slice(0, 30).replace(/\\n/g, ' ') : ''
                    });
                }
            });
            return issues;
        }""")

        await browser.close()

        with open("detailed_results.json", "w") as f:
            json.dump({
                "console_msgs": console_msgs,
                "page_errors": page_errors,
                "modal_visible": modal_visible,
                "modal_content": modal_content,
                "dialog_text": dialog_text,
                "mobile_layout_issues": mobile_layout_issues
            }, f, indent=2)

        print("Detailed test completed successfully.")

asyncio.run(detailed_test())
