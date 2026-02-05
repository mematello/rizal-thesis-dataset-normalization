
import csv
import re
import os

INPUT_FILE = 'noli_chapter_sentences_titles_fixed_v2.csv'
OUTPUT_FILE = 'noli_chapter_sentences_titles_fixed_v3.csv'
SUMMARY_FILE = 'phase_t3_noli_correction_summary.md'

CORRECTIONS = {
    # Full replacement
    'LIV.': 'QUIDQUID LATET, ADPAREBIT, NIL INULTUM REMANEBIT',
    'LIV': 'QUIDQUID LATET, ADPAREBIT, NIL INULTUM REMANEBIT',
    
    # Substring replacements
    'PANGANGANAC': 'PANGANGANAK',
    'FILOSOFO': 'PILOSOPO',
    'INAACALA': 'INAAKALA',
}

def apply_corrections():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file not found: {INPUT_FILE}")
        return

    changes_made = {} # title -> new_title

    print("Processing Noli T.3 Corrections...")
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f_in, \
         open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f_out:
         
        reader = csv.DictReader(f_in)
        writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
        writer.writeheader()
        
        for row in reader:
            original = row['chapter_title']
            new_title = original
            
            # 1. Exact match for LIV
            if new_title.strip() in ['LIV.', 'LIV']:
                new_title = CORRECTIONS['LIV']
                
            # 2. Substring replacements
            # Order matters? No overlaps here.
            for key, val in CORRECTIONS.items():
                if key in ['LIV.', 'LIV']: continue
                if key in new_title:
                    new_title = new_title.replace(key, val)
            
            if new_title != original:
                if original not in changes_made:
                    changes_made[original] = new_title
                row['chapter_title'] = new_title
            
            writer.writerow(row)
            
    # Write Summary
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f_sum:
        f_sum.write("# Phase T.3 Noli Title Correction Summary\n\n")
        f_sum.write("## Modified Titles\n")
        for old, new in changes_made.items():
            f_sum.write(f"- `{old}` -> `{new}`\n")
    
    print("Done. Changes:")
    for old, new in changes_made.items():
        print(f" - {old} -> {new}")

if __name__ == '__main__':
    apply_corrections()
