import pandas as pd

CSV_FILE = '/Users/marcusoliver/Desktop/rizal-thesis-dataset-normalization/noli_chapter_sentences_NORMALIZED.csv'

def fix_errors():
    try:
        df = pd.read_csv(CSV_FILE)
        print(f"Loaded {len(df)} rows.")
        
        # Repair 1: Sentence 78 (Chapter 42) - "la ocasion la pintan calva"
        # We look for the normalized version to revert it
        # Note: The grep showed the context was: "la okasion la pintan kalva"
        target_1_err = 'la okasion la pintan kalva'
        target_1_corr = 'la ocasion la pintan calva'
        
        # Repair 2: "poco" - "estudiantillos de poco latin"
        # Grep showed: "estudiantillos de poko latin"
        target_2_err = 'estudiantillos de poko latin'
        target_2_corr = 'estudiantillos de poco latin'
        
        corrections = 0
        
        for idx, row in df.iterrows():
            text = str(row['sentence_text'])
            new_text = text
            modified = False
            
            if target_1_err in text:
                new_text = new_text.replace(target_1_err, target_1_corr)
                print(f"Fixed Row {idx}: Reverted 'okasion/kalva'")
                modified = True
                
            if target_2_err in text:
                new_text = new_text.replace(target_2_err, target_2_corr)
                print(f"Fixed Row {idx}: Reverted 'poko'")
                modified = True
                
            if modified:
                df.at[idx, 'sentence_text'] = new_text
                corrections += 1
                
        if corrections > 0:
            df.to_csv(CSV_FILE, index=False)
            print(f"Applied {corrections} corrections. Saved to {CSV_FILE}.")
        else:
            print("No Error patterns found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_errors()
