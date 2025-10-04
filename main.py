import csv
import asyncio
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from playwright.async_api import async_playwright
from helper import parse_count, generateParaprashe, saveAudio
from test import get_transcriptt as get_transcript


# ---------------------- Config ----------------------
KEYWORD = "quantam physics ai "
MAX_PAGES = 10
VIRAL_LIKES_THRESHOLD = 1000
OUTPUT_CSV = "spirituality.csv"
DELAY_BETWEEN_SCROLLS = 1.0  # seconds
MAX_WORKERS = 5  # Number of concurrent threads for transcript/paraphrase processing


def process_video(video_data):
    """
    Process a single video: get transcript, paraphrase, and generate audio.
    This function runs in a thread.
    """
    url = video_data["url"]
    print(f"Processing: {url}")

    try:
        # Get transcript
        transcript = get_transcript(url)
        video_data["transcript"] = transcript

        # Generate paraphrase
        if transcript:
            paraphrase = generateParaprashe(transcript)
            video_data["paraphrase"] = paraphrase

            # Generate audio from paraphrase
            audio_path = saveAudio(paraphrase)
            video_data["audio_path"] = audio_path

            print(f"  ✓ {url} - Transcript, paraphrase, and audio generated")
        else:
            video_data["paraphrase"] = ""
            video_data["audio_path"] = ""
            print(f"  ⚠ {url} - No transcript found")

        return video_data
    except Exception as e:
        print(f"  ✗ {url} - Error: {e}")
        video_data["transcript"] = ""
        video_data["paraphrase"] = ""
        video_data["audio_path"] = ""
        return video_data


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
                    raw_text = await parent.inner_text()  # type: ignore
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

        # -------- Get Transcripts, Paraphrases, and Generate Audio with Threading --------
        print(f"\nProcessing videos using {MAX_WORKERS} threads...")

        # Use ThreadPoolExecutor to process videos concurrently
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit all tasks
            future_to_video = {
                executor.submit(process_video, video): video for video in viral
            }

            # Collect results as they complete
            processed_videos = []
            for future in as_completed(future_to_video):
                try:
                    result = future.result()
                    processed_videos.append(result)
                except Exception as e:
                    print(f"  ✗ Thread error: {e}")

        # Save to CSV
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["url", "likes", "transcript", "paraphrase", "audio_path"]
            )
            writer.writeheader()
            for row in sorted(processed_videos, key=lambda x: x["likes"], reverse=True):
                writer.writerow(row)

        print(f"\nSaved to {OUTPUT_CSV}")
        print(f"Total videos processed: {len(processed_videos)}")


if __name__ == "__main__":
    asyncio.run(scrape())
