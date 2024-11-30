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
    from flask import Flask, render_template, request, jsonify, session, send_file
    import os
    import re  
    import random
    import requests
    import json
    import logging
    import logging.config 
    import urllib.parse  # Add this import for URL decoding
    
    # Project-specific imports
    from config import Config
    from dotenv import load_dotenv
except ImportError as e:
    input(f"Module not found: {e}")

# Configure logging
logging.config.dictConfig(Config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

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




currentPath = os.getcwd()




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
    """
    This function handles the root route ('/') and renders the 'home.html' template
    with statistics about the novels, chapters, and categories.

    Parameters:
    None

    Returns:
    render_template: A rendered HTML template named 'home.html' with statistics.
    """
    try:
        novels_folder_path = os.path.join(app.root_path, 'templates', 'novels')
        total_novels = 0
        total_chapters = 0
        all_categories = set()

        for novel in os.listdir(novels_folder_path):
            novel_path = os.path.join(novels_folder_path, novel)
            if os.path.isdir(novel_path):
                total_novels += 1

                json_path = os.path.join(novel_path, 'chapters.json')
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        total_chapters += len(json.load(f))
                else:
                    chapters = [file for file in os.listdir(novel_path) if file.endswith('.txt') and file.startswith('chapter-')]
                    total_chapters += len(chapters)

                categories_file = os.path.join(novel_path, 'categories.txt')
                if os.path.exists(categories_file):
                    with open(categories_file, 'r', encoding='utf-8') as f:
                        all_categories.update(line.strip() for line in f if line.strip())

        return render_template('home.html',
                               total_novels=total_novels,
                               total_chapters=total_chapters,
                               total_categories=len(all_categories))   
    except Exception as e:
        send_discord_message(str(e))
        return render_template('error.html'), 500




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
        result = webscrapers.lightNovelPubDotVip.genChapters.yes(base_url=novel_link)
        webscrapers.lightNovelPubDotVip.getPics.main(base_url=novel_link) 
        return jsonify({"result": result})
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
def get_chapters():
    """
    Get chapter(s) for a novel. If a specific chapter is requested via the 'c' parameter,
    only that chapter is returned. Otherwise, all chapters are returned.
    """
    try:
        novel_name = request.args.get('n', '')
        chapter_number = request.args.get('c', '')
        
        # Clean up any text files if JSON exists
        if novel_name:
            decoded_name = urllib.parse.unquote(novel_name).replace('+', ' ')
            if not decoded_name.endswith('-chapters'):
                decoded_name = decoded_name + '-chapters'
            cleanup_chapter_files(decoded_name)
        
        # Handle single chapter request
        if chapter_number:
            try:
                # Convert chapter number to appropriate type (float or int)
                chapter_number = float(chapter_number) if '.' in chapter_number else int(chapter_number)
                
                # URL decode the novel name
                novel_name = urllib.parse.unquote(novel_name).replace('+', ' ')
                if not novel_name.endswith('-chapters'):
                    novel_name = novel_name + '-chapters'
                
                # Check for JSON file first
                json_path = os.path.join(app.root_path, 'templates', 'novels', novel_name, 'chapters.json')
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as json_file:
                        chapters = json.load(json_file)
                        if str(chapter_number) in chapters:
                            return {chapter_number: chapters[str(chapter_number)]}
                        return jsonify({"error": "Chapter not found"}), 404
                
                # If no JSON file, look for individual chapter file
                chapter_path = os.path.join(
                    app.root_path, 
                    'templates', 
                    'novels', 
                    novel_name, 
                    f'chapter-{int(chapter_number)}.txt' if chapter_number.is_integer() 
                    else f'chapter-{int(chapter_number)}-{str(chapter_number).split(".")[1]}.txt'
                )
                
                if os.path.exists(chapter_path):
                    with open(chapter_path, 'r', encoding='utf-8') as f:
                        content = f.read().replace('<br>', '\n')
                        return {chapter_number: content}
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
                return json.load(json_file)
        else:
            chapters = fetch_chapters_for_novel(novel_name)
            create_chapters_json(novel_name)
            return chapters
            
    except Exception as e:
        print(f"Error in get_chapters: {str(e)}")
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
        if not os.path.exists(f"{currentPath}/templates/novels"):
            os.makedirs(f"{currentPath}/templates/novels")
        else:
            print("Novel folder already exists")

        novels_folder_path = os.path.join(app.root_path, 'templates', 'novels')
        novels_with_data = []
        emojis = ["🌙", "📚", "✨", "🌟", "🔥", "🌹", "💫", "📖"]

        all_categories = set()
        
        for novel in os.listdir(novels_folder_path):
            if novel == "The%20Beginning%20After%20The%20End-chapters":
                continue
            novel_path = os.path.join(novels_folder_path, novel)
            categories_file = os.path.join(novel_path, 'categories.txt')
            print(novel[:-9])
            if os.path.exists(categories_file):
                with open(categories_file, 'r', encoding='utf-8') as f:
                    categories = [line.strip() for line in f if line.strip()]
                    categories_str = ', '.join(categories)
                    all_categories.update(categories)
            else:
                categories_str = ""

            novel_name_clean = re.sub(r'\s*\(.*?\)', '', novel[:-9] if len(novel) >= 9 else novel)
            novels_with_data.append((novel, novel_name_clean, categories_str))

        sorted_categories = sorted(all_categories, key=lambda x: x.lower())

        total_novels = len([novel for novel in os.listdir(novels_folder_path) if os.path.isdir(os.path.join(novels_folder_path, novel)) and novel != "The%20Beginning%20After%20The%20End-chapters"])

        return render_template('novels.html', novels=novels_with_data, emojis=emojis, all_categories=sorted_categories, total_novels=total_novels)
    except Exception as e:
        error_message = str(e)
        send_discord_message(error_message)
        return render_template('error.html'), 500




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




def fetch_popular_novels():
    """
    Fetch three popular novels from the 'novels' directory.

    The function retrieves all novels from the 'novels' directory, selects three at random if there are at least three novels,
    and returns the selected novels. If there are less than three novels, it returns all novels.

    Parameters:
    None

    Returns:
    list: A list of three randomly selected novels from the 'novels' directory.
          If there are less than three novels, it returns all novels.
    """
    novels_folder_path = os.path.join(app.root_path, 'templates', 'novels')
    all_novels = [novel for novel in os.listdir(novels_folder_path) if os.path.isdir(os.path.join(novels_folder_path, novel))]
    popular_novels = random.sample(all_novels, 3) if len(all_novels) >= 3 else all_novels
    return popular_novels



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
        all_novels = [novel for novel in os.listdir(novels_folder_path) if os.path.isdir(os.path.join(novels_folder_path, novel))]

        if len(all_novels) < 3:
            popular_novels = all_novels
        else:
            popular_novels = random.sample(all_novels, 3)

        novels_with_data = []
        emojis = ["🌙", "📚", "✨", "🌟", "🔥", "🌹", "💫", "📖"]

        all_categories = set()

        for novel in popular_novels:
            novel_path = os.path.join(novels_folder_path, novel)
            categories_file = os.path.join(novel_path, 'categories.txt')
            if os.path.exists(categories_file):
                with open(categories_file, 'r', encoding='utf-8') as f:
                    categories = [line.strip() for line in f if line.strip()]
                    categories_str = ', '.join(categories)
                    all_categories.update(categories)
            else:
                categories_str = ""

            novel_name_clean = re.sub(r'\s*\(.*?\)', '', novel[:-9] if len(novel) >= 9 else novel)
            novels_with_data.append((novel, novel_name_clean, categories_str))
 
        # Sort the categories by words
        sorted_categories = sorted(all_categories, key=lambda x: x.lower())

        return render_template('popularNovels.html', novels=novels_with_data, emojis=emojis, all_categories=sorted_categories)
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
    path = os.path.join(os.getcwd(), 'webscrapers')
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
                chapter_number = float(f"{parts[1]}.{parts[2].split('.')[0]}")
            else:
                chapter_number = int(parts[1].split('.')[0])
            chapter_keys.append(parse_chapter_number(chapter_number))
        
        return sorted(chapter_keys)
def get_novel_categories(novel_name):
    """
    Retrieve categories for a given novel.
    
    Args:
        novel_name (str): Name of the novel
    
    Returns:
        str: Comma-separated list of categories, or empty string if not found
    """
    novel_path = os.path.join(app.root_path, 'templates', 'novels', novel_name)
    categories_file = os.path.join(novel_path, 'categories.txt')
    
    if os.path.exists(categories_file):
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories = [line.strip() for line in f if line.strip()]
        return ', '.join(categories)
    else:
        return ""

@app.route('/novels_chapters')
def novels_chapters():
    """
    Route to display list of chapters for a novel.
    
    Returns:
        Rendered template with chapter keys
    """
    novel_name = request.args.get('n')
    if not novel_name:
        return "No novel specified", 400
    
    try:
        novel_path = os.path.join(app.root_path, 'templates', 'novels', novel_name)
        json_path = os.path.join(novel_path, 'chapters.json')
        
        if os.path.exists(json_path):
            chapter_keys = get_chapter_keys(novel_name)
        else:
            chapters = [f for f in os.listdir(novel_path) if f.startswith('chapter-') and f.endswith('.txt')]
            chapter_keys = []
            for chapter in chapters:
                parts = chapter.split('-')
                if len(parts) == 3:
                    chapter_number = float(f"{parts[1]}.{parts[2].split('.')[0]}")
                else:
                    chapter_number = int(parts[1].split('.')[0])
                chapter_keys.append(chapter_number)
            chapter_keys.sort(key=lambda x: (int(x) if isinstance(x, int) else int(x.split('.')[0]), x))
        
        return render_template('novelsChapters.html', 
                               chapters=chapter_keys, 
                               novel_title=novel_name,
                               categories=get_novel_categories(novel_name),
                               novel_title_clean=novel_name[:-9])
    except Exception as e:
        error_message = str(e)
        send_discord_message(error_message)
        return render_template('error.html'), 500




if __name__ == "__main__":
    try:
        logger.info(f"Starting Flask application on {Config.HOST}:{Config.PORT}")
        app.run(
            debug=Config.DEBUG, 
            host=Config.HOST, 
            port=Config.PORT
        )
    except Exception as e:
        logger.critical(f"Error running the app: {e}")
        input(f"Critical error: {e}")

