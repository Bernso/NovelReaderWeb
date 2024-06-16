try:
    from flask import Flask, render_template, request, jsonify
    import os
    import genChapters
    import re
    import updateNovel
    import requests
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
        subfolder_path = os.path.join(app.root_path, 'templates', 'novels', novelTitle)
        
        text_files = [file for file in os.listdir(subfolder_path) if file.endswith('.txt')]
        text_files.sort(key=lambda x: int(x.split('-')[1].split('.')[0]))

        if chapter_number < 1 or chapter_number > len(text_files):
            return render_template('chapterNotFound.html'), 404

        chapter_file = text_files[chapter_number - 1]
        chapter_path = os.path.join(subfolder_path, chapter_file)

        with open(chapter_path, 'r', encoding='utf-8') as f:
            chapter_text = f.read()

        novel_title_clean = re.sub(r'\s*\(.*?\)', '', novelTitle[:-9] if len(novelTitle) >= 9 else novelTitle)
        
        
        
        novel_title_encoded = novelTitle.replace(' ', '%20')

        return render_template('chapterPage.html',
                               novel_title_clean=novel_title_clean,
                               novel_title_encoded=novel_title_encoded,
                               chapter_number=chapter_number,
                               chapter_text=chapter_text)

    except FileNotFoundError:
        return render_template('chapterNotFound.html'), 404
    except Exception as e:
        error_message = str(e)
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

        chapter_numbers = [int(file.split('-')[1].split('.')[0]) for file in chapters]

        chapter_numbers.sort()

        novel_title2 = re.sub(r'\s*\(.*?\)', '', novel_title[:-9] if len(novel_title) >= 9 else novel_title)
        
        
        # Novel title 2 is the one that is meant to look nice and is the one the suer is meant to see,
        # while novel title 1 is the one that is accurate and is the one the user is not meant to see

        return render_template('novelsChapters.html', novel_title2=novel_title2, chapters=chapter_numbers, novel_title1=novel_title)
    except Exception as e:
        error_message=str(e)
        send_discord_message(error_message)
        return render_template('error.html'), 500




@app.route('/novels')
def list_novels():
    try:
        # Path to the novels folder
        novels_folder_path = os.path.join(app.root_path, 'templates', 'novels')

        # List directories only, assuming each novel has its own directory
        novels = [folder for folder in os.listdir(novels_folder_path) 
                  if os.path.isdir(os.path.join(novels_folder_path, folder))]

        novels_with_modified = [
            (novel, re.sub(r'\s*\(.*?\)', '', novel[:-9] if len(novel) >= 9 else novel)) 
            for novel in novels
        ]
        emojis = ["🌙", "📚", "✨", "🌟", "🔥", "🌹", "💫", "📖"]
        print(novels_with_modified)
        
        return render_template('novels.html', novels=novels_with_modified, emojis=emojis)
    except Exception as e:
        error_message=str(e)
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

@app.route('/error_test')
def error_test():
    return render_template('error.html')


if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        input(f"Error running the app: {e}")
