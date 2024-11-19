import requests
from bs4 import BeautifulSoup
import os
#import threading
import urllib
import re


class genChapters:
    def __init__(self, url='https://lightnovelpub.vip/novel/damn-reincarnation-16091348'):
        self.url = url
        self.chapters = f'{self.url}/chapters'
        self.__headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        self.novelTitle = self.__getNovelTitle()
    
    def __str__(self):
        return "A webscraper for light novel pub vip"
    
    def __transformTitle(self, novel_title: str) -> str:
        decoded_title = urllib.parse.unquote(novel_title)
        transformed_title = decoded_title.lower()
        transformed_title = re.sub(r"[’'’]", "", transformed_title)  # Remove special apostrophes
        transformed_title = re.sub(r'[^a-zA-Z0-9\s]', '', transformed_title)  # Remove non-alphanumeric characters
        transformed_title = transformed_title.replace(" ", "-")
        transformed_title = transformed_title.replace(":", "")
        transformed_title = transformed_title.replace("/", "")  # Remove slashes
        return transformed_title
    
    def __validDirName(self, name):
        name = re.sub(r"[’'’]", "'", name)  # Replace special apostrophes with single quote
        name = name.replace(":", "")  # Remove colons
        name = name.replace("/", "")  # Remove slashes
        return name
    
    def __scrapeCategories(self):
        try:
            response = requests.get(self.url, headers=self.__headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            categories_div = soup.find('div', class_='categories')
            if categories_div is None:
                print("No 'div' with class 'categories' found.")
                return []

            ul = categories_div.find('ul')
            if ul is None:
                print("No 'ul' found inside the 'div.categories'.")
                return []

            list_items = ul.find_all('li')
            categories = [item.get_text(strip=True) for item in list_items]

            return categories

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return []
        except Exception as e:
            print(f"Error scraping categories: {e}")
            return []
    
    def __getNovelTitle(self):
        try:
            response = requests.get(self.url, headers=self.__headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            novel_title = soup.find('h1', class_='novel-title text2row').get_text().strip()

            return novel_title

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def __getTotalPages(self, thesoup):
        try:
            aLink = thesoup.find('li', class_='PagedList-skipToLast')
            if aLink:
                fullLink = f'https://lightnovelpub.vip{aLink.find('a')['href']}'
                page_number = fullLink.split('=')[-1]
                return int(page_number)
            return None
        except Exception as e:
            input(e)
    
    def __scrapeChapter(self, link, num):
        try:
            folder_name = self.__validDirName(self.__getNovelTitle())
            file_dir = f'templates/novels/{folder_name}-chapters'
            num = str(num)
            num = num.replace('.', '-')
            file_path = os.path.join(file_dir, f'chapter-{num}.txt')

            
            response = requests.get(link, headers=self.__headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            chapter_container = soup.find('div', id='chapter-container')
            if chapter_container:
                chapter_text = chapter_container.get_text(separator='\n').strip()

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(chapter_text.replace('\n', '<br><br>'))

                print(f"TXT file created successfully\n")

            else:
                print("Error: 'chapter-container' not found on the page.")
        
        except Exception as e:
            input(e)
        
    def getChapters(self):
        try:
            response = requests.get(self.chapters, headers=self.__headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            pages = self.__getTotalPages(soup)
            print(pages)
            
            for i in range(pages):
                response = requests.get(f'{self.chapters}?page={i+1}', headers=self.__headers) # i+1 because of 0 indexing
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                chapter_list = soup.find('ul', class_='chapter-list')
                if chapter_list:
                    chapters = chapter_list.find_all('a')
                    for chapter in chapters:
                        chapterLink = chapter['href']
                        chapter_part = chapterLink.split('/')[-1]
                        # Remove 8 digits at end
                        if chapter_part[-8:].isdigit():
                            chapter_part = chapter_part[:-9] 
                        
                        chapter_part = chapter_part.replace('chapter-', '')
                        
                        chapterLinkNum = chapter_part.replace('-', '.')
                        chapterLink = f"https://lightnovelpub.vip{chapterLink}"
                        print(f"Chapter link:   {chapterLink}")
                        print(f"Chapter Number: {chapterLinkNum}")
                        self.__scrapeChapter(chapterLink, chapterLinkNum)
                else:
                    print("No chapter list found")
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return []
        except Exception as e:
            print(f"Error scraping categories: {e}")
            return []

scraper = genChapters()#'https://lightnovelpub.vip/novel/shadow-slave-05122222')
scraper.getChapters()