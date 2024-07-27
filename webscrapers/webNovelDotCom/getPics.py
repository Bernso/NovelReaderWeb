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
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {url}")
        return
    
    response = requests.get(base_url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    if response.status_code == 200:
        title = soup.find('h1', class_='pt4 pb4 oh mb4 auto_height fs36 lh40 c_l').get_text().strip()
        print(title)
        return title
    return None    
    
    

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
    base_url = 'https://www.webnovel.com/book/i-stayed-at-home-for-a-century-when-i-emerged-i-was-invincible_22969003505340005'
    main(base_url)
    #folder_path = os.getcwd()
    #scrape_and_download_images(base_url, folder_path=folder_path)
