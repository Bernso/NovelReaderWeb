import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import base64
import os
import requests
import re
import urllib

def transform_title(novel_title):
    """
    Transform the novel title for URL:
    1. Decode URL-encoded characters.
    2. Remove anything within brackets (including brackets).
    3. Convert to lowercase.
    4. Replace special characters and spaces with hyphens.
    5. Remove trailing hyphens and spaces.
    """
    # Remove anything within brackets and the brackets themselves
    novel_title_cleaned = re.sub(r'\(.*?\)', '', novel_title)
    decoded_title = urllib.parse.unquote(novel_title_cleaned)
    transformed_title = decoded_title.lower()
    transformed_title = re.sub(r"[''']", "", transformed_title)  # Remove special apostrophes
    transformed_title = re.sub(r'[^a-zA-Z0-9\s]', '', transformed_title)  # Remove non-alphanumeric characters
    transformed_title = transformed_title.replace(" ", "-")
    transformed_title = transformed_title.rstrip('- ')  # Remove trailing hyphens and spaces
    return transformed_title

def valid_dir_name(novel_title):
    """
    Sanitize novel title for use in directory names:
    1. Remove special characters and spaces.
    2. Replace certain characters like ':' and '/'.
    """
    novel_title_clean = re.sub(r"[''']", "'", novel_title)
    novel_title_clean = novel_title_clean.replace(":", "")
    novel_title_clean = novel_title_clean.replace("/", "") 
    novel_title_clean = novel_title_clean.replace("’", "'")
    return novel_title_clean

def get_base_url(novel_title):
    """
    Construct the base URL using the transformed title.
    """
    base_url = f"https://lightnovelpub.vip/novel/{transform_title(novel_title)}"
    return base_url

# Function to set up the web driver and fetch page source
def get_page_source(url):
    """
    Fetches the page source of the given URL using Selenium.
    """
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode to avoid opening a window
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "fixed-img")))
        page_source = driver.page_source
    finally:
        driver.quit()
    
    return page_source

# Function to find image URL and novel title from the HTML source
def find_image_url_and_title(page_source):
    """
    Parses the page source and extracts the image URL or base64 data from the div with class 'fixed-img'
    and the novel title from the h1 inside the div with class 'main-head'.
    """
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Extract image URL
    fixed_img_div = soup.find('div', class_='fixed-img')
    if not fixed_img_div:
        raise ValueError("No 'div' with class 'fixed-img' found.")
    
    figure = fixed_img_div.find('figure')
    if not figure:
        raise ValueError("No 'figure' inside 'fixed-img' div found.")
    
    img_tag = figure.find('img')
    if not img_tag or 'src' not in img_tag.attrs:
        raise ValueError("No 'img' tag with 'src' found inside 'figure'.")
    
    image_url = img_tag['src']
    
    # Extract novel title
    main_head_div = soup.find('div', class_='main-head')
    if not main_head_div:
        raise ValueError("No 'div' with class 'main-head' found.")
    
    h1_tag = main_head_div.find('h1')
    if not h1_tag:
        raise ValueError("No 'h1' tag inside 'main-head' div found.")
    
    novel_title = h1_tag.get_text(strip=True)
    
    return image_url, novel_title

# Function to download image from URL or base64 data
def download_image(image_url, novel_title, filename="cover_image.jpg"):
    """
    Downloads an image from the given URL or base64 string and saves it to a file within the novel's folder.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Construct the directory path
    folder_name = valid_dir_name(novel_title)
    file_dir = f'templates/novels/{folder_name}-chapters'
    os.makedirs(file_dir, exist_ok=True)
    file_path = os.path.join(file_dir, filename)
    
    if image_url.startswith('data:image'):
        # Base64-encoded image
        header, encoded = image_url.split(',', 1)
        data = base64.b64decode(encoded)
        with open(file_path, 'wb') as f:
            f.write(data)
    else:
        # URL image
        response = requests.get(image_url, headers=headers)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
        else:
            raise ValueError(f"Failed to download image. Status code: {response.status_code}")

    print(f"Image downloaded successfully as {file_path}.")

# Main function to orchestrate the workflow
def main(base_url):
    url = base_url
    page_source = get_page_source(url)
    try:
        image_url, novel_title = find_image_url_and_title(page_source)
        download_image(image_url, novel_title)
    except Exception as e:
        print(f"An error occurred: {e}")
        raise  # Re-raise the exception for further debugging
    finally:
        sys.exit()  # Terminate the script after execution

def withoutLink(novel_title):
    url = get_base_url(novel_title)
    main(url)

if __name__ == "__main__":
    try:
        main("https://lightnovelpub.vip/novel/shadow-slave-05122222")
    except Exception as e:
        print(f"Failed to run the script: {e}")
        sys.exit()  # Terminate the script after execution
