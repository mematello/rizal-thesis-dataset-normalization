import pandas as pd
import re
import csv
import sys

# Configuration
MAPPING_FILE = "mapping_proposal.csv"
INPUT_CSV = "noli_chapter_sentences_FINAL_v2.csv"
OUTPUT_CSV = "noli_chapter_sentences_NORMALIZED.csv"
CHANGELOG_FILE = "change_log.csv"
SUMMARY_FILE = "normalization_summary.txt"

def load_mappings(filepath):
    """Load only APPROVED mappings from CSV"""
    try:
        df = pd.read_csv(filepath)
        approved = df[df['reviewer_decision'] == 'APPROVED']
        #Sort by length desc to avoid substring issues just in case, though we use whole word match
        approved = approved.sort_values(by="old_token", key=lambda x: x.str.len(), ascending=False)
        return dict(zip(approved['old_token'], approved['new_token']))
    except FileNotFoundError:
        print(f"Mapping file {filepath} not found.")
        sys.exit(1)

def preserve_case_replace(text, old, new):
    """
    Replace whole-word instances of 'old' with 'new', preserving case.
    Returns: (modified_text, changes_list)
    """
    changes = []
    
    # Escape old token for regex, allow apostrophes/hyphens inside if needed
    # But we are matching exact tokens from our inventory.
    # Use word boundaries. Note that \b in regex might consist of non-word chars.
    # Our tokens include hyphens and apostrophes. 
    # \b matches between \w and \W. 
    # If token ends in "'", \b might not work as expected if next char is space (which is \W).
    # So we need careful boundary checks. 
    # Simple \b works for standard words.
    # For "sacali't", \b matches start s, but 't is word char? ' is non-word.
    # So sacali't\b might fail if ' is distinct. 
    # Let's use a custom boundary or just \b if we trust the tokenizer.
    # Our tokenizer was `[a-zA-ZñÑáéíóúÁÉÍÓÚüÜ'’\-]+`.
    # So ' and - are parts of the word.
    # If use \b, python re considers [a-zA-Z0-9_] as word chars.
    # It does NOT consider ' or - as word chars.
    # So \bpar-par\b will match "par" in "par-par". Bad.
    
    # Better approach: Iterate tokens in the sentence, replace if match, rebuild sentence.
    # BUT, that destroys original whitespace/punctuation formatting if we just join().
    # We want to preserve exact string except the target word.
    
    # So we MUST use regex replacement with correct lookarounds or custom boundaries.
    # Custom boundary: (?<![a-zA-ZñÑáéíóúÁÉÍÓÚüÜ'’\-])WORD(?![a-zA-ZñÑáéíóúÁÉÍÓÚüÜ'’\-])
    
    boundary_char_class = r"[a-zA-ZñÑáéíóúÁÉÍÓÚüÜ'’\-]"
    pattern = r'(?<!{}){}(?!{})'.format(boundary_char_class, re.escape(old), boundary_char_class)
    
    def replacer(match):
        matched_text = match.group(0)
        start_pos = match.start()
        
        # Determine case pattern
        replacement = new
        if matched_text.isupper():
            replacement = new.upper()
        elif matched_text[0].isupper():
            replacement = new[0].upper() + new[1:]
        # else keep lower (default)
        
        # Log change
        changes.append({
            'original': matched_text,
            'replacement': replacement,
            'position': start_pos
        })
        
        return replacement
    
    modified_text = re.sub(pattern, replacer, str(text), flags=re.UNICODE)
    return modified_text, changes

def apply_normalization():
    print("Loading mappings...")
    mappings = load_mappings(MAPPING_FILE)
    print(f"Loaded {len(mappings)} mappings.")
    
    print(f"Loading corpus from {INPUT_CSV}...")
    try:
        df = pd.read_csv(INPUT_CSV)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        sys.exit(1)
        
    changelog_entries = []
    
    # Process row by row
    # To speed this up, maybe we can just iterate the mappings and apply regex on the whole column?
    # No, we need per-sentence logging with ID.
    # Efficiency: 3000 mappings * 8000 sentences = 24M checks. That's slow in Python loop.
    # Better: Tokenize sentence -> check if token in map -> replace.
    # But "Tokenize -> Reconstruct" risks formatting loss.
    
    # Hybrid:
    # 1. Provide a "fast check" - if sentence contains any of the old_token substrings?
    # Still slow.
    
    # Optimization: Compile ONE huge regex for all old_tokens?
    # regex = r'\b(word1|word2|...)\b'
    # Then in callback, look up the replacement.
    # YES. This is the standard way.
    
    # Sort mappings by length (desc) to ensure longest match first in regex OR
    
    sorted_keys = sorted(mappings.keys(), key=len, reverse=True)
    boundary_char_class = r"[a-zA-ZñÑáéíóúÁÉÍÓÚüÜ'’\-]"
    
    # Regex escaping
    escaped_keys = [re.escape(k) for k in sorted_keys]
    
    # Batch the regex if it's too huge? 3000 words might be fine.
    # Try one big regex.
    pattern_str = r'(?<!{})({})(?!{})'.format(boundary_char_class, "|".join(escaped_keys), boundary_char_class)
    regex = re.compile(pattern_str, re.UNICODE)
    
    print("Processing sentences...")
    modified_sentences = []
    total_changes = 0
    
    for idx, row in df.iterrows():
        original_text = str(row['sentence_text'])
        sentence_id = row.get('sentence_number', idx) # Use sentence_number if avail
        
        changes_in_sentence = []
        
        def replacement_func(match):
            matched_text = match.group(1) # group 1 is the word
            
            # Lookup lower case or exact?
            # Our mapping keys are exact tokens from inventory.
            # But the regex match might be case variant if we used IGNORECASE?
            # We constructed pattern from keys. Token keys are case-sensitive in our map?
            # In Phase 2, we extracted tokens exactly.
            # BUT: 'Cain' and 'cain' might be distinct entries in mapping?
            # Let's check. 
            # If `mapping_proposal.csv` has 'cain', does it have 'Cain'?
            # `preserve_case_replace` logic assumed we match the word and then adjust case.
            # But if we match EXACTLY `cain`, it won't match `Cain`.
            # If we want to catch 'Cain' with 'cain' mapping, we need case-insensitive match,
            # BUT look up lower-case key. 
            # Our mapping dict keys are case-sensitive specific tokens from inventory.
            
            # Strategy: The mapping file should theoretically contain both 'cain' and 'Cain' if both exist in candidates.
            # IF `generate_candidates` processed ALL tokens from inventory.
            # Yes, inventory has separate entries for 'cain' and 'Cain' if they appear.
            # So we can do EXACT matching with the big regex.
            
            # Wait, `generate_candidates` loop: `for token in inventory`.
            # If `Cain` was in inventory, it was processed.
            # So `mappings` has `Cain` -> `Kain` (maybe).
            # If so, we can trust the regex to find `Cain` exactly.
            
            # Optimization: If `Cain` is NOT in mapping but `cain` is, strict regex won't touch `Cain`.
            # This is safer for "Deterministic" approach. 
            # If `Cain` wasn't flagged, we don't change it.
            
            target = mappings[matched_text]
            
            # Case preservation logic (even though we matched exact token, 
            # the Mapping might map 'Cain' -> 'kain' (lowercase target).
            # We want 'Kain'.
            
            final_token = target
            if matched_text.isupper():
                final_token = target.upper()
            elif matched_text[0].isupper():
                 final_token = target[0].upper() + target[1:]
            
            changes_in_sentence.append({
                'sentence_id': sentence_id,
                'row_index': idx,
                'original_token': matched_text,
                'new_token': final_token,
                'position': match.start()
            })
            return final_token

        new_text = regex.sub(replacement_func, original_text)
        
        if new_text != original_text:
            modified_sentences.append(new_text)
            total_changes += len(changes_in_sentence)
            
            # Enrich log with before/after context?
            for ch in changes_in_sentence:
                ch['before_context'] = original_text
                ch['after_context'] = new_text
                changelog_entries.append(ch)
        else:
            modified_sentences.append(original_text)

    # Update DF
    df['sentence_text'] = modified_sentences
    
    print(f"Saving normalized corpus to {OUTPUT_CSV}...")
    df.to_csv(OUTPUT_CSV, index=False)
    
    print(f"Saving changelog to {CHANGELOG_FILE}...")
    log_df = pd.DataFrame(changelog_entries)
    if not log_df.empty:
        # Reorder columns
        cols = ['row_index', 'sentence_id', 'original_token', 'new_token', 'position', 'before_context', 'after_context']
        log_df = log_df[cols]
        log_df.to_csv(CHANGELOG_FILE, index=False)
    else:
        print("No changes made!")
        with open(CHANGELOG_FILE, 'w') as f: f.write("No changes")

    # Summary
    summary = f"""NORMALIZATION SUMMARY
=====================
Total Sentences Processed: {len(df)}
Total Changes Applied: {total_changes}
Sentences Modified: {len(set(log_df['row_index'])) if not log_df.empty else 0}
Unique Tokens Normalized: {log_df['original_token'].nunique() if not log_df.empty else 0}
"""
    print(summary)
    with open(SUMMARY_FILE, 'w') as f:
        f.write(summary)

if __name__ == "__main__":
    apply_normalization()
