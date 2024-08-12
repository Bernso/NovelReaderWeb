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
def scrape_categories(base_url: str):
    """
    Scrape the categories of a web novel from its main page.

    Parameters:
    base_url (str): The URL of the web novel's main page.

    Returns:
    List[str]: A list of categories found on the web novel's main page.
    If the request fails or the required elements are not found, returns an empty list.
    """
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the <span> element with the class 'detail-content'
        detail_content_span = soup.find('span', class_='detail-content')
        if detail_content_span is None:
            print("No <span> with class 'detail-content' found.")
            return []

        # Find all 'a' tags within the 'detail-content' span
        a_tags = detail_content_span.find_all('a')
        if not a_tags:
            print("No <a> tags found within the 'detail-content' span.")
            return []

        categories = [a.get_text(strip=True) for a in a_tags]

        return categories

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []
    except Exception as e:
        print(f"Error scraping categories: {e}")
        return []




# Function to get the latest chapter number
def get_latest_chapter_number(base_url: str):
    """
    This function retrieves the latest chapter number and chapter links from a web novel's main page.

    Parameters:
    base_url (str): The URL of the web novel's main page.

    Returns:
    Tuple[Optional[int], List[str]]: A tuple containing the latest chapter number (as an integer) and a list of chapter links.
    If the request fails or the required elements are not found, returns (None, []).
    """
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        listOfChapters = soup.find('section', class_='wp-show-posts-columns wp-show-posts')

        if listOfChapters is None:
            print("No 'section' with class 'wp-show-posts-columns wp-show-posts' found.")
            return None, []

        # Find all <a> elements inside the <section>
        li_elements = listOfChapters.find_all('a')
        if not li_elements:
            print("No 'a' elements found inside the 'section'.")
            return None, []

        # Extract the text and href from each <a> inside the <li> elements
        chapter_texts = [a.get_text(strip=True) for a in li_elements]
        chapter_links = [a['href'] for a in li_elements]

        print(f"There are {len(chapter_texts)} chapters")
        latestChapterNumber = len(chapter_texts)
        return latestChapterNumber, chapter_links

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None, []




# Function to get the novel title
def get_novel_title(base_url: str) -> str:
    """
    This function retrieves the title of a web novel from its main page URL.

    Parameters:
    base_url (str): The URL of the web novel's main page.

    Returns:
    str: The title of the web novel. If the request fails or the title is not found, returns None.
    """
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        novel_title = soup.find('h1', class_='product_title entry-title elementor-heading-title elementor-size-default').get_text().strip()

        return novel_title

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


# Function to fetch and save chapter content
def main(url: str, novel_title: str) -> None:
    """
    This function fetches and saves a web novel chapter content to a local file.
    It also checks if the chapter has already been downloaded before saving it.

    Parameters:
    url (str): The URL of the web novel chapter page.
    novel_title (str): The title of the web novel.

    Returns:
    None
    """
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




    file_path = os.path.join(file_dir, f'chapter-{chapterNumber}.txt')

    # Check if the file already exists
    if os.path.exists(file_path):
        print(f"Chapter {chapterNumber} already downloaded. Skipping...")
        return

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        chapter_container = soup.find('div', class_='smart_content_wrapper')
        if chapter_container:
            chapter_text = chapter_container.get_text(separator='\n').strip()

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(chapter_text.replace('\n', '<br><br>').replace('\\', ''))

            print(f"TXT file created successfully for * {novel_title} * chapter * {chapterNumber} *")

        else:
            print("Error: 'chapter-container' not found on the page.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")




# Function to iterate over all chapters and save them
def yes(base_url: str) -> None:
    """
    This function is responsible for scraping a web novel website, saving the novel's title, categories, 
    and chapters to local files. It also creates a directory for the novel's chapters.

    Parameters:
    base_url (str): The URL of the web novel's main page.

    Returns:
    None
    """

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

        readWebNovel = os.path.join(file_dir, 'readWebNovel.txt')

        with open(readWebNovel, 'w') as f:
            f.write('readWebNovel')
            print(f"Certification saved to {readWebNovel}")
    else:
        print("Failed to scrape categories. Skipping...")



    latest_chapter_number, chapterLinks = get_latest_chapter_number(base_url)
    if latest_chapter_number is None:
        print("Failed to get the latest chapter number.")
        return

    print(f"First chapter: {chapterLinks[0]}")


    for Link in chapterLinks:
        main(url=Link, novel_title=novel_title)
    print(f"Finished scraping * {novel_title} *")





# Example usage
if __name__ == '__main__':
    base_url = 'https://read-webnovel.com/novels/i-can-copy-and-evolve-talents/'
    yes(base_url)
