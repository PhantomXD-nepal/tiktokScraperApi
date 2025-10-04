import requests
import json
import re

url = "https://scriptadmin.tokbackup.com/v1/tiktok/fetchMultipleTikTokData?get_transcript=true&ip=103.10.31.107"

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Origin": "*",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Host": "scriptadmin.tokbackup.com",
    "Origin": "https://www.script.tokaudit.io",
    "Referer": "https://www.script.tokaudit.io/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
    "cross-origin-resource-policy": "cross-origin",
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "x-api-key": "Toktools2024@!NowMust",
}


def get_transcript(video_url):
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
        return subtitles

    except ValueError:
        print("Non-JSON response:")
        print(response.text)


def parse_count(s: str) -> int:
    """
    Parse a string representing a count with possible suffixes like 1.2M or 5.4K into an integer.
    """
    if not s:
        return 0

    s = s.strip().replace(",", "")
    m = re.match(r"^([\d,.]+)\s*([MKk]?)$", s)
    if not m:
        digits = re.findall(r"\d+", s)
        return int(digits[0]) if digits else 0
    number, suffix = m.groups()
    number = float(number)
    if suffix.upper() == "M":
        number *= 1_000_000
    elif suffix.upper() == "K":
        number *= 1_000
    return int(number)


def audio_fetcher(url: str):
    pass
