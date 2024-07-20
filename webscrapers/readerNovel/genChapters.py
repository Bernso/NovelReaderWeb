try:
    import requests
    from bs4 import BeautifulSoup
    import os
    #import threading
    import urllib
    import re
except ImportError as e:
    input(f"Module not found: {e}")

# Define headers to mimic browser requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Function to transform the novel title for URL
def transform_title(novel_title: str) -> str:
    """
    Transform the novel title for URL:
    1. Decode URL-encoded characters.
    2. Convert to lowercase.
    3. Replace special characters and spaces with hyphens.

    Parameters:
    novel_title (str): The original novel title.

    Returns:
    str: The transformed novel title suitable for URL.
    """
    decoded_title = urllib.parse.unquote(novel_title)
    transformed_title = decoded_title.lower()
    transformed_title = re.sub(r"[’'’]", "", transformed_title)  # Remove special apostrophes
    transformed_title = re.sub(r'[^a-zA-Z0-9\s]', '', transformed_title)  # Remove non-alphanumeric characters
    transformed_title = transformed_title.replace(" ", "-")
    transformed_title = transformed_title.replace(":", "")
    transformed_title = transformed_title.replace("/", "")  # Remove slashes
    return transformed_title



def valid_dir_name(novel_title: str) -> str:
    """
    Prepare a valid directory name by removing special characters and replacing spaces with hyphens.

    Parameters:
    novel_title (str): The original novel title.

    Returns:
    str: The transformed novel title suitable for creating a directory.
    """
    novel_title = re.sub(r"[’'’]", "'", novel_title)  # Replace special apostrophes with single quote
    novel_title = novel_title.replace(":", "")  # Remove colons
    novel_title = novel_title.replace("/", "")  # Remove slashes
    return novel_title




# Function to scrape categories
def scrape_categories(base_url):
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the <strong> element with the text "Genre(s)"
        genre_strong = soup.find('strong', string='Genre(s) :')
        if genre_strong is None:
            print("No <strong> with text 'Genre(s)' found.")
            return []

        # Find the parent or relevant container that holds the genres
        categories_container = genre_strong.find_parent('li')
        if categories_container is None:
            print("No parent 'li' containing the genres found.")
            return []

        # Find all 'a' tags within the container to extract the genre names
        li = categories_container.find_all('a')
        if not li:
            print("No categories found within the container.")
            return []

        categories = [item.get_text(strip=True) for item in li]

        return categories

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []
    except Exception as e:
        print(f"Error scraping categories: {e}")
        return []

# Function to get the latest chapter number
def get_latest_chapter_number(base_url):
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        listOfChapters = soup.find('ul', class_='list-unstyled rounded-sketch-4')

        if listOfChapters is None:
            print("No 'ul' with class 'list-unstyled rounded-sketch-4' found.")
            return None

        # Find all <li> elements inside the <ul>
        li_elements = listOfChapters.find_all('li')
        if not li_elements:
            print("No 'li' elements found inside the 'ul'.")
            return None

        # Extract the text and href from each <a> inside the <li> elements
        chapter_texts = []
        chapter_links = []
        for li in li_elements:
            a_tag = li.find('a')
            if a_tag:
                chapter_texts.append(a_tag.get_text(strip=True))
                chapter_links.append(f"https://www.readernovel.net{a_tag['href']}")

        print(f"There are {len(chapter_texts)} chapters")
        latestChapterNumber = len(chapter_texts)
        return latestChapterNumber, chapter_links

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None



# Function to get the novel title
def get_novel_title(base_url):
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        novel_title = soup.find('h1', class_='page-title pt-2 mb-3').get_text().strip()

        return novel_title

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Function to fetch and save chapter content
def main(url, novel_title):
    folder_name = valid_dir_name(novel_title)
    file_dir = f'templates/novels/{folder_name}-chapters'
    os.makedirs(file_dir, exist_ok=True)
    
    chapterNumberTemp = url[-5:]
    chapterNumber = ''
    for number in chapterNumberTemp:
        if number == '.':
            chapterNumber += '-'
        
        elif number.isnumeric():
            chapterNumber += number
        
        else:
            print("Hi there!")

    
    file_path = os.path.join(file_dir, f'chapter-{chapterNumber}.txt')

    # Check if the file already exists
    if os.path.exists(file_path):
        print(f"Chapter {chapterNumber} already downloaded. Skipping...")
        return

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        chapter_container = soup.find('div', id='chapter-container')
        if chapter_container:
            chapter_text = chapter_container.get_text(separator='\n').strip()

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(chapter_text.replace('\n', '<br>'))

            print(f"TXT file created successfully for * {novel_title} * chapter * {chapterNumber} *")

        else:
            print("Error: 'chapter-container' not found on the page.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")



# Function to iterate over all chapters and save them
def yes(base_url):
    
    base_url_temp = base_url[-5:]
    print(base_url_temp)
    base_url_number = ''
    for number in base_url_temp:
        if number.isdigit():
            print(int(number))
            base_url_number += number

    print(base_url_number)    
    
    
    #def thread_target():
        
    novel_title = get_novel_title(base_url)
    print(novel_title)
    
    categories = scrape_categories(base_url)
    print(categories)

    if categories:
        folder_name = valid_dir_name(novel_title)
        file_dir = f'templates/novels/{folder_name}-chapters'
        os.makedirs(file_dir, exist_ok=True)

        categories_path = os.path.join(file_dir, 'categories.txt')

        with open(categories_path, 'w') as f:
            f.write('\n'.join(categories))
            print(f"Categories saved to {categories_path}")
    else:
        print("Failed to scrape categories. Skipping...")
    
    if base_url_number:
        os.makedirs(file_dir, exist_ok=True)
        base_url_number_path = os.path.join(file_dir, 'base_url_number.txt')
        
        with open(base_url_number_path, 'w') as f:
            f.write(base_url_number)
            print(f"Base URL Number saved to {base_url_number_path}")
    else:
        print("Failed to get the base URL number. Skipping...")
    
    
    latest_chapter_number, chapterLinks = get_latest_chapter_number(base_url)
    if latest_chapter_number is None:
        print("Failed to get the latest chapter number.")
        return
    chapterLinksSorted = chapterLinks[::-1]
    print(f"Latest chapter number: {latest_chapter_number}")

    print(chapterLinksSorted[0])


    for Link in chapterLinksSorted:
        main(url=Link, novel_title=novel_title)
    print(f"Finished scraping * {novel_title} *")

    #thread = threading.Thread(target=thread_target)
    #thread.start()

# Example usage
if __name__ == '__main__':
    base_url = 'https://www.readernovel.net/novel/deep-sea-embers-4055/'
    yes(base_url)
