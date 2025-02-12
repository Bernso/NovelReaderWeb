import requests
from bs4 import BeautifulSoup
import os
import re
import urllib.parse
import json
import base64
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class NovelImageScraper:
    def __init__(self):
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        # Initialize Selenium driver
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Set up Chrome driver with appropriate options"""
        if self.driver is None:
            print("Setting up Chrome driver...")
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            for key, value in self.__headers.items():
                options.add_argument(f'{key}={value}')
            
            service = Service(ChromeDriverManager(driver_version="131.0.6778.109").install())
            self.driver = webdriver.Chrome(service=service, options=options)
    
    def cleanup_driver(self):
        """Clean up the Selenium driver"""
        if self.driver:
            print("Cleaning up Chrome driver...")
            self.driver.quit()
            self.driver = None
    
    def transform_title(self, novel_title: str) -> str:
        """Transform novel title for URL construction"""
        novel_title_cleaned = re.sub(r'\(.*?\)', '', novel_title)
        decoded_title = urllib.parse.unquote(novel_title_cleaned)
        transformed_title = decoded_title.lower()
        transformed_title = re.sub(r"[''']", "", transformed_title)
        transformed_title = transformed_title.replace(" ", "-")
        transformed_title = transformed_title.replace("é", "e")
        transformed_title = transformed_title.rstrip('- ')
        transformed_title = re.sub(r'[^a-zA-Z0-9\s-]', '', transformed_title)
        return transformed_title
    
    def __validDirName(self, name):
        name = re.sub(r"[''']", "'", name)
        name = name.replace(":", "")
        name = name.replace("/", "")
        return name
    
    def __get_base_url(self, novel_title: str) -> str:
        """Construct base URL from novel title"""
        return f"https://lightnovelpub.vip/novel/{self.transform_title(novel_title)}"
    
    def fetch_page(self, url: str) -> tuple:
        """Fetch page using Selenium and wait for image to load"""
        try:
            print(f"Fetching page: {url}")
            #self.setup_driver()
            self.driver.get(url)
            
            # Wait for either the fixed-img div or the cover figure
            wait = WebDriverWait(self.driver, 10)
            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'fixed-img')))
            except:
                try:
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'cover')))
                except:
                    print("Could not find image container")
                    return None, None
            
            # Wait a bit for the image to load
            time.sleep(2)
            
            # Get image URL and title
            try:
                # Try different selectors for the image
                img_elem = None
                for selector in ['div.fixed-img img', 'figure.cover img', 'div.cover img']:
                    try:
                        img_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if img_elem:
                            break
                    except:
                        continue
                
                if not img_elem:
                    print("Could not find image element")
                    return None, None
                
                # Try different attributes for the image URL
                image_url = None
                for attr in ['src', 'data-src']:
                    try:
                        image_url = img_elem.get_attribute(attr)
                        if image_url and not image_url.endswith('spinner.gif'):
                            break
                    except:
                        continue
                
                if not image_url:
                    print("Could not find valid image URL")
                    return None, None
                
                # Get title
                title_elem = self.driver.find_element(By.CLASS_NAME, 'novel-title')
                novel_title = title_elem.text if title_elem else None
                
                print(f"Found image URL: {image_url}")
                print(f"Found title: {novel_title}")
                
                return image_url, novel_title
                
            except Exception as e:
                print(f"Error extracting image and title: {e}")
                return None, None
                
        except Exception as e:
            print(f"Error fetching page {url}: {e}")
            return None, None
    
    def __download_image(self, image_url: str, novel_title: str, filename: str = "cover_image.jpg") -> bool:
        """Download and save image"""
        try:
            print(f"Attempting to download image from: {image_url}")
            
            # Create directory if it doesn't exist
            folder_name = self.__validDirName(novel_title)
            file_dir = f'templates/novels/{folder_name}-chapters'
            os.makedirs(file_dir, exist_ok=True)
            file_path = os.path.join(file_dir, filename)
            
            # Check if image already exists
            if os.path.exists(file_path):
                print(f"Image already exists at {file_path}")
                return True
            
            # Handle base64 encoded images
            if image_url.startswith('data:image'):
                try:
                    base64_data = image_url.split(',')[1]
                    image_data = base64.b64decode(base64_data)
                    with open(file_path, 'wb') as f:
                        f.write(image_data)
                    print(f"Successfully saved base64 image to {file_path}")
                    return True
                except Exception as e:
                    print(f"Error saving base64 image: {e}")
                    return False
            
            # Handle URL images
            print("Downloading image...")
            response = requests.get(image_url, headers=self.__headers, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"Successfully downloaded image to {file_path}")
            return True
        
        except Exception as e:
            print(f"Error downloading image: {e}")
            return False
    
    def __scrape_novel_image(self, url: str = None, novel_title: str = None) -> bool:
        """Main function to scrape novel image"""
        try:
            if novel_title and not url:
                url = self.__get_base_url(novel_title)
            
            print(f"\nStarting image scraping for: {url}")
            
            # Fetch page and extract image URL and title
            image_url, page_title = self.fetch_page(url)
            if not image_url:
                print("Could not find image URL")
                return False
            
            # Use the found title if none was provided
            if not novel_title:
                novel_title = page_title
            
            print(f"Found novel title: {novel_title}")
            
            # Download the image
            success = self.__download_image(image_url, novel_title)
            
            return success
        
        except Exception as e:
            print(f"Error in main scraping process: {e}")
            return False
        
        #finally:
        #    self.cleanup_driver()


if __name__ == "__main__":
    scraper = NovelImageScraper()
    links = [
            'https://lightnovelpub.vip/novel/shadow-slave-05122222',
            "https://lightnovelpub.vip/novel/return-of-the-mount-hua-sect-16091350",
            'https://lightnovelpub.vip/novel/the-beginning-after-the-end-web-novel-11110049', 
            'https://lightnovelpub.vip/novel/circle-of-inevitability-17122007', 
            'https://lightnovelpub.vip/novel/damn-reincarnation-16091348',
            'https://lightnovelpub.vip/novel/return-of-the-mount-hua-sect-16091350'
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
    # Example usage with URL
        success = scraper._NovelImageScraper__scrape_novel_image(url=link)
    scraper.cleanup_driver()
    
    #if not success:
    #    print("\nRetrying with different URL format...")
    #    # Try alternate URL format
    #    success = scraper._NovelImageScraper__scrape_novel_image(novel_title="Advent of the Three Calamities")