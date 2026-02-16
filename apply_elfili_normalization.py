import pandas as pd
import sys
import re

# Configuration
INPUT_CORPUS = "/Users/marcusoliver/Desktop/rizal-thesis-dataset-normalization/elfili_chapter_sentences_FINAL_v2.csv"
CHANGE_LOG = "/Users/marcusoliver/Desktop/rizal-thesis-dataset-normalization/change_log_elfili.csv"
OUTPUT_CORPUS = "elfili_chapter_sentences_NORMALIZED.csv"

def main():
    print("Loading resources...")
    try:
        df_corpus = pd.read_csv(INPUT_CORPUS)
        df_log = pd.read_csv(CHANGE_LOG)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    print(f"Loaded Corpus: {len(df_corpus)} sentences")
    print(f"Loaded Log: {len(df_log)} actions")
    
    # Filter for applied changes (APPROVE or EDIT)
    applied_changes = df_log[df_log['action'].isin(['APPROVE', 'EDIT'])]
    print(f"Applying {len(applied_changes)} changes...")
    
    # Create a map of Sentence ID -> List of changes
    changes_by_id = {}
    for _, row in applied_changes.iterrows():
        sid = str(row['sentence_id']) # Ensure String ID
        if sid not in changes_by_id:
            changes_by_id[sid] = []
        changes_by_id[sid].append((row['original_word'], row['final_word']))
        
    data = []
    corrections_count = 0
    
    TOKEN_PATTERN = r"[a-zA-ZñÑáéíóúÁÉÍÓÚüÜ'’\-]+"
    
    for idx, row in df_corpus.iterrows():
        # Match ID type: The precompute script used `str(idx)`
        sid = str(idx) 
        
        original_text = str(row['sentence_text'])
        new_text = original_text
        
        if sid in changes_by_id:
            changes = changes_by_id[sid]
            
            # Use a list to track processed tokens
            # We want to replace tokens that match our pending changes.
            # To handle multiple occurrences of the same word in a sentence:
            # The HITL review was sequential.
            # If "cat" appears twice and we approved both, both change.
            # If we approved one and rejected one, we have a problem in the *log* format.
            # BUT, given the log structure, we only have (original, final).
            # The probability of a mixed action on the exact same word token in one sentence is low for this specific task.
            # So we will replace ALL instances of 'original' with 'final' for this sentence.
            
            # Sort changes by length of original word descending? 
            # Better: Tokenize and replace exact matches.
            
            def replace_token(match):
                token = match.group(0)
                # Check if this token is in our changes list
                for orig, final in changes:
                    if token == orig:
                        return final
                return token
            
            new_text = re.sub(TOKEN_PATTERN, replace_token, original_text)
            
            if new_text != original_text:
                corrections_count += 1
                
        out_row = row.copy()
        out_row['sentence_text'] = new_text
        data.append(out_row)
        
    out_df = pd.DataFrame(data)
    out_df.to_csv(OUTPUT_CORPUS, index=False)
    
    print("="*40)
    print(f"Normalization Complete.")
    print(f"Sentences Modified: {corrections_count}")
    print(f"Output saved to: {OUTPUT_CORPUS}")
    print("="*40)

if __name__ == "__main__":
    main()
