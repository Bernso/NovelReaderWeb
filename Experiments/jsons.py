import os
import json

def create_chapters_json(novel_name):
    novel_path = os.path.join(os.getcwd(), 'templates', 'novels', novel_name)
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

    print(f"Chapters JSON file created for {novel_name}")



create_chapters_json('Reverend Insanity-chapters')