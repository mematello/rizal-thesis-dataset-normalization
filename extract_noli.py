
from bs4 import BeautifulSoup
import csv
import html
import re
import os

INPUT_FILE = "Noli Me Tangere | Project Gutenberg.html"
OUTPUT_FILE = "noli_extraction.csv"

def clean_text(text):
    if not text: return ""
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_noli():
    print(f"Parsing {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        
    rows = []
    
    chapter_index = 0
    chapter_title = "FRONT_MATTER"
    para_idx = 0
    global_para_idx = 0
    
    # Iterate through content elements
    # Using find_all with a list guarantees document order? Yes.
    
    elements = soup.find_all(['h1', 'h2', 'h3', 'p'])
    
    # Pre-process pagenums: Remove them entirely
    for span in soup.find_all('span', class_='pagenum'):
        span.decompose()
        
    for elem in elements:
        # Skip Gutenberg boilerplate/navigation if identifiable
        # Usually checking class or content strings
        # "Project Gutenberg License", "End of the Project Gutenberg EBook"
        
        text_content = elem.get_text()
        
        # Heuristic skip
        if "Project Gutenberg License" in text_content or "End of the Project Gutenberg EBook" in text_content:
            continue
            
        # Extract text preserving drop caps
        final_text = ""
        
        if elem.name == 'p':
            # Handle children for drop caps
            parts = []
            for child in elem.children:
                if child.name == 'img':
                    # Check for drop cap
                    # usually has class 'figleft' or single letter 'alt' inside a paragraph
                    alt = child.get('alt', '')
                    if len(alt) == 1 and alt.isalpha(): # Drop cap likely
                        parts.append(alt)
                    elif 'figleft' in child.get('class', []):
                        parts.append(alt)
                elif child.name == 'br':
                    parts.append(" ")
                elif child.string:
                    parts.append(child.string)
                else:
                    parts.append(child.get_text())
            final_text = "".join(parts)
        else:
            final_text = elem.get_text()
            
        final_text = clean_text(final_text)
        
        if not final_text:
            continue
            
        # Determine Text Type & Metadata
        text_type = 'paragraph'
        
        if elem.name in ['h1', 'h2', 'h3']:
            # Header
            # Check if it is a Roman Numeral (Chapter Number)
            if re.match(r'^[XVI]+\.?$', final_text):
                # It's a chapter number marker
                # Increment index
                # But don't change title yet? Or reset title?
                # Usually Title follows in next H3
                # We can store this row as 'chapter_number' type or just skip/log it?
                # User wants "chapter_index" in CSV.
                
                # Logic: Found Roman Numeral -> Increment Index
                chapter_index += 1
                para_idx = 0
                text_type = 'chapter_number'
                # Don't update chapter_title yet, keep previous? Or set to "Unknown"?
                # Ideally, title comes next.
                
            else:
                # It's a text title (e.g. "ISANG PAGCACAPISAN", "TALAAN...", "NOLI...")
                text_type = 'chapter_title'
                chapter_title = final_text
                para_idx = 0
                
                # If we are in front matter (chapter_index 0), this is just a Section Title.
                
        else:
            # Paragraph
            # Check if footnote
            if 'footnote' in str(elem.get('class', [])) or 'fn' in str(elem.get('id', '')):
                continue
            # Links to footnotes often textual [1], [2]. 
            # We normalized away?
            # Clean foot note refs? [1]
            # Replace [1], [2] with empty string?
            final_text = re.sub(r'\[\d+\]', '', final_text).strip()
            if not final_text: continue
            
            para_idx += 1
            global_para_idx += 1
            
        # Add to CSV
        rows.append({
            'book_title': 'Noli Me Tangere',
            'author': 'Jose Rizal',
            'source': 'Project Gutenberg',
            'source_filename': INPUT_FILE,
            'chapter_index': chapter_index,
            'chapter_title': chapter_title,
            'para_index_in_chapter': para_idx,
            'global_para_index': global_para_idx,
            'text': final_text,
            'text_type': text_type
        })
        
    # Write CSV
    print(f"Extracted {len(rows)} rows.")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['book_title', 'author', 'source', 'source_filename', 'chapter_index', 'chapter_title', 'para_index_in_chapter', 'global_para_index', 'text', 'text_type']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    # Report Titles
    print("First 10 Chapter Titles detected:")
    seen_titles = []
    for r in rows:
        if r['text_type'] == 'chapter_title':
            if r['text'] not in seen_titles:
                seen_titles.append(r['text'])
                if len(seen_titles) >= 10: break
    for t in seen_titles:
        print(f"  {t}")
        
    # Check total paragraphs
    paras = [r for r in rows if r['text_type'] == 'paragraph']
    print(f"Total Narrative Paragraphs: {len(paras)}")

if __name__ == '__main__':
    extract_noli()
