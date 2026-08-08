import asyncio
from playwright.async_api import async_playwright

async def inspect_chart():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # Desktop
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        await page.goto('https://verdischain.com/tokenomics/?nocache=50006', wait_until='networkidle')
        
        chart_data = await page.evaluate('''() => {
            const chartCanvas = document.getElementById('tokenomicsChart');
            const chartInst = Chart.getChart(chartCanvas);
            if (!chartInst) return "Chart instance not found";
            return {
                labels: chartInst.data.labels,
                data: chartInst.data.datasets[0].data,
                colors: chartInst.data.datasets[0].backgroundColor,
                legendItems: chartInst.legend.legendItems.map(item => ({
                    text: item.text,
                    hidden: item.hidden,
                    fillStyle: item.fillStyle
                }))
            };
        }''')
        print("CHART DATA INSTANCE:", chart_data)
        
        # Take canvas screenshot
        canvas = await page.query_selector('#tokenomicsChart')
        if canvas:
            await canvas.screenshot(path='chart_canvas.png')

        await browser.close()

asyncio.run(inspect_chart())
