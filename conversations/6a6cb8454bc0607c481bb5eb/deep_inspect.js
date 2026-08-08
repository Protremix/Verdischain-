const { chromium } = require('playwright');
const fs = require('fs');

const pages = [
  { name: 'eco', url: 'https://verdischain.com/eco/?nocache=50009' },
  { name: 'validators', url: 'https://verdischain.com/validators/?nocache=50010' },
  { name: 'incentives', url: 'https://verdischain.com/incentives/?nocache=50011' },
  { name: 'referral', url: 'https://verdischain.com/referral/?nocache=50012' }
];

async function deepInspect() {
  const browser = await chromium.launch();

  for (const pageInfo of pages) {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    await page.goto(pageInfo.url, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    const data = await page.evaluate(() => {
      // Collect all interactive elements (buttons, links, social share, etc)
      const allElements = Array.from(document.querySelectorAll('a, button, [onclick], input, select'));
      const interactive = allElements.map(el => ({
        tag: el.tagName,
        id: el.id,
        class: el.className,
        text: el.innerText ? el.innerText.trim() : el.value || '',
        href: el.getAttribute('href'),
        onclick: el.getAttribute('onclick'),
        type: el.getAttribute('type')
      }));

      // Collect all visible text blocks with their selectors/classes
      const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => ({
        tag: h.tagName,
        text: h.innerText.trim(),
        class: h.className
      }));

      // Check for hardcoded stats / numbers / text in DOM
      const statCards = Array.from(document.querySelectorAll('.stat-card, .metric-card, .card, [class*="stat"], [class*="card"], [class*="metric"]')).map(c => ({
        class: c.className,
        text: c.innerText.trim()
      }));

      return {
        interactive,
        headings,
        statCards
      };
    });

    fs.writeFileSync(`deep_${pageInfo.name}.json`, JSON.stringify(data, null, 2));

    await context.close();
  }

  await browser.close();
}

deepInspect();
