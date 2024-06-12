try:
    from flask import Flask, render_template, request, jsonify
    import os
    import genChapters
    import re
except ImportError as e:
    input(f"Module not found: {e}")

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
        
        # List/sort chapter files
        html_files = [file for file in os.listdir(subfolder_path) if file.endswith('.html')]
        html_files.sort(key=lambda x: int(x.split('-')[1].split('.')[0]))

        # Validate chapter number
        if chapter_number < 1 or chapter_number > len(html_files):
            return render_template('chapterNotFound.html'), 404

        chapter_file = html_files[chapter_number - 1]
        chapter_path = os.path.join(subfolder_path, chapter_file)

        with open(chapter_path, 'r', encoding='utf-8') as f:
            rendered_html = f.read()


        return rendered_html
    except FileNotFoundError:
        return render_template('chapterNotFound.html'), 404
    except Exception as e:
        return render_template('error.html', error_message=str(e)), 500
    

@app.route('/plans')
def show_plans():
     return render_template('plans.html')



@app.route('/novels/<novel_title>')
def show_novel_chapters(novel_title):
    try:
        novel_folder_path = os.path.join(app.root_path, 'templates', 'novels', novel_title)
        
        chapters = [file for file in os.listdir(novel_folder_path) if file.endswith('.html')]

        chapter_numbers = [int(file.split('-')[1].split('.')[0]) for file in chapters]

        chapter_numbers.sort()

        novel_title2 = re.sub(r'\s*\(.*?\)', '', novel_title[:-9] if len(novel_title) >= 9 else novel_title)
        
        
        # Novel title 2 is the one that is meant to look nice and is the one the suer is meant to see,
        # while novel title 1 is the one that is accurate and is the one the user is not meant to see

        return render_template('novelsChapters.html', novel_title2=novel_title2, chapters=chapter_numbers, novel_title1=novel_title)
    except Exception as e:
        return render_template('error.html', error_message=str(e)), 500

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
        
        print(novels_with_modified)
        
        return render_template('novels.html', novels=novels_with_modified)
    except Exception as e:
        return render_template('error.html', error_message=str(e)), 500


if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        input(f"Error running the app: {e}")
