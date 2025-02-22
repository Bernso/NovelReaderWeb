import requests
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor
import urllib
import re
from functools import lru_cache
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # This may be flagged as not imported but it will work, dw
import json
import threading
import time

class genChapters:
    def __init__(self, url='https://lightnovelpub.vip/novel/shadow-slave-05122222'):
        self.url = url
        self.chapters = f'{self.url}/chapters'
        self.__headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update(self.__headers)
        
        # Initialize novel info
        self.novel_info = self.__get_novel_info()
        self.novelTitle = self.novel_info['title']
        
        # Initialize chapters dictionary to store in memory
        self.chapters_data = {}
        self.chapters_lock = threading.Lock()

    def __str__(self):
        return "A webscraper for light novel pub vip"
    
    def __transformTitle(self, novel_title: str) -> str:
        decoded_title = urllib.parse.unquote(novel_title)
        transformed_title = decoded_title.lower()
        transformed_title = re.sub(r"[''']", "", transformed_title)
        transformed_title = re.sub(r'[^a-zA-Z0-9\s]', '', transformed_title)
        transformed_title = transformed_title.replace(" ", "-")
        transformed_title = transformed_title.replace(":", "")
        transformed_title = transformed_title.replace("/", "")
        return transformed_title
    
    def __validDirName(self, name):
        name = re.sub(r"[''']", "'", name)
        name = name.replace(":", "")
        name = name.replace("/", "")
        return name
    
    @lru_cache(maxsize=32)
    def __fetch_page(self, url: str) -> BeautifulSoup:
        """Cached function to fetch and parse a webpage with a 3-second timeout.
           If a timeout occurs, the request will be retried up to 3 times."""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = self.session.get(url, timeout=3)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.exceptions.Timeout:
                print(f"Timeout fetching page {url}. Retrying {attempt+1}/{max_attempts}...")
                time.sleep(1)  # Optional backoff delay before retrying
            except Exception as e:
                print(f"Error fetching page {url}: {e}")
                return None
        print(f"Failed to fetch page {url} after {max_attempts} attempts due to timeout.")
        return None
    
    def __get_novel_info(self):
        """Combined function to get novel title, categories in a single request"""
        soup = self.__fetch_page(self.url)
        if not soup:
            return {'title': None, 'categories': []}
        
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
        
        return info
    
    def __getTotalPages(self, thesoup):
        try:
            current_page = 1
            while True:
                # Find the "Next" button
                next_button = thesoup.find('li', class_='PagedList-skipToNext')
                if not next_button or not next_button.find('a'):
                    # If there's no next button, we're on the last page
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
                        return max_page
                    
                    # If we can't find pagination div but have chapters, assume it's single page
                    chapter_list = thesoup.find('ul', class_='chapter-list')
                    if chapter_list and chapter_list.find_all('li'):
                        return current_page
                    
                    print("No chapters found on the page")
                    return 0
                
                # Get the next page URL and fetch it
                next_url = f"https://lightnovelpub.vip{next_button.find('a')['href']}"
                thesoup = self.__fetch_page(next_url)
                if not thesoup:
                    return current_page
                
                current_page += 1
                print(f"Scanning page {current_page}...")
            
        except Exception as e:
            print(f"Error getting total pages: {e}")
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
            print(f"Warning: Invalid chapter number format: {chapter_num}")
            return False

    def __process_chapter(self, args):
        """Process a single chapter in parallel"""
        link, num = args
        try:
            folder_name = self.__validDirName(self.novelTitle)
            file_dir = f'templates/novels/{folder_name}-chapters'
            os.makedirs(file_dir, exist_ok=True)
            
            num = str(num).replace('.', '-')
            chapter_num = num.replace('-', '.')
            
            # Skip if chapter already exists in memory
            with self.chapters_lock:
                if chapter_num in self.chapters_data:
                    print(f"Chapter {chapter_num} already exists in memory, skipping...")
                    return
            
            soup = self.__fetch_page(link)
            if not soup:
                return
            
            chapter_container = soup.find('div', id='chapter-container')
            if chapter_container:
                chapter_text = chapter_container.get_text(separator='\n').strip()
                
                # Store chapter in memory with thread safety
                with self.chapters_lock:
                    self.chapters_data[chapter_num] = chapter_text.replace('\n', '\n\n')
                    # Write to JSON file after each chapter to prevent data loss
                    json_path = os.path.join(file_dir, 'chapters.json')
                    try:
                        # First read existing data
                        existing_data = {}
                        if os.path.exists(json_path):
                            with open(json_path, 'r', encoding='utf-8') as f:
                                try:
                                    existing_data = json.load(f)
                                except json.JSONDecodeError:
                                    print(f"Error reading JSON for chapter {chapter_num}, starting fresh")
                        
                        # Update with new chapter
                        existing_data[chapter_num] = chapter_text.replace('\n', '\n\n')
                        
                        # Write back to file
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump(existing_data, f, ensure_ascii=False, indent=2)
                        
                        print(f"Chapter {chapter_num} downloaded and saved successfully")
                    except Exception as e:
                        print(f"Error saving chapter {chapter_num} to JSON: {e}")
            else:
                print(f"Error: content not found for chapter {num}")
        
        except Exception as e:
            print(f"Error processing chapter {num}: {e}")

    def __process_page(self, page_num):
        """Process all chapters in a single page"""
        url = f'{self.chapters}?page={page_num}'
        soup = self.__fetch_page(url)
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
            
            # Check for existing text files
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
                    print(f"Skipping chapter with invalid number format: {chapterLinkNum}")
                    continue

                # Skip if chapter already exists
                if chapterLinkNum in existing_chapters:
                    print(f"Chapter {chapterLinkNum} already exists, skipping...")
                    continue
                
                chapterLink = f"https://lightnovelpub.vip{chapterLink}"
                chapter_args.append((chapterLink, chapterLinkNum))
        
        return chapter_args
    
    def getChapters(self, retry_chapters=None):
        try:
            # Save categories
            folder_name = self.__validDirName(self.novelTitle)
            file_dir = f'templates/novels/{folder_name}-chapters'
            os.makedirs(file_dir, exist_ok=True)
            
            # Load existing JSON data if it exists
            json_path = os.path.join(file_dir, 'chapters.json')
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    try:
                        self.chapters_data = json.load(f)
                        print(f"Loaded {len(self.chapters_data)} existing chapters from JSON")
                    except json.JSONDecodeError:
                        print("Error reading existing JSON file, starting fresh")
                        self.chapters_data = {}
            
            # If we're retrying specific chapters, skip categories and page scanning
            if retry_chapters is None:
                categories_path = os.path.join(file_dir, 'categories.txt')
                with open(categories_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(self.novel_info['categories']))
                
                # Get total pages
                soup = self.__fetch_page(self.chapters)
                if not soup:
                    return
                
                total_pages = self.__getTotalPages(soup)
                print(f"Total pages: {total_pages}")
                
                # Process pages sequentially to maintain chapter order
                all_chapter_args = []
                for page_num in range(1, total_pages + 1):
                    print(f"Processing page {page_num}/{total_pages}")
                    page_args = self.__process_page(page_num)
                    all_chapter_args.extend(page_args)
            else:
                # If retrying specific chapters, only process those
                print(f"Retrying download of {len(retry_chapters)} missing chapters...")
                all_chapter_args = []
                soup = self.__fetch_page(self.chapters)
                if not soup:
                    return
                
                # Find the links for missing chapters
                chapter_list = soup.find('ul', class_='chapter-list')
                if chapter_list:
                    chapters = chapter_list.find_all('a')
                    for chapter in chapters:
                        chapterLink = chapter['href']
                        chapter_part = chapterLink.split('/')[-1]
                        if chapter_part[-8:].isdigit():
                            chapter_part = chapter_part[:-9]
                        
                        chapter_part = chapter_part.replace('chapter-', '')
                        chapterLinkNum = chapter_part.replace('-', '.')
                        
                        if chapterLinkNum in retry_chapters:
                            chapterLink = f"https://lightnovelpub.vip{chapterLink}"
                            all_chapter_args.append((chapterLink, chapterLinkNum))
            
            print(f"\nDownloading {len(all_chapter_args)} chapters...")
            
            # Process chapters in smaller batches to maintain order
            batch_size = 5
            for i in range(0, len(all_chapter_args), batch_size):
                batch = all_chapter_args[i:i + batch_size]
                with ThreadPoolExecutor(max_workers=5) as executor:
                    list(executor.map(self.__process_chapter, batch))
                print(f"Progress: {min(i + batch_size, len(all_chapter_args))}/{len(all_chapter_args)} chapters processed")
            
            # Verify all chapters were scraped correctly
            expected_chapters = set(str(arg[1]) for arg in all_chapter_args)
            scraped_chapters = set(self.chapters_data.keys())
            
            missing_chapters = expected_chapters - scraped_chapters
            if missing_chapters:
                print("\nWARNING: Some chapters are still missing:")
                for chapter in sorted(missing_chapters, key=lambda x: float(x)):
                    print(f"- Chapter {chapter}")
                if retry_chapters is None:
                    print("Retrying missing chapters only...")
                    self.getChapters(retry_chapters=missing_chapters)
                else:
                    print("Failed to download some chapters after retry, manual intervention may be needed")
            else:
                print("\nVerification complete: All chapters were successfully scraped!")
            
        except Exception as e:
            print(f"Error in getChapters: {e}")

if __name__ == '__main__':
    start = time.time()
    links = [
        'https://lightnovelpub.vip/novel/vampires-slice-of-life-16091320',
        'https://lightnovelpub.vip/novel/shadow-slave-05122222',
        "https://lightnovelpub.vip/novel/return-of-the-mount-hua-sect-16091350",
        'https://lightnovelpub.vip/novel/the-beginning-after-the-end-web-novel-11110049', 
        'https://lightnovelpub.vip/novel/circle-of-inevitability-17122007', 
        'https://lightnovelpub.vip/novel/damn-reincarnation-16091348',
        'https://lightnovelpub.vip/novel/return-of-the-mount-hua-sect-16091350',
        'https://lightnovelpub.vip/novel/a-regressors-tale-of-cultivation',
        'https://lightnovelpub.vip/novel/overgeared-wn-16091311',
        'https://lightnovelpub.vip/novel/trash-count-wn-05122225',
        'https://lightnovelpub.vip/novel/the-legendary-mechanic-novel-05122221',
        'https://lightnovelpub.vip/novel/the-authors-pov-05122222',
        'https://lightnovelpub.vip/novel/advent-of-the-three-calamities',
        'https://lightnovelpub.vip/novel/lord-of-the-mysteries-wn-16091313',
        'https://lightnovelpub.vip/novel/the-world-after-the-fall-16091325',
        'https://lightnovelpub.vip/novel/orv-wn-16091308',
        'https://lightnovelpub.vip/novel/reverend-insanity-05122222',
        'https://lightnovelpub.vip/novel/the-novels-extra-05122223',
    ]
    for link in links:
        scraper = genChapters(link)
        scraper.getChapters()
    
    end = time.time()

    print(f"Finished scraping all novel in {end - start:.2f} seconds")
