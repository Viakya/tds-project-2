from playwright.async_api import async_playwright
import asyncio

async def render_page(url: str) -> str:
    """
    Loads the given quiz URL, waits for JS rendering, 
    and returns the fully rendered DOM HTML.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Load and wait for network & JS modules
        await page.goto(url, wait_until="networkidle")

        # Wait for the quiz root container to appear
        try:
            await page.wait_for_selector("#root", timeout=5000)
        except:
            print("⚠ #root not found, still extracting HTML...")

        # Give JS time to populate content
        await asyncio.sleep(15)

        final_html = await page.content()
        await browser.close()
        return final_html
