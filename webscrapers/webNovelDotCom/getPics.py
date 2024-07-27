try:
    import requests
    from bs4 import BeautifulSoup
    import logging
    import os
    import re
except ImportError as e:
    input(f"Import Error: {e}")


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




def scrape_and_download_images(base_url, folder_path):
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    
    
    # Creating the URL for the pic scraper
    
    reversed_base_url = base_url[::-1]

    print(reversed_base_url)

    novelCode = ''
    for character in base_url:
        if character.isdigit():
            novelCode += character
            
    image_url = f"https://book-pic.webnovel.com/bookcover/{novelCode}"
    print(url)
    
    download_image(image_url=image_url, folder_path)




def getTitle(url):
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
