try:
    import requests
    from bs4 import BeautifulSoup
    import logging
    import os
    import re
except ImportError as e:
    input(f"Import Error: {e}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

url = 'https://book-pic.webnovel.com/bookcover/'

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')




# Custom headers to mimic a real browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


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

def download_image(image_url, folder_path):
    response = requests.get(image_url, headers=HEADERS)
    if response.status_code == 200:
        image_name = 'cover_image.jpg'
        with open(os.path.join(folder_path, image_name), 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded: {image_name}")
    else:
        print(f"Failed to download image: {image_url}")




def scrape_and_download_images(base_url: str, folder_path: str) -> None:
    """
    This function scrapes the webnovel.com website for a novel's cover image and downloads it to a specified folder.
    If the folder does not exist, it is created. The novel's unique code is extracted from the base_url and used to construct
    the image URL. The image is then downloaded and saved with the name 'cover_image.jpg' in the specified folder.

    Parameters:
    base_url (str): The URL of the novel's webnovel.com page. It is used to extract the novel's unique code.
    folder_path (str): The path of the directory where the cover image will be saved.

    Returns:
    None. However, it prints the reversed base_url, the constructed image_url, and logs any errors that occur during the process.
    """
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Creating the URL for the pic scraper
    reversed_base_url = base_url[::-1]
    print(reversed_base_url)

    reversedNovelCode = ''
    for character in reversed_base_url:
        if character.isdigit():
            reversedNovelCode += character
        else:
            break

    novelCode = reversedNovelCode[::-1]
    fileName = "webNovelDotComCode.txt"
    with open(os.path.join(folder_path, fileName), 'w') as file:
        file.write(novelCode)

    image_url = f"https://book-pic.webnovel.com/bookcover/{novelCode}"
    print(image_url)

    download_image(image_url=image_url, folder_path=folder_path)





def getTitle(url):
    """
    This function retrieves the title of a novel from its webnovel.com URL.

    Parameters:
    url (str): The URL of the novel's webnovel.com page.

    Returns:
    str: The title of the novel if successfully retrieved, otherwise None.
    """
    try:
        response = requests.get(url, headers=headers)
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

    
    

def main(url):
    """
    This function is the main entry point for the web scraper. It initiates the scraping process by
    retrieving the novel's title from the provided URL, creating a directory for the novel, and downloading
    the cover image.

    Parameters:
    url (str): The URL of the novel's webnovel.com page.

    Returns:
    None. However, it prints the path of the created directory and logs any errors that occur during the process.
    """
    logging.info("Web Scraper started")
    try:
        title = getTitle(url)
        path = fr"{os.getcwd()}\templates\novels\{valid_dir_name(title)}-chapters"
        scrape_and_download_images(base_url=url, folder_path=path)
        print(path)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print("An error occurred. Please try again.")



# Example usage
if __name__ == '__main__':
    base_url = 'https://www.webnovel.com/book/origins-of-blood_31471588608620705'
    main(base_url)
    #folder_path = os.getcwd()
    #scrape_and_download_images(base_url, folder_path=folder_path)
