from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import base64
import os

def download_cover_image(website_url):
    # Setup Chrome and Selenium
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(website_url)

    # Get the page source after JavaScript has loaded
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Find the image inside the div or figure with class 'cover'
    cover_div = soup.find_all(['div', 'figure'], class_='cover')
    if cover_div:
        for cover in cover_div:
            img_tag = cover.find('img')
            if img_tag and 'src' in img_tag.attrs:
                image_url = img_tag['src']
                if image_url.startswith('data:image'):
                    # Handle base64-encoded images
                    header, encoded = image_url.split(',', 1)
                    data = base64.b64decode(encoded)
                    image_path = os.path.join(os.getcwd(), 'cover_image.jpg')
                    with open(image_path, 'wb') as f:
                        f.write(data)
                    print("Image downloaded successfully.")
                    break
                else:
                    print("Image URL found but not base64: ", image_url)
            else:
                print("No 'img' tag with 'src' found in this 'cover' element.")
    else:
        print("No 'cover' div or figure found in the HTML.")

    driver.quit()

download_cover_image(input("Enter the website URL: "))
