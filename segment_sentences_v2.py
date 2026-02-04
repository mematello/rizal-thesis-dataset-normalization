
import csv
import re
import sys

INPUT_FILE = 'elfili_extraction_normalized.csv'
OUTPUT_FILE = 'elfili_chapter_sentences.csv'

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
    print("Starting corrected segmentation...")
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    out_rows = []
    
    chapter_num = 0
    chapter_title_str = ""
    sent_in_chapter = 0
    
    # Flags
    skip_section = False
    
    for row in rows:
        ttype = row['text_type']
        text = row['text']
        
        if ttype == 'chapter_title':
            if text.strip() == 'ALAALA':
                skip_section = True
                continue
            else:
                skip_section = False
                chapter_num += 1
                sent_in_chapter = 0
                
                # Apply Renaming Rules
                if chapter_num == 1:
                    chapter_title_str = "Sa Ibabaw ng Kubyerta"
                elif chapter_num == 2:
                    chapter_title_str = "Sa Ilalim ng Kubyerta"
                elif chapter_num == 39:
                    chapter_title_str = "XXXIX KATAPUSAN"
                else:
                    chapter_title_str = text
                
                # Validation check for ordering?
                # We assume generic processing.
                continue
        
        if skip_section:
            continue
            
        # Process Content
        if ttype in ['paragraph', 'epigraph']:
            # Segmentation
            if chapter_num == 0:
                # Should not happen if ALAALA is skipped correctly and next is Ch 1
                continue
                
            sents = split_sentences_regex(text)
            
            for s in sents:
                sent_in_chapter += 1
                out_rows.append({
                    'book_title': 'El Filibusterismo',
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
        
    # Validation
    print("\n=== Validation Report ===")
    print(f"Total Sentences: {len(out_rows)}")
    print(f"Total Chapters Detected: {chapter_num}")
    
    # Check Titles
    titles_map = {}
    for r in out_rows:
        cn = int(r['chapter_number'])
        ct = r['chapter_title']
        titles_map[cn] = ct
        
    print(f"\nTitle Check:")
    print(f"  Ch 1: '{titles_map.get(1, 'MISSING')}' (Exp: Sa Ibabaw ng Kubyerta)")
    print(f"  Ch 2: '{titles_map.get(2, 'MISSING')}' (Exp: Sa Ilalim ng Kubyerta)")
    print(f"  Ch 39: '{titles_map.get(39, 'MISSING')}' (Exp: XXXIX KATAPUSAN)")
    
    # Sentence Samples
    ch1_sents = [r for r in out_rows if int(r['chapter_number']) == 1]
    last_ch_sents = [r for r in out_rows if int(r['chapter_number']) == 39]
    
    print("\nFirst 3 sentences of Chapter 1:")
    for i, x in enumerate(ch1_sents[:3]):
        print(f"{i+1}: {x['sentence_text']}")
        
    print(f"\nLast 3 sentences of Chapter {chapter_num} ({titles_map.get(chapter_num)}):")
    for i, x in enumerate(last_ch_sents[-3:]):
        print(f"{i+1}: {x['sentence_text']}")

if __name__ == '__main__':
    main()
