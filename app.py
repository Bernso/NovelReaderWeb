try:
    from flask import Flask, render_template, request, jsonify, session
    import os
    import genChapters
    import re
    import updateNovel
    import requests
    import urllib
    import json
    from dotenv import load_dotenv
except ImportError as e:
    input(f"Module not found: {e}")




def send_discord_message(message):
    load_dotenv()
    webhook_url = os.getenv("WEBHOOK_URL")
    data = {
        "content": message,
        "username": "WebhookBot"
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(webhook_url, data=json.dumps(data), headers=headers)

    if response.status_code == 204:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Response status code: {response.status_code}")
        print(f"Response body: {response.text}")




app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")




@app.route('/test')
def test_site():
    return render_template('test.html')


@app.route('/')
def home():
    return render_template('home.html')




@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404




@app.route('/run_script', methods=['POST'])
def run_script():
    try:
        novel_link = request.json.get('novelLink')
        result = genChapters.yes(base_url=novel_link)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500








@app.route('/novels/<novelTitle>/chapters/<int:chapter_number>')
def show_chapter(novelTitle, chapter_number):   
    try:
        # Construct the path to the novel's subfolder
        subfolder_path = os.path.join(app.root_path, 'templates', 'novels', novelTitle)

        # Check if the directory exists
        if not os.path.exists(subfolder_path):
            print(f"Directory not found: {subfolder_path}")
            return render_template('chapterNotFound.html'), 404

        # List and sort text files in the subfolder
        text_files = [file for file in os.listdir(subfolder_path) if file.endswith('.txt')]
        valid_files = sorted([file for file in text_files if re.match(r'chapter-(\d+)\.txt', file)],
                             key=lambda x: int(re.match(r'chapter-(\d+)\.txt', x).group(1)))

        # Check if the chapter number is within the valid range
        if not valid_files or chapter_number < 1 or chapter_number > int(re.match(r'chapter-(\d+)\.txt', valid_files[-1]).group(1)):
            print(f"Chapter number {chapter_number} is out of range or no valid chapters found.")
            return render_template('chapterNotFound.html'), 404

        # Access the correct chapter file
        chapter_file = f'chapter-{chapter_number}.txt'
        if chapter_file not in valid_files:
            print(f"Chapter file {chapter_file} not found in valid files.")
            return render_template('chapterNotFound.html'), 404

        # Read the chapter content
        chapter_path = os.path.join(subfolder_path, chapter_file)
        with open(chapter_path, 'r', encoding='utf-8') as f:
            chapter_text = f.read()

        # Clean and encode the novel title for display and URL
        novel_title_clean = re.sub(r'\s*\(.*?\)', '', novelTitle[:-9] if len(novelTitle) >= 9 else novelTitle)
        novel_title_encoded = novelTitle.replace(' ', '%20')

        session[f'last_read_{novelTitle}'] = chapter_number

        return render_template('chapterPage.html',
                               novel_title_clean=novel_title_clean,
                               novel_title_encoded=novel_title_encoded,
                               chapter_number=chapter_number,
                               chapter_text=chapter_text)

    except FileNotFoundError:
        print(f"FileNotFoundError: Chapter file for {novelTitle}, chapter {chapter_number} not found.")
        return render_template('chapterNotFound.html'), 404
    except IndexError as e:
        print(f"IndexError: {str(e)}")
        return render_template('chapterNotFound.html'), 404
    except Exception as e:
        error_message = str(e)
        print(f"Exception: {error_message}")
        send_discord_message(error_message)
        return render_template('error.html'), 500



    



@app.route('/plans')
def show_plans():
    return render_template('plans.html')




@app.route('/currentChapter')
def currentChapter():
    return render_template('currentChapter.html')




@app.route('/novels/<novel_title>')
def show_novel_chapters(novel_title):
    try:
        novel_folder_path = os.path.join(app.root_path, 'templates', 'novels', novel_title)
        
        chapters = [file for file in os.listdir(novel_folder_path) if file.endswith('.txt')]
        
        categories_file = os.path.join(novel_folder_path, 'categories.txt')
        if os.path.exists(categories_file):
            with open(categories_file, 'r', encoding='utf-8') as f:
                categories = f.read().strip().split('\n')
                categories_str = ', '.join(categories)
        else:
            categories_str = ""

        chapters = [file for file in chapters if not file.startswith('categories')]

        chapter_numbers = [int(file.split('-')[1].split('.')[0]) for file in chapters]

        chapter_numbers.sort()

        novel_title_clean = re.sub(r'\s*\(.*?\)', '', novel_title[:-9] if len(novel_title) >= 9 else novel_title)

        categories_string = f"{categories_str}" if categories_str else ""

        return render_template('novelsChapters.html', novel_title2=novel_title_clean, chapters=chapter_numbers, novel_title1=novel_title, categories=categories_string)
    
    except Exception as e:
        error_message = str(e)
        send_discord_message(error_message)
        return render_template('error.html'), 500


def transform_title(novel_title):

    """

    Transform the novel title for URL:

    1. Decode URL-encoded characters.

    2. Convert to lowercase.

    3. Replace special characters and spaces with hyphens.

    """

    decoded_title = urllib.parse.unquote(novel_title)

    transformed_title = decoded_title.lower()

    transformed_title = re.sub(r"[''']", "", transformed_title)  # Remove special apostrophes

    transformed_title = re.sub(r'[^a-zA-Z0-9\s]', '', transformed_title)  # Remove non-alphanumeric characters

    transformed_title = transformed_title.replace(" ", "-")

    transformed_title = transformed_title.replace(":", "")

    transformed_title = transformed_title.replace("/", "")  # Remove slashes

    return transformed_title





@app.route('/novels')

def list_novels():

    try:

        # Path to the novels folder

        novels_folder_path = os.path.join(app.root_path, 'templates', 'novels')



        # List directories only, assuming each novel has its own directory

        novels_with_data = []

        emojis = ["🌙", "📚", "✨", "🌟", "🔥", "🌹", "💫", "📖"]



        for novel in os.listdir(novels_folder_path):

            novel_path = os.path.join(novels_folder_path, novel)

            categories_file = os.path.join(novel_path, 'categories.txt')



            if os.path.exists(categories_file):

                with open(categories_file, 'r', encoding='utf-8') as f:

                    categories = f.read().strip().split('\n')

                    categories_str = ', '.join(categories)

            else:

                categories_str = ""



            novel_name_clean = re.sub(r'\s*\(.*?\)', '', novel[:-9] if len(novel) >= 9 else novel)

            novels_with_data.append((novel, novel_name_clean, categories_str))



        return render_template('novels.html', novels=novels_with_data, emojis=emojis)



    except Exception as e:

        error_message = str(e)

        send_discord_message(error_message)

        return render_template('error.html'), 500








@app.route('/update_novel/<novel_title>', methods=['POST'])
def update_novel(novel_title):
    try:
        novel_title2 = request.json.get('novelTitle2')  

        if novel_title2 is None:
            raise ValueError("novelTitle2 is missing or None.")

        result = updateNovel.yes(novel_title2)
        
        return jsonify({"status": "success", "message": f"{novel_title} updated successfully.", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500




@app.route('/update_novel/<novel_title>')
def youShouldntBeHere(novel_title):
    return render_template('notHere.html', novel_title=novel_title)








if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        input(f"Error running the app: {e}")

