import requests
from bs4 import BeautifulSoup
import webbrowser
import tkinter as tk
import os


# EXAMPLE URL 'https://lightnovelpub.vip/novel/the-beginning-after-the-end-548/chapter-482'


def main(url, i):
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
                chapterNumber = chapter_title.get_text().split()[1]
            else:
                print("Error: 'chapter-title' not found on the page.")
                return
            
            for letter in chapterNumber:
                if not letter.isdigit():
                    chapterNumber = chapterNumber.replace(letter, '')
            
            chapter_container = soup.find('div', id='chapter-container')
            if chapter_container:
                chapter_text = chapter_container.get_text(separator='\n').strip()
                
            
                
                html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chapter {chapterNumber}</title>
    <link rel="icon" type="image/png" href="{{ url_for('static', filename='MAINICON-20240501-rounded.png') }}">
    <link rel="icon" type="image/png" href="/./static/MAINICON-20240501-rounded.png">
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="chapter">
        <div class="content">
            <span class="speaker">
                Chapter {chapterNumber}
            </span>
            <button> <a href=/chapters/{int(chapterNumber)-1}>Previous Chapter</a></button>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <button> <a href=/chapters/{int(chapterNumber)+1}>Next Chapter</a></button>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <button> <a href="/">Home</a></button>&nbsp;&nbsp;<button> <a href="/chapters">Chapters</a></button>
            
            <p class="content">
                <br>
                {chapter_text.replace('\n', '<br>')}
            </p>
        </div>
        <br>
        <button> <a href=/chapters/{int(chapterNumber)-1}>Previous Chapter</a></button>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <button> <a href=/chapters/{int(chapterNumber)+1}>Next Chapter</a></button>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <button> <a href="/">Home</a></button>&nbsp;&nbsp;<button> <a href="/chapters">Chapters</a></button>
    </div>
</body>
</html>"""
                if not os.path.exists('templates/chapters'):
                    os.makedirs('templates/chapters')
                
                with open(os.path.join('templates/chapters', f'chapter-{chapterNumber}.html'), 'w', encoding='utf-8') as file:
                    file.write(html_template)
                    
                print(f"HTML file created successfully. For chapter {i}")
                #webbrowser.open(os.path.join('Chapters', f'chapter-{chapterNumber}.html'))
                #os._exit(0)
            else:
                print("Error: 'chapter-container' not found on the page.")
            
            
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
def yes():
    for i in range(1, 482 + 1):
        main(url=f"https://lightnovelpub.vip/novel/the-beginning-after-the-end-548/chapter-{i}", i=i)
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='MAINICON-20240501.ico') }}">
    <title>Script</title>
    <style>/* Basic reset */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        /* Body styles */
        body {
            background-color: #121212; /* Dark background */
            color: #E0E0E0; /* Light text */
            font-family: 'Arial', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        /* Chapter container */
        .chapter {
            background-color: #1E1E1E; /* Slightly lighter background for contrast */
            border-radius: 10px;
            padding: 20px;
            max-width: 120vh; /* Increased width */
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.2); /* Subtle glow effect */
            margin: 0 auto; /* Center the container */
        }

        /* Content paragraph */
        .content {
            font-size: 1.2em;
            line-height: 1.6; /* Improved readability */
        }

        /* Speaker names */
        .content .speaker {
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
            color: #BB86FC; /* Highlight color for speaker names */
            font-size: 60px;
        }

        /* Dialogue text */
        .content .dialogue {
            margin-left: 20px; /* Indent dialogue for clarity */
            margin-bottom: 10px; /* Space between dialogues */
        }

        /* Adding link styles */
        a {
            color: #03DAC5; /* Highlight color for links */
            text-decoration: none;
            transition: color 0.3s ease;
        }

        a:hover {
            color: #BB86FC; /* Link hover color */
        }

        /* Scrollbar styles */
        ::-webkit-scrollbar {
            width: 10px; /* Width of the scrollbar */
        }

        /* Scrollbar Handle */
        ::-webkit-scrollbar-thumb {
            background: #bb86fc8e; /* Color of the scrollbar handle */
            border-radius: 5px; /* Border radius of the scrollbar handle */
        }

        /* Scrollbar Track */
        ::-webkit-scrollbar-track {
            background: #000000; /* Background color of the scrollbar track */
        }

        /* Scrollbar Handle on hover */
        ::-webkit-scrollbar-thumb:hover {
            background: #bb86fcab; /* Color of the scrollbar handle on hover */
        }

        ::-webkit-scrollbar-thumb:active {
            background: #bb86fc; /* Color of the scrollbar handle on hover */
        }

        /* Button Styles */
        button {
            background-color: #BB86FC; /* Initial background color */
            color: #121212; /* Button text color */
            border: none;
            padding: 10px 20px; /* Padding for the button */
            font-size: 1em; /* Font size */
            border-radius: 5px; /* Rounded corners */
            cursor: pointer; /* Cursor on hover */
            transition: background-color 0.3s, transform 0.3s; /* Smooth transition for background and scale */
            margin-top: 20px; /* Space above the button */
        }

        /* Button Hover Effect */
        button:hover {
            background-color: #BB86FC; /* Background color on hover */
            transform: scale(1.05); /* Slightly enlarge on hover */
        }

        /* Button Active State */
        button:active {
            background-color: #6200EE; /* Background color on active */
            transform: scale(0.95); /* Slightly shrink on click */
        }</style>
</head>
<body>
    <div class="chapter">
        <div class="content">
            <span class="speaker">
                Complete
            </span>
            <p class="dialogue">
                All of the chapters are at '/chapter-{chapterNumber}'
            </p>
        </div>
    </div>
</body>
</html>"""

if __name__ == '__main__':
    yes()



