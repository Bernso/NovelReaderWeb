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





def capitalize_first_letter_of_each_word(input_string):
    """
    Capitalizes the first letter of each word in the input string.

    Parameters:
    input_string (str): The input string where each word's first letter needs to be capitalized.

    Returns:
    str: The input string with the first letter of each word capitalized.
    """
    return ' '.join(word.capitalize() for word in input_string.split())




# Function to scrape categories
def scrape_categories(base_url: str) -> list:
    """
    Scrape the categories of a novel from the given base URL.

    Parameters:
    base_url (str): The URL of the novel's main page.

    Returns:
    list: A list of categories extracted from the webpage. If any error occurs during scraping, an empty list is returned.
    """
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the <div> element with the class 'm-tags'
        detail_content_div = soup.find('div', class_='m-tags')
        if detail_content_div is None:
            print("No <div> with class 'm-tags' found.")
            return []

        # Find all 'a' tags within the 'detail-content' div
        a_tags = detail_content_div.find_all('a')
        if not a_tags:
            print("No <a> tags found within the 'detail-content' div.")
            return []

        # Extract, clean, and capitalize the categories
        categories = [capitalize_first_letter_of_each_word(a.get_text(strip=True)[2:]) for a in a_tags]

        return categories

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []
    except Exception as e:
        print(f"Error scraping categories: {e}")
        return []




# Function to get the latest chapter number
def get_latest_chapter_number(base_url: str) -> tuple:
    """
    This function retrieves the latest chapter number and a list of chapter links from a given base URL.

    Parameters:
    base_url (str): The base URL of the novel's main page.

    Returns:
    tuple: A tuple containing two elements:
        1. latestChapterNumber (int): The latest chapter number. If the 'div' with class 'fs16 det-con-ol oh j_catalog_list' is not found or if no 'a' elements are found inside the 'div', this value will be None.
        2. chapterLinks (list): A list of chapter links. If the 'div' with class 'fs16 det-con-ol oh j_catalog_list' is not found or if no 'a' elements are found inside the 'div', this list will be empty.
    """
    try:
        base_url = f"{base_url}/catalog"
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        listOfChapters = soup.find('div', class_='fs16 det-con-ol oh j_catalog_list')

        if listOfChapters is None:
            print("No 'div' with class 'fs16 det-con-ol oh j_catalog_list' found.")
            return None, []

        # Find all <a> elements inside the <div>
        li_elements = listOfChapters.find_all('a')
        if not li_elements:
            print("No 'a' elements found inside the 'div'.")
            return None, []

        # Extract the text and href from each <a> inside the <li> elements
        chapter_texts = [a.get_text(strip=True) for a in li_elements]
        chapter_links = [f"https://www.webnovel.com{a['href']}" for a in li_elements]

        print(f"There are {len(chapter_texts)} chapters")
        latestChapterNumber = len(chapter_texts)
        return latestChapterNumber, chapter_links

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None, []




# Function to get the novel title
def get_novel_title(base_url: str) -> str:
    """
    This function retrieves the novel title from the given base URL.

    Parameters:
    base_url (str): The base URL of the novel's main page.

    Returns:
    str: The novel title extracted from the webpage. If the required HTML elements are not found, this function will print an error message and return None.
    """
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        paragraph = soup.find('p', class_='lh24 fs16 pt24 pb24 ell c_000')

        if paragraph:
            spans = paragraph.find_all('span')
            if spans:
                last_span_text = spans[-1].get_text().strip()
                return last_span_text
            else:
                print("No <span> elements found within the paragraph.")
                return None
        else:
            print("Paragraph with specified class not found.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    
    # Change this script to get the last <span> in the <p> with class 'lh24 fs16 pt24 pb24 ell c_000'

# Function to fetch and save chapter content
def main(url: str, novel_title: str) -> None:
    """
    This function fetches and saves the chapter content from a given URL and novel title.

    Parameters:
    url (str): The URL of the novel chapter.
    novel_title (str): The title of the novel.

    Returns:
    None: This function does not return any value. It prints messages to the console and saves chapter content to a file.
    """
    folder_name = valid_dir_name(novel_title)
    file_dir = f'templates/novels/{folder_name}-chapters'
    os.makedirs(file_dir, exist_ok=True)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        chapterNumber = ""
        chapterNumberTemp = soup.find('h1', class_='dib mb0 fw700 fs24 lh1.5').get_text().strip()
        # Process characters from position 8 to 15
        for number in chapterNumberTemp[8:15]:
            if number.isnumeric():
                chapterNumber += number

        # Validate the chapter number
        if not chapterNumber:
            print("Invalid chapter number")
            return

        # Create the file path
        file_path = os.path.join(file_dir, f'chapter-{chapterNumber}.txt')

        # Check if the file already exists
        if os.path.exists(file_path):
            print(f"Chapter {chapterNumber} already downloaded. Skipping...")
            return        

        chapter_container = soup.find('div', class_='cha-words')
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
def yes(base_url: str) -> None:
    """
    This function is the main entry point for the web novel scraper. It retrieves the novel title,
    scrapes categories, saves them to a file, fetches and saves chapter content from the given base URL.

    Parameters:
    base_url (str): The base URL of the novel's main page.

    Returns:
    None: This function does not return any value. It prints messages to the console and saves data to files.
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

        webNovelDotCom = os.path.join(file_dir, 'webNovelDotCom.txt')

        with open(webNovelDotCom, 'w') as f:
            f.write('webNovelDotCom')
            print(f"Certification saved to {webNovelDotCom}")
    else:
        print("Failed to scrape categories. Skipping...")

    #

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
    base_url = 'https://www.webnovel.com/book/world-online_23126079305076205'
    yes(base_url)
