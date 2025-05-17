#!/usr/bin/env python3
# novelbin_scraper.py
import time
import random
import csv
import logging
import cloudscraper
import undetected_chromedriver as uc
from selenium_stealth import stealth
from bs4 import BeautifulSoup
from itertools import cycle

# ───── CONFIGURATION ────────────────────────────────────────────
BASE_URL      = "https://novelbin.com"
LISTING_PATH  = "/sort/latest"
MAX_PAGES     = 20     # how many listing pages to scrape
OUTPUT_CSV    = "novels.csv"
DELAY_RANGE   = (1.0, 3.0)
LOG_LEVEL     = logging.INFO

# Rotate among these real user‑agents:
USER_AGENTS = [
    # e.g. fetched from https://developers.whatismybrowser.com/useragents/explore/
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    # … add 20–50 more…
]

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(message)s"
)
# ─────────────────────────────────────────────────────────────────

def rand_headers():
    """Generate a realistic set of browser headers."""
    ua = random.choice(USER_AGENTS)
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;"
                  "q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Referer": BASE_URL,
        "Sec-CH-UA": '"Chromium";v="114", "Google Chrome";v="114"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"',
    }


def fetch_via_cloudscraper(url: str) -> str:
    """Attempt Cloudflare JS-challenge bypass via cloudscraper."""
    logging.info(f"Trying Cloudscraper for {url}")
    scraper = cloudscraper.create_scraper(
        browser={"custom": random.choice(USER_AGENTS)}
    )
    resp = scraper.get(url, headers=rand_headers(), timeout=30)
    resp.raise_for_status()
    time.sleep(random.uniform(*DELAY_RANGE))
    return resp.text


def init_stealth_driver() -> uc.Chrome:
    """Start an undetected, stealthy ChromeDriver instance."""
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("window-size=1200,800")
    driver = uc.Chrome(options=options)
    stealth(
        driver,
        languages=["en-GB", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver


def fetch_via_selenium(url: str) -> str:
    """Fallback to real browser emulation if Cloudscraper fails."""
    logging.info(f"Falling back to Selenium for {url}")
    driver = init_stealth_driver()
    driver.get(url)
    # simulate human pause
    time.sleep(random.uniform(2.0, 5.0))
    content = driver.page_source
    driver.quit()
    time.sleep(random.uniform(*DELAY_RANGE))
    return content


def parse_listing(html: str) -> list:
    """Extract novel page URLs from a listing page."""
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.select("div.novel-item > a"):
        href = a.get("href")
        if href and href.startswith("/"):
            links.append(BASE_URL + href)
        elif href:
            links.append(href)
    return list(dict.fromkeys(links))  # dedupe, preserve order


def parse_novel(html: str, url: str) -> dict:
    """Extract metadata and chapter links from a novel page."""
    soup = BeautifulSoup(html, "html.parser")
    data = {
        "url":         url,
        "title":       soup.select_one("h1.novel-title") and soup.select_one("h1.novel-title").get_text(strip=True),
        "author":      soup.select_one("a.novel-author") and soup.select_one("a.novel-author").get_text(strip=True),
        "cover_image": soup.select_one("div.novel-cover img") and soup.select_one("div.novel-cover img")["src"],
        "genres":      [g.get_text(strip=True) for g in soup.select("span.genre")],
        "status":      soup.select_one("span.status") and soup.select_one("span.status").get_text(strip=True),
        "description": soup.select_one("div.novel-description") and soup.select_one("div.novel-description").get_text(strip=True),
        "chapters":    []
    }
    for chap in soup.select("ul.chapter-list li a"):
        data["chapters"].append({
            "title": chap.get_text(strip=True),
            "url":   chap.get("href")
        })
    return data


def save_to_csv(all_data: list, filename: str):
    """Write novel metadata list to a CSV file."""
    keys = ["url", "title", "author", "cover_image", "genres", "status", "description"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for nd in all_data:
            row = {k: ";".join(v) if isinstance(v, list) else v for k, v in nd.items() if k in keys}
            writer.writerow(row)
    logging.info(f"Saved {len(all_data)} novels to {filename}")


def main():
    all_novel_data = []
    seen_urls = set()

    # Scrape listing pages
    for page in range(1, MAX_PAGES + 1):
        list_url = BASE_URL + LISTING_PATH.format(page=page)
        try:
            html = fetch_via_cloudscraper(list_url)
        except Exception as e:
            logging.warning(f"Cloudscraper failed: {e}")
            html = fetch_via_selenium(list_url)

        novel_links = parse_listing(html)
        logging.info(f"Found {len(novel_links)} novels on page {page}")

        # Scrape each novel’s details
        for novel_url in novel_links:
            if novel_url in seen_urls:
                continue
            seen_urls.add(novel_url)

            try:
                # try Cloudscraper first
                novel_html = fetch_via_cloudscraper(novel_url)
            except Exception:
                novel_html = fetch_via_selenium(novel_url)

            data = parse_novel(novel_html, novel_url)
            all_novel_data.append(data)
            logging.info(f"Parsed novel: {data.get('title')}")

    # Output results
    save_to_csv(all_novel_data, OUTPUT_CSV)
    logging.info("Scraping complete.")


if __name__ == "__main__":
    main()
