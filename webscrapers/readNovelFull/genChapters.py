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
        self.baseURL = 'https://readnovelfull.com'
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
        return "A webscraper for ReadNovelFull"
    
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
            return {'title': None, 'categories': [], 'summary': None, 'novel_id': None}
        
        info = {}
        
        # Get title
        title_elem = soup.find('h3', class_='title')
        info['title'] = title_elem.get_text(strip=True) if title_elem else None
        
        # Get novel ID from rating div
        rating_div = soup.find('div', id='rating')
        info['novel_id'] = rating_div.get('data-novel-id') if rating_div else None
        
        # Get genres from info-meta
        genres: list[str] = []
        # Find the h3 with text 'Genre:'
        genre_heading = soup.find('h3', string='Genre:')
        if genre_heading:
            # Get the parent element (li) and find all a tags within it
            parent_li = genre_heading.parent
            if parent_li:
                genres = [a.get_text(strip=True) for a in parent_li.find_all('a')]
        info['categories'] = genres
        
        # Get description
        desc_text = soup.find('div', class_='desc-text')
        if desc_text:
            # Get all paragraphs and join them with newlines
            description_paragraphs = []
            for p in desc_text.find_all('p'):
                text = p.get_text(strip=True)
                if text:  # Only add non-empty paragraphs
                    description_paragraphs.append(text)
            info['summary'] = '\n\n'.join(description_paragraphs)
        else:
            info['summary'] = None
        
        return info

    async def __get_chapter_list(self, session, novel_id):
        """Async function to get chapter list from AJAX endpoint"""
        if not novel_id:
            logger.error("No novel ID provided")
            return []
            
        chapter_archive_url = f"{self.baseURL}/ajax/chapter-archive?novelId={novel_id}"
        soup = await self.__fetch_page(session, chapter_archive_url)
        if not soup:
            logger.error(f"Failed to fetch chapter archive for novel ID {novel_id}")
            return []
            
        chapters = []
        for index, li in enumerate(soup.find_all('li')):
            a_tag = li.find('a')
            if a_tag:
                chapter_url = f"{self.baseURL}{a_tag.get('href')}"
                chapter_title = a_tag.get_text(strip=True)
                if chapter_url and chapter_title:
                    chapters.append((chapter_url, chapter_title, str(index + 1)))  # Add 1 to make it 1-based indexing
                    
        return chapters

    def __extract_chapter_number(self, title: str, position: int = None) -> int:
        """Extract chapter number from title with fallback to position"""
        # Common patterns for chapter numbers
        patterns = [
            r'Chapter\s+(\d+)',  # "Chapter 1"
            r'Ch\.\s*(\d+)',     # "Ch. 1"
            r'(\d+)\s*-\s*',     # "1 - Title"
            r'^(\d+)\s*',        # "1 Title"
            r'Chapter\s+(\d+)\s*-\s*',  # "Chapter 1 - Title"
            r'Chapter\s+(\d+)\s*\.',    # "Chapter 1. Title"
            r'Ch\.\s*(\d+)\s*\.',       # "Ch. 1. Title"
            r'(\d+)\s*\.',              # "1. Title"
            r'Chapter\s+(\d+)\s*:',     # "Chapter 1: Title"
            r'Ch\.\s*(\d+)\s*:',        # "Ch. 1: Title"
            r'(\d+)\s*:',               # "1: Title"
            r'Chapter\s+(\d+)\s*–',     # "Chapter 1 – Title" (en dash)
            r'Ch\.\s*(\d+)\s*–',        # "Ch. 1 – Title" (en dash)
            r'(\d+)\s*–',               # "1 – Title" (en dash)
        ]
        
        # Try to find a number in the title
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        # If no number found and position is provided, use it as fallback
        if position is not None:
            return position + 1  # Add 1 to make it 1-based indexing
        
        # If no position provided and no number found, return a large number
        return 999999

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
            content_div = soup.find('div', id='chr-content')
            if not content_div:
                logger.error(f"Content not found for chapter {title}")
                return
            
            # Get chapter title - ensure it's not too long (likely content)
            chapter_title = content_div.find('h3')
            if chapter_title:
                chapter_title = chapter_title.get_text(strip=True)
                # Validate title length - if it's too long, it's probably content
                if len(chapter_title) > 200:  # Reasonable max length for a chapter title
                    logger.warning(f"Chapter title too long, using original title: {title}")
                    chapter_title = title
            else:
                chapter_title = title
            
            # Extract and clean chapter content
            paragraphs = []
            for p in content_div.find_all('p'):
                # Skip paragraphs that only contain strong tags (ads)
                if p.find('strong'):
                    continue
                
                # Remove strong tags but keep their text
                for strong in p.find_all('strong'):
                    strong.replace_with('')
                
                # Get text while preserving content within angular brackets
                text = str(p)
                # Remove outer <p> tags
                text = text.replace('<p>', '').replace('</p>', '')
                # Remove any remaining HTML tags except those within angular brackets
                text = re.sub(r'<(?!\w+>)[^>]*>', '', text)
                text = text.strip()
                if text:  # Only add non-empty paragraphs
                    paragraphs.append(text)
            
            chapter_content = '\n\n'.join(paragraphs)
            
            # Validate that content is not empty and not too short
            if not chapter_content or len(chapter_content) < 100:  # Minimum reasonable chapter length
                logger.error(f"Chapter content too short or empty for {title}")
                return
            
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
                existing_data[chapter_num] = [chapter_title, chapter_content]
                
                # Write back to file
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=2)
                
                logger.custom_log(f"Chapter {title} | index {chapter_num}")
            except Exception as e:
                logger.error(f"Error saving chapter {title} to JSON: {e}")
        
        except Exception as e:
            logger.error(f"Error processing chapter {title}: {e}")

    async def getChapters(self):
        """Main async function to get chapters"""
        try:
            async with aiohttp.ClientSession(headers=self.__headers) as session:
                # Initialize novel info
                self.novel_info = await self.__get_novel_info(session)
                self.novelTitle = self.novel_info['title']
                novel_id = self.novel_info['novel_id']
                
                if not self.novelTitle:
                    logger.error(f"Failed to get novel title for {self.url}, skipping...")
                    return
                    
                if not novel_id:
                    logger.error(f"Failed to get novel ID for {self.url}, skipping...")
                    return
                
                logger.info(f"Processing novel: {self.novelTitle} (ID: {novel_id})")
                
                folder_name = self.__validDirName(self.novelTitle)
                file_dir = f'templates/novels/{folder_name}-chapters'
                os.makedirs(file_dir, exist_ok=True)
                
                # Create or update metadata.json first
                metadata_path = os.path.join(file_dir, 'metadata.json')
                metadata = {
                    'title': self.novelTitle,
                    'categories': self.novel_info['categories'],
                    'summary': self.novel_info['summary'],
                    'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Save metadata immediately
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved metadata for {self.novelTitle}")
                
                # Load existing chapters data
                json_path = os.path.join(file_dir, 'chapters.json')
                existing_chapters = {}
                if os.path.exists(json_path):
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                            # Store both chapter number and title for comparison
                            for chapter_num, [title, _] in existing_data.items():
                                existing_chapters[chapter_num] = title
                    except json.JSONDecodeError:
                        logger.error(f"Error reading existing JSON file for {self.novelTitle}, starting fresh")
                        existing_chapters = {}
                
                # Get chapter list from AJAX endpoint
                chapters_to_process = await self.__get_chapter_list(session, novel_id)
                if not chapters_to_process:
                    logger.error(f"No chapters found for {self.novelTitle}")
                    return
                
                # Filter out existing chapters by comparing chapter numbers
                new_chapters = []
                for url, title, chapter_num in chapters_to_process:
                    if chapter_num not in existing_chapters:
                        new_chapters.append((url, title, chapter_num))
                    else:
                        # Log that we're skipping this chapter
                        logger.info(f"Skipping existing chapter {chapter_num}: {title}")
                
                if not new_chapters:
                    logger.info(f"No new chapters found for {self.novelTitle}")
                    return
                
                logger.info(f"Found {len(new_chapters)} new chapters to download for {self.novelTitle}")
                
                # Process chapters in larger batches
                batch_size = 20  # Increased from 10
                new_chapters_found = False
                
                for i in range(0, len(new_chapters), batch_size):
                    batch = new_chapters[i:i + batch_size]
                    batch_tasks = []
                    for url, title, chapter_num in batch:
                        batch_tasks.append(self.__process_chapter(session, url, title, chapter_num))
                    
                    await asyncio.gather(*batch_tasks)
                    logger.info(f"Progress: {min(i + batch_size, len(new_chapters))}/{len(new_chapters)} chapters processed")
                
                # Update metadata only if new chapters were found
                if new_chapters:
                    logger.info(f"New chapters found for {self.novelTitle}, updating last_updated timestamp")
                    metadata['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                else:
                    logger.info(f"No new chapters were actually saved for {self.novelTitle}")
                
        except Exception as e:
            logger.error(f"Error in getChapters for {self.url}: {e}")

    async def init_directories(self):
        """Async method to initialize directories and metadata"""
        async with aiohttp.ClientSession(headers=self.__headers) as session:
            self.novel_info = await self.__get_novel_info(session)
            self.novelTitle = self.novel_info['title']
            
            if self.novelTitle:
                transformed_title = self.__transformTitle(self.novelTitle)
                folder_name = self.__validDirName(transformed_title)
                file_dir = f'templates/novels/{folder_name}-chapters'
                os.makedirs(file_dir, exist_ok=True)
                
                # Create metadata.json
                metadata_path = os.path.join(file_dir, 'metadata.json')
                metadata = {
                    'title': self.novelTitle,
                    'categories': self.novel_info['categories'],
                    'genres': self.novel_info['genres'],
                    'summary': self.novel_info['summary'],
                }
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    # Change script such that only if a novel got a new chapter it will update the time on the 'last_updated' in the 'metadata.json' file
    
    from getPics import get_cover_image
    start = time.time()
    links = [
        'https://readnovelfull.com/shadow-slave.html',
        'https://readnovelfull.com/re-evolution-online.html',
        'https://readnovelfull.com/return-of-the-mount-hua-sect.html',
        'https://readnovelfull.com/the-beginning-after-the-end-v1.html',
        'https://readnovelfull.com/overgeared.html',
        'https://readnovelfull.com/trash-of-the-counts-family-v1.html',
        'https://readnovelfull.com/kill-the-sun.html',
        
        # 'https://readnovelfull.com/lightning-is-the-only-way-v1.html', # Completed
        # 'https://readnovelfull.com/the-perfect-run.html', # Completed
        'https://readnovelfull.com/the-innkeeper.html',
        'https://readnovelfull.com/cultivation-online-v3.html'
        
        
        # Add more novel URLs here
    ]
    
    async def process_novel(link):
        try:
            logger.info(f"Starting to process: {link}")
            get_cover_image(link)
            scraper = genChapters(link)
            
            await scraper.getChapters()
            
        except Exception as e:
            logger.error(f"Failed to process {link}: {e}")
    
    async def main():
        # Process novels concurrently in batches
        batch_size = 8  # Process 3 novels at a time
        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            await asyncio.gather(*[process_novel(link) for link in batch])
            # Small delay between batches
            if i + batch_size < len(links):
                await asyncio.sleep(1)
    
    asyncio.run(main())
    
    end = time.time()
    logger.success(f"Finished scraping all novels in {end - start:.2f} seconds")
    
    
    
