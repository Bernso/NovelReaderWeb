import requests
from bs4 import BeautifulSoup
import os
import re

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
    file_path = f'templates/novels/{novel_title}-chapters/chapter-{chapter_number}.html'

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

                html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chapter {chapter_number}</title>
    <link rel="icon" type="image/png" href="{{{{ url_for('static', filename='MAINICON-20240501-rounded.png') }}}}">
    <link rel="icon" type="image/png" href="/./static/MAINICON-20240501-rounded.png">
    <link rel="stylesheet" href="{{{{ url_for('static', filename='style.css') }}}}">
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="chapter">
        <div class="content">
            <span class="speaker" style="font-size: 40px;">
                {novel_title_clean} - Chapter {chapter_number}
            </span>
            <button><a href="/novels/{novel_title_encoded}-chapters/chapters/{int(chapter_number)-1}">Previous Chapter</a></button>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
            <button><a href="/novels/{novel_title_encoded}-chapters/chapters/{int(chapter_number)+1}">Next Chapter</a></button>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
            <button><a href="/">Home</a></button>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
            <button><a href="/novels/{novel_title_encoded}-chapters">Chapters</a></button>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
            <button id="openModal">Settings</button>
            <p class="content">
                <br>
                {chapter_text.replace('\n', '<br><br>')}
            </p>
        </div>
        <br>
        <button><a href="/novels/{novel_title_encoded}-chapters/chapters/{int(chapter_number)-1}">Previous Chapter</a></button>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
        <button><a href="/novels/{novel_title_encoded}-chapters/chapters/{int(chapter_number)+1}">Next Chapter</a></button>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
        <button><a href="/">Home</a></button>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
        <button><a href="/novels/{novel_title_encoded}-chapters">Chapters</a></button>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
        <button id="openModal2">Settings</button>
    </div>

    <!-- Settings Modal -->
    <div id="settingsModal" class="modal">
        <div class="modal-content" id="modalContent">
            <span class="close" id="closeModal">&times;</span>
            <h2>Settings</h2>
            <input type="range" min="10" max="72" value="16" class="slider" id="fontSizeSlider">
            <div class="value-display">Current Font Size: <span id="fontSizeValue">16</span>px</div>
            <div class="theme-selector">
                <span class="theme-label">Dark Mode:</span>
                <input type="checkbox" id="themeToggle" class="theme-toggle">
            </div>
        </div>
    </div>

    <script>
        // Get references to elements
        const openModalButton = document.getElementById('openModal');
        const openModalButton2 = document.getElementById('openModal2');
        const modal = document.getElementById('settingsModal');
        const closeModalButton = document.getElementById('closeModal');
        const slider = document.getElementById('fontSizeSlider');
        const textContent = document.querySelector('.content');
        const fontSizeValue = document.getElementById('fontSizeValue');
        const themeToggle = document.getElementById('themeToggle');
        const modalContent = document.getElementById('modalContent');

        // Function to open the modal
        openModalButton.onclick = function() {{
            modal.style.display = "block";
        }}
        openModalButton2.onclick = function() {{
            modal.style.display = "block";
        }}

        // Function to close the modal
        closeModalButton.onclick = function() {{
            modal.style.display = "none";
        }}

        // Close the modal if the user clicks outside of it
        window.onclick = function(event) {{
            if (event.target == modal) {{
                modal.style.display = "none";
            }}
        }}

        // Add an event listener to the slider to update the font size
        slider.addEventListener('input', function() {{
            const fontSize = slider.value;
            textContent.style.fontSize = fontSize + 'px';
            fontSizeValue.textContent = fontSize;
        }});

        // Function to toggle light and dark mode
        themeToggle.addEventListener('change', function() {{
            if (themeToggle.checked) {{
                document.body.classList.add('dark-mode');
                modalContent.classList.add('dark-mode');
            }} else {{
                document.body.classList.remove('dark-mode');
                modalContent.classList.remove('dark-mode');
            }}
        }});
    </script>
</body>
</html>
"""

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

def yes(base_url):
    latest_chapter_number = get_latest_chapter_number(base_url)
    novel_title = get_novel_title(base_url)

    if latest_chapter_number is None:
        print("Failed to get the latest chapter number.")
        return

    print(f"Latest chapter number: {latest_chapter_number}")

    for i in range(1, int(latest_chapter_number) + 1):
        main(url=f"{base_url}/chapter-{i}", chapter_number=i, novel_title=novel_title)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/x-icon" href="{{{{ url_for('static', filename='MAINICON-20240501.ico') }}}}">
    <title>Script</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background-color: #121212;
            color: #E0E0E0;
            font-family: 'Arial', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}

        .chapter {{
            background-color: #1E1E1E;
            border-radius: 10px;
            padding: 20px;
            max-width: 120vh;
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
            margin: 0 auto;
        }}

        .content {{
            font-size: 1.2em;
            line-height: 1.6;
        }}

        .content .speaker {{
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
            color: #BB86FC;
            font-size: 60px;
        }}

        .content .dialogue {{
            margin-left: 20px;
            margin-bottom: 10px;
        }}

        a {{
            color: #03DAC5;
            text-decoration: none;
            transition: color 0.3s ease;
        }}

        a:hover {{
            color: #BB86FC;
        }}

        ::-webkit-scrollbar {{
            width: 10px;
        }}

        ::-webkit-scrollbar-thumb {{
            background: #bb86fc8e;
            border-radius: 5px;
        }}

        ::-webkit-scrollbar-track {{
            background: #000000;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: #bb86fcab;
        }}

        ::-webkit-scrollbar-thumb:active {{
            background: #bb86fc;
        }}

        button {{
            background-color: #BB86FC;
            color: #121212;
            border: none;
            padding: 10px 20px;
            font-size: 1em;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s, transform 0.3s;
            margin-top: 20px;
        }}

        button:hover {{
            background-color: #BB86FC;
            transform: scale(1.05);
        }}

        button:active {{
            background-color: #6200EE;
            transform: scale(0.95);
        }}
    </style>
</head>
<body>
    <div class="chapter">
        <div class="content">
            <span class="speaker">
                Complete
            </span>
            <p class="dialogue">
                All of the chapters are at '/chapter-{latest_chapter_number}'
            </p>
        </div>
    </div>
</body>
</html>"""

# Example usage:
# base_url = 'http://example.com/novel'
# yes(base_url)
