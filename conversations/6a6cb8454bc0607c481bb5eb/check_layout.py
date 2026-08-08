from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    for view in [(1920, 1080, "Desktop 1920"), (1280, 800, "Desktop 1280"), (375, 812, "Mobile 375")]:
        w, h, label = view
        page = browser.new_page(viewport={"width": w, "height": h})
        page.goto("https://verdischain.com/faucet/?nocache=50007", wait_until="networkidle")
        
        cards = page.evaluate("""() => {
            const list = Array.from(document.querySelectorAll(".float-card, .faucet-card, .stat-card, input, button, table")).map(el => {
                const r = el.getBoundingClientRect();
                return {
                    tag: el.tagName,
                    id: el.id,
                    cls: el.className,
                    x: r.x, y: r.y, w: r.width, h: r.height, right: r.x + r.width, bottom: r.y + r.height
                };
            });
            return list;
        }""")
        
        print("===", label, "===")
        for c in cards:
            name = c["cls"] or c["id"] or c["tag"]
            print(f"{name}: x={c['x']:.1f}, y={c['y']:.1f}, w={c['w']:.1f}, h={c['h']:.1f}, bottom={c['bottom']:.1f}")
            
        page.close()
    browser.close()
