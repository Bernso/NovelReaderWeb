import os
import requests
from bs4 import BeautifulSoup
import boLogger
import re

logger = boLogger.Logging()

def get_cover_image(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the title
    title_elem = soup.find('h3', class_='title')
    if title_elem:
        title = title_elem.get_text(strip=True)
    else:
        logger.warning("Title not found")
        return
    
    if not title:
        # Generate a fallback directory title if title is None
        url_parts = url.split('/')
        fallback = url_parts[-1] if url_parts else "unknown-novel"
        logger.warning(f"Novel title is None, using fallback title: {fallback}")
        return fallback
            
    title = re.sub(r"[''']", "'", title)
    title = title.replace(":", "")
    title = title.replace("/", "")

    # Find the book div and image src
    book_div = soup.find('div', class_='book')
    if book_div:
        img_tag = book_div.find('img')
        if img_tag:
            img_src = img_tag.get('src')
        else:
            logger.warning("Image not found")
            return
    else:
        logger.warning("Book div not found")
        return

    # Save the image
    folder_name = os.path.join('templates', 'novels', f"{title}-chapters")
    os.makedirs(folder_name, exist_ok=True)
    img_path = os.path.join(folder_name, 'cover_image.jpg')
    response = requests.get(img_src)
    with open(img_path, 'wb') as f:
        f.write(response.content)

    logger.success(f"Cover image saved for {title}")

# Example usage
url = "https://readnovelfull.com/overgeared.html"
get_cover_image(url)

