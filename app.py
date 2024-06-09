try:
    from flask import Flask, render_template, request, jsonify  
    import os
    import genChapters
except ImportError as e:
    input(e)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('404.html'), 404

@app.route('/run_script', methods=['GET', 'POST'])
def run_script():
    if request.method == 'POST':
         
        result = genChapters.yes()
        
        return result 
    else:
        return "This route only accepts POST requests."



@app.route('/chapters/<int:chapter_number>')
def show_chapter(chapter_number):
    subfolder_path = os.path.join(app.root_path, 'templates', 'chapters')

    html_files = [file for file in os.listdir(subfolder_path) if file.endswith('.html')]

    html_files.sort(key=lambda x: int(x.split('-')[1].split('.')[0]))   
     
    if chapter_number < 1 or chapter_number > len(html_files):
        return render_template('chapterNotFound.html')

    chapter_file = html_files[chapter_number - 1]  # Adjusting for 0-based index
    with open(os.path.join(subfolder_path, chapter_file), 'r', encoding='utf-8') as f:
        rendered_html = f.read()

    return rendered_html


@app.route('/chapters')
def index():
    subfolder_path = os.path.join(app.root_path, 'templates', 'chapters')

    html_files = [file for file in os.listdir(subfolder_path) if file.endswith('.html')]

    chapter_numbers = [int(file.split('-')[1].split('.')[0]) for file in html_files]

    chapter_numbers.sort()

    return render_template('chapters.html', chapter_numbers=chapter_numbers)




if __name__ == '__main__':
    try:
       app.run(debug=True)
    except Exception as e:
        input(e)