
import csv
import unicodedata
import re
import sys

INPUT_CSV = 'noli_extraction.csv'
OUTPUT_CSV = 'noli_extraction_normalized.csv'
OUTPUT_TXT = 'noli_normalized_ortho.txt'
LOG_FILE = 'normalization_log_noli.txt'

def normalize_text(text):
    if not isinstance(text, str):
        return text, 0, 0, 0, 0

    # Validation Counters
    g_tilde_fixed_count = 0
    ng_fixed_count = 0
    enye_protected_count = 0
    diacritics_removed_count = 0

    # Phase A: Unicode Canonicalization (NFC)
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Phase B: Archaic g-tilde Resolution
    # Look for g + combined tilde
    matches = list(re.finditer(r'g\u0303', text, flags=re.IGNORECASE))
    g_tilde_fixed_count += len(matches)
    text = re.sub(r'g\u0303', 'g', text, flags=re.IGNORECASE)

    # Normalize standalone particle variants: ñg, ñg -> ng
    matches_ng = list(re.finditer(r'\b(?:ñg|n\u0303g)\b', text, flags=re.IGNORECASE))
    ng_fixed_count += len(matches_ng)
    
    # helper for casing
    def replace_ng(match):
        token = match.group(0)
        return "Ng" if token[0].isupper() else "ng"

    text = re.sub(r'\b(?:ñg|n\u0303g)\b', replace_ng, text, flags=re.IGNORECASE)

    # Phase C: Diacritic Removal with ñ Preservation
    # Protect ñ/Ñ
    enye_matches = list(re.finditer(r'ñ|Ñ', text))
    enye_protected_count += len(enye_matches)
    
    TEMP_ENYE = "___TEMP_ENYE___"
    TEMP_ENYE_CAP = "___TEMP_ENYE_CAP___"
    
    text = text.replace("ñ", TEMP_ENYE)
    text = text.replace("Ñ", TEMP_ENYE_CAP)
    
    # Strip Diacritics (NFD -> numeric Mn strip -> NFC)
    text = unicodedata.normalize('NFD', text)
    
    chars = []
    for c in text:
        if unicodedata.category(c) == 'Mn':
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
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)
            
    print(f"Loaded {len(rows)} rows.")
    
    total_g = 0
    total_ng = 0
    total_enye = 0
    total_mn = 0
    
    normalized_rows = []
    
    print("Normalizing...")
    for row in rows:
        orig = row.get('text', '')
        norm, g, ng, enye, dia = normalize_text(orig)
        
        # Validation stats
        total_g += g
        total_ng += ng
        total_enye += enye
        total_mn += dia
        
        row['text'] = norm
        normalized_rows.append(row)
        
    # Validation check for final output
    final_mn = 0
    final_g_tilde = 0
    final_enye = 0
    
    for row in normalized_rows:
        t = row['text']
        final_g_tilde += len(re.findall(r'g\u0303', t, flags=re.IGNORECASE))
        final_mn += sum(1 for c in t if unicodedata.category(c) == 'Mn')
        final_enye += len(re.findall(r'ñ|Ñ', t))
        
    # Write CSV
    print(f"Writing {OUTPUT_CSV}...")
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(normalized_rows)
        
    # Write TXT (Narrative Paragraphs Only)
    # The requirement: "noli_normalized_ortho.txt (narrative paragraphs only, one per line)"
    # Filter by text_type == 'paragraph'
    
    print(f"Writing {OUTPUT_TXT}...")
    para_rows = [r for r in normalized_rows if r['text_type'] == 'paragraph']
    with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
        f.write('\n'.join([r['text'] for r in para_rows]))
        
    # Write Log / Report
    report = f"""Normalization Report: Noli Me Tangere

Total Rows: {len(normalized_rows)}
Total Narrative Paragraphs: {len(para_rows)}

Changes Applied:
- G-Tilde Fixed: {total_g}
- NG Variants Fixed: {total_ng}
- Diacritics Removed: {total_mn}
- Ñ Protected: {total_enye}

Final Validation:
- Remaining G-Tilde: {final_g_tilde} (Must be 0)
- Remaining Combining Marks (Mn): {final_mn} (Must be 0)
- Preserved Ñ/Ñ: {final_enye} (Should match protected count ideally)
"""
    print(report)
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
        
    if final_g_tilde == 0 and final_mn == 0:
        print("✅ VALIDATION SUCCESS")
    else:
        print("❌ VALIDATION FAILED")

if __name__ == '__main__':
    main()
