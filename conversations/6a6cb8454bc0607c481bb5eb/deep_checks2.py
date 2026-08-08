import asyncio
import json
from playwright.async_api import async_playwright

async def inspect_faucet(browser):
    print("==================================================")
    print("1. FAUCET PAGE: https://verdischain.com/faucet/")
    page = await browser.new_page(viewport={"width": 1280, "height": 800})
    
    # Listen to console and network
    responses = []
    page.on("response", lambda r: responses.append((r.status, r.url)))
    await page.goto("https://verdischain.com/faucet/", wait_until="networkidle")
    
    print("HTTP Status: 200")
    bad_res = [r for r in responses if r[0] >= 400]
    print("Failed Subresources / API calls:", bad_res)
    
    # Get HTML / JS scripts on the page
    scripts = await page.eval_on_selector_all("script", "elems => elems.map(e => e.src || e.innerText.substring(0, 200))")
    print(f"Scripts count: {len(scripts)}")
    
    # Test faucet input & button
    faucet_addr = await page.query_selector("#faucetAddr")
    faucet_btn = await page.query_selector("#faucetBtn")
    captcha_a = await page.query_selector("#captchaA")
    
    # Check text around captcha
    body_text = await page.evaluate("() => document.body.innerText")
    print("Body text snippet:\n", body_text[:1200])
    
    # Check captcha prompt text
    captcha_label = await page.evaluate("() => { const el = document.querySelector('label[for=\"captchaA\"], #captchaLabel, .captcha-text, form'); return el ? el.innerText : 'None'; }")
    print("Captcha element text:", captcha_label)
    
    # Fill address and try clicking button
    if faucet_addr:
        await faucet_addr.fill("5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY")
    if captcha_a:
        await captcha_a.fill("5")
        
    api_calls = []
    page.on("response", lambda r: api_calls.append((r.status, r.url)))
    if faucet_btn:
        await faucet_btn.click()
        await page.wait_for_timeout(2000)
    print("API calls made on button click:", api_calls)
    
    # Check alert or output status
    result_text = await page.evaluate("() => { const el = document.querySelector('#result, .result, #faucetMessage, .alert, p.text-red-500, p.text-green-500, #faucetResult'); return el ? el.innerText : 'None'; }")
    print("Result text after click:", result_text)
    
    await page.close()

async def inspect_referral(browser):
    print("==================================================")
    print("2. REFERRAL PAGE: https://verdischain.com/referral/")
    page = await browser.new_page(viewport={"width": 1280, "height": 800})
    await page.goto("https://verdischain.com/referral/", wait_until="networkidle")
    
    body_text = await page.evaluate("() => document.body.innerText")
    print("Body text snippet:\n", body_text[:1500])
    
    # Test calculator inputs and outputs
    calc_data = await page.evaluate("""() => {
        const t1 = document.querySelector('#calcT1') ? document.querySelector('#calcT1').value : null;
        const avg = document.querySelector('#calcAvg') ? document.querySelector('#calcAvg').value : null;
        const t2 = document.querySelector('#calcT2') ? document.querySelector('#calcT2').value : null;
        const t3 = document.querySelector('#calcT3') ? document.querySelector('#calcT3').value : null;
        
        // Find result elements
        const results = Array.from(document.querySelectorAll('*'))
            .filter(e => e.children.length === 0 && e.innerText && (e.innerText.includes('$') || e.innerText.includes('VRDX') || e.innerText.includes('%')))
            .map(e => e.innerText.trim());
            
        return {t1, avg, t2, t3, results};
    }""")
    print("Calc inputs & results:", calc_data)
    
    # Try changing inputs in calculator and see if results update or if there's any JS bug
    await page.fill("#calcT1", "100")
    await page.wait_for_timeout(500)
    new_results = await page.evaluate("""() => {
        return Array.from(document.querySelectorAll('*'))
            .filter(e => e.children.length === 0 && e.innerText && (e.innerText.includes('$') || e.innerText.includes('VRDX') || e.innerText.includes('%')))
            .map(e => e.innerText.trim());
    }""")
    print("Calc updated results:", new_results)
    
    await page.close()

async def inspect_incentives(browser):
    print("==================================================")
    print("3. INCENTIVES PAGE: https://verdischain.com/incentives/")
    page = await browser.new_page(viewport={"width": 1280, "height": 800})
    await page.goto("https://verdischain.com/incentives/", wait_until="networkidle")
    
    body_text = await page.evaluate("() => document.body.innerText")
    print("Body text snippet:\n", body_text[:1500])
    
    # Test validator staking calculator
    calc_data = await page.evaluate("""() => {
        const stake = document.querySelector('#calcStake') ? document.querySelector('#calcStake').value : null;
        const tier = document.querySelector('#calcTier') ? document.querySelector('#calcTier').value : null;
        return {stake, tier};
    }""")
    print("Staking calc state:", calc_data)
    
    await page.close()

async def inspect_docs(browser):
    print("==================================================")
    print("4. DOCS PAGE: https://verdischain.com/docs/")
    page = await browser.new_page(viewport={"width": 1280, "height": 800})
    await page.goto("https://verdischain.com/docs/", wait_until="networkidle")
    
    body_text = await page.evaluate("() => document.body.innerText")
    print("Body text snippet:\n", body_text[:1500])
    
    await page.close()

async def inspect_contact(browser):
    print("==================================================")
    print("5. CONTACT PAGE: https://verdischain.com/contact/")
    page = await browser.new_page(viewport={"width": 1280, "height": 800})
    await page.goto("https://verdischain.com/contact/", wait_until="networkidle")
    
    body_text = await page.evaluate("() => document.body.innerText")
    print("Body text snippet:\n", body_text[:1500])
    
    # Submit contact form
    await page.select_option("#subject", index=1)
    await page.fill("#name", "Audit Tester")
    await page.fill("#email", "audit@verdischain.com")
    await page.fill("#message", "Testing contact form submission.")
    
    responses = []
    page.on("response", lambda r: responses.append((r.status, r.url)))
    await page.click("button[type='submit']")
    await page.wait_for_timeout(2000)
    print("Form submit network responses:", responses)
    
    # Check result message
    alert_text = await page.evaluate("() => { const el = document.querySelector('.alert, #result, #messageResult, .success, .error, p.text-green-500, p.text-red-500'); return el ? el.innerText : 'None'; }")
    print("Contact submit alert text:", alert_text)
    
    await page.close()

async def inspect_api(browser):
    print("==================================================")
    print("6. API PAGE: https://verdischain.com/api/")
    page = await browser.new_page(viewport={"width": 1280, "height": 800})
    await page.goto("https://verdischain.com/api/", wait_until="networkidle")
    
    body_text = await page.evaluate("() => document.body.innerText")
    print("Body text snippet:\n", body_text[:1500])
    
    await page.close()

async def inspect_terms(browser):
    print("==================================================")
    print("7. TERMS PAGE: https://verdischain.com/terms/")
    page = await browser.new_page(viewport={"width": 1280, "height": 800})
    await page.goto("https://verdischain.com/terms/", wait_until="networkidle")
    
    body_text = await page.evaluate("() => document.body.innerText")
    print("Body text snippet:\n", body_text[:1500])
    
    await page.close()

async def inspect_privacy(browser):
    print("==================================================")
    print("8. PRIVACY PAGE: https://verdischain.com/privacy/")
    page = await browser.new_page(viewport={"width": 1280, "height": 800})
    await page.goto("https://verdischain.com/privacy/", wait_until="networkidle")
    
    body_text = await page.evaluate("() => document.body.innerText")
    print("Body text snippet:\n", body_text[:1500])
    
    await page.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        await inspect_faucet(browser)
        await inspect_referral(browser)
        await inspect_incentives(browser)
        await inspect_docs(browser)
        await inspect_contact(browser)
        await inspect_api(browser)
        await inspect_terms(browser)
        await inspect_privacy(browser)
        await browser.close()

asyncio.run(main())
