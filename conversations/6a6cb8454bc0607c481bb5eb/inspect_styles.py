from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 375, 'height': 812})
    page.goto('https://verdischain.com/eco/', wait_until='networkidle')

    nav_open_styles = page.evaluate('''() => {
        const h = document.getElementById('navHamburger');
        h.click();
        const nav = document.querySelector('.nav-links');
        const style = window.getComputedStyle(nav);
        return {
            display: style.display,
            position: style.position,
            top: style.top,
            left: style.left,
            width: style.width,
            height: style.height,
            background: style.backgroundColor,
            zIndex: style.zIndex
        };
    }''')

    print("Mobile Nav Open computed styles:", nav_open_styles)

    # Inspect hero stats on mobile
    hero_stats_styles = page.evaluate('''() => {
        const stats = document.querySelectorAll('.stat-card');
        return Array.from(stats).map(s => {
            const rect = s.getBoundingClientRect();
            return {
                text: s.innerText.replace('\\n', ' '),
                width: rect.width,
                height: rect.height,
                left: rect.left,
                right: rect.right
            };
        });
    }''')
    print("Mobile Stat Cards bounding rects:", hero_stats_stats = hero_stats_styles)

    browser.close()
