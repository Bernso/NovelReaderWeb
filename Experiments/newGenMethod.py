import requests
from bs4 import BeautifulSoup
import os
import re
import threading

# Define headers to mimic browser requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Function to scrape categories and save them to a file
def scrape_categories(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    categories_div = soup.find('div', class_='categories')
    if categories_div is None:
        print("No 'div' with class 'categories' found.")
        return

    ul = categories_div.find('ul')
    if ul is None:
        print("No 'ul' found inside the 'div.categories'.")
        return

    list_items = ul.find_all('li')
    with open('categories.txt', 'w') as file:
        for item in list_items:
            text = item.get_text(strip=True)
            file.write(text + '\n')

    print("Categories content saved to categories.txt")

# Function to get the latest chapter number
def get_latest_chapter_number(base_url):
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        header_stats_div = soup.find('div', class_='header-stats')

        if header_stats_div:
            span_tags = header_stats_div.find_all('span')
            for span in span_tags:
                strong_tag = span.find('strong')
                if strong_tag:
                    text = strong_tag.get_text(strip=True)
                    value = ''.join(filter(str.isdigit, text))
                    print(f'Extracted value: {value}')
                    return value

        print('Div with class "header-stats" not found.')
        return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Function to get the novel title
def get_novel_title(base_url):
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        novel_title = soup.find('h1', class_='novel-title text2row').get_text().strip()
        return novel_title

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Function to fetch and save chapter content
def main(url, chapter_number, novel_title):
    file_path = f'templates/novels/{novel_title}-chapters/chapter-{chapter_number}.txt'

    if os.path.exists(file_path):
        print(f"Chapter {chapter_number} already exists. Skipping...")
        return

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        chapter_container = soup.find('div', id='chapter-container')
        if chapter_container:
            chapter_text = chapter_container.get_text(separator='\n').strip()

            os.makedirs(f'templates/novels/{novel_title}-chapters', exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(chapter_text.replace('\n', '<br><br>'))

            print(f"HTML file created successfully for {novel_title} chapter {chapter_number}")

        else:
            print("Error: 'chapter-container' not found on the page.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# Function to iterate over all chapters and save them
def yes(base_url):
    def thread_target():
        categories = scrape_categories(base_url)
        latest_chapter_number = get_latest_chapter_number(base_url)
        novel_title = get_novel_title(base_url)

        if latest_chapter_number is None:
            print("Failed to get the latest chapter number.")
            return

        print(f"Latest chapter number: {latest_chapter_number}")

        for i in range(1, int(latest_chapter_number) + 1):
            main(url=f"{base_url}/chapter-{i}", chapter_number=i, novel_title=novel_title)

    thread = threading.Thread(target=thread_target)
    thread.start()



# Example usage
if __name__ == '__main__':
    base_url = 'https://lightnovelpub.vip/novel/the-beginning-after-the-end-web-novel-11110049'
    
    yes(base_url)
