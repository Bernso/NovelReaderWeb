import requests
from bs4 import BeautifulSoup
import os
#import threading
import urllib
import re

# Define headers to mimic browser requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Function to transform the novel title for URL
def transform_title(novel_title: str) -> str:
    """
    This function transforms a novel title into a valid filename by decoding it, converting it to lowercase,
    removing special apostrophes, non-alphanumeric characters, spaces, colons, and slashes.

    Parameters:
    novel_title (str): The original novel title.

    Returns:
    str: The transformed novel title suitable for use as a filename.
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
    This function is used to transform a novel title into a valid directory name by removing special characters,
    colons, and slashes.

    Parameters:
    novel_title (str): The original novel title.

    Returns:
    str: The transformed novel title suitable for use as a directory name.
    """
    novel_title = re.sub(r"[’'’]", "'", novel_title)  # Replace special apostrophes with single quote
    novel_title = novel_title.replace(":", "")  # Remove colons
    novel_title = novel_title.replace("/", "")  # Remove slashes
    return novel_title






# Function to scrape categories
def scrape_categories(base_url: str) -> list:
    """
    This function scrapes the categories from a given base URL. It sends a GET request to the URL,
    parses the HTML content using BeautifulSoup, and extracts the categories from the 'div' with class 'categories'.

    Parameters:
    base_url (str): The base URL of the website from which to scrape the categories.

    Returns:
    list: A list of categories extracted from the website. If the 'div' with class 'categories' or 'ul' inside it is not found,
    or if any exceptions occur during the request or parsing, an empty list is returned.
    """
    try:
        response = requests.get(base_url, headers=headers)
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


# Function to get the latest chapter number
def get_latest_chapter_number(base_url: str) -> str:
    """
    This function retrieves the latest chapter number from a given base URL.
    It sends a GET request to the URL, parses the HTML content using BeautifulSoup,
    and extracts the latest chapter number from the 'div' with class 'header-stats'.

    Parameters:
    base_url (str): The base URL of the novel's website.

    Returns:
    str: The latest chapter number as a string. If the request fails or the latest chapter number is not found, returns None.
    """
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
def get_novel_title(base_url: str) -> str:
    """
    This function retrieves the novel title from the given base URL.
    It sends a GET request to the URL, parses the HTML content using BeautifulSoup,
    and extracts the novel title from the 'h1' tag with the class 'novel-title text2row'.

    Parameters:
    base_url (str): The base URL of the novel's website.

    Returns:
    str: The novel title. If the request fails or the title is not found, returns None.
    """
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
def main(url: str, chapter_number: int, novel_title: str) -> None:
    """
    This function fetches and saves a novel chapter content from a given URL.
    It creates a directory for the novel if it doesn't exist, checks if the chapter has already been downloaded,
    and saves the chapter content into a text file.

    Parameters:
    url (str): The URL of the novel chapter.
    chapter_number (int): The number of the novel chapter.
    novel_title (str): The title of the novel.

    Returns:
    None
    """
    folder_name = valid_dir_name(novel_title)
    file_dir = f'templates/novels/{folder_name}-chapters'
    os.makedirs(file_dir, exist_ok=True)
    file_path = os.path.join(file_dir, f'chapter-{chapter_number}.txt')

    # Check if the file already exists
    if os.path.exists(file_path):
        print(f"Chapter {chapter_number} already downloaded. Skipping...")
        return

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        chapter_container = soup.find('div', id='chapter-container')
        if chapter_container:
            chapter_text = chapter_container.get_text(separator='\n').strip()

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(chapter_text.replace('\n', '<br><br>'))

            print(f"TXT file created successfully for * {novel_title} * chapter * {chapter_number} *")

        else:
            print("Error: 'chapter-container' not found on the page.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")


# Function to iterate over all chapters and save them
def yes(base_url: str) -> None:
    """
    This function is responsible for scraping a novel's information and chapters from a given base URL.
    It retrieves the novel's title, categories, and the latest chapter number.
    Then, it iterates over all chapters and saves them into separate text files.

    Parameters:
    base_url (str): The base URL of the novel's website.

    Returns:
    None
    """
    #def thread_target():

    novel_title = get_novel_title(base_url)
    categories = scrape_categories(base_url)

    if categories:
        folder_name = valid_dir_name(novel_title)
        file_dir = f'templates/novels/{folder_name}-chapters'
        os.makedirs(file_dir, exist_ok=True)

        categories_path = os.path.join(file_dir, 'categories.txt')

        with open(categories_path, 'w') as f:
            f.write('\n'.join(categories))
            print(f"Categories saved to {categories_path}")
    else:            print("Failed to scrape categories. Skipping...")

    latest_chapter_number = get_latest_chapter_number(base_url)
    if latest_chapter_number is None:
        print("Failed to get the latest chapter number.")
        return

    print(f"Latest chapter number: {latest_chapter_number}")

    for i in range(1, int(latest_chapter_number) + 1):
        main(url=f"{base_url}/chapter-{i}", chapter_number=i, novel_title=novel_title)
    print(f"Finished scraping * {novel_title} *")


    #thread = threading.Thread(target=thread_target)
    #thread.start()

# Example usage
if __name__ == '__main__':
    base_url = 'https://lightnovelpub.vip/novel/atticuss-odyssey-reincarnated-into-a-playground'
    yes(base_url)
