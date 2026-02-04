
import csv
import re
import sys

INPUT_FILE = 'noli_extraction_normalized.csv'
OUTPUT_FILE = 'noli_chapter_sentences.csv'

# Explicit Abbreviations
ABBREVIATIONS = {'G', 'P', 'D', 'Sr', 'Sra', 'Sta', 'Dr', 'Fr'}

def split_sentences_regex(text):
    if not text:
        return []
    
    # 1. Protect Abbreviations
    for abbr in ABBREVIATIONS:
        pattern = r'(^|\s)(' + abbr + r')\.'
        text = re.sub(pattern, r'\1\2<DOT>', text)
        
    def protect_initials(match):
        return match.group(0).replace('.', '<DOT>')
    
    pattern_initials = r'(?:^|\s)[A-Z]\.(?=\s+[A-Z])'
    text = re.sub(pattern_initials, protect_initials, text)
    
    # 2. Split
    parts = re.split(r'([.!?]+)', text)
    
    sentences = []
    current_sent = ""
    
    i = 0
    while i < len(parts):
        chunk = parts[i]
        delim = parts[i+1] if i+1 < len(parts) else ""
        
        current_sent += chunk + delim
        
        split_here = True
        
        if not delim:
            split_here = True
        else:
            if i + 2 < len(parts):
                next_chunk = parts[i+2]
                stripped_next = next_chunk.strip()
                is_ellipsis = '...' in delim
                
                if stripped_next:
                    first_char = stripped_next[0]
                    if first_char.islower():
                        if is_ellipsis:
                            split_here = False
                        else:
                            split_here = True
                    elif first_char in ['—', '¿', '¡', '"', '“', '‘']:
                        split_here = True
            else:
                split_here = True
                
        if split_here:
            s_clean = current_sent.strip()
            if s_clean:
                sentences.append(s_clean)
            current_sent = ""
            
        i += 2
        
    if current_sent.strip():
        sentences.append(current_sent.strip())
        
    # 3. Restore
    final_sentences = []
    for s in sentences:
        s = s.replace('<DOT>', '.')
        final_sentences.append(s)
        
    return final_sentences

def main():
    print("Starting Noli segmentation...")
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    out_rows = []
    
    chapter_num = 0
    chapter_title_str = ""
    sent_in_chapter = 0
    
    found_start = False
    
    # Iterate
    for row in rows:
        ttype = row['text_type']
        text = row['text']
        
        # Check start condition
        if not found_start:
            if ttype == 'chapter_title' and text.strip() == 'ISANG PAGCACAPISAN.':
                found_start = True
                chapter_num = 1
                chapter_title_str = text.strip()
                sent_in_chapter = 0
                continue # The chapter title row itself isn't a sentence usually? 
                         # Wait, sentence dataset schema usually doesn't include the title as a sentence.
                         # El Fili segmentation skipped ttype='chapter_title'.
            else:
                continue
                
        # Normal processing

            
        if ttype == 'chapter_number':
           # e.g. "II."
           # Just ignore, the Title usually follows or we wait for valid title?
           # Noli has "II" then "CRISOSTOMO IBARRA".
           # If I increment ch num on number, then ch title update on title?
           # My extract script marked H2 (Roman) as 'chapter_number' and H3 as 'chapter_title'.
           # If I increment on Title, I should ignore Number.
           # BUT what if there is no Title, only Number?
           # User instruction: "Chapter 1 title must be ISANG PAGCACAPISAN."
           # I'll increment on 'chapter_title'.
           # If a chapter has no title, my extractor might have labeled the number as 'chapter_number'.
           # Let's hope all chapters have titles? Noli usually does.
           # If I encounter 'chapter_number', I do nothing? The next rows belong to PREV chapter until new TITLE?
           # No. "II." marks new chapter.
           # So if I see 'chapter_number', I should increment `chapter_num`?
           # Then when I see `chapter_title`, I update the title (same number).
           
           # Logic:
           # trigger on chapter_number OR chapter_title?
           # If 'chapter_number' comes first: New Chapter, Title="[Number]".
           # Then 'chapter_title' comes: Update Title of current chapter.
           pass 
           # Let's refine.
           # Start: found_start=True at "ISANG PAGCACAPISAN.". This is TITLE. So Ch=1.
           # Next will be "II." (chapter_number). 
           # I should increment Ch to 2. Title="II." (temp).
           # Next is "CRISOSTOMO IBARRA" (chapter_title). 
           # Update Ch 2 Title to "CRISOSTOMO IBARRA".
           
        if ttype == 'chapter_number':
             chapter_num += 1
             sent_in_chapter = 0
             chapter_title_str = text.strip() # Temp title
             continue
             
        if ttype == 'chapter_title':
             # If we just incremented via number, don't increment again?
             # Check if we are "inside" the same chapter block?
             # Heuristic: If sent_in_chapter == 0, we can overwrite title?
             # Yes.
             current_is_roman = re.match(r'^[XVI\.]+$', chapter_title_str)
             # DEBUG CHECK
             if current_is_roman:
                  # print(f"DEBUG: Roman Match: {chapter_title_str}")
                  pass
             else:
                  print(f"DEBUG: NO Roman Match: '{chapter_title_str}'")

             if sent_in_chapter == 0 or current_is_roman or (chapter_title_str in ['LIV.', 'LV.', 'LVI.']): 
                 # Allow overwrite/merge
                 chapter_title_str = text.strip()
             else:
                 # Unexpected title in middle of text? New chapter.
                 chapter_num += 1
                 # DEBUG
                 print(f"DEBUG: Incr Ch {chapter_num} (Prev: '{chapter_title_str}' -> New: '{text}')")
                 sent_in_chapter = 0
                 chapter_title_str = text.strip()
            
             if "MGA TALABABA" in chapter_title_str.upper():
                 break
             continue

        # Content
        if ttype in ['paragraph', 'epigraph']:
            sents = split_sentences_regex(text)
            for s in sents:
                sent_in_chapter += 1
                out_rows.append({
                    'book_title': 'Noli Me Tangere',
                    'chapter_number': chapter_num,
                    'chapter_title': chapter_title_str,
                    'sentence_number': sent_in_chapter,
                    'sentence_text': s
                })
                
    # Write
    print(f"Writing {len(out_rows)} sentences to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['book_title', 'chapter_number', 'chapter_title', 'sentence_number', 'sentence_text']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)
        
    # Validation Report
    print(f"\nTotal Chapters: {chapter_num}")
    print(f"Total Sentences: {len(out_rows)}")
    
    # Verify Ch 1 Title
    ch1_rows = [r for r in out_rows if int(r['chapter_number']) == 1]
    if ch1_rows:
        print(f"Ch 1 Title: {ch1_rows[0]['chapter_title']}")
    else:
        print("Ch 1: Empty")
        
    # Verify Ch 1 sentences
    print("\nFirst 5 Sentences Ch 1:")
    for i, s in enumerate(ch1_rows[:5]):
        print(f"{i+1}: {s['sentence_text']}")
        
    # Verify Last Ch
    ch_last_rows = [r for r in out_rows if int(r['chapter_number']) == chapter_num]
    print(f"\nLast 5 Sentences Ch {chapter_num}:")
    for i, s in enumerate(ch_last_rows[-5:]):
        print(f"{i+1}: {s['sentence_text']}")

if __name__ == '__main__':
    main()
