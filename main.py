import csv
import asyncio
import re
from playwright.async_api import async_playwright
from helper import parse_count

# ---------------------- Config ----------------------
KEYWORD = "quantam physics ai "
MAX_PAGES = 1
VIRAL_LIKES_THRESHOLD = 1000
OUTPUT_CSV = "spirituality.csv"
DELAY_BETWEEN_SCROLLS = 1.0  # seconds


async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        search_url = (
            f"https://www.tiktok.com/search?q={KEYWORD.replace(' ', '%20')}&t=0"
        )
        print(f"Navigating to {search_url}")
        await page.goto(search_url)

        results = {}

        # -------- Loop through search result pages --------
        for page_index in range(MAX_PAGES):
            await page.wait_for_timeout(3000)  # Wait for content to load
            anchors = await page.query_selector_all('a[href*="/video/"]')

            for a in anchors:
                href = await a.get_attribute("href")
                if not href:
                    continue

                # Extract canonical TikTok video URL
                match = re.search(
                    r"(https?://www\.tiktok\.com/[@\w\-.]+/video/\d+)", href
                )
                url = match.group(1) if match else href.split("?")[0]

                if url in results:
                    continue

                # Extract like count near the video link
                likes = 0
                try:
                    parent = await a.evaluate_handle("el => el.closest('div')")
                    raw_text = await parent.inner_text()
                    likes = parse_count(raw_text)
                except Exception:
                    pass

                results[url] = {"url": url, "likes": likes}

            # Scroll to load more results
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            await page.wait_for_timeout(int(DELAY_BETWEEN_SCROLLS * 1000))

        await browser.close()

        # -------- Print Results --------
        for url, data in results.items():
            print(f"{url} → {data['likes']} likes")

        # Filter viral content
        viral = [v for v in results.values() if v["likes"] >= VIRAL_LIKES_THRESHOLD]
        print(f"Total found: {len(results)}; Viral: {len(viral)}")

        # Save to CSV
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["url", "likes"])
            writer.writeheader()
            for row in sorted(viral, key=lambda x: x["likes"], reverse=True):
                writer.writerow(row)

        print("Saved to", OUTPUT_CSV)


if __name__ == "__main__":
    asyncio.run(scrape())
