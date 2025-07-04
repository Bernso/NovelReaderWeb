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

logger = boLogger.Logging()
title_div = 'chapter-title'

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
            
            # Add small random delay to prevent exact pattern detection
            await asyncio.sleep(random.uniform(0.1, 0.3))
            self.timestamps.append(time.time())

class genChapters:
    def __init__(self, url='https://lightnovelpub.vip/novel/shadow-slave-05122222'):
        self.url = url
        self.chapters = f'{self.url}/chapters'
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        
        # Initialize rate limiter and semaphore
        self.rate_limiter = RateLimiter(calls_per_second=2)
        self.semaphore = Semaphore(2)
        
        # Initialize novel info
        self.novel_info = None
        self.novelTitle = None
        self.chapters_data = {}
        
        # Configure timeout - set to exactly 3 seconds as requested
        self.timeout = ClientTimeout(total=3, connect=3)

    def __str__(self):
        return "A webscraper for light novel pub vip"
    
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
        
        # Get title
        title_elem = soup.find('h1', class_='novel-title text2row')
        info['title'] = title_elem.get_text(strip=True) if title_elem else None
        
        # Get categories
        categories = []
        categories_div = soup.find('div', class_='categories')
        if categories_div and (ul := categories_div.find('ul')):
            categories = [item.get_text(strip=True) for item in ul.find_all('li')]
        info['categories'] = categories
        
        # Get summary with preserved line breaks
        summary = ""
        summary_div = soup.find('div', class_='content expand-wrapper')
        if summary_div:
            # Find the main paragraph that contains the summary
            summary_p = summary_div.find('p')
            if summary_p:
                # Get the HTML content
                html_content = str(summary_p)
                
                # Split by <br> or <br/> tags
                segments = re.split(r'<br\s*/?>', html_content)
                
                # Clean each segment (remove HTML tags and strip whitespace)
                clean_segments = []
                for segment in segments:
                    # Remove any HTML tags
                    text = re.sub(r'<[^>]+>', '', segment)
                    # Strip whitespace but keep the content
                    text = text.strip()
                    if text:  # Only add non-empty segments
                        clean_segments.append(text)
                
                # Join segments with newlines to preserve the breaks
                summary = "\n".join(clean_segments)
            else:
                # Fallback: get text with newlines if no paragraph found
                summary = summary_div.get_text(separator='\n', strip=True)
        
        info['summary'] = summary
        
        return info
    
    async def __getTotalPages(self, session, thesoup):
        try:
            if not thesoup:
                return 0
                
            current_page = 1
            
            # First check if we can determine the max page directly
            pagination = thesoup.find('div', class_='pagination')
            if pagination:
                page_links = pagination.find_all('li')
                max_page = 1
                for link in page_links:
                    try:
                        page_num = int(link.get_text(strip=True))
                        max_page = max(max_page, page_num)
                    except (ValueError, TypeError):
                        continue
                
                if max_page > 1:
                    return max_page
            
            # Check if there's only one page of chapters
            chapter_list = thesoup.find('ul', class_='chapter-list')
            if chapter_list and chapter_list.find_all('li'):
                if not thesoup.find('li', class_='PagedList-skipToNext'):
                    return 1
            
            # If we're here, we need to follow next buttons
            soup_copy = thesoup
            while True:
                next_button = soup_copy.find('li', class_='PagedList-skipToNext')
                if not next_button or not next_button.find('a'):
                    return current_page
                
                # Get the next page URL and fetch it
                next_url = f"https://lightnovelpub.vip{next_button.find('a')['href']}"
                soup_copy = await self.__fetch_page(session, next_url)
                if not soup_copy:
                    return current_page
                
                current_page += 1
                logger.info(f"Scanning page {current_page}...")
                
                # Safety check to avoid infinite loops
                if current_page > 50:  # Assuming no novel has more than 50 pages of chapter listings
                    logger.warning("Too many pages, stopping scan")
                    return current_page
            
        except Exception as e:
            logger.error(f"Error getting total pages: {e}")
            return 0
    
    def __validate_chapter_number(self, chapter_num: str) -> bool:
        """
        Validate if a chapter number can be converted to float.
        Returns True if valid, False otherwise.
        """
        try:
            float(chapter_num)
            return True
        except ValueError:
            logger.warning(f"Invalid chapter number format: {chapter_num}")
            return False

    async def __process_chapter(self, session, link, num):
        """Async function to process a single chapter"""
        try:
            if not self.novelTitle:
                logger.error(f"Cannot process chapter {num} - novel title is None")
                return
                
            folder_name = self.__validDirName(self.novelTitle)
            file_dir = f'templates/novels/{folder_name}-chapters'
            os.makedirs(file_dir, exist_ok=True)
            
            num = str(num).replace('.', '-')
            chapter_num = num.replace('-', '.')
            
            # Skip if chapter already exists in memory
            if chapter_num in self.chapters_data:
                return
            
            soup = await self.__fetch_page(session, link)
            if not soup:
                logger.error(f"Failed to fetch chapter {chapter_num}")
                return
            
            # Extract chapter title using the provided title_div
            chapter_title_elem = soup.find(class_=title_div)
            if chapter_title_elem:
                chapter_title = chapter_title_elem.get_text(strip=True)
            else:
                chapter_title = f"Chapter {chapter_num}"
            
            chapter_container = soup.find('div', id='chapter-container')
            if chapter_container:
                chapter_text = chapter_container.get_text(separator='\n').strip()
                
                # Store chapter in memory
                self.chapters_data[chapter_num] = [chapter_title, chapter_text]
                
                # Write to JSON file
                json_path = os.path.join(file_dir, 'chapters.json')
                try:
                    # First read existing data
                    existing_data = {}
                    if os.path.exists(json_path):
                        with open(json_path, 'r', encoding='utf-8') as f:
                            try:
                                existing_data = json.load(f)
                                if '_metadata' in existing_data:
                                    del existing_data['_metadata']
                            except json.JSONDecodeError:
                                logger.error(f"Error reading JSON for chapter {chapter_num}, starting fresh")
                    
                    # Format with double newlines for better readability
                    formatted_text = chapter_text.replace('\n', '\n\n')
                    
                    # Update with new chapter data
                    existing_data[chapter_num] = [chapter_title, formatted_text]
                    
                    # Write back to file
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(existing_data, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"Chapter {chapter_num} downloaded and saved successfully")
                except Exception as e:
                    logger.error(f"Error saving chapter {chapter_num} to JSON: {e}")
            else:
                logger.error(f"Content not found for chapter {num}")
        
        except Exception as e:
            logger.error(f"Error processing chapter {num}: {e}")

    async def __process_page(self, session, page_num):
        """Async function to process all chapters in a single page"""
        if not self.novelTitle:
            logger.error(f"Cannot process page {page_num} - novel title is None")
            return []
            
        url = f'{self.chapters}?page={page_num}'
        soup = await self.__fetch_page(session, url)
        if not soup:
            return []
        
        chapter_args = []
        chapter_list = soup.find('ul', class_='chapter-list')
        if chapter_list:
            chapters = chapter_list.find_all('a')
            
            # Check for existing chapters before processing
            folder_name = self.__validDirName(self.novelTitle)
            file_dir = f'templates/novels/{folder_name}-chapters'
            json_path = os.path.join(file_dir, 'chapters.json')
            existing_chapters = set()
            
            # Check JSON file for existing chapters
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        chapters_data = json.load(f)
                        existing_chapters.update(chapters_data.keys())
                except json.JSONDecodeError:
                    pass
            
            # Check for existing text files (legacy support)
            if os.path.exists(file_dir):
                for filename in os.listdir(file_dir):
                    if filename.startswith('chapter-') and filename.endswith('.txt'):
                        chapter_num = filename.replace('chapter-', '').replace('.txt', '')
                        existing_chapters.add(chapter_num)
            
            for chapter in chapters:
                chapterLink = chapter['href']
                chapter_part = chapterLink.split('/')[-1]
                if chapter_part[-8:].isdigit():
                    chapter_part = chapter_part[:-9]
                
                chapter_part = chapter_part.replace('chapter-', '')
                chapterLinkNum = chapter_part.replace('-', '.')
                
                # Validate chapter number format
                if not self.__validate_chapter_number(chapterLinkNum):
                    continue

                # Skip if chapter already exists
                if chapterLinkNum in existing_chapters:
                    logger.info(f"Chapter {chapterLinkNum} already exists, skipping...")
                    continue
                
                chapterLink = f"https://lightnovelpub.vip{chapterLink}"
                chapter_args.append((chapterLink, chapterLinkNum))
        
        return chapter_args
    
    async def getChapters(self, retry_chapters=None):
        """Main async function to get chapters"""
        try:
            async with aiohttp.ClientSession(headers=self.__headers) as session:
                # Initialize novel info
                self.novel_info = await self.__get_novel_info(session)
                self.novelTitle = self.novel_info['title']
                
                if not self.novelTitle:
                    logger.error(f"Failed to get novel title for {self.url}, skipping...")
                    return
                
                logger.info(f"Processing novel: {self.novelTitle}")
                
                folder_name = self.__validDirName(self.novelTitle)
                file_dir = f'templates/novels/{folder_name}-chapters'
                os.makedirs(file_dir, exist_ok=True)
                
                # Load existing data and check for updates
                json_path = os.path.join(file_dir, 'chapters.json')
                metadata_path = os.path.join(file_dir, 'metadata.json')
                
                existing_chapters = set()
                if os.path.exists(json_path):
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            self.chapters_data = json.load(f)
                            existing_chapters = set(self.chapters_data.keys())
                    except json.JSONDecodeError:
                        logger.error(f"Error reading existing JSON file for {self.novelTitle}, starting fresh")
                        self.chapters_data = {}
                
                # Create or update metadata.json
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                    except json.JSONDecodeError:
                        metadata = {}
                else:
                    metadata = {
                        'title': self.novelTitle,
                        'categories': self.novel_info['categories'],
                        'summary': self.novel_info.get('summary', ''),
                        'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                # Process chapters
                soup = await self.__fetch_page(session, self.chapters)
                if not soup:
                    logger.error(f"Failed to fetch chapters page for {self.novelTitle}")
                    return
                
                total_pages = await self.__getTotalPages(session, soup)
                if total_pages == 0:
                    logger.error(f"No chapter pages found for {self.novelTitle}")
                    return
                
                logger.info(f"Found {total_pages} pages of chapters for {self.novelTitle}")
                
                all_chapter_args = []
                
                # Gather all chapter information
                tasks = []
                for page_num in range(1, total_pages + 1):
                    tasks.append(self.__process_page(session, page_num))
                
                results = await asyncio.gather(*tasks)
                for page_args in results:
                    all_chapter_args.extend(page_args)
                
                if not all_chapter_args:
                    logger.info(f"No new chapters found for {self.novelTitle}")
                    return
                
                logger.info(f"Found {len(all_chapter_args)} new chapters to download for {self.novelTitle}")
                
                # Process chapters in batches
                batch_size = 3  # Reduced batch size for more stability
                new_chapters_found = False
                
                for i in range(0, len(all_chapter_args), batch_size):
                    batch = all_chapter_args[i:i + batch_size]
                    batch_tasks = []
                    for link, num in batch:
                        batch_tasks.append(self.__process_chapter(session, link, num))
                    
                    await asyncio.gather(*batch_tasks)
                    
                    # Check if any new chapters were added
                    current_chapters = set(self.chapters_data.keys())
                    if current_chapters - existing_chapters:
                        new_chapters_found = True
                    
                    logger.info(f"Progress: {min(i + batch_size, len(all_chapter_args))}/{len(all_chapter_args)} chapters processed")
                
                # Update metadata only if new chapters were found
                if new_chapters_found:
                    logger.info(f"New chapters found for {self.novelTitle}, updating last_updated timestamp")
                    metadata['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                else:
                    logger.info(f"No new chapters were actually saved for {self.novelTitle}")
                
        except Exception as e:
            logger.error(f"Error in getChapters for {self.url}: {e}")

if __name__ == '__main__':
    start = time.time()
    links = [
        #'https://lightnovelpub.vip/novel/shadow-slave-05122222', #
        #"https://lightnovelpub.vip/novel/re-evolution-online-05122223", #
        #"https://lightnovelpub.vip/novel/return-of-the-mount-hua-sect-16091350", #
        #'https://lightnovelpub.vip/novel/the-beginning-after-the-end-web-novel-11110049',  #
        #'https://lightnovelpub.vip/novel/circle-of-inevitability-17122007', #
        #'https://lightnovelpub.vip/novel/damn-reincarnation-16091348', #
        #'https://lightnovelpub.vip/novel/a-regressors-tale-of-cultivation',
        #'https://lightnovelpub.vip/novel/overgeared-wn-16091311', #
        #'https://lightnovelpub.vip/novel/trash-count-wn-05122225', #
        #'https://lightnovelpub.vip/novel/the-legendary-mechanic-novel-05122221', #
        #'https://lightnovelpub.vip/novel/the-authors-pov-05122222', #
        #'https://lightnovelpub.vip/novel/advent-of-the-three-calamities', #
        #'https://lightnovelpub.vip/novel/lord-of-the-mysteries-wn-16091313', #
        #'https://lightnovelpub.vip/novel/the-world-after-the-fall-16091325', #
        #'https://lightnovelpub.vip/novel/orv-wn-16091308', #
        #'https://lightnovelpub.vip/novel/reverend-insanity-05122222', #
        #'https://lightnovelpub.vip/novel/the-novels-extra-05122223',
        #'https://lightnovelpub.vip/novel/the-first-order-16091316',
        #"https://lightnovelpub.vip/novel/renegade-immortal-05122225",
        "https://lightnovelpub.vip/novel/sword-god-in-a-world-of-magic-05122221"
    ]
    
    async def main():
        # Process novels sequentially to be more gentle with the server
        for link in links:
            try:
                logger.info(f"Starting to process: {link}")
                scraper = genChapters(link)
                await scraper.getChapters()
                # Add a delay between novels
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Failed to process {link}: {e}")
    
    asyncio.run(main())
    
    end = time.time()
    logger.success(f"Finished scraping all novels in {end - start:.2f} seconds")
