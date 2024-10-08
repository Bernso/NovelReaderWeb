import os
import requests
from bs4 import BeautifulSoup
import base64
import io
from PIL import Image

def download_image_from_link():
    link = input("Please enter the image link: ")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(link, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    figure_tag = soup.find('figure', class_='cover')
    if figure_tag:  # Check if the figure tag is found
        img_tag = figure_tag.find('img')
        if img_tag:
            img_url = img_tag['src']
            if not os.path.exists('pics'):
                os.makedirs('pics')
            if img_url.startswith('data:image'):
                # Handle base64 encoded images
                format, base64_str = img_url.split(';base64,')
                image_data = base64.b64decode(base64_str)
                img_format = format.split('/')[-1]
                img_name = f'downloaded_image.{img_format}'
                image = Image.open(io.BytesIO(image_data))
                image = image.convert('RGB')
                image.save(os.path.join('pics', img_name), format='JPEG')
                print(f"Image decoded from base64 and saved as {img_name} in 'pics' folder.")
            else:
                # Handle standard image URLs
                img_data = requests.get(img_url, headers=headers).content
                img_name = os.path.basename(img_url)
                with open(os.path.join('pics', img_name), 'wb') as f:
                    f.write(img_data)
                print(f"Image downloaded successfully and saved as {img_name} in 'pics' folder.")
        else:
            print("No image tag found within the figure element.")
    else:
        print("No figure with class 'cover' found.")

download_image_from_link()

#Generate some code that will download the image from the link inputted, the image will be in the 'cover' figure and inside of that there will be an 'img' this is where the image is, i want this to be downloaded to a folder called 'pics' if it doesnt already exist i want it to create the directory

