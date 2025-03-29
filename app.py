try:
    # Webscrapers
    import webscrapers.lightNovelPubDotVip.genChapters
    import webscrapers.lightNovelPubDotVip.getPics 
    
    import webscrapers.readerNovel.genChapters
    import webscrapers.readerNovel.getPics 
    
    import webscrapers.readWebNovel.genChapters
    import webscrapers.readWebNovel.getPics
    
    import webscrapers.webNovelDotCom.genChapters
    import webscrapers.webNovelDotCom.getPics
    
    import webscrapers.updateNovel
    
    
    
    # Flask and standard libraries
    from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
    from flask_caching import Cache
    import os
    import re  
    import random
    import requests
    import json
    import boLogger # My logger
    import urllib.parse  # Add this import for URL decoding
    import time
    import datetime
    
    
    # Project-specific imports
    from config import Config
    from dotenv import load_dotenv

except ImportError as e:
    input(f"Module not found: {e}")

logger = boLogger.Logging()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

app.config['CACHE_TYPE'] = 'SimpleCache'
cache = Cache(app)

# Port Number (Keep as string)
port = Config.PORT

# Debug True/Flase
debug = Config.DEBUG



# Everything documented here is done by tabnine AI (not me)


def send_discord_message(message):
    """
    Send a message to a Discord channel using a webhook URL.

    Parameters:
    message (str): The message to be sent to the Discord channel.

    Returns:
    None. Logs the result of sending the message.
    """
    try:
        webhook_url = Config.DISCORD_WEBHOOK_URL
        data = {
            "content": message,
            "username": "Novel Reader Website"
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(webhook_url, data=json.dumps(data), headers=headers)

        if response.status_code == 204:
            logger.info("Discord message sent successfully!")
        else:
            logger.error(f"Failed to send Discord message. Status code: {response.status_code}")
            logger.error(f"Response body: {response.text}")
    except Exception as e:
        logger.error(f"Error sending Discord message: {e}")




logger.info("Reading chapters")
start = time.time()
        
# Leave this code raw
#
#
#
currentPath = app.root_path


# Getting the stats for the home page

novels_folder_path = os.path.join(app.root_path, 'templates', 'novels')
total_novels = 0
total_chapters = 0
all_categories = []

for novel in os.listdir(novels_folder_path):
    novel_path = os.path.join(novels_folder_path, novel)
    if os.path.isdir(novel_path):
        total_novels += 1

        json_path = os.path.join(novel_path, 'chapters.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                total_chapters += len(json.load(f))
                f.close()
        else:
            chapters = [file for file in os.listdir(novel_path) if file.endswith('.txt') and file.startswith('chapter-')]
            total_chapters += len(chapters)

        categories_file = os.path.join(novel_path, 'metadata.json')
        if os.path.exists(categories_file):
            with open(categories_file, 'r', encoding='utf-8') as f:
                content = json.load(f)['categories']
                for category in content:
                    if category not in all_categories:
                        all_categories.append(category)
               
                f.close()
end = time.time()
logger.success(f"All data successfully read after {round((end - start), 2)} seconds")





@app.route('/random_directory')
def random_directory():
    """
    This function selects a random directory from the 'novels' directory and returns its name.

    Parameters:
    None

    Returns:
    jsonify: A JSON response containing the name of the chosen directory.
              If no directories are found, it returns a JSON response indicating that no directories were found.
    """
    folder_path = os.path.join(app.root_path, 'templates', 'novels')  # Path to the 'novels' directory
    directories = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
    if directories:
        chosen_directory = random.choice(directories)
        return jsonify({'directory': chosen_directory})
    return jsonify({'directory': 'No directories found'})




@app.route('/')
def home():
    data = {"total_novels": total_novels, "total_chapters": total_chapters, "total_categories": len(all_categories)}
    return render_template('home.html', data=data)

    
 
    


@app.errorhandler(404)
def page_not_found(error):
    """
    This function handles the 404 error, which is returned when a requested resource is not found.
    It renders a custom 404 error page.

    Parameters:
    error (Exception): The exception object that caused the 404 error.

    Returns:
    render_template: A rendered HTML template named '404.html' with a 404 status code.
    """
    return render_template('404.html'), 404




@app.route('/lightNovelPubDotVip', methods=['POST'])
def run_scriptlightNovelPubDotVip():
    """
    This function handles a POST request to the '/lightNovelPubDotVip' endpoint.
    It receives a novel link from the request JSON data, runs a script to generate chapters,
    and returns the result of the script execution.

    Parameters:
    None

    Returns:
    jsonify: A JSON response containing the result of the script execution.
              If an exception occurs, it returns a JSON response with an error message.
    """
    try:
        print("Received request to /lightNovelPubDotVip")  # Debugging statement
        novel_link = request.json.get('novelLink')
        print(f"Novel link received: {novel_link}")  # Debugging statement
        import webscrapers.lightNovelPubDotVip.getPics
        scraper = webscrapers.lightNovelPubDotVip.getPics.NovelImageScraper()
        scraper._NovelImageScraper__scrape_novel_image(url=novel_link)
        scraper.cleanup_driver()
        
        import webscrapers.lightNovelPubDotVip.genChaptersV2
        scraper = webscrapers.lightNovelPubDotVip.genChaptersV2.genChapters(novel_link)
        scraper.getChapters()
        return jsonify({"result": "Done"})
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debugging statement
        return jsonify({"error": str(e)}), 500




@app.route('/readerNovel', methods=['POST'])
def run_scriptreaderNovel():
    """
    This function handles a POST request to the '/readerNovel' endpoint.
    It receives a novel link from the request JSON data, runs a script to generate chapters,
    and returns the result of the script execution.

    Parameters:
    None

    Returns:
    jsonify: A JSON response containing the result of the script execution.
              If an exception occurs, it returns a JSON response with an error message.
    """
    try:
        print("Received request to /readerNovel")  # Debugging statement
        novel_link = request.json.get('novelLink')
        print(f"Novel link received: {novel_link}")  # Debugging statement
        result = webscrapers.readerNovel.genChapters.yes(base_url=novel_link)
        webscrapers.readerNovel.getPics.main(url=novel_link) 
        return jsonify({"result": result})
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debugging statement
        return jsonify({"error": str(e)}), 500




@app.route('/readWebNovel', methods=['POST'])
def run_scriptreadWebNovel():
    """
    This function handles the POST request to run the 'readWebNovel' web scraper.
    It receives a novel link from the request JSON data, runs the 'yes' function from the 'genChapters' module of the 'readWebNovel' web scraper,
    and then runs the 'main' function from the 'getPics' module of the 'readWebNovel' web scraper.
    If any exception occurs during the execution, it returns an error response with the error message.

    Parameters:
    None

    Returns:
    jsonify: A JSON response containing the result of the web scraper execution.
              If an error occurs, it returns a JSON response with the error message and a status code of 500.
    """
    try:
        print("Received request to /readerNovel")  # Debugging statement
        novel_link = request.json.get('novelLink')
        print(f"Novel link received: {novel_link}")  # Debugging statement
        result = webscrapers.readWebNovel.genChapters.yes(base_url=novel_link)
        webscrapers.readWebNovel.getPics.main(url=novel_link) 
        return jsonify({"result": result})
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debugging statement
        return jsonify({"error": str(e)}), 500

    



@app.route('/webNovelDotCom', methods=['POST'])
def run_scriptwebNovelDotCom():
    """
    This function is responsible for handling a POST request to the '/webNovelDotCom' endpoint.
    It retrieves a novel link from the request JSON data, runs the 'yes' function from the 'genChapters' module of the 'webNovelDotCom' web scraper,
    and then runs the 'main' function from the 'getPics' module of the 'webNovelDotCom' web scraper.
    If any exceptions occur during the execution, it returns an error response with the exception message.

    Parameters:
    None

    Returns:
    jsonify: A JSON response containing the result of the 'yes' function from the 'genChapters' module if the execution is successful.
              If an exception occurs, it returns a JSON response containing the error message with a 500 status code.
    """
    try:
        print("Received request to /webNovelDotCom")  # Debugging statement
        novel_link = request.json.get('novelLink')
        print(f"Novel link received: {novel_link}")  # Debugging statement
        result = webscrapers.webNovelDotCom.genChapters.yes(base_url=novel_link)
        webscrapers.webNovelDotCom.getPics.main(url=novel_link) 
        return jsonify({"result": result})
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debugging statement
        return jsonify({"error": str(e)}), 500


def fetch_chapters_for_novel(novel_name):
    # URL decode and transform novel name if needed
    novel_name = urllib.parse.unquote(novel_name)
    if not novel_name.endswith('-chapters'):
        novel_name = novel_name + '-chapters'
    
    print(f"Fetching chapters for novel: {novel_name}")
    
    path = os.path.join(app.root_path, 'templates', 'novels', novel_name)
    print(f"Looking in path: {path}")
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"Novel directory not found: {path}")
        
    chapters = [f for f in os.listdir(path) if f.startswith('chapter-') and f.endswith('.txt')]
    if not chapters:
        raise ValueError(f"No chapters found for novel: {novel_name}")
        
    print(f"Found {len(chapters)} chapters")
    
    chapterContent = {}
    for chapter in chapters:
        # Split the chapter filename and handle both integer and decimal chapter numbers
        parts = chapter.split('-')
        if len(parts) == 3:  # For decimal chapters like chapter-3-2.txt
            chapter_number = float(f"{parts[1]}.{parts[2].split('.')[0]}")
        else:  # For integer chapters like chapter-3.txt
            chapter_number = int(parts[1].split('.')[0])
        
        chapter_path = os.path.join(path, chapter)
        with open(chapter_path, 'r', encoding='utf-8') as f:
            content = f.read()
            content = content.replace('<br>', "\n")
            chapterContent[chapter_number] = content
            
    return chapterContent

def fetch_chapters_around_chapter_for_novel(novel_name, chapter_number):
    path = os.path.join(app.root_path,'templates', 'novels', novel_name)
    
    chapter_dict = {}
    for f in os.listdir(path):
        if f.startswith('chapter-') and f.endswith('.txt'):
            # Split the chapter filename and handle both integer and decimal chapter numbers
            parts = f.split('-')
            if len(parts) == 3:  # For decimal chapters like chapter-3-2.txt
                chapter_number = float(f"{parts[1]}.{parts[2].split('.')[0]}")
            else:  # For integer chapters like chapter-3.txt
                chapter_number = int(parts[1].split('.')[0])
            
            with open(os.path.join(app.root_path, path, f), 'r', encoding='utf-8') as file:
                content = file.read()
                content = content.replace('<br>', "\n")
                chapter_dict[chapter_number] = content
    return chapter_dict

def create_chapters_json(novel_name):
    novel_name = urllib.parse.unquote(novel_name).replace('%27', "'")
    novel_path = os.path.join(app.root_path, 'templates', 'novels', novel_name)
    
    chapters = [f for f in os.listdir(novel_path) if f.startswith('chapter-') and f.endswith('.txt')]
    chapter_content = {}

    for chapter in chapters:
        parts = chapter.split('-')
        if len(parts) == 3:
            chapter_number = float(f"{parts[1]}.{parts[2].split('.')[0]}")
        else:
            chapter_number = int(parts[1].split('.')[0])
        
        with open(os.path.join(novel_path, chapter), 'r', encoding='utf-8') as f:
            content = f.read()
            content = content.replace('<br>', "\n")
            chapter_content[chapter_number] = content

    json_path = os.path.join(novel_path, 'chapters.json')
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(chapter_content, json_file, ensure_ascii=False, indent=4)

    # Delete chapter text files after creating JSON
    for chapter in chapters:
        chapter_path = os.path.join(novel_path, chapter)
        try:
            os.remove(chapter_path)
        except Exception as e:
            logger.error(f"Error deleting chapter file {chapter}: {e}")

    print(f"Chapters JSON file created and text files deleted for {novel_name}")


def cleanup_chapter_files(novel_name):
    """Remove individual chapter text files if chapters.json exists"""
    novel_path = os.path.join(app.root_path, 'templates', 'novels', novel_name)
    json_path = os.path.join(novel_path, 'chapters.json')
    
    if os.path.exists(json_path):
        for file in os.listdir(novel_path):
            if file.startswith('chapter-') and file.endswith('.txt'):
                try:
                    os.remove(os.path.join(novel_path, file))
                except Exception as e:
                    logger.error(f"Error deleting {file}: {e}")

@app.route('/api/chapters', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_chapters():
    """
    Retrieve chapter(s) for a novel.
    If a specific chapter ('c' parameter) is provided, returns only that chapter;
    otherwise, returns all chapters.
    The response is cached for 5 minutes to reduce file I/O.
    """
    try:
        novel_name = request.args.get('n', '')
        chapter_number = request.args.get('c', '')

        # Cleanup individual chapter files if chapters.json exists
        if novel_name:
            decoded_name = urllib.parse.unquote(novel_name).replace('+', ' ')
            if not decoded_name.endswith('-chapters'):
                decoded_name = decoded_name + '-chapters'
            cleanup_chapter_files(decoded_name)

        # Handle single chapter request
        if chapter_number:
            try:
                chapter_number = float(chapter_number) if '.' in chapter_number else int(chapter_number)
                novel_name = urllib.parse.unquote(novel_name).replace('+', ' ')
                if not novel_name.endswith('-chapters'):
                    novel_name = novel_name + '-chapters'
                json_path = os.path.join(app.root_path, 'templates', 'novels', novel_name, 'chapters.json')
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as json_file:
                        chapters = json.load(json_file)
                        if str(chapter_number) in chapters:
                            return jsonify({chapter_number: chapters[str(chapter_number)]})
                        return jsonify({"error": "Chapter not found"}), 404
                # Fallback: read individual chapter file
                chapter_path = os.path.join(
                    app.root_path, 
                    'templates', 
                    'novels', 
                    novel_name, 
                    f'chapter-{int(chapter_number)}.txt' if isinstance(chapter_number, int) else f'chapter-{int(chapter_number)}-{str(chapter_number).split(".")[1]}.txt'
                )
                if os.path.exists(chapter_path):
                    with open(chapter_path, 'r', encoding='utf-8') as f:
                        content = f.read().replace('<br>', '\n')
                        return jsonify({chapter_number: content})
                return jsonify({"error": "Chapter not found"}), 404

            except ValueError as e:
                return jsonify({"error": f"Invalid chapter number: {str(e)}"}), 400

        # Handle full chapter list request
        novel_name = urllib.parse.unquote(novel_name).replace('+', ' ')
        if not novel_name.endswith('-chapters'):
            novel_name = novel_name + '-chapters'
        json_path = os.path.join(app.root_path, 'templates', 'novels', novel_name, 'chapters.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as json_file:
                return jsonify(json.load(json_file))
        else:
            chapters = fetch_chapters_for_novel(novel_name)
            create_chapters_json(novel_name)
            return jsonify(chapters)

    except Exception as e:
        logger.error(f"Error in get_chapters: {e}")
        return jsonify({"error": str(e)}), 500





@app.route('/read', methods=['GET'])
def read_chapter():
    novel_name = request.args.get('n')
    chapter_number = request.args.get('c')

    if not novel_name or not chapter_number:
        return render_template('error.html'), 400
    print(novel_name)
    print(chapter_number)
    novel_name = urllib.parse.unquote(novel_name).replace(' ', ' ').replace("'", "%27") #.replace('-', '%2D')
    
    # Convert chapter_number to float if it contains a decimal
    chapter_number = float(chapter_number) if '.' in str(chapter_number) else int(chapter_number)
    
    # Fetch chapters from API
    json_path = os.path.join(app.root_path, 'templates', 'novels', novel_name.replace("%27", "'"), 'chapters.json')        
    if not os.path.exists(json_path):
        create_chapters_json(novel_name.replace("%27", "'"))
        
    

    
    return render_template('chapterPage.html', novel_title=novel_name, chapter_number=chapter_number, novel_title_clean=novel_name[:-9].replace("%27", "'"))


@app.route('/novels/<novel>/chapters/<chapter_number>')
def goToNewRouteChapters(novel, chapter_number):
    return redirect(url_for('read_chapter', n=novel, c=chapter_number))

@app.route('/novels/<novel>')
def goToNewRouteNovels(novel):
    return redirect(url_for('novels_chapters', n=novel))



    
@app.route('/p-notes')
def patchNotes():
    return render_template("patchNotes.html")



@app.route('/plans')
def show_plans():
    """
    This function handles the '/plans' route and renders the 'plans.html' template.

    Parameters:
    None

    Returns:
    render_template: A rendered HTML template named 'plans.html'.
    """
    return render_template('plans.html')




@app.route('/currentChapter')
def currentChapter():
    """
    This function handles the '/currentChapter' route and renders the 'currentChapter.html' template.

    Parameters:
    None

    Returns:
    render_template: A rendered HTML template named 'currentChapter.html'.
    """
    return render_template('currentChapter.html')




@app.route('/novels/<novel_title>')
def show_novel_chapters(novel_title):
    """
    Display the chapters of a novel.

    Parameters:
    novel_title (str): The title of the novel.

    Returns:
    render_template: A rendered HTML template with the novel's title, chapter numbers, and categories.
                      If an exception occurs, it returns an error message and renders an error template.
    """
    try:
        novel_folder_path = os.path.join(app.root_path, 'templates', 'novels', novel_title)
        
        # List all chapter files in the novel's folder
        chapters = [file for file in os.listdir(novel_folder_path) if file.endswith('.txt')]
        
        # Read the categories file if it exists
        categories_file = os.path.join(novel_folder_path, 'categories.txt')
        if os.path.exists(categories_file):
            with open(categories_file, 'r', encoding='utf-8') as f:
                categories = f.read().strip().split('\n')
                categories_str = ', '.join(categories)
        else:
            categories_str = ""

        # Filter out the categories file from the chapters list
        chapters = [file for file in chapters if not file.startswith(('categories', 'base_url_number', 'readWebNovel', 'webNovelDotCom'))]

        # Extract the chapter numbers from the chapter files, handling decimal chapters
        chapter_numbers = []
        for file in chapters:
            # Extract everything between 'chapter-' and '.txt'
            match = re.search(r'chapter-(.+?)\.txt', file)
            if match:
                chapter_num = match.group(1)
                try:
                    # Handle cases like "12-1" by converting to "12.1"
                    num = float(chapter_num.replace('-', '.'))
                    # Convert to int if it's a whole number
                    chapter_numbers.append(int(num) if num.is_integer() else num)
                except ValueError:
                    continue

        # Sort the chapter numbers
        chapter_numbers.sort()

        # Clean the novel title by removing anything within brackets
        novel_title_clean = re.sub(r'\s*\(.*?\)', '', novel_title[:-9] if len(novel_title) >= 9 else novel_title)

        # Prepare the categories string
        categories_string = f"{categories_str}" if categories_str else ""

        # Render the novelsChapters.html template with the necessary data
        return render_template('novelsChapters.html', novel_title2=novel_title_clean, chapters=chapter_numbers, novel_title1=novel_title, categories=categories_string)
    
    except Exception as e:
        # Handle any exceptions that occur during the execution of the function
        error_message = str(e)
        send_discord_message(error_message)
        return render_template('error.html'), 500




def transform_title(novel_title):
    """
    Transform the novel title for URL:
    1. Decode URL-encoded characters.
    2. Remove anything within brackets (including brackets).
    3. Convert to lowercase.
    4. Replace special characters and spaces with hyphens.
    5. Remove trailing hyphens and spaces.
    """
    # First decode any URL-encoded characters
    novel_title = urllib.parse.unquote(novel_title)
    
    # Handle the -chapters suffix
    if novel_title.endswith('-chapters'):
        novel_title = novel_title[:-9]
    
    # Keep apostrophes and spaces, but remove other special characters
    transformed_title = novel_title.replace('+', ' ')  # Replace + with space
    transformed_title = transformed_title.strip()  # Remove leading/trailing whitespace
    
    # Add -chapters suffix
    transformed_title += '-chapters'
    
    print(f"Transformed title: {transformed_title}")
    return transformed_title







@app.route('/images/<novel_title>')
def serve_image(novel_title):
    """
    Serves the cover image of a novel.

    This function constructs the path to the cover image of a novel based on the provided novel title.
    It then checks if the image file exists at the constructed path. If the image exists, it sends the image file
    as a response with the appropriate MIME type. If the image does not exist, it returns a 404 status code with a message
    indicating that the image was not found.

    Parameters:
    novel_title (str): The title of the novel for which the cover image is to be served. This parameter is extracted
                        from the URL and passed to the function.

    Returns:
    send_file: If the image file exists, it returns a response with the image file and the appropriate MIME type.
    str, int: If the image file does not exist, it returns a 404 status code with a message indicating that the image was not found.
    """
    try:
        image_path = os.path.join(app.root_path, 'templates', 'novels', novel_title, 'cover_image.jpg')
        if os.path.exists(image_path):
            return send_file(image_path, mimetype='image/jpeg')
        else:
            return "Image not found", 404
    except Exception as e:
        error_message = str(e)
        send_discord_message(error_message)
        return "Error serving image", 500




@app.route('/update_novel/<novel_title>', methods=['POST'])
def update_novel(novel_title):
    """
    This function handles the POST request to update a novel. It fetches the novel title from the request JSON data,
    validates it, and then calls the 'updateNovel.yes' and 'withoutLink' functions to update the novel.

    Parameters:
    novel_title (str): The title of the novel to be updated. This parameter is extracted from the URL and passed to the function.

    Returns:
    jsonify: A JSON response containing the status, message, and result of the update operation.
              If the update is successful, the status will be 'success', the message will indicate the successful update,
              and the result will be the output of the 'updateNovel.yes' function.
              If an exception occurs during the update process, the status will be 'error', the message will contain the error message,
              and the result will be None.
    """
    try:
        print(f"Received request to update novel: {novel_title}")  # Debugging statement
        novel_title2 = request.json.get('novelTitle2')
        print(f"Received novelTitle2: {novel_title2}")  # Debugging statement

        if novel_title2 is None:
            raise ValueError("novelTitle2 is missing or None.")
        
        print("Calling webscrapers.updateNovel.yes function...")  # Debugging statement
        result = webscrapers.updateNovel.yes(novel_title2)

        # After update, make sure metadata.json exists
        novel_path = os.path.join(app.root_path, 'templates', 'novels', novel_title)
        metadata_path = os.path.join(novel_path, 'metadata.json')
        if not os.path.exists(metadata_path):
            # Create metadata from categories if possible
            get_novel_metadata(novel_title)

        return jsonify({"status": "success", "message": f"{novel_title} updated successfully.", "result": result})
    except Exception as e:
        print(f"Exception occurred: {str(e)}")  # Debugging statement
        return jsonify({"status": "error", "message": str(e)}), 500




@app.route('/update_novel/<novel_title>')
def youShouldNotBeHere(novel_title):
    """
    This function is a route handler for the '/update_novel/<novel_title>' endpoint.
    It is intended to render a template named 'notHere.html' with a 'novel_title' variable.
    This function is not meant to be accessed directly, and is used as a placeholder for a potential future feature.

    Parameters:
    novel_title (str): The title of the novel for which the update is requested.
                       This parameter is extracted from the URL and passed to the function.

    Returns:
    render_template: A rendered HTML template with the 'novel_title' variable passed to it.
    """
    return render_template('notHere.html', novel_title=novel_title)







@app.route('/popular-novels')
def popular_novels():
    """
    Display a page with three randomly selected popular novels.

    The function retrieves all novels from the 'novels' directory, selects three at random if there are at least three novels,
    and retrieves the necessary data for each selected novel, such as categories and cover image.

    Parameters:
    None

    Returns:
    render_template: A rendered HTML template with the selected novels' data.
    If an exception occurs, it returns an error message and renders an error template.
    """
    try:
        novels_folder_path = os.path.join(app.root_path, 'templates', 'novels')
        
        # Ensure the novels directory exists
        os.makedirs(novels_folder_path, exist_ok=True)
        
        novels_with_data = []
        all_categories = set()
        
        
        for novel in os.listdir(novels_folder_path):
            if novel == "The%20Beginning%20After%20The%20End-chapters":
                continue
            
            novel_path = os.path.join(novels_folder_path, novel)
            
            # Get metadata instead of reading categories.txt
            metadata = get_novel_metadata(novel)
            categories = metadata.get("categories", [])
            categories_str = ", ".join(categories)
            all_categories.update(categories)
            
            novel_name_clean = re.sub(r'\s*\(.*?\)', '', novel[:-9] if len(novel) >= 9 else novel)
            novels_with_data.append((novel, novel_name_clean, categories_str))
        
        # Sort novels alphabetically
        novels_with_data.sort(key=lambda x: x[1].lower())
        
        return render_template(
            'popularNovels.html', 
            novels=novels_with_data[:3], 
        )
    except Exception as e:
        error_message = str(e)
        send_discord_message(error_message)
        return render_template('error.html'), 500



@app.route('/webscrapers')
def webscraperss():
    """
    This function retrieves the names of all web scrapers in the 'webscrapers' directory.
    
    Parameters:
    None
    
    Returns:
    render_template: A rendered HTML template with the number of web scrapers and their names.
    """
    path = os.path.join(app.root_path, 'webscrapers')
    directory_names = []
    
    for root, dirs, files in os.walk(path):
        for dir_name in dirs:
            if dir_name != '__pycache__':
                directory_names.append(dir_name)  # Just the directory name, not the full path
    
    return render_template('webscrapers.html', noOfWebscrapers=len(directory_names), webscraperName=directory_names)



def get_chapter_keys(novel_name):
    """
    Retrieve chapter keys from JSON file or generate from text files.
    
    Args:
        novel_name (str): Name of the novel
    
    Returns:
        list: Sorted list of chapter keys
    """
    novel_path = os.path.join(app.root_path, 'templates', 'novels', novel_name)
    json_path = os.path.join(novel_path, 'chapters.json')
    
    def parse_chapter_number(num):
        return int(num) if num.is_integer() else num

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            chapters = json.load(f)
        
        chapter_keys = sorted(parse_chapter_number(float(k)) for k in chapters.keys())
        return chapter_keys
    
    except (FileNotFoundError, json.JSONDecodeError):
        chapters = [f for f in os.listdir(novel_path) if f.startswith('chapter-') and f.endswith('.txt')]
        
        chapter_keys = []
        for chapter in chapters:
            parts = chapter.split('-')
            if len(parts) == 3:
                try:
                    chapter_number = float(f"{parts[1]}.{parts[2].split('.')[0]}")
                except ValueError:
                    continue
            else:
                try:
                    chapter_number = int(parts[1].split('.')[0])
                except ValueError:
                    continue
            chapter_keys.append(parse_chapter_number(chapter_number))
        
        return sorted(chapter_keys)

def get_novel_categories(novel_name):
    """Get categories from metadata"""
    metadata = get_novel_metadata(novel_name)
    return metadata.get("categories", [])

def get_novel_summary(novel_name):
    """Get summary from metadata"""
    metadata = get_novel_metadata(novel_name)
    return metadata.get("summary", "")

def get_novel_last_updated(novel_name):
    """Get last updated date from metadata"""
    metadata = get_novel_metadata(novel_name)
    return metadata.get("last_updated", "")

def get_novel_metadata(novel_name):
    """
    Retrieve metadata for a novel from metadata.json
    
    Args:
        novel_name (str): Name of the novel
    
    Returns:
        dict: Novel metadata including title, categories, summary, and last_updated
    """
    novel_path = os.path.join(app.root_path, 'templates', 'novels', novel_name)
    metadata_path = os.path.join(novel_path, 'metadata.json')
    
    # Default empty metadata
    default_metadata = {
        "title": novel_name[:-9] if novel_name.endswith('-chapters') else novel_name,
        "categories": [],
        "summary": "",
        "last_updated": ""
    }
    
    # Try to read from metadata.json
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error reading metadata.json for {novel_name}")
            return default_metadata
    
    # Fallback: Use existing categories.txt for backward compatibility
    categories_file = os.path.join(novel_path, 'categories.txt')
    if os.path.exists(categories_file):
        print(f"Using legacy categories.txt for {novel_name} - consider updating to metadata.json")
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories = [line.strip() for line in f if line.strip()]
        
        # Create metadata.json from categories.txt for future use
        metadata = default_metadata.copy()
        metadata["categories"] = categories
        metadata["last_updated"] = time.strftime('%Y-%m-%d')
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            print(f"Created metadata.json for {novel_name} from categories.txt")
        except Exception as e:
            print(f"Error creating metadata.json: {e}")
        
        return metadata
    
    return default_metadata


@app.route('/novels_chapters')
def novels_chapters():
    """
    Route to display list of chapters for a novel.
    
    Returns:
        Rendered template with chapter keys and metadata
    """
    novel_name = request.args.get('n')
    if not novel_name:
        return "No novel specified", 400
    
    chapterNumber = request.args.get('c')
    if chapterNumber:
        return redirect(url_for('read_chapter', n=novel_name, c=chapterNumber))
    
    try:
        # Get metadata (single function call now gets all information)
        metadata = get_novel_metadata(novel_name)
        categories_str = ", ".join(metadata.get("categories", []))
        summary = metadata.get("summary", "")
        last_updated = metadata.get("last_updated", "")
        title = metadata.get("title", novel_name[:-9] if novel_name.endswith('-chapters') else novel_name)
        
        # If it's a string, convert it to a Unix timestamp (float)
        if isinstance(last_updated, str):
            try:
                # Assuming the format is "YYYY-MM-DD"
                dt = datetime.datetime.strptime(last_updated, "%Y-%m-%d")
                last_updated = dt.timestamp()  # returns a float (seconds since epoch)
            except ValueError:
                # If parsing fails, leave it as is or handle the error
                pass
        
        # Get chapters (existing code remains the same)
        novel_path = os.path.join(app.root_path, 'templates', 'novels', novel_name)
        chapter_keys = get_chapter_keys(novel_name)
        
        return render_template('novelsChapters.html', 
                              chapters=chapter_keys, 
                              novel_title=novel_name,
                              novel_title2=title,
                              categories=categories_str,
                              summary=summary,
                              last_updated=last_updated,
                              novel_title_clean=novel_name[:-9] if novel_name.endswith('-chapters') else novel_name)
    except Exception as e:
        error_message = str(e)
        send_discord_message(error_message)
        return render_template('error.html'), 500


#
@app.route('/novels')
def list_novels():
    """
    List and display novels in the 'novels' directory.

    This function retrieves all novels from the 'novels' directory, reads their categories, and prepares the data for display.
    If a novel does not have a 'categories.txt' file, an empty string is assigned to its categories.
    The novels are then sorted by their names and displayed in the 'novels.html' template.
    Novels with the title "The%20Beginning%20After%20The%20End-chapters" are ignored.

    Parameters:
    None

    Returns:
    render_template: A rendered HTML template with the novels' data.
                     If an exception occurs, it returns an error message and renders an error template.
    """
    try:
        novels_folder_path = os.path.join(app.root_path, 'templates', 'novels')
        
        # Ensure the novels directory exists
        os.makedirs(novels_folder_path, exist_ok=True)
        
        novels_with_data = []
        all_categories = set()
        
        
        for novel in os.listdir(novels_folder_path):
            if novel == "The%20Beginning%20After%20The%20End-chapters":
                continue
            
            novel_path = os.path.join(novels_folder_path, novel)
            
            # Get metadata instead of reading categories.txt
            metadata = get_novel_metadata(novel)
            categories = metadata.get("categories", [])
            last_updated = metadata.get("last_updated", "")
            categories_str = ", ".join(categories)
            all_categories.update(categories)
            
            novel_name_clean = re.sub(r'\s*\(.*?\)', '', novel[:-9] if len(novel) >= 9 else novel)
            novels_with_data.append((novel, novel_name_clean, categories_str, last_updated))
        
        # Sort novels alphabetically
        novels_with_data.sort(key=lambda x: x[1].lower())
        sorted_categories = sorted(all_categories, key=lambda x: x.lower())
        
        total_novels = sum(
            os.path.isdir(os.path.join(novels_folder_path, novel)) 
            and novel != "The%20Beginning%20After%20The%20End-chapters"
            for novel in os.listdir(novels_folder_path)
        )
        
        return render_template(
            'novels.html', 
            novels=novels_with_data, 
            all_categories=sorted_categories, 
            total_novels=total_novels
        )
    except Exception as e:
        error_message = str(e)
        send_discord_message(error_message)
        return render_template('error.html'), 500





@app.template_filter('nl2br')
def nl2br_filter(text: str):
    """Convert newlines to HTML line breaks"""
    if not text:
        return text
    return text.replace('\n', '<br>')




if __name__ == "__main__":
    try:
        logger.header("Welcome to the Novel Reader developed by Bernso")
        
        logger.info(f"Starting Flask application on {Config.HOST}:{Config.PORT}")
        app.run(
            debug=Config.DEBUG, 
            host=Config.HOST, 
            port=Config.PORT
        )
    except Exception as e:
        logger.error(f"Error running the app: {e}")
        input(f"Critical error: {e}")

