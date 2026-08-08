const { chromium } = require('playwright');
const fs = require('fs');

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('https://verdischain.com/eco/?nocache=50009', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  const data = await page.evaluate(() => {
    // Collect all text nodes/elements
    const allText = document.body.innerText;

    // Check images
    const images = Array.from(document.querySelectorAll('img')).map(img => ({
      src: img.src,
      alt: img.alt,
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
      complete: img.complete
    }));

    // Check stats cards and demo data tags
    const stats = Array.from(document.querySelectorAll('.stat-card, .metric-card, .eco-stat, .stat-box, [class*="stat"], [class*="metric"], [class*="card"]')).map(el => ({
      className: el.className,
      text: el.innerText
    }));

    // Check all buttons/links and their href/onclick
    const actions = Array.from(document.querySelectorAll('a, button, input, select')).map(el => ({
      tag: el.tagName,
      text: el.innerText || el.value,
      href: el.getAttribute('href'),
      onclick: el.getAttribute('onclick'),
      id: el.id,
      className: el.className
    }));

    // Check overlapping or clipped elements
    const elements = Array.from(document.querySelectorAll('body *'));
    const clipped = [];
    elements.forEach(el => {
      const style = window.getComputedStyle(el);
      if (style.overflow === 'hidden' || style.overflowX === 'hidden') {
        if (el.scrollWidth > el.clientWidth + 1) {
          clipped.push({
            tag: el.tagName,
            id: el.id,
            className: el.className,
            scrollWidth: el.scrollWidth,
            clientWidth: el.clientWidth,
            text: el.innerText ? el.innerText.substring(0, 50) : ''
          });
        }
      }
    });

    return { images, stats, actions, clipped };
  });

  fs.writeFileSync('detailed_eco.json', JSON.stringify(data, null, 2));
  await browser.close();
}

main();
