import asyncio
import json
from playwright.async_api import async_playwright

async def deep_check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # ----------------------------------------------------
        # 1. FAUCET DEEP CHECK
        # ----------------------------------------------------
        print("=== 1. FAUCET PAGE ===")
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        responses = []
        page.on("response", lambda r: responses.append((r.status, r.url)))
        await page.goto("https://verdischain.com/faucet/", wait_until="networkidle")
        
        print("Faucet subresource responses:", [r for r in responses if r[0] >= 400])
        
        # Test Faucet Form submission
        try:
            await page.fill("#faucetAddr", "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY")
            # captcha question text
            captcha_label = await page.evaluate("() => document.querySelector('label[for=\"captchaA\"]') ? document.querySelector('label[for=\"captchaA\"]').innerText : ''")
            print("Captcha label:", captcha_label)
            # Fill captcha answer
            await page.fill("#captchaA", "4") # assume or calculate
            
            # Click button
            click_resp = []
            page.on("response", lambda r: click_resp.append((r.status, r.url)))
            await page.click("#faucetBtn")
            await page.wait_for_timeout(2000)
            
            # Check alert or message
            msg = await page.evaluate("() => document.querySelector('.alert, .message, #faucetResult, #result, p.text-red-500, p.text-green-500') ? document.querySelector('.alert, .message, #faucetResult, #result, p.text-red-500, p.text-green-500').innerText : ''")
            print("Faucet submit result message:", msg)
            print("Click network responses:", click_resp)
        except Exception as e:
            print("Faucet interaction error:", e)
        await page.close()

        # ----------------------------------------------------
        # 2. REFERRAL DEEP CHECK
        # ----------------------------------------------------
        print("\n=== 2. REFERRAL PAGE ===")
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto("https://verdischain.com/referral/", wait_until="networkidle")
        
        # Check referral calculator math
        # Inputs: calcT1 (50), calcAvg (500), calcT2 (100), calcT3 (200)
        # Rates mentioned on page: Tier 1: 10%, Tier 2: 5%, Tier 3: 2.5%
        # Let's see displayed results on page
        calc_results = await page.evaluate("""() => {
            const elems = document.querySelectorAll('*');
            let text = document.body.innerText;
            return {
                t1: document.querySelector('#calcT1') ? document.querySelector('#calcT1').value : null,
                avg: document.querySelector('#calcAvg') ? document.querySelector('#calcAvg').value : null,
                t2: document.querySelector('#calcT2') ? document.querySelector('#calcT2').value : null,
                t3: document.querySelector('#calcT3') ? document.querySelector('#calcT3').value : null,
                outputs: Array.from(document.querySelectorAll('.calculator-result, .result, span, div'))
                    .map(e => e.innerText)
                    .filter(t => t && (t.includes('$') or t.includes('VRDX') or t.includes('%')))
            }
        }""")
        print("Referral Calc initial state:", calc_results['t1'], calc_results['avg'], calc_results['t2'], calc_results['t3'])
        
        # Get full text around calculator
        calc_section = await page.evaluate("() => document.querySelector('#calculator, .calculator, section:nth-of-type(3), main') ? document.querySelector('#calculator, .calculator, section:nth-of-type(3), main').innerText : document.body.innerText")
        print("Referral page body text snippet:\n", calc_section[:1000])
        await page.close()

        # ----------------------------------------------------
        # 3. INCENTIVES DEEP CHECK
        # ----------------------------------------------------
        print("\n=== 3. INCENTIVES PAGE ===")
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto("https://verdischain.com/incentives/", wait_until="networkidle")
        inc_text = await page.evaluate("() => document.body.innerText")
        print("Incentives body snippet:\n", inc_text[:1000])
        await page.close()

        # ----------------------------------------------------
        # 4. DOCS DEEP CHECK
        # ----------------------------------------------------
        print("\n=== 4. DOCS PAGE ===")
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto("https://verdischain.com/docs/", wait_until="networkidle")
        docs_text = await page.evaluate("() => document.body.innerText")
        print("Docs body snippet:\n", docs_text[:1000])
        
        # Check all sidebar links or anchors
        doc_links = await page.eval_on_selector_all("a", "elems => elems.map(e => ({href: e.getAttribute('href'), text: e.innerText.trim()}))")
        print("Docs link sample:", doc_links[:10])
        await page.close()

        # ----------------------------------------------------
        # 5. CONTACT DEEP CHECK
        # ----------------------------------------------------
        print("\n=== 5. CONTACT PAGE ===")
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto("https://verdischain.com/contact/", wait_until="networkidle")
        
        # Fill form and submit
        await page.select_option("#subject", index=1)
        await page.fill("#name", "Test User")
        await page.fill("#email", "test@example.com")
        await page.fill("#message", "Testing contact form functionality.")
        
        contact_res = []
        page.on("response", lambda r: contact_res.append((r.status, r.url)))
        await page.click("button[type='submit']")
        await page.wait_for_timeout(2000)
        print("Contact form submission network responses:", contact_res)
        contact_msg = await page.evaluate("() => document.body.innerText")
        print("Contact body after submit snippet:\n", contact_msg[-500:])
        await page.close()

        # ----------------------------------------------------
        # 6. API DEEP CHECK
        # ----------------------------------------------------
        print("\n=== 6. API PAGE ===")
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto("https://verdischain.com/api/", wait_until="networkidle")
        api_text = await page.evaluate("() => document.body.innerText")
        print("API body snippet:\n", api_text[:1000])
        await page.close()

        # ----------------------------------------------------
        # 7. TERMS DEEP CHECK
        # ----------------------------------------------------
        print("\n=== 7. TERMS PAGE ===")
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto("https://verdischain.com/terms/", wait_until="networkidle")
        terms_text = await page.evaluate("() => document.body.innerText")
        print("Terms snippet:\n", terms_text[:1000])
        await page.close()

        # ----------------------------------------------------
        # 8. PRIVACY DEEP CHECK
        # ----------------------------------------------------
        print("\n=== 8. PRIVACY PAGE ===")
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto("https://verdischain.com/privacy/", wait_until="networkidle")
        priv_text = await page.evaluate("() => document.body.innerText")
        print("Privacy snippet:\n", priv_text[:1000])
        await page.close()

        await browser.close()

asyncio.run(deep_check())
