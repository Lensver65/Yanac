#!/usr/bin/env python3
# coding: utf-8

import json
import re
import logging
import requests
from pathlib import Path
from time import sleep
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ===== CONFIG =====
INPUT_FILE = "404-2026.json"
OUTPUT_FILE = "404_urls-2026.txt"
LOG_FILE = "404_checker.log"
URL_PATTERN = r'https://yanac\.hu[^\s"]+'
TIMEOUT = 5
DELAY = 2  # seconds between requests
# ===================

# ----- Logging setup -----
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def create_session():
    """Create requests session with retry strategy."""
    session = requests.Session()

    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update({
        "User-Agent": "Yanac404Checker/1.0"
    })

    return session


def load_json(path):
    """Safely load JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("JSON root must be a list.")

        return data

    except Exception as e:
        logging.error(f"Failed to load JSON: {e}")
        raise


def extract_urls(text):
    """Extract URLs from text using regex."""
    return re.findall(URL_PATTERN, text or "")


def main():
    logging.info("Script started.")

    data = load_json(INPUT_FILE)

    session = create_session()
    checked_urls = set()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
        for item in data:

            if not isinstance(item, dict):
                continue

            text = item.get("post_content", "")
            title = item.get("post_title", "")

            urls = extract_urls(text)

            for url in urls:

                if url in checked_urls:
                    continue  # avoid duplicate checks

                checked_urls.add(url)

                try:
                    response = session.get(url, timeout=TIMEOUT)

                    if response.status_code == 404:
                        line = f"Cim: {title}, URL: {url}\n"
                        output_file.write(line)
                        logging.info(f"404 detected: {url}")
                        print(f"404 → {url}")

                    sleep(DELAY)

                except requests.RequestException as e:
                    logging.warning(f"Request failed for {url}: {e}")

    logging.info("Script finished.")


if __name__ == "__main__":
    main()
