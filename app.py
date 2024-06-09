try:
    from flask import Flask, render_template, request, jsonify
    import os
    import genChapters
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
        result = genChapters.yes()
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chapters/<int:chapter_number>')
def show_chapter(chapter_number):
    try:
        subfolder_path = os.path.join(app.root_path, 'templates', 'chapters')
        html_files = [file for file in os.listdir(subfolder_path) if file.endswith('.html')]
        html_files.sort(key=lambda x: int(x.split('-')[1].split('.')[0]))

        if chapter_number < 1 or chapter_number > len(html_files):
            return render_template('chapterNotFound.html'), 404

        chapter_file = html_files[chapter_number - 1]  # Adjusting for 0-based index
        chapter_path = os.path.join(subfolder_path, chapter_file)
        with open(chapter_path, 'r', encoding='utf-8') as f:
            rendered_html = f.read()

        return rendered_html
    except FileNotFoundError:
        return render_template('chapterNotFound.html'), 404
    except Exception as e:
        return render_template('error.html', error_message=str(e)), 500

@app.route('/chapters')
def index():
    try:
        subfolder_path = os.path.join(app.root_path, 'templates', 'chapters')
        html_files = [file for file in os.listdir(subfolder_path) if file.endswith('.html')]
        chapter_numbers = [int(file.split('-')[1].split('.')[0]) for file in html_files]
        chapter_numbers.sort()

        return render_template('chapters.html', chapter_numbers=chapter_numbers)
    except Exception as e:
        return render_template('error.html', error_message=str(e)), 500

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        input(f"Error running the app: {e}")
