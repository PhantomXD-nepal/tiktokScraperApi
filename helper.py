import requests
import json
import re
from sambanova import SambaNova
from dotenv import load_dotenv
import os
from test import get_transcriptt

load_dotenv()


url = "https://scriptadmin.tokbackup.com/v1/tiktok/fetchMultipleTikTokData?get_transcript=true&ip=103.10.31.107"

headers = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Origin": "https://www.script.tokaudit.io",
    "Referer": "https://www.script.tokaudit.io/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
    "x-api-key": "Toktools2024@!NowMust",
}


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


def generateParaprashe(
    content: str,
    system_prompt: str = """You are a skilled Nepali‑language paraphraser.
When the user supplies a passage, rewrite it in Nepali, making the text shorter while preserving every original idea, fact, and nuance.

Guidelines

Keep the meaning exactly the same; do not add, delete, or alter any information.
Use clear, natural Nepali and avoid overly formal or archaic expressions unless the original tone demands it.
If shortening is impossible without loss of meaning, keep the text as concise as possible while still retaining all essential content.
If the user’s request is unrelated to paraphrasing, respond appropriately to the new request.
never break character or reveal that you are an AI model. only give the paraphrased content. nothing else""",
) -> str:
    if content == "":
        return ""

    client = SambaNova(
        base_url="https://api.sambanova.ai/v1", api_key=os.getenv("AI_API")
    )

    completion = client.chat.completions.create(
        model="DeepSeek-V3-0324",
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant. {system_prompt}",
            },
            {"role": "user", "content": f"Paraprashe this content{content}"},
        ],
    )

    return completion.choices[0].message.content  # type: ignore


url = "https://speechma.com/com.api/tts-api.php"
headers = {
    "Host": "speechma.com",
    "Sec-Ch-Ua-Platform": "Windows",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Chromium";v="131", "Not_A Brand";v="24"',
    "Content-Type": "application/json",
    "Sec-Ch-Ua-Mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36",
    "Accept": "*/*",
    "Origin": "https://speechma.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://speechma.com/",
    "Accept-Encoding": "gzip, deflate, br",
    "Priority": "u=1, i",
}


# Function to get audio from the server
def get_audio(url, data, headers):
    try:
        json_data = json.dumps(data)
        response = requests.post(url, data=json_data, headers=headers)
        response.raise_for_status()
        if response.headers.get("Content-Type") == "audio/mpeg":
            return response.content
        else:
            print(
                f"Unexpected response format: {response.headers.get('Content-Type')}",
                "red",
            )
            return None
    except requests.exceptions.RequestException as e:
        if e.response:
            print(f"Server response: {e.response.text}", "red")
        print(f"Request failed: {e}", "red")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}", "red")
        return None


# Function to save audio to a file
def save_audio(response, directory, chunk_num):
    if response:
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, f"audio_chunk_{chunk_num}.mp3")
        try:
            with open(file_path, "wb") as f:
                f.write(response)
            print(f"Audio saved to {file_path}", "green")
        except IOError as e:
            print(f"Error saving audio: {e}", "red")
    else:
        print("No audio data to save", "red")


def saveAudio(text: str) -> str:
    if not text:
        print("Error: No text provided. Exiting.", "red")
        return ""
    if text == "":
        print("Error: Empty text provided. Exiting.", "red")
        return ""

    data = {
        "text": f"{text}",
        "voice": "voice-210",
    }

    try:
        response = get_audio(url, data, headers)
        save_audio(response, "output_audio", text[:10])
    except Exception as e:
        print(f"An unexpected error occurred: {e}", "red")
        return ""

    return "output_audio/audio_chunk_1.mp3"
