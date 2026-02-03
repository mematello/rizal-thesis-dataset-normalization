
import sys
import csv
import re
from bs4 import BeautifulSoup
import os

input_filename = "Ang _Filibusterismo_, by José Rizal_ A Project Gutenberg eBook.html"
output_filename = "elfili_extraction.csv"

def roman_to_int(s):
    # Basic Roman numeral parser for common chapter numbers
    s = s.upper().strip().rstrip('.')
    # Handle simple cases or standard roman
    romans = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100}
    total = 0
    prev_value = 0
    for char in reversed(s):
        value = romans.get(char, 0)
        # If unknown char, ignore or handle? Stick to standard.
        if value < prev_value:
            total -= value
        else:
            total += value
        prev_value = value
    return total

def clean_text(text):
    if not text:
        return ""
    # Collaborate whitespace: newlines, tabs, multiple spaces -> single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def main():
    if not os.path.exists(input_filename):
        print(f"Error: {input_filename} not found.")
        return

    print(f"Reading {input_filename}...")
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
    except Exception as e:
        print(f"Failed to parse HTML: {e}")
        return

    # Metadata extraction
    print("Extracting metadata...")
    # Title
    title_tag = soup.find('h1')
    book_title = clean_text(title_tag.get_text()) if title_tag else "Unknown"
    
    # Author
    author_tag = soup.find(id='author')
    author = clean_text(author_tag.get_text()) if author_tag else "Unknown"
    
    source = "Project Gutenberg"
    source_filename = input_filename

    rows = []
    global_para_index = 0
    processed_chapters = 0
    total_content_paragraphs = 0

    text_div = soup.find('div', id='text')
    if not text_div:
        print("Error: div#text not found")
        return

    # Iterate over relevant content blocks inside div#text
    # We look for div.chapter and div#dedication
    
    for child in text_div.children:
        if child.name != 'div':
            continue
            
        div_id = child.get('id', '')
        div_class = child.get('class', [])
        
        # Skip Front Matter / Back Matter / Boilerplate
        if div_id == 'title-page': continue
        if div_id == 'Indice': continue
        if 'transnote' in div_class: continue
        if 'frontispiece' in div_class: continue
        if 'bastard-page' in div_class: continue
        
        # Identify valid content blocks
        is_chapter = 'chapter' in div_class
        is_dedication = div_id == 'dedication'
        
        if not (is_chapter or is_dedication):
            continue

        processed_chapters += 1
        
        # Extract Chapter Info
        chapter_index = 0
        chapter_title_text = ""
        
        h2 = child.find('h2')
        if h2:
            # Handle Chapter Number parsing
            chapno_span = h2.find('span', class_='chapno')
            if chapno_span:
                c_num_str = clean_text(chapno_span.get_text())
                try:
                    chapter_index = roman_to_int(c_num_str)
                except:
                    chapter_index = 0
            
            # Use full H2 text as title (includes number if present in text)
            # Remove any anchor links if needed? get_text() strips tags anyway.
            chapter_title_text = clean_text(h2.get_text())
            
        if is_dedication:
            chapter_title_text = "ALAALA" if not chapter_title_text else chapter_title_text
            chapter_index = 0

        # Add Chapter Title as encoded row
        if chapter_title_text:
            global_para_index += 1
            rows.append({
                'book_title': book_title,
                'author': author,
                'source': source,
                'source_filename': source_filename,
                'chapter_index': chapter_index,
                'chapter_title': chapter_title_text,
                'para_index_in_chapter': 0, 
                'global_para_index': global_para_index,
                'text': chapter_title_text,
                'text_type': 'chapter_title'
            })
            
        chapter_para_count = 0
        
        # Iterate Paragraphs
        # Using find_all('p') traverses descendants. We need to be careful with nested structures.
        # But looking at structural CSS, p's are mostly direct children or in blockquotes.
        # We need to filter out p's that are inside nested excluded divs (like footnotes).
        
        all_ps = child.find_all('p')
        
        for p in all_ps:
            # 1. Exclusion Checks
            
            # Check for footnote parent
            is_footnote = False
            curr = p
            while curr and curr != child:
                if 'footnote' in curr.get('class', []):
                    is_footnote = True
                    break
                curr = curr.parent
            if is_footnote:
                continue
                
            # Check if this paragraph IS a boilerplate element itself
            # e.g. <p class="end">Wakás...</p> is fine to include as text
            # But line 381: <p><a class="pagenum"...>[5]</a></p>
            
            # Remove pagenum anchors from the P element
            pagenums = p.find_all('a', class_='pagenum')
            for pn in pagenums:
                pn.decompose()
                
            # Get text
            raw_text = clean_text(p.get_text())
            
            # If empty after removing pagenum, skip
            if not raw_text:
                continue
                
            # Skip decorative separators (only asterisks or spaces)
            if set(raw_text) <= {'*', ' '}:
                continue
                
            # Determine text_type
            text_type = 'paragraph'
            
            # Check for Epigraph
            # Either direct class on p (unlikely) or parent blockquote
            parent_node = p.parent
            if parent_node.name == 'blockquote' and 'epigraph' in parent_node.get('class', []):
                text_type = 'epigraph'
            elif 'attrib' in p.get('class', []):
                # Attribution often goes with epigraphs or blockquotes
                # Treating as paragraph for now, or 'other' if needed? 
                # Prompt allows: paragraph, chapter_title, epigraph, other. 
                # Let's call attrib 'other' or just 'paragraph'. 
                # Epigraph attribution -> Epigraph?
                # User asked for "Structured text". 
                # If it's the author of the epigraph, 'epigraph' text_type is reasonable 
                # OR 'other'. Let's stick to 'paragraph' unless explicitly 'epigraph' block.
                # Actually, if parent is epigraph poem, keep as epigraph.
                pass

            chapter_para_count += 1
            global_para_index += 1
            total_content_paragraphs += 1
            
            rows.append({
                'book_title': book_title,
                'author': author,
                'source': source,
                'source_filename': source_filename,
                'chapter_index': chapter_index,
                'chapter_title': chapter_title_text,
                'para_index_in_chapter': chapter_para_count,
                'global_para_index': global_para_index,
                'text': raw_text,
                'text_type': text_type
            })

    print(f"Writing {len(rows)} rows to {output_filename}...")
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['book_title', 'author', 'source', 'source_filename', 'chapter_index', 
                      'chapter_title', 'para_index_in_chapter', 'global_para_index', 'text', 'text_type']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    print("\nExtraction Summary")
    print("------------------")
    print(f"Total chapters detected: {processed_chapters}")
    print(f"Total content paragraphs extracted: {total_content_paragraphs}")
    print(f"Total CSV rows: {len(rows)}")
    
    print("\nPreview (First 3 rows):")
    for r in rows[:3]:
        print(r)

if __name__ == "__main__":
    main()
