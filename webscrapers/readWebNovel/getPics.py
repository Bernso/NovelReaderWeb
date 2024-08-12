try:
    import requests
    from bs4 import BeautifulSoup
    import logging
    import os
    import re
except ImportError as e:
    input(f"Import Error: {e}")




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
    """
    Downloads an image from the given URL and saves it to the specified folder.

    Parameters:
    image_url (str): The URL of the image to download.
    folder_path (str): The path of the folder where the image will be saved.

    Returns:
    None. Prints a success message if the image is downloaded successfully, or an error message if the download fails.
    """
    response = requests.get(image_url, headers=HEADERS)
    if response.status_code == 200:
        image_name = 'cover_image.jpg'
        with open(os.path.join(folder_path, image_name), 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded: {image_name}")
    else:
        print(f"Failed to download image: {image_url}")





def scrape_and_download_images(base_url, folder_path):
    """
    This function scrapes the images from a given URL and downloads them to a specified folder.
    It uses BeautifulSoup to parse the HTML content and requests to make HTTP requests.

    Parameters:
    base_url (str): The URL of the webpage containing the images.
    folder_path (str): The path of the folder where the images will be saved.

    Returns:
    None. Prints error messages if the webpage retrieval or image download fails.
    """
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    response = requests.get(base_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {base_url}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    image_divs = soup.find_all('div', class_='woocommerce-product-gallery__image')

    for div in image_divs:
        a_tag = div.find('a')
        if a_tag and 'href' in a_tag.attrs:
            image_url = a_tag['href']
            download_image(image_url, folder_path)





def getTitle(url):
    """
    Retrieves the title of a novel from a given URL.

    This function sends an HTTP GET request to the specified URL, parses the HTML content using BeautifulSoup,
    and extracts the title of the novel from the webpage. The title is then printed and returned.

    Parameters:
    url (str): The URL of the webpage containing the novel's title.

    Returns:
    str: The title of the novel if found, otherwise None.
    """
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {url}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    title_header = soup.find('h1', class_='product_title entry-title elementor-heading-title elementor-size-default')

    if title_header:
        novel_title = title_header.get_text().strip()
        print(f"Title: {novel_title}")
        return novel_title
    else:
        print("Title not found")

    
    
    

def main(url):
    """
    The main function of the web scraper. It initiates the scraping process by retrieving the novel's title,
    creating a directory for the novel's chapters, downloading images, and handling any exceptions that may occur.

    Parameters:
    url (str): The URL of the webpage containing the novel's information.

    Returns:
    None. Prints the path of the created directory and handles exceptions by logging the error and displaying a message.
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
    base_url = 'https://read-webnovel.com/novels/against-the-gods/'
    main(base_url)
    #folder_path = os.getcwd()
    #scrape_and_download_images(base_url, folder_path=folder_path)
