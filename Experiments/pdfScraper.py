import pdfplumber
import re
import json

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def remove_links(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub('', text)

def fix_paragraphs(text):
    """
    Repairs paragraphs by joining lines broken by PDF formatting.
    Empty lines trigger a paragraph break.
    Also starts a new paragraph if a line begins with a capitalized word
    or a common paragraph starter.
    """
    paragraphs = []
    buffer = []
    
    # Regular expressions for detecting potential paragraph starts
    sentence_starter = re.compile(r"^[A-Z][a-z]")
    paragraph_starters = ["Chapter", "Meanwhile", "However", "Suddenly", "Then", "But"]
    
    lines = text.split("\n")
    
    for line in lines:
        line = line.strip()
        if not line:
            if buffer:
                paragraphs.append(" ".join(buffer))
                buffer = []
            continue
        
        # If the line appears to start a new paragraph, push the buffered text as a paragraph.
        if buffer and (sentence_starter.match(line) or any(line.startswith(word) for word in paragraph_starters)):
            paragraphs.append(" ".join(buffer))
            buffer = [line]
        else:
            buffer.append(line)
    
    if buffer:  # Append any remaining content as the last paragraph
        paragraphs.append(" ".join(buffer))
    
    return paragraphs

def split_into_chapters(paragraphs, n=10):
    """
    Groups every n paragraphs into a chapter.
    """
    chapters = []
    for i in range(0, len(paragraphs), n):
        chapter = "\n\n".join(paragraphs[i:i+n])
        chapters.append(chapter)
    return chapters

def work():
    content = {}
    global_chapter_count = 1  # Global chapter counter for all volumes

    # Process volumes 1 to 26 (adjust the range as needed)
    for volume in range(1, 27):
        pdf_path = fr"Experiments\rezeroPdf\Re_ZERO -Starting Life in Another World-, Vol. {volume}.pdf"
        extracted_text = extract_text_from_pdf(pdf_path)
        cleaned_text = remove_links(extracted_text)
        paragraphs = fix_paragraphs(cleaned_text)
        chapters = split_into_chapters(paragraphs, 100)  # Group every 10 paragraphs into a chapter

        # Add each chapter to the content dictionary with a title
        for chapter_index, chapter_text in enumerate(chapters, start=1):
            title = f"Starting Life in Another World-, Vol. {volume} (part {chapter_index}, chapter {global_chapter_count})"
            content[str(global_chapter_count)] = [title, chapter_text]
            global_chapter_count += 1

        print(f"Processed Volume {volume}: {len(chapters)} chapters extracted.")

    print(f"Total chapters extracted: {global_chapter_count - 1}")

    with open(r'templates\novels\Re Zero-chapters\chapters.json', 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    work()    