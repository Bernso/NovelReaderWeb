try:
    import requests
    from bs4 import BeautifulSoup
    import os
    import re
    import urllib
except ImportError as e:
    input(f"Import error: {e}")

# Script needed to update the novels


# Define headers to mimic browser requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
}



# Function to transform the novel title for URL
def transform_title(novel_title: str) -> str:
    """
    Transform the novel title for URL:
    1. Decode URL-encoded characters.
    2. Remove anything within brackets (including brackets).
    3. Convert to lowercase.
    4. Replace special characters and spaces with hyphens.
    5. Remove trailing hyphens and spaces.

    Parameters:
    novel_title (str): The original novel title.

    Returns:
    str: The transformed novel title suitable for use in URLs.
    """
    # Remove anything within brackets and the brackets themselves
    novel_title_cleaned = re.sub(r'\(.*?\)', '', novel_title)
    decoded_title = urllib.parse.unquote(novel_title_cleaned)
    transformed_title = decoded_title.lower()
    transformed_title = re.sub(r"[''']", "", transformed_title)  # Remove special apostrophes
    transformed_title = transformed_title.replace(" ", "-")
    transformed_title = transformed_title.replace("é", "e")
    transformed_title = transformed_title.rstrip('- ')  # Remove trailing hyphens and spaces
    transformed_title = re.sub(r'[^a-zA-Z0-9\s-]', '', transformed_title)  # Remove non-alphanumeric characters except hyphens
    return transformed_title




# Function to sanitize novel title for use in directory names
def valid_dir_name(novel_title: str) -> str:
    """
    Sanitize novel title for use in directory names.

    This function takes a novel title as input and performs several operations to sanitize it for use in directory names.
    It removes special characters and spaces, replaces certain characters like ':' and '/', and ensures that the resulting
    string is valid for directory names.

    Parameters:
    novel_title (str): The original novel title.

    Returns:
    str: The sanitized novel title suitable for use in directory names.
    """
    novel_title_clean = re.sub(r"[''']", "'", novel_title)  # Replace single quotes with apostrophes
    novel_title_clean = novel_title_clean.replace(":", "")  # Remove colons
    novel_title_clean = novel_title_clean.replace("/", "")  # Remove slashes
    novel_title_clean = novel_title_clean.replace("’", "'")  # Replace right single quote with apostrophes
    return novel_title_clean




# Function to get the base URL
def get_base_url(novel_title):
    """
    Construct the base URL using the transformed title.
    """
    base_url = f"https://lightnovelpub.vip/novel/{transform_title(novel_title)}"
    return base_url




# Function to scrape categories and return them as a list
def scrape_categories(url):
    """
    Scrape the categories of a novel from the given URL.

    Parameters:
    url (str): The URL of the novel's page.

    Returns:
    list: A list of categories extracted from the URL. If any error occurs during the scraping process,
    an empty list is returned.
    """
    try:
        response = requests.get(url, headers=headers)
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




def get_latest_chapter_number(base_url: str) -> str:
    """
    This function retrieves the latest chapter number from the given base URL.
    It sends a GET request to the URL, parses the HTML content using BeautifulSoup,
    and extracts the chapter number from the 'div' with the class 'header-stats'.

    Parameters:
    base_url (str): The URL from which to retrieve the latest chapter number.

    Returns:
    str: The latest chapter number extracted from the URL. If the request fails or the chapter number is not found, returns None.
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




# Function to get the novel title from the URL
def get_novel_title(base_url: str) -> str:
    """
    This function retrieves the novel title from the given base URL.
    It sends a GET request to the URL, parses the HTML content using BeautifulSoup,
    and extracts the novel title from the 'h1' tag with the class 'novel-title text2row'.

    Parameters:
    base_url (str): The URL from which to retrieve the novel title.

    Returns:
    str: The novel title extracted from the URL. If the request fails or the title is not found, returns None.
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











# Function to iterate over all chapters and save them
def yes(novel_title: str) -> None:
    """
    This function is responsible for updating and scraping novel chapters and pictures from various websites.
    It checks the type of novel (Reader Novel, Read Web Novel, Web Novel Dot Com, or Light Novel Pub) and performs
    the necessary operations accordingly.

    Parameters:
    novel_title (str): The title of the novel to be updated.

    Returns:
    None
    """
    if os.path.exists(f'templates/novels/{valid_dir_name(novel_title)}-chapters/base_url_number.txt'): # path for reader-novel novels
        print("'Reader Novel' Novel found")
        # Link creator
        with open(f'templates/novels/{valid_dir_name(novel_title)}-chapters/base_url_number.txt', 'r') as file:
            urlNum = file.read()
            url = f"https://www.readernovel.net/novel/{transform_title(novel_title)}-{urlNum}/"
            print(f"URL made: {url}")
            file.close()
        import webscrapers.readerNovel.genChapters
        import webscrapers.readerNovel.getPics
        webscrapers.readerNovel.genChapters.yes(url) # Get chapters
        webscrapers.readerNovel.getPics.main(url) # Get picture

    elif os.path.exists(f'templates/novels/{valid_dir_name(novel_title)}-chapters/readWebNovel.txt'):
        # URL creator
        url = f"https://read-webnovel.com/novels/{transform_title(novel_title)}"
        import webscrapers.readWebNovel.genChapters
        import webscrapers.readWebNovel.getPics
        webscrapers.readWebNovel.genChapters.yes(url) # Get chapters
        webscrapers.readWebNovel.getPics.main(url) # Get picture

    elif os.path.exists(f'templates/novels/{valid_dir_name(novel_title)}-chapters/webNovelDotCom.txt'):
        # URL creator
        with open(f'templates/novels/{novel_title}-chapters/webNovelDotCom.txt', 'r') as f:
            novel_code = f.read()
            f.close()
        url = f"https://www.webnovel.com/book/{transform_title(novel_title)}_{novel_code}"
        import webscrapers.webNovelDotCom.genChapters
        import webscrapers.webNovelDotCom.getPics
        webscrapers.webNovelDotCom.genChapters.yes(url) # Get chapters
        webscrapers.webNovelDotCom.getPics.main(url=url) # Get picture

    else:
        print("'Light Novel Pub' Novel found")
        if 'Death Is The Only Ending For The Villainess' in novel_title:
            novel_title = novel_title[:-3]

        base_url = get_base_url(novel_title)
        
        import webscrapers.lightNovelPubDotVip.getPics
        scraper = webscrapers.lightNovelPubDotVip.getPics.NovelImageScraper()
        scraper._NovelImageScraper__scrape_novel_image(url=base_url)
        scraper.cleanup_driver()
        
        import webscrapers.lightNovelPubDotVip.genChaptersV2
        scraper = webscrapers.lightNovelPubDotVip.genChaptersV2.genChapters(base_url)
        scraper.getChapters()
        



    
    
# Example usage
if __name__ == '__main__':
    yes("Prodigiously Amazing Weaponsmith")

