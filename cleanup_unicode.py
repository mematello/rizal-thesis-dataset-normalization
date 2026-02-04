
import csv
import unicodedata
import os

INPUT_CSV = 'elfili_extraction_normalized.csv'
OUTPUT_CSV = 'elfili_extraction_normalized.csv' # Overwriting as requested/implied by "Updated:" deliverables
INPUT_TXT = 'elfili_normalized_ortho.txt'
OUTPUT_TXT = 'elfili_normalized_ortho.txt'

def check_counts(text):
    # check for g + U+0303
    g_tilde_count = text.count("g\u0303") + text.count("G\u0303")
    
    # check for Mn
    mn_count = sum(1 for c in text if unicodedata.category(c) == 'Mn')
    
    # check for ñ/Ñ (precomposed) matches
    # We want to verify they exist as single chars
    enye_count = text.count('\u00f1') + text.count('\u00d1')
    
    return g_tilde_count, mn_count, enye_count

def main():
    print("Starting Unicode Cleanup...")
    
    # 1. Process CSV
    rows = []
    
    # Read
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)
            
    print(f"Read {len(rows)} CSV rows.")
    
    cleaned_rows = []
    
    csv_g_tilde = 0
    csv_mn = 0
    csv_enye = 0
    
    espada_before = None
    dona_before = None
    espana_before = None
    ibanez_before = None
    
    for row in rows:
        text = row['text']
        
        # Capture verification samples before change (if interesting) -> mostly checking they exist
        if "Espadaña" in text and espada_before is None: espada_before = text
        if "Doña" in text and dona_before is None: dona_before = text
        if "España" in text and espana_before is None: espana_before = text
        if "Ibañez" in text and ibanez_before is None: ibanez_before = text
        
        # Operations
        # 1. NFC
        text = unicodedata.normalize('NFC', text)
        
        # 2. Ensure ñ/Ñ are precomposed
        # NFC usually does this. U+006E U+0303 -> U+00F1
        # Double check?
        # If normalizing NFC, 'n\u0303' becomes '\u00f1'.
        
        # Stats
        g, mn, enye = check_counts(text)
        csv_g_tilde += g
        csv_mn += mn
        csv_enye += enye
        
        row['text'] = text
        cleaned_rows.append(row)

    # Write CSV
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)
        
    print(f"Updated {OUTPUT_CSV} with NFC text.")
    
    # 2. Process TXT
    # Read
    with open(INPUT_TXT, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        
    print(f"Read {len(lines)} TXT lines (paragraphs).")
    
    txt_g_tilde = 0
    txt_mn = 0
    txt_enye = 0
    
    cleaned_lines = []
    
    for line in lines:
        # Operations
        text = unicodedata.normalize('NFC', line)
        
        g, mn, enye = check_counts(text)
        txt_g_tilde += g
        txt_mn += mn
        txt_enye += enye
        
        cleaned_lines.append(text)
        
    # Write TXT
    with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
        
    print(f"Updated {OUTPUT_TXT} with NFC text.")
    
    # 3. Validation Report
    
    print("\n=== Validation Summary ===")
    print(f"CSV Rows: {len(cleaned_rows)} (Target: 2456)")
    print(f"TXT Lines: {len(cleaned_lines)} (Target: 2410)")
    
    print("\nMetrics (CSV):")
    print(f"  Count(g + ~): {csv_g_tilde} (Target: 0)")
    print(f"  Count(Mn):    {csv_mn} (Target: 0)")
    print(f"  Count(ñ/Ñ):   {csv_enye} (Target ~143)")
    
    print("\nMetrics (TXT):")
    print(f"  Count(g + ~): {txt_g_tilde} (Target: 0)")
    print(f"  Count(Mn):    {txt_mn} (Target: 0)")
    print(f"  Count(ñ/Ñ):   {txt_enye} (Target ~143)")
    
    print("\nSpot Verification (Post-Cleanup):")
    
    def check_word(word, rows):
        found = False
        for r in rows:
            if word in r['text']:
                print(f"  ✅ '{word}' found in: ...{r['text'][r['text'].find(word)-10:r['text'].find(word)+20]}...")
                # Verify chars of word
                extracted = r['text'][r['text'].find(word):r['text'].find(word)+len(word)]
                hex_str = " ".join([f"U+{ord(c):04X}" for c in extracted])
                print(f"     Hex: {hex_str}")
                found = True
                break
        if not found:
            print(f"  ❌ '{word}' NOT FOUND")

    check_word("Espadaña", cleaned_rows)
    check_word("Doña", cleaned_rows)
    check_word("España", cleaned_rows)
    check_word("Ibañez", cleaned_rows)
if __name__ == '__main__':
    main()
