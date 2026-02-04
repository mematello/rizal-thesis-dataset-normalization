
import csv
import re
import sys

INPUT_FILE = 'elfili_extraction_normalized.csv'
OUTPUT_FILE = 'elfili_chapter_sentences.csv'

# Explicit Abbreviations from user request + observation
ABBREVIATIONS = {'G', 'P', 'D', 'Sr', 'Sra', 'Sta', 'Dr', 'Fr'}

def split_sentences_regex(text):
    if not text:
        return []
        
    # preserve original for debug if needed, but we work on 'text'
    
    # 1. Protect Abbreviations
    # Replace dot with <DOT>
    
    # Explicit list
    # Match word boundary or start/space, then Abbr, then dot
    for abbr in ABBREVIATIONS:
        # Regex: (?<=^|\s)Abbr\.
        # But lookbehind needs fixed width usually.
        # Use simple sub with groups.
        pattern = r'(^|\s)(' + abbr + r')\.'
        text = re.sub(pattern, r'\1\2<DOT>', text)
        
    # Initials: Single Capital Letter followed by dot, THEN space, THEN Capital Letter
    # e.g. "J. Rizal", "M. Viola"
    # We substitute matches.
    
    def protect_initials(match):
        return match.group(0).replace('.', '<DOT>')
        
    # Pattern: 
    # (Start/Space) [A-Z] \. Space [A-Z]
    # We match the whole sequence to ensure context, then replace ONLY the dot?
    # Actually just replacing the dot in the match is easier if we correctly capture.
    
    pattern_initials = r'(?:^|\s)[A-Z]\.(?=\s+[A-Z])'
    # Note: re.sub passes the match object.
    text = re.sub(pattern_initials, protect_initials, text)
    
    # 2. Split by punctuation
    # We treat ..., ., !, ? as delimiters.
    # Group capture to keep them.
    parts = re.split(r'([.!?]+)', text)
    
    sentences = []
    current_sent = ""
    
    # Iterate pairs ideally, but parts len is 2n+1
    i = 0
    while i < len(parts):
        chunk = parts[i]
        delim = parts[i+1] if i+1 < len(parts) else ""
        
        current_sent += chunk + delim
        
        # Decide to split or join
        split_here = True
        
        # If no delim, we are at end
        if not delim:
            split_here = True
        else:
            # Check next chunk
            if i + 2 < len(parts):
                next_chunk = parts[i+2]
                stripped_next = next_chunk.strip()
                
                # Heuristic: Join if next word starts with lowercase
                # AND it's an ellipsis (common pause)
                # OR it's a comma/semi-colon? (Unlikely to have . ,)
                
                is_ellipsis = '...' in delim
                
                # Check start of next significant char
                if stripped_next:
                    first_char = stripped_next[0]
                    # Check if lower case
                    if first_char.islower():
                        # Assume continuation if ellipsis
                        if is_ellipsis:
                            split_here = False
                        else:
                            # Period followed by lowercase?
                            # "Ginoo. ako ay..." -> Likely split?
                            # Tagalog: "Opo. hindi ba..." -> Split.
                            # So enforce split on non-ellipsis.
                            split_here = True
                    # Check for other punctuation starts?
                    # — (Em dash) usually starts new clause/sentence
                    elif first_char in ['—', '¿', '¡', '"', '“', '‘']:
                        split_here = True
                else:
                    # Next chunk is empty/whitespace -> likely continue to find next text?
                    # No, simply consume whitespace in next loop iter?
                    # re.split leaves whitespace in the 'chunk'.
                    # If parts[i+2] is just " ", then parts[i+3] is delim?
                    # e.g. "Hello.  World." -> ["Hello", ".", "  ", ".", "World", ".", ""]
                    # i=0: Hello.
                    # next_chunk="  ". stripped is empty.
                    # We shouldn't split yet? 
                    # Actually standard logic: "Hello." is a sentence. "  " is leading space of next.
                    # So if next chunk is whitespace only *and followed by more text*, we assume split.
                    pass
            else:
                # End of string
                split_here = True
                
        if split_here:
            s_clean = current_sent.strip()
            if s_clean:
                sentences.append(s_clean)
            current_sent = ""
            
        i += 2
        
    if current_sent.strip():
        sentences.append(current_sent.strip())
        
    # 3. Restore dots
    final_sentences = []
    for s in sentences:
        s = s.replace('<DOT>', '.')
        final_sentences.append(s)
        
    return final_sentences

def main():
    print("Starting segmentation...")
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    out_rows = []
    
    # 1-based chapter counting
    chapter_num = 0
    chapter_title = ""
    sent_in_chapter = 0
    
    # Iterate
    for row in rows:
        ttype = row['text_type']
        text = row['text']
        
        if ttype == 'chapter_title':
            chapter_num += 1
            chapter_title = text
            sent_in_chapter = 0
            # Metadata update only
            continue
            
        if ttype not in ['paragraph', 'epigraph']:
            # Should be covered (the types are p, c, e)
            continue
            
        # Segment
        # Validate that we have a chapter 1?
        # Row 0 is ALAALA (dedication) -> Chapter 1.
        # Parags follow.
        if chapter_num == 0:
            # Should not happen if first row is title, but safety:
            chapter_num = 1
            chapter_title = "UNKNOWN_START"
            
        sents = split_sentences_regex(text)
        
        for s in sents:
            sent_in_chapter += 1
            out_rows.append({
                'book_title': 'El Filibusterismo',
                'chapter_number': chapter_num,
                'chapter_title': chapter_title,
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
    
    # Report
    print("\n=== Validation Report ===")
    print(f"Total Sentences: {len(out_rows)}")
    print(f"Total Chapters: {chapter_num}")
    if chapter_num > 0:
        print(f"Avg Sentences/Chapter: {len(out_rows)/chapter_num:.1f}")
        
    # Samples
    ch1 = [r for r in out_rows if int(r['chapter_number']) == 1]
    print("\nFirst 5 sentences of Chapter 1:")
    for i, x in enumerate(ch1[:5]):
        print(f"{i+1}: {x['sentence_text']}")
        
    ch_last = [r for r in out_rows if int(r['chapter_number']) == chapter_num]
    print(f"\nLast 5 sentences of Chapter {chapter_num}:")
    for i, x in enumerate(ch_last[-5:]):
        print(f"{i+1}: {x['sentence_text']}")

if __name__ == '__main__':
    main()
