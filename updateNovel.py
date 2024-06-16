import requests
from bs4 import BeautifulSoup
import os
import re
import urllib
import threading

def transform_title(novel_title):
    """
    Transform the novel title:
    1. Convert to lowercase.
    2. Remove apostrophes and URL-encoded apostrophes.
    3. Replace spaces with hyphens.
    4. Remove the last 9 characters.
    """
    # Decode URL-encoded characters
    decoded_title = urllib.parse.unquote(novel_title)

    # Convert to lowercase
    transformed_title = decoded_title.lower()

    # Remove apostrophes and URL-encoded apostrophes
    transformed_title = transformed_title.replace("'", "")
    transformed_title = transformed_title.replace("’", "")
    transformed_title = transformed_title.replace("%E2%80%99", "")
    
    # Replace spaces with hyphens
    transformed_title = transformed_title.replace(" ", "-")
    
    # Remove the last 9 characters
    #transformed_title = transformed_title[:-9]
    
    return transformed_title

def get_base_url(novel_title):
    """
    Construct the base URL using the transformed title.
    """
    base_url = f"https://lightnovelpub.vip/novel/{transform_title(novel_title)}"
    return base_url

def get_latest_chapter_number(base_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
    }

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        header_stats_div = soup.find('div', class_='header-stats')

        extracted_values = []

        if header_stats_div:
            span_tags = header_stats_div.find_all('span')

            for span in span_tags:
                strong_tag = span.find('strong')
                if strong_tag:
                    text = strong_tag.get_text(strip=True)
                    value = ''.join(filter(str.isdigit, text))
                    extracted_values.append(value)
                    print(f'Extracted value: {value}')
        else:
            print('Div with class "header-stats" not found.')

        return extracted_values[0]

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def get_novel_title(base_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
    }

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        novel_title = soup.find('h1', class_='novel-title text2row').get_text().strip()

        return novel_title

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def main(url, chapter_number, novel_title):
    # Define the file path for the chapter
    file_path = f"templates/novels/{novel_title}-chapters/chapter-{chapter_number}.txt"

    # Check if the chapter file already exists
    if os.path.exists(file_path):
        print(f"Chapter {chapter_number} already exists. Skipping...")
        return  # Skip the current chapter if it already exists

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
    }

    try:
        with requests.Session() as session:
            session.headers.update(headers)
            response = session.get(url=url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            chapter_title = soup.find(class_='chapter-title')
            if chapter_title:
                chapter_number = chapter_title.get_text().split()[1]
            else:
                print("Error: 'chapter-title' not found on the page.")
                return

            for letter in chapter_number:
                if not letter.isdigit():
                    chapter_number = chapter_number.replace(letter, '')

            chapter_container = soup.find('div', id='chapter-container')
            if chapter_container:
                chapter_text = chapter_container.get_text(separator='\n').strip()

                novel_title_encoded = novel_title.replace(' ', '%20')

                novel_title_clean = re.sub(r'\s*\(.*?\)', '', novel_title)

                html_template = f"""{chapter_text.replace('\n', '<br><br>')}"""

                # Ensure the directories exist
                os.makedirs(f'templates/novels/{novel_title}-chapters', exist_ok=True)

                # Write the chapter content to the file
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(html_template)
                
                print(f"HTML file created successfully for {novel_title} chapter {chapter_number}")

            else:
                print("Error: 'chapter-container' not found on the page.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def yes(novel_title):
    def thread_target():
        base_url = get_base_url(novel_title)

        if base_url is None:
            print("Failed to construct the base URL for the novel.")
            return

        latest_chapter_number = get_latest_chapter_number(base_url)
        novel_title_clean = get_novel_title(base_url)

        if latest_chapter_number is None:
            print("Failed to get the latest chapter number.")
            return

        print(f"Latest chapter number: {latest_chapter_number}")

        for i in range(1, int(latest_chapter_number) + 1):
            main(url=f"{base_url}/chapter-{i}", chapter_number=i, novel_title=novel_title_clean)

    # Creating a new thread for the yes function
    thread = threading.Thread(target=thread_target)
    thread.start()


if __name__ == '__main__':
    yes("Vampire's Slice Of Life") 