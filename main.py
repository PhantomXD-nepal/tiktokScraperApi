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
