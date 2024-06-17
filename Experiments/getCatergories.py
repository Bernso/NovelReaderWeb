import requests
from bs4 import BeautifulSoup

# URL of the page to scrape
url = ""  # Replace with the actual URL

# Set up headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Fetch the webpage content
response = requests.get(url, headers=headers)
if response.status_code != 200:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    exit()

# Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

# Find the div with class 'categories'
categories_div = soup.find('div', class_='categories')

if categories_div is None:
    print("No 'div' with class 'categories' found.")
    exit()

# Find the ul inside the div
ul = categories_div.find('ul')

if ul is None:
    print("No 'ul' found inside the 'div.categories'.")
    exit()

# Get all the li elements inside the ul
list_items = ul.find_all('li')

# Open a text file to save the content
with open('categories.txt', 'w') as file:
    for item in list_items:
        # Get the text content of each li and strip any extra whitespace
        text = item.get_text(strip=True)
        file.write(text + '\n')

print("Content saved to categories.txt")