import requests
import json
import re

url = "https://scriptadmin.tokbackup.com/v1/tiktok/fetchMultipleTikTokData?get_transcript=true&ip=103.10.31.107"

headers = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Origin": "https://www.script.tokaudit.io",
    "Referer": "https://www.script.tokaudit.io/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
    "x-api-key": "Toktools2024@!NowMust",
}


def get_transcriptt(video_url):
    payload = {"videoUrls": [video_url]}

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Extract and print only subtitles
    try:
        data = response.json()
        subtitles = data["data"][0]["subtitles"]
        subtitles = re.sub(r"WEBVTT.*?\n\n", "", subtitles, flags=re.DOTALL)
        subtitles = re.sub(
            r"\d{2}:\d{2}:\d{2}\s*-->\s*\d{2}:\d{2}:\d{2}\n?", "", subtitles
        )
        subtitles = subtitles.replace("\n", " ").strip()
        subtitles = " ".join(subtitles.split())
        if not isinstance(subtitles, str):
            print(
                f"Warning: Subtitles not available for {video_url} (type: {type(subtitles).__name__})"
            )
            return ""
        return subtitles

    except ValueError:
        print("Non-JSON response:")
        print(response.text)
