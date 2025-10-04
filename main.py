import csv
import asyncio
from playwright.async_api import async_playwright
import re
import time
from urllib.parse import urlparse
from helper import parse_count

# Config
KEYWORD = "funny cats"
MAX_PAGES = 3
VIRAL_VIEWS_THRESHOLD = 100_000
OUTPUT_CSV = "tiktok_viral_urls.csv"
DELAY_BETWEEN_SCROLLS = 2.0


# print(parse_count("3.4k"))
async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            + "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        )
        page = await context.new_page()

        search_url = (
            f"https://www.tiktok.com/search?q={KEYWORD.replace(' ', '%20')}&t=0"
        )
        print(f"Navigating to {search_url}")
        await page.goto(search_url)

        results = {}
        for page_index in range(MAX_PAGES):
            await page.wait_for_timeout(3000)  # Wait for initial content to load
            anchors = await page.query_selector_all('a[href*="/video/"]')

            for a in anchors:
                href = await a.get_attribute("href")
                if not href:
                    continue
                m = re.search(r"(https?://www\.tiktok\.com/[@\w\-.]+/video/\d+)", href)
                if m:
                    url = m.group(1)
                else:
                    # fall back use raw url
                    url = href.split("?")[0]
                if url in results:
                    continue

                # Extract view count and like near the anchor


asyncio.run(scrape())
