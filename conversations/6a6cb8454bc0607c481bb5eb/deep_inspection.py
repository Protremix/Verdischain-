from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # --- DESKTOP (1440x900) ---
    page_d = browser.new_page(viewport={'width': 1440, 'height': 900})
    page_d.goto('https://verdischain.com/eco/', wait_until='networkidle')
    page_d.wait_for_timeout(3000)

    # Check block height display
    stat_block_d = page_d.locator('#stat-block').text_content()
    hero_block_d = page_d.locator('#hero-block-num').text_content()
    stat_validators_d = page_d.locator('#stat-validators').text_content()
    stat_peers_d = page_d.locator('#stat-peers').text_content()

    print(f"Desktop Block Height in Stat Card: '{stat_block_d}'")
    print(f"Desktop Block Height in Hero Badge: '{hero_block_d}'")
    print(f"Desktop Validators: '{stat_validators_d}'")
    print(f"Desktop Peers: '{stat_peers_d}'")

    # --- MOBILE (375x812) ---
    page_m = browser.new_page(viewport={'width': 375, 'height': 812}, user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)")
    page_m.goto('https://verdischain.com/eco/', wait_until='networkidle')
    page_m.wait_for_timeout(3000)

    # Check hamburger menu interaction
    hamburger = page_m.locator('#navHamburger')
    nav_links = page_m.locator('.nav-links')
    
    print("Hamburger visible on mobile:", hamburger.is_visible())
    if hamburger.is_visible():
        print("Nav links visible before click:", nav_links.is_visible())
        hamburger.click()
        page_m.wait_for_timeout(500)
        print("Nav links visible after click:", nav_links.is_visible())

    # Check mobile table behavior and horizontal scrolling
    table = page_m.locator('#reforestationTable')
    table_box = table.bounding_box() if table.count() > 0 else None
    print("Reforestation Table Bounding Box on Mobile:", table_box)

    # Check modal on mobile
    buy_btn = page_m.locator('.card-marketplace button').first
    if buy_btn.count() > 0:
        buy_btn.click()
        page_m.wait_for_timeout(500)
        modal = page_m.locator('#tradeModal')
        modal_box = page_m.locator('#tradeModal .modal-content').bounding_box()
        print("Modal visible on mobile:", modal.is_visible())
        print("Modal box on mobile:", modal_box)
        # screenshot modal on mobile
        page_m.screenshot(path='mobile_modal.png')

    browser.close()
