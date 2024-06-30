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

# Function to find image URL from the HTML source
def find_image_url(page_source):
    """
    Parses the page source and extracts the image URL or base64 data from the div with class 'fixed-img'.
    """
    soup = BeautifulSoup(page_source, 'html.parser')
    fixed_img_div = soup.find('div', class_='fixed-img')
    
    if not fixed_img_div:
        raise ValueError("No 'div' with class 'fixed-img' found.")
    
    figure = fixed_img_div.find('figure')
    if not figure:
        raise ValueError("No 'figure' inside 'fixed-img' div found.")
    
    img_tag = figure.find('img')
    if not img_tag or 'src' not in img_tag.attrs:
        raise ValueError("No 'img' tag with 'src' found inside 'figure'.")
    
    return img_tag['src']

# Function to download image from URL or base64 data
def download_image(image_url, filename="cover_image.jpg"):
    """
    Downloads an image from the given URL or base64 string and saves it to a file.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    if image_url.startswith('data:image'):
        # Base64-encoded image
        header, encoded = image_url.split(',', 1)
        data = base64.b64decode(encoded)
        with open(filename, 'wb') as f:
            f.write(data)
    else:
        # URL image
        response = requests.get(image_url, headers=headers)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
        else:
            raise ValueError(f"Failed to download image. Status code: {response.status_code}")

    print(f"Image downloaded successfully as {filename}.")

# Main function to orchestrate the workflow
def main():
    url = input("Enter the website URL: ")
    page_source = get_page_source(url)
    try:
        image_url = find_image_url(page_source)
        download_image(image_url)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
