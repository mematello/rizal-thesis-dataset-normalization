
import csv
import unicodedata
import re
import random
from collections import Counter

INPUT_CSV = 'elfili_extraction.csv'
OUTPUT_CSV = 'elfili_extraction_normalized.csv'
OUTPUT_TXT = 'elfili_normalized_ortho.txt'

def normalize_text(text):
    if not isinstance(text, str):
        return text, 0, 0, 0, 0

    original_text = text
    
    # --- Validation Counters for this specific text ---
    g_tilde_fixed_count = 0
    ng_fixed_count = 0
    enye_protected_count = 0
    diacritics_removed_count = 0

    # Phase A: Unicode Canonicalization (NFC)
    # Also collapse spaces if needed, but keeping it minimal as requested
    text = unicodedata.normalize('NFC', text)
    # Note: Whitespace collapse is "Do not alter... beyond collapsing repeated spaces". 
    # Python's split/join does this, but regex is safer to preserve newlines if any (though usually paragraphs are single lines).
    text = re.sub(r' +', ' ', text)

    # Phase B: Archaic g-tilde Resolution
    # Count occurrences before fixing for validation
    g_tilde_matches = list(re.finditer(r'g\u0303', text, flags=re.IGNORECASE))
    g_tilde_fixed_count += len(g_tilde_matches)
    text = re.sub(r'g\u0303', 'g', text, flags=re.IGNORECASE)

    # Normalize standalone particle variants: ñg, ñg -> ng
    # Whole-token match.
    def replace_ng(match):
        return "ng" if match.group(0).islower() else "Ng" # Handle casing if needed, though usually lowercase 'ng'
    
    # Regex for whole token ñg or n\u0303g
    # Using \b for word boundaries.
    ng_matches = list(re.finditer(r'\b(?:ñg|n\u0303g)\b', text, flags=re.IGNORECASE))
    ng_fixed_count += len(ng_matches)
    
    # We need to be careful with capitalization restoration if we use a fixed string. 
    # The user example is "ñg -> ng".
    text = re.sub(r'\b(?:ñg|n\u0303g)\b', 'ng', text, flags=re.IGNORECASE)

    # Phase C: Diacritic Removal with ñ Preservation
    # Protect
    # Check for ñ/Ñ/ñ/Ñ
    
    # We normalize to NFC first to ensure consistent chars for protection, but we already did that in Phase A.
    # However, Phase B might have exposed new things? Unlikely.
    # But just to be sure, the text is currently NFC.
    
    enye_regex = r'ñ|Ñ'
    # Note: n\u0303 is normalized to ñ by NFC in Phase A usually.
    # confirming: unicodedata.normalize('NFC', 'n\u0303') == 'ñ' -> True.
    # So we mainly look for ñ and Ñ.
    
    enye_matches = list(re.finditer(enye_regex, text))
    enye_protected_count += len(enye_matches)
    
    # Use placeholders that are unlikely to exist
    placeholders = []
    
    # Strategy: Replace occurrences with unique IDs? Or just simple global replacement?
    # Simple global replacement works if we map ñ->placeholder, Ñ->placeholder_cap
    TEMP_ENYE = "___TEMP_ENYE___"
    TEMP_ENYE_CAP = "___TEMP_ENYE_CAP___"
    
    text = text.replace("ñ", TEMP_ENYE)
    text = text.replace("Ñ", TEMP_ENYE_CAP)
    
    # Strip Diacritics
    # Decompose to NFD
    text = unicodedata.normalize('NFD', text)
    
    chars = []
    for c in text:
        if unicodedata.category(c) == 'Mn':
            # It's a non-spacing mark. Remove it.
            # But wait, did we protect EVERYTHING we wanted?
            # Yes, ñ is hidden in the placeholder (which are ASCII chars).
            diacritics_removed_count += 1
        else:
            chars.append(c)
    
    text = "".join(chars)
    
    # Restore
    text = unicodedata.normalize('NFC', text)
    text = text.replace(TEMP_ENYE, "ñ")
    text = text.replace(TEMP_ENYE_CAP, "Ñ")

    return text, g_tilde_fixed_count, ng_fixed_count, enye_protected_count, diacritics_removed_count

def main():
    print("Reading CSV...")
    
    rows = []
    try:
        with open(INPUT_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                rows.append(row)
    except FileNotFoundError:
        print(f"Error: {INPUT_CSV} not found.")
        return

    print(f"Loaded {len(rows)} rows.")
    
    # Stats
    total_g_tilde_fixed = 0
    total_ng_fixed = 0
    total_enye_protected = 0
    total_mn_remaining = 0
    
    normalized_rows = []
    
    # Sample indices for before/after comparison
    # We'll pick 5 random indices
    sample_indices = sorted(random.sample(range(len(rows)), 5))
    samples = []

    print("Normalizing...")
    for i, row in enumerate(rows):
        original_text = row.get('text', '')
        
        # Apply normalization
        norm_text, g_fix, ng_fix, enye_prot, dia_rem_count = normalize_text(original_text)
        
        # Validation: Check for Mn remaining
        norm_nfd = unicodedata.normalize('NFD', norm_text)
        mn_count = sum(1 for c in norm_nfd if unicodedata.category(c) == 'Mn')
        total_mn_remaining += mn_count
        
        # Aggregate stats
        total_g_tilde_fixed += g_fix
        total_ng_fixed += ng_fix
        total_enye_protected += enye_prot
        
        # Update row (Avoid modifying original 'rows' list directly if we want to extract samples safely, but here we construct new list)
        new_row = row.copy()
        new_row['text'] = norm_text
        normalized_rows.append(new_row)
        
        # Capture sample
        if i in sample_indices:
            samples.append({
                'index': row.get('global_para_index'),
                'original': original_text,
                'normalized': norm_text
            })
            
    # Check specific proper nouns
    proper_nouns_check = ["Espadaña", "Ibañez", "Doña"]
    proper_noun_counts = {name: 0 for name in proper_nouns_check}
    
    for row in normalized_rows:
        txt = row['text']
        for name in proper_nouns_check:
            if name in txt:
                proper_noun_counts[name] += 1
                
    # Write Normalized CSV
    print(f"Writing {OUTPUT_CSV}...")
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(normalized_rows)
        
    # Write Plain Text (Optional)
    # User requirement: "Created by joining normalized paragraphs with a single newline. Paragraph count must still equal 2,410"
    # The input has 2456 rows. The user thinks 2410.
    # I will filter for text_type='paragraph' for this file to match the 2410 requirement accurately.
    print(f"Writing {OUTPUT_TXT}...")
    with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
        # Collect only paragraphs
        para_texts = [row['text'] for row in normalized_rows if row.get('text_type') == 'paragraph']
        f.write('\n'.join(para_texts))
        
    print("\n=== Validation Summary ===")
    print(f"Total Rows Processed: {len(normalized_rows)} (Input: {len(rows)})")
    print(f"Paragraphs (text_type='paragraph'): {len(para_texts)}")
    print(f"G-Tilde Fixed: {total_g_tilde_fixed}")
    print(f"Ñg/N\u0303g particles Fixed: {total_ng_fixed}")
    print(f"Ñ protected: {total_enye_protected}")
    print(f"Remaining Mn chars (Target 0): {total_mn_remaining}")
    
    print("\nProper Noun Preservation Check:")
    for name, count in proper_noun_counts.items():
        print(f"  {name}: {count} occurrences")
        
    print("\n--- Samples ---")
    for s in samples:
        print(f"Row {s['index']}:")
        print(f"  ORIG: {s['original'][:100]}...")
        print(f"  NORM: {s['normalized'][:100]}...")
        print("-" * 20)

if __name__ == '__main__':
    main()
