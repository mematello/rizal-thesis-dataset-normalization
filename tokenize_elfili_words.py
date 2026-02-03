
import csv
import re
import unicodedata
from collections import Counter

input_filename = "elfili_extraction.csv"
output_filename = "elfili_word_tokens.csv"

def get_token_type(token):
    if token.isdigit():
        return "number"
    # Word check: starts with alphabetic or is mostly alphabetic
    # We must consider characters with diacritics as alpha
    if any(c.isalpha() for c in token):
        return "word"
    return "punct"

def main():
    print(f"Reading {input_filename}...")
    
    rows = []
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    except FileNotFoundError:
        print(f"Error: {input_filename} not found.")
        return

    print(f"Processing {len(rows)} rows (filtering for text_type='paragraph')...")

    # Regex Definitions
    # 1. Word: Starts with letter (including unicode), can contain letters, numbers, combining marks.
    #    Can have internal hyphens or apostrophes followed by letters.
    #    We include \u0303 explicitly for the tilde in ng̃ if it's not covered by \w
    #    We use [^\W\d_] to match letters primarily.
    
    # Pattern Logic:
    # Group 1: Word -> Starts with letter. Can contain alphanums + combining marks. Can contain [-’'] in middle.
    # Group 2: Number -> \d+
    # Group 3: Punct -> Any non-whitespace char that wasn't matched above.
    
    # Note: 'ng̃' (n, g, combining tilde) 
    # Python's \w usually includes alphanumeric but not combining marks unless normalized?
    # Actually, in regex module, one might need specific props, but in 're', \w matches unicode chars that are letters.
    # Combining marks are category Mn. \w usually does NOT include Mn.
    # So we strictly add \u0303 (combining tilde) to the allowed chars in a word to be safe.
    
    word_char = r"[\w\u0303]" 
    alpha_start = r"[^\W\d_]" # Matches letters
    
    # Structure: (StartChar)(Body*)( (Separator)(Body+) )*
    # Body includes word_char.
    pattern = re.compile(
        r"(?P<word>" + alpha_start + r"(?:" + word_char + r"*(?:[-’']" + word_char + r"+)*)?)|"
        r"(?P<number>\d+)|"
        r"(?P<punct>[^\s])"
    )

    output_rows = []
    
    total_paras = 0
    total_tokens = 0
    
    token_counts = Counter()
    
    sample_tokens = [] # For global_para_index = 2
    
    for row in rows:
        if row['text_type'] != 'paragraph':
            continue
            
        text = row['text']
        # Normalize whitespace inside paragraph for clean splitting? 
        # The regex ignores whitespace anyway, but let's be consistent.
        # But we do NOT normalize content (spelling).
        
        matches = pattern.finditer(text)
        
        token_index = 0
        
        for m in matches:
            kind = m.lastgroup
            token_text = m.group(kind)
            
            # Map regex group to output type
            if kind == 'word':
                t_type = 'word'
            elif kind == 'number':
                t_type = 'number'
            else:
                # Distinguish punct vs symbol?
                # Simple heuristic: if it's standard punctuation
                if token_text in ".,;?!:()[]{}'\"-—":
                    t_type = 'punct'
                else:
                    t_type = 'symbol' # e.g. * or $ usually
                    # Prompt allows 'word, punct, number, symbol'
                    # Let's call almost everything 'punct' unless distinct symbol? 
                    # Simplicity: just 'punct' for typical, 'symbol' for exotic if needed. 
                    # Prompt example: "Joba!" -> "!" is punct.
                    # Let's map everything non-word/number to 'punct' for now, or 'symbol' if it really looks like one.
                    # Re-reading prompt: "token_type (one of: word, punct, number, symbol)"
                    if not token_text.isalnum():
                         # Fine-grained
                         if token_text in "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~—":
                             t_type = 'punct'
                         else:
                             t_type = 'symbol' 

            # Create Output Row
            out_row = {
                'book_title': row['book_title'],
                'author': row['author'],
                'chapter_index': row['chapter_index'],
                'chapter_title': row['chapter_title'],
                'global_para_index': row['global_para_index'],
                'para_index_in_chapter': row['para_index_in_chapter'],
                'token_index_in_para': token_index,
                'token': token_text,
                'token_type': t_type,
                'paragraph_text': row['text'], # Original text
                'lower_token': token_text.lower(),
                'is_alpha': token_text[0].isalpha() # Approximation
            }
            
            output_rows.append(out_row)
            token_counts[token_text] += 1
            
            # Sample collection
            if row['global_para_index'] == '2':
                if len(sample_tokens) < 30:
                    sample_tokens.append(f"{token_text} ({t_type})")
            
            token_index += 1
            total_tokens += 1
            
        total_paras += 1

    print(f"Writing {len(output_rows)} tokens to {output_filename}...")
    
    cols = [
        'book_title', 'author', 'chapter_index', 'chapter_title',
        'global_para_index', 'para_index_in_chapter', 'token_index_in_para',
        'token', 'token_type', 'paragraph_text', 'lower_token', 'is_alpha'
    ]
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(output_rows)

    print("\nTokenization Summary")
    print("--------------------")
    print(f"Total paragraphs tokenized: {total_paras}")
    print(f"Total tokens created: {total_tokens}")
    print("\nTop 20 Frequent Tokens:")
    for t, c in token_counts.most_common(20):
        print(f"  '{t}': {c}")
        
    print("\nFirst 30 tokens for global_para_index = 2:")
    print(sample_tokens)

if __name__ == "__main__":
    main()
