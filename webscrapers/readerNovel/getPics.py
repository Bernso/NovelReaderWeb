import requests
from bs4 import BeautifulSoup
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define headers to mimic browser requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Function to get the novel title
def get_novel_title(base_url):
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()  # Check if the request was successful

        soup = BeautifulSoup(response.text, 'html.parser')
        novel_title_tag = soup.find('h1', class_='page-title pt-2 mb-3')
        if novel_title_tag:
            novel_title = novel_title_tag.get_text(strip=True)
            return novel_title
        else:
            logging.warning("No <h1> with class 'page-title pt-2 mb-3' found.")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None


def downloadImage(url, basePath):

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Open a file in binary write mode and save the content
        with open(f'{basePath}/cover_image.jpg', 'wb') as file:
            file.write(response.content)
        print('Image downloaded successfully!')
    else:
        print(f'Failed to download image. Status code: {response.status_code}')



# Main function
def main(url):
    novel_title = get_novel_title(url)
    if novel_title:
        logging.info(f"Novel Title: {novel_title}")
        path = os.getcwd()
        basePath = f'{path}/templates/novels/{novel_title}-chapters'
        base_url_number_file = f'{path}/templates/novels/{novel_title}-chapters/base_url_number.txt'
        
        numberFile = open(base_url_number_file, 'r')
        numbers = numberFile.read()
        numberFile.close()
        
        website = f'https://www.readernovel.net/imgs/medium/{novel_title}-{numbers}.jpg'
        downloadImage(url=website, basePath=basePath)
        
    else:
        logging.info("Failed to retrieve the novel title.")

# Example usage
if __name__ == '__main__':
    base_url = 'https://www.readernovel.net/novel/deep-sea-embers-4055/'
    main(base_url)