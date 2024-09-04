try:
    import sys
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeType
    from webdriver_manager.chrome import ChromeDriverManager
    from bs4 import BeautifulSoup
    import base64
    import os
    import requests
    import re
    import urllib
except ImportError as e:
    input(f"Import error: {e}")

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
    transformed_title = transformed_title.replace(" ", "-")
    transformed_title = transformed_title.replace("é", "e")
    transformed_title = transformed_title.rstrip('- ')  # Remove trailing hyphens and spaces
    transformed_title = re.sub(r'[^a-zA-Z0-9\s-]', '', transformed_title)  # Remove non-alphanumeric characters except hyphens
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
    novel_title_clean = novel_title_clean.replace(u"\u2019", "'")
    return novel_title_clean

def get_base_url(novel_title):
    """
    Construct the base URL using the transformed title.
    """
    base_url = f"https://lightnovelpub.vip/novel/{transform_title(novel_title)}"
    return base_url

# Function to set up the web driver and fetch page source
def get_page_source(url: str) -> str:
    """
    This function sets up a ChromeDriver, navigates to the given URL, waits for the presence of a specific element,
    and then retrieves the page source. The ChromeDriver is automatically managed and closed after the page source is fetched.

    Parameters:
    url (str): The URL of the webpage to fetch the page source from.

    Returns:
    str: The page source of the given URL.
    """
    # Automatically match the ChromeDriver version to your installed Chrome version

    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
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
def find_image_url_and_title(page_source: str) -> tuple:
    """
    This function extracts the novel cover image URL and the novel title from the given HTML page source.

    Parameters:
    page_source (str): The HTML source code of the webpage containing the novel details.

    Returns:
    tuple: A tuple containing the novel cover image URL and the novel title.

    Raises:
    ValueError: If any of the required HTML elements (div, figure, img, h1) are not found in the page source.
    """
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extract image URL
    fixed_img_div = soup.find('div', class_='fixed-img')
    if not fixed_img_div:
        raise ValueError("No 'div' with class 'fixed-img' found.")

    figure = fixed_img_div.find('figure')
    if not figure:
        raise ValueError("No 'figure' inside 'fixed-img' div found.")

    try:
        img_tag = figure.find('img')
        if not img_tag or 'src' not in img_tag.attrs:
            raise ValueError("No 'img' tag with 'src' found inside 'figure'.")

        image_url = img_tag['src']
    except  Exception as e:
        print(f"Error: {e}")


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
    Downloads the novel cover image from the given URL or base64 data and saves it to a specified file path.

    Parameters:
    image_url (str): The URL of the image or base64 data of the image.
    novel_title (str): The title of the novel to be used for constructing the directory path.
    filename (str, optional): The name of the downloaded file. Defaults to "cover_image.jpg".

    Returns:
    None: The function does not return any value. It prints a success message upon successful download.

    Raises:
    ValueError: If the image download fails due to an HTTP status code other than 200.
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
def main(base_url: str) -> None:
    """
    The main function orchestrates the workflow of fetching the novel cover image from a given URL.

    Parameters:
    base_url (str): The base URL of the novel's page on the website.

    Returns:
    None: The function does not return any value. It prints success messages or error messages.
    """
    url = base_url
    if 'death-is-the-only-ending-for-the-villainess' in url:
        url = url[:-3]
    page_source = get_page_source(url)
    try:
        image_url, novel_title = find_image_url_and_title(page_source)
        download_image(image_url, novel_title)
    except Exception as e:
        print(f"An error occurred: {e}")
        raise  # Re-raise the exception for further debugging
    finally:
        sys.exit()


def withoutLink(novel_title: str) -> None:
    """
    This function constructs the base URL using the transformed novel title and calls the main function.

    Parameters:
    novel_title (str): The title of the novel. It will be used to construct the base URL.

    Returns:
    None: The function does not return any value. It simply calls the main function with the constructed URL.
    """
    url = get_base_url(novel_title)
    main(url)


if __name__ == "__main__":
    try:
        main(base_url="https://lightnovelpub.vip/novel/the-beginning-after-the-end-web-novel-11110049")
    except Exception as e:
        print(f"Failed to run the script: {e}")
        sys.exit()  # Terminate the script after execution
