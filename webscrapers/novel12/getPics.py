import requests
from bs4 import BeautifulSoup
import os
import urllib
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define headers to mimic browser requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Base URL for the website
BASE_URL = 'https://www.novel12.com'

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

def valid_dir_name(name):
    """
    Create a valid directory name from the novel title.
    
    Parameters:
    name (str): The novel title.
    
    Returns:
    str: A valid directory name.
    """
    if not name:
        return "unknown-novel"
        
    name = re.sub(r"[''']", "'", name)
    name = name.replace(":", "")
    name = name.replace("/", "")
    return name

def get_novel_title(base_url: str) -> str:
    """
    Retrieves the novel title from the given URL.

    Parameters:
    base_url (str): The URL of the novel's main page.

    Returns:
    str: The novel title if found, otherwise None.
    """
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        title_div = soup.find('div', class_='title')
        if title_div:
            title_elem = title_div.find('h1')
            if title_elem:
                return title_elem.get_text(strip=True)
        
        logger.warning("Title not found")
        return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

def main(url: str) -> None:
    """
    Main function to download the novel's cover image.

    Parameters:
    url (str): The URL of the novel's main page.

    Returns:
    None
    """
    try:
        # Get novel title
        novel_title = get_novel_title(url)
        if not novel_title:
            logger.error("Failed to get novel title")
            return

        # Create directory for the novel
        folder_name = valid_dir_name(novel_title)
        file_dir = f'templates/novels/{folder_name}-chapters'
        os.makedirs(file_dir, exist_ok=True)

        # Get the page content
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the cover image
        cover_img = soup.find('a', class_='imagesCrop')
        if not cover_img or not cover_img.find('img'):
            logger.error("Cover image not found")
            return

        img_url = cover_img.find('img').get('src')
        if not img_url:
            logger.error("Image URL not found")
            return

        # Add base URL if the image URL is relative
        if not img_url.startswith(('http://', 'https://')):
            img_url = f"{BASE_URL}{img_url}"

        # Download the image
        img_response = requests.get(img_url, headers=headers)
        img_response.raise_for_status()

        # Save the image
        img_path = os.path.join(file_dir, 'cover_image.jpg')
        with open(img_path, 'wb') as f:
            f.write(img_response.content)

        logger.info(f"Cover image saved for {novel_title}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    # Example usage
    novel_url = f"{BASE_URL}/254188/golden-son.htm"  # Replace with actual URL
    main(novel_url) 