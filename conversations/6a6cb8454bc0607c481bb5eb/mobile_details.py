from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    # 375px viewport
    page = browser.new_page(viewport={'width': 375, 'height': 812})
    page.goto('https://verdischain.com/eco/', wait_until='networkidle')
    page.wait_for_timeout(2000)

    # 1. Test Hamburger menu
    nav_links = page.locator('.nav-links')
    hamburger = page.locator('#navHamburger')
    
    print("Nav links class initially:", nav_links.get_attribute('class'))
    hamburger.click()
    page.wait_for_timeout(500)
    print("Nav links class after click:", nav_links.get_attribute('class'))
    page.screenshot(path='mobile_nav_open.png')

    # 2. Check table wrapper
    table_parent = page.locator('#reforestationTable').element_handle().evaluate_handle('el => el.parentElement')
    parent_overflow = table_parent.evaluate('el => getComputedStyle(el).overflowX')
    print("Reforestation table parent overflowX:", parent_overflow)

    # 3. Check Chart responsiveness
    chart_container = page.locator('.chart-container, .impact-grid, .analytics-card')
    for i in range(chart_container.count()):
        box = chart_container.nth(i).bounding_box()
        print(f"Chart/Analytics box {i}:", box)

    # 4. Check simulator sliders touch usability
    ren_slider = page.locator('#input-ren')
    if ren_slider.count() > 0:
        box = ren_slider.bounding_box()
        print("Simulator slider bounding box:", box)

    browser.close()
