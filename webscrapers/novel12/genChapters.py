import aiohttp
import asyncio
from bs4 import BeautifulSoup
import os
import urllib
import re
from functools import lru_cache
import json
import time
from aiohttp import ClientTimeout
from asyncio import Semaphore
import random
import boLogger  # Use boLogger instead of standard logging

logger = boLogger.CustomLog()
logger.set_default_custom(title='Downloaded', color='Blue', bold=False, underlined=False)

class RateLimiter:
    def __init__(self, calls_per_second):
        self.calls_per_second = calls_per_second
        self.timestamps = []
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.time()
            # Remove timestamps older than 1 second
            self.timestamps = [ts for ts in self.timestamps if now - ts < 1]
            
            if len(self.timestamps) >= self.calls_per_second:
                # Wait until we can make another request
                sleep_time = 1 - (now - self.timestamps[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            
            # Add very small random delay to prevent exact pattern detection
            await asyncio.sleep(random.uniform(0.05, 0.1))
            self.timestamps.append(time.time())

class genChapters:
    def __init__(self, url):
        self.url = url
        self.baseURL = 'https://www.novel12.com'
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        
        # Initialize rate limiter and semaphore with higher limits
        self.rate_limiter = RateLimiter(calls_per_second=5)  # Increased from 2
        self.semaphore = Semaphore(5)  # Increased from 2
        
        # Initialize novel info
        self.novel_info = None
        self.novelTitle = None
        self.chapters_data = {}
        
        # Configure timeout
        self.timeout = ClientTimeout(total=5, connect=3)  # Increased total timeout

    def __str__(self):
        return "A webscraper for Novel12"
    
    def __transformTitle(self, novel_title: str) -> str:
        if not novel_title:
            return "unknown-novel"
        
        decoded_title = urllib.parse.unquote(novel_title)
        transformed_title = decoded_title.lower()
        transformed_title = re.sub(r"[''']", "", transformed_title)
        transformed_title = re.sub(r'[^a-zA-Z0-9\s]', '', transformed_title)
        transformed_title = transformed_title.replace(" ", "-")
        transformed_title = transformed_title.replace(":", "")
        transformed_title = transformed_title.replace("/", "")
        return transformed_title
    
    def __validDirName(self, name):
        if not name:
            # Generate a fallback directory name if title is None
            url_parts = self.url.split('/')
            fallback = url_parts[-1] if url_parts else "unknown-novel"
            logger.warning(f"Novel title is None, using fallback name: {fallback}")
            return fallback
            
        name = re.sub(r"[''']", "'", name)
        name = name.replace(":", "")
        name = name.replace("/", "")
        return name
    
    async def __fetch_page(self, session, url: str) -> BeautifulSoup:
        """Async function to fetch and parse a webpage with strict 3 second timeout"""
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                await self.rate_limiter.acquire()
                async with self.semaphore:
                    # Create a task for the request with timeout
                    try:
                        async with asyncio.timeout(3):  # Strict 3-second timeout
                            async with session.get(url) as response:
                                if response.status == 200:
                                    content = await response.text()
                                    return BeautifulSoup(content, 'html.parser')
                                elif response.status == 503:
                                    wait_time = (attempt + 1) * 1  # Shorter backoff
                                    logger.warning(f"503 error for {url}, retrying soon (attempt {attempt+1}/{max_attempts})")
                                    await asyncio.sleep(wait_time)
                                else:
                                    logger.warning(f"HTTP {response.status} for {url}")
                                    response.raise_for_status()
                    except asyncio.TimeoutError:
                        # Just log and continue to retry if timeout occurs
                        logger.warning(f"Request timed out after 3s for {url}, retrying...")
                        continue
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                if attempt < (max_attempts - 1):
                    await asyncio.sleep(0.1)  # Short delay before retrying
                else:
                    return None
        
        logger.error(f"Failed to fetch {url} after {max_attempts} attempts")
        return None

    async def __get_novel_info(self, session):
        """Async function to get novel info"""
        soup = await self.__fetch_page(session, self.url)
        if not soup:
            logger.error(f"Failed to retrieve novel info for {self.url}")
            return {'title': None, 'categories': [], 'summary': None}
        
        info = {}
        
        # Get title from div with class 'title' and h1
        title_div = soup.find('div', class_='title')
        if title_div:
            title_elem = title_div.find('h1')
            info['title'] = title_elem.get_text(strip=True) if title_elem else None
        
        # Get cover image
        cover_img = soup.find('a', class_='imagesCrop')
        if cover_img and cover_img.find('img'):
            info['cover_image'] = cover_img.find('img').get('src')
        
        # Get categories (if available)
        info['categories'] = []  # Add category extraction if available
        
        # Get summary (if available)
        info['summary'] = None  # Add summary extraction if available
        
        return info

    async def __get_chapter_list(self, session):
        """Async function to get chapter list"""
        soup = await self.__fetch_page(session, self.url)
        if not soup:
            logger.error(f"Failed to fetch chapter list for {self.url}")
            return []
            
        chapters = []
        chapter_list = soup.find('ul', class_='chuong')
        if chapter_list:
            for index, a_tag in enumerate(chapter_list.find_all('a')):
                chapter_url = a_tag.get('href')
                if chapter_url:
                    # Add base URL if the URL is relative
                    if not chapter_url.startswith(('http://', 'https://')):
                        chapter_url = f"{self.baseURL}{chapter_url}"
                chapter_title = a_tag.get_text(strip=True)
                if chapter_url and chapter_title:
                    chapters.append((chapter_url, chapter_title, str(index + 1)))  # Add 1 to make it 1-based indexing
                    
        return chapters

    async def __process_chapter(self, session, link, title, chapter_num):
        """Async function to process a single chapter"""
        try:
            if not self.novelTitle:
                logger.error(f"Cannot process chapter {title} - novel title is None")
                return
                
            folder_name = self.__validDirName(self.novelTitle)
            file_dir = f'templates/novels/{folder_name}-chapters'
            os.makedirs(file_dir, exist_ok=True)
            
            soup = await self.__fetch_page(session, link)
            if not soup:
                logger.error(f"Failed to fetch chapter {title}")
                return
            
            # Extract chapter content
            content_div = soup.find('div', class_='content-center wl')
            if not content_div:
                logger.error(f"Content not found for chapter {title}")
                return
            
            # Get all paragraphs within the content div
            paragraphs = []
            for p in content_div.find_all('p'):
                text = p.get_text(strip=True)
                if text:  # Only add non-empty paragraphs
                    paragraphs.append(text)
            
            # Format chapter content
            chapter_content = '\n\n'.join(paragraphs)
            
            # Write to JSON file
            json_path = os.path.join(file_dir, 'chapters.json')
            try:
                # First read existing data
                existing_data = {}
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        try:
                            existing_data = json.load(f)
                        except json.JSONDecodeError:
                            logger.error(f"Error reading JSON for chapter {title}, starting fresh")
                
                # Add new chapter with its sequential index
                existing_data[chapter_num] = [title, chapter_content]
                
                # Write back to file
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Saved chapter {chapter_num}: {title}")
            except Exception as e:
                logger.error(f"Error saving chapter {title} to JSON: {e}")
            
        except Exception as e:
            logger.error(f"Error processing chapter {title}: {e}")

    async def getChapters(self):
        """Main function to get all chapters"""
        async with aiohttp.ClientSession(headers=self.__headers, timeout=self.timeout) as session:
            # Get novel info
            self.novel_info = await self.__get_novel_info(session)
            self.novelTitle = self.novel_info.get('title')
            
            if not self.novelTitle:
                logger.error("Failed to get novel title")
                return
            
            # Create directory and save metadata
            folder_name = self.__validDirName(self.novelTitle)
            file_dir = f'templates/novels/{folder_name}-chapters'
            os.makedirs(file_dir, exist_ok=True)
            
            # Create or update metadata.json
            metadata_path = os.path.join(file_dir, 'metadata.json')
            metadata = {
                'title': self.novelTitle,
                'categories': self.novel_info.get('categories', []),
                'summary': self.novel_info.get('summary', ''),
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # Get chapter list
            chapters = await self.__get_chapter_list(session)
            if not chapters:
                logger.error("No chapters found")
                return
            
            # Process chapters
            tasks = []
            for link, title, chapter_num in chapters:
                task = asyncio.create_task(self.__process_chapter(session, link, title, chapter_num))
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            logger.info(f"Completed processing {len(chapters)} chapters for {self.novelTitle}")

async def process_novel(link):
    """Process a single novel"""
    scraper = genChapters(link)
    await scraper.getChapters()

async def main():
    """Main function to process novels"""
    # Example usage
    novel_url = "https://novel12.com/254188/golden-son.htm"  # Replace with actual URL
    await process_novel(novel_url)

if __name__ == "__main__":
    asyncio.run(main())
