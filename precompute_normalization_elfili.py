import pandas as pd
import re
import json
import sys

# Configuration
INPUT_FILE = "/Users/marcusoliver/Desktop/rizal-thesis-dataset-normalization/elfili_chapter_sentences_FINAL_v2.csv"
CANDIDATES_FILE = "elfili_candidates.csv"
REVIEW_QUEUE_FILE = "review_queue.json"
PROTECTED_TERMS_FILE = "protected_terms_elfili.txt"

# Regex for tokens (same as audit)
TOKEN_PATTERN = r"[a-zA-ZñÑáéíóúÁÉÍÓÚüÜ'’\-]+"

def load_resources():
    try:
        df_corpus = pd.read_csv(INPUT_FILE)
        df_cand = pd.read_csv(CANDIDATES_FILE)
        
        # Create mapping dict: token -> suggestion
        # Only use candidates that have a suggestion
        mapping = {}
        for _, row in df_cand.iterrows():
            mapping[row['token']] = {
                'suggestion': row['modern_suggestion'],
                'rule': row['pattern_match']
            }
            
        with open(PROTECTED_TERMS_FILE, 'r') as f:
            protected_list = set(line.strip() for line in f)
            
        return df_corpus, mapping, protected_list
    except Exception as e:
        print(f"Error loading resources: {e}")
        sys.exit(1)

def is_spanish_context(text, token_start, token_end):
    # Heuristic: Check if inside quotas "..." or <<...>> or «...»
    # This is a simple check; for robust check we might need more complex parsing
    # But for now, let's assume if the line has spanish quotes, we are careful.
    
    # Check for Spanish markers in the *sentence*
    # "la ocasion la pintan calva"
    
    # Actually, the user asked for:
    # r'"[^"]*\b(ocasion|calva|poco|cuando|cual)\b[^"]*"'
    # But we want to protect ANY match if it's inside quotes generally?
    # Or just specifically Spanish phrases?
    # User said: "Check Spanish phrases (inside quotes or via Spanish lexicon)"
    
    # Let's detect if the token is inside a quoted section.
    prefix = text[:token_start]
    suffix = text[token_end:]
    
    # Count quotes in prefix
    quote_count = prefix.count('"') + prefix.count('“') + prefix.count('”')
    angle_count = prefix.count('«') + prefix.count('»')
    
    # If odd number of quotes, likely inside quotes
    if quote_count % 2 == 1:
        return True
    if angle_count % 2 == 1:
        return True
        
    return False

def tokenize_with_spans(text):
    # Return list of (token, start, end)
    return [(m.group(), m.start(), m.end()) for m in re.finditer(TOKEN_PATTERN, str(text))]

def process_corpus(df, mapping, protected_list):
    queue = []
    
    for idx, row in df.iterrows():
        sentence_id = row.get('sentence_number', idx) # Use sentence_number if available, else index
        # ACTUALLY: sentence_number is not unique across corpus, need composite ID?
        # User said: "sentence_id, original_sentence..."
        # If the input CSV has 'sentence_number', let's use row index as unique ID for the tool to be safe, 
        # or composite "Chapter-Sentence".
        # Let's use the 0-based index from the dataframe as a stable ID for the review session.
        unique_id = str(idx) 
        
        original_text = str(row['sentence_text'])
        
        tokens_spans = tokenize_with_spans(original_text)
        
        processed_tokens = []
        has_change = False
        
        # We need to reconstruction string carefully or just store token list?
        # The UI needs to render the full sentence.
        # Let's store tokens with their status.
        
        last_end = 0
        sentence_segments = [] # Mixed str (whitespace/punct) and dict (token)
        
        for token, start, end in tokens_spans:
            # Add whitespace/punct before this token
            if start > last_end:
                sentence_segments.append(original_text[last_end:start])
            
            token_status = "normal"
            proposed = token
            rule = None
            
            # 1. Check Protected
            if token in protected_list:
                token_status = "protected_lexicon"
                
            elif is_spanish_context(original_text, start, end):
                token_status = "protected_quote"
                
            elif token in mapping:
                # 2. Candidate Match
                token_status = "candidate"
                proposed = mapping[token]['suggestion']
                rule = mapping[token]['rule']
                has_change = True
            
            processed_tokens.append({
                "original": token,
                "proposed": proposed,
                "status": token_status,
                "rule": rule,
                "start": start,
                "end": end
            })
            
            sentence_segments.append({
                "type": "token",
                "data": processed_tokens[-1]
            })
            
            last_end = end
            
        # Add remaining text
        if last_end < len(original_text):
            sentence_segments.append(original_text[last_end:])
            
        # Only add to queue if there are candidates
        # OR if we want to review everything? Usually just candidates.
        if has_change:
            queue.append({
                "id": unique_id,
                "chapter": row.get('chapter_number', ''),
                "original_sentence": original_text,
                "segments": sentence_segments
            })
            
    return queue

def main():
    print("Loading resources...")
    df, mapping, protected = load_resources()
    
    print("Processing corpus...")
    queue = process_corpus(df, mapping, protected)
    
    print(f"Generated review queue with {len(queue)} items.")
    
    with open(REVIEW_QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)
        
    print(f"Saved to {REVIEW_QUEUE_FILE}")

if __name__ == "__main__":
    main()
