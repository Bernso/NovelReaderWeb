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
    folder_path = os.path.join('templates', 'novels')  # Path to the 'novels' directory
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
        # Get total number of novels
        novels_folder_path = os.path.join(app.root_path, 'templates', 'novels')
        total_novels = len([novel for novel in os.listdir(novels_folder_path) 
                          if os.path.isdir(os.path.join(novels_folder_path, novel))])

        # Get total number of chapters
        total_chapters = 0
        all_categories = set()

        # Iterate through each novel directory
        for novel in os.listdir(novels_folder_path):
            novel_path = os.path.join(novels_folder_path, novel)
            if os.path.isdir(novel_path):
                # Count chapters
                chapters = [file for file in os.listdir(novel_path) 
                          if file.endswith('.txt') and file.startswith('chapter-')]
                total_chapters += len(chapters)

                # Get categories
                categories_file = os.path.join(novel_path, 'categories.txt')
                if os.path.exists(categories_file):
                    with open(categories_file, 'r', encoding='utf-8') as f:
                        categories = [line.strip() for line in f if line.strip()]
                        all_categories.update(categories)

        # Get total number of unique categories
        total_categories = len(all_categories)

        return render_template('home.html', 
                             total_novels=total_novels,
                             total_chapters=total_chapters,
                             total_categories=total_categories)
    except Exception as e:
        error_message = str(e)
        send_discord_message(error_message)
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





@app.route('/novels/<novelTitle>/chapters/<int:chapter_number>')  # For whole numbers
def show_whole_chapter(novelTitle, chapter_number):   
    try:
        subfolder_path = os.path.join(app.root_path, 'templates', 'novels', novelTitle)
        
        # Get all chapter numbers
        chapters = []
        for file in os.listdir(subfolder_path):
            if file.startswith('chapter-') and file.endswith('.txt'):
                match = re.search(r'chapter-(.+?)\.txt', file)
                if match:
                    chapter_num = match.group(1)
                    try:
                        if '-' in chapter_num:
                            num = float(chapter_num.replace('-', '.'))
                        else:
                            num = float(chapter_num)
                        chapters.append(num)
                    except ValueError:
                        continue
        
        chapters.sort()
        
        # Find next and previous chapters
        next_chapter = None
        prev_chapter = None
        for i, num in enumerate(chapters):
            if num == chapter_number:
                if i > 0:
                    prev_chapter = chapters[i-1]
                if i < len(chapters)-1:
                    next_chapter = chapters[i+1]
                break

        # Rest of your existing code...
        chapter_file = f'chapter-{chapter_number}.txt'
        chapter_path = os.path.join(subfolder_path, chapter_file)
        
        if not os.path.exists(chapter_path):
            return render_template('chapterNotFound.html'), 404

        with open(chapter_path, 'r', encoding='utf-8') as f:
            chapter_text = f.read()

        novel_title_clean = re.sub(r'\s*\(.*?\)', '', novelTitle[:-9] if len(novelTitle) >= 9 else novelTitle)
        novel_title_encoded = novelTitle.replace(' ', '%20')

        session[f'last_read_{novelTitle}'] = chapter_number

        return render_template('chapterPage.html',
                           novel_title_clean=novel_title_clean,
                           novel_title_encoded=novel_title_encoded,
                           chapter_number=chapter_number,
                           chapter_text=chapter_text,
                           next_chapter=next_chapter,
                           prev_chapter=prev_chapter)

    except Exception as e:
        error_message = str(e)
        print(f"Exception: {error_message}")
        send_discord_message(error_message)
        return render_template('error.html'), 500


@app.route('/novels/<novelTitle>/chapters/<float:chapter_number>')  # Changed to float to handle all cases
def show_chapter(novelTitle, chapter_number):   
    try:
        subfolder_path = os.path.join(app.root_path, 'templates', 'novels', novelTitle)
        
        # Get all chapter numbers
        chapters = []
        for file in os.listdir(subfolder_path):
            if file.startswith('chapter-') and file.endswith('.txt'):
                match = re.search(r'chapter-(.+?)\.txt', file)
                if match:
                    chapter_num = match.group(1)
                    try:
                        if '-' in chapter_num:
                            # Convert "12-1" to 12.1
                            whole, decimal = chapter_num.split('-')
                            num = float(f"{whole}.{decimal}")
                        else:
                            num = float(chapter_num)
                        chapters.append(num)
                    except ValueError:
                        continue
        
        chapters.sort()
        
        # Find next and previous chapters
        next_chapter = None
        prev_chapter = None
        for i, num in enumerate(chapters):
            if abs(num - chapter_number) < 0.0001:  # Using small epsilon for float comparison
                if i > 0:
                    prev_chapter = chapters[i-1]
                if i < len(chapters)-1:
                    next_chapter = chapters[i+1]
                break

        # Determine the correct file name format
        if chapter_number.is_integer():
            chapter_file = f'chapter-{int(chapter_number)}.txt'
        else:
            whole = int(chapter_number)
            decimal = str(chapter_number).split('.')[1]
            chapter_file = f'chapter-{whole}-{decimal}.txt'
        
        chapter_path = os.path.join(subfolder_path, chapter_file)
        
        if not os.path.exists(chapter_path):
            return render_template('chapterNotFound.html'), 404

        with open(chapter_path, 'r', encoding='utf-8') as f:
            chapter_text = f.read()

        novel_title_clean = re.sub(r'\s*\(.*?\)', '', novelTitle[:-9] if len(novelTitle) >= 9 else novelTitle)
        novel_title_encoded = novelTitle.replace(' ', '%20')

        session[f'last_read_{novelTitle}'] = chapter_number

        return render_template('chapterPage.html',
                           novel_title_clean=novel_title_clean,
                           novel_title_encoded=novel_title_encoded,
                           chapter_number=chapter_number,
                           chapter_text=chapter_text,
                           next_chapter=next_chapter,
                           prev_chapter=prev_chapter)

    except Exception as e:
        error_message = str(e)
        print(f"Exception: {error_message}")
        send_discord_message(error_message)
        return render_template('error.html'), 500



    



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
    transformed_title = re.sub(r"[''']", "", novel_title)  # Remove special apostrophes
    transformed_title = re.sub(r'[^a-zA-Z0-9\s]', '', transformed_title)  # Remove non-alphanumeric characters
    transformed_title = transformed_title.replace(" ", "%20")
    transformed_title = transformed_title.rstrip('- ')  # Remove trailing hyphens and spaces
    transformed_title = transformed_title[:-8]
    transformed_title += '-chapters'
    return transformed_title





@app.route('/novels')
def list_novels():
    """
    List and display novels in the 'novels' directory.

    This function retrieves all novels from the 'novels' directory, reads their categories, and prepares the data for display.
    If a novel does not have a 'categories.txt' file, an empty string is assigned to its categories.
    The novels are then sorted by their names and displayed in the 'novels.html' template.

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

        # Sort the categories by words
        sorted_categories = sorted(all_categories, key=lambda x: x.lower())

        # Calculate the total number of novels available
        total_novels = len([novel for novel in os.listdir(novels_folder_path) if os.path.isdir(os.path.join(novels_folder_path, novel))])

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
