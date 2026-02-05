
import csv
import re
import os

# Input/Output Files
INPUT_FILES = {
    'elfili': 'elfili_chapter_sentences_modernized_v2.csv',
    'noli': 'noli_chapter_sentences_modernized_v2.csv'
}
OUTPUT_FILES = {
    'elfili': 'elfili_chapter_sentences_titles_fixed.csv',
    'noli': 'noli_chapter_sentences_titles_fixed.csv'
}
LOG_FILES = {
    'elfili': 'phase_t_title_log_elfili.csv',
    'noli': 'phase_t_title_log_noli.csv'
}
NORMALIZED_TITLES_FILES = {
    'elfili': 'elfili_chapter_titles_normalized.csv',
    'noli': 'noli_chapter_titles_normalized.csv'
}
SUMMARY_FILES = {
    'elfili': 'phase_t_title_summary_elfili.md',
    'noli': 'phase_t_title_summary_noli.md'
}

# Explicit Mappings (UPPERCASE Source -> Target)
# Note: Input titles will be converted to UPPER case first before mapping check.
EXPLICIT_MAPPINGS = {
    'PAGCACAPISAN': 'PAGKAKAPISAN',
    'MANGA': 'MGA',
    'ANgA': 'ANG', # Typos if any
    'CAUGALIAN': 'KAUGALIAN',
    'MACAPANGYARIHAN': 'MAKAPANGYARIHAN',
    'CALOLOWANG': 'KALULUWANG',
    'CASAYSAYAN': 'KASAYSAYAN',
    'CAISIPAN': 'KAISIPAN',
    'PAGCAIN': 'PAGKAIN',
    'CATUWIRA\'T': 'KATUWIRA\'T',
    'LACAS': 'LAKAS',
    'PANUCALA': 'PANUKALA',
    'MAGCURO': 'MAGKURO',
    'KINAGUISNANG': 'KINAGISNANG',
    'PANGANANGANAC': 'PANGANANGANAK',
    'PANGWACAS': 'PANGWAKAS',
    'BAHAGUI': 'BAHAGI',
    'CONG': 'KONG', # Just in case
}

# Foreign Titles to Preserve (UPPERCASE)
# These will skip word-level mapping, but will still effectively be uppercased.
FOREIGN_TITLES = [
    'IL BUON DI SI CONOSCE DA MATTINA.',
    '¡VAE VICTIS!',
    'LIV.', # Chapter 54 title is just LIV.
    'LOS BAÑOS', # Partial spanish, likely fine
    'ELIAS', # Name
    'BASILIO',
    'SISA',
    'CRISOSTOMO IBARRA'
]

def clean_title(title, chapter_num):
    """
    Apply normalization rules to a title string.
    Returns: (normalized_title, change_notes)
    """
    original = title
    if not title:
        return "", "Empty title"

    # Step 1: Casing extraction artifact cleanup (pre-upper)
    # Some artifacts might be 'MANgA' -> 'MGA' before upper?
    # Actually plan said normalize casing to FULL UPPERCASE first.
    # But wait, 'MANgA' upper is 'MANGA'. Our mapping handles 'MANGA' -> 'MGA'.
    # So we can just upper first.
    
    current = title.strip()
    
    # Step 2: Remove Artifacts [210], [261]
    current = re.sub(r'\[\d+\]', '', current).strip()
    
    # Step 3: Remove Roman Numerals at START
    # e.g. "III MGA ALAMAT" -> "MGA ALAMAT"
    # Regex: ^(M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))\s+
    # We must ensure we don't match empty string (unlikely with \s+)
    # Also handle 'III. ' with dot?
    match = re.match(r'^([XIVLMC]+\.?)\s+(.*)', current, re.IGNORECASE)
    if match:
        # Check if the captured group 1 looks like a valid numeral sequence for the chapter?
        # Or just blindly remove?
        # "IV SI KABISANG TALES".
        # "ISANG PAGCACAPISAN" -> Start with I? "I" is roman numeral 1.
        # But "ISANG" is a word.
        # So we need to be careful using \s+.
        # "ISANG" does NOT match "Numeral + Space + Rest" if strict roman parsing?
        # "I" matches. "SANG" is rest.
        # "ISANG" -> I SANG? No.
        # Let's rely on space.
        # "III " matches.
        # "ISANG " -> "I" is numeral? Yes.
        # Risk: "ISANG" starts with "I".
        # If text is "ISANG..."
        # If we assume explicit check: Is the first word a roman numeral?
        # And is the rest of the title meaningful?
        # Or, explicit check against chapter number?
        # Chapter 1 Noli: "ISANG PAGCACAPISAN".
        # If we strip "I ", we get "SANG...". Bad.
        # El Fili Ch 3: "III MGA ALAMAT".
        # Solution: Only strip if it matches the current chapter number?
        # Or checking if title starts with roman numeral commonly used.
        # Noli titles DO NOT have numerals in string usually (based on extraction).
        # El Fili titles DO have them.
        # So we can restrict roman stripping to El Fili dataset?
        # Or just check if the first token is a Roman Numeral AND the second token is NOT part of it?
        pass # implemented in loop below
        
    # Better approach for Roman Numerals:
    # Split by space.
    parts = current.split()
    if len(parts) > 1:
        first = parts[0].upper().replace('.', '')
        # Check if first is roman numeral
        if re.fullmatch(r'M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})', first):
            # Potential numeral.
            # "ISANG" -> "ISANG" is not valid roman (S, G not valid).
            # "III" -> valid.
            # "VI" -> valid.
            # "ANG" -> not valid.
            # So checking validity of chars is good.
            # What about "D" (Di)? "IL BUON DI..."
            # "DI" -> 501? D=500, I=1. Yes valid.
            # But "IL" is not valid (I before L ok? No, I before X/V. X before L/C. C before D/M).
            # standard roman regex: ^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$
            # "DI" is D+I = 501? Yes.
            # Is "DI" a chapter title word? "IL BUON DI..." -> First word is IL.
            # IL is invalid roman. (I can only precede V or X).
            # So "IL" is safe.
            # "IV" -> Valid.
            # "I" -> Valid.
            # What about "I" in "I GABING..." (typo)? "ISANG" is safe.
            # "A" -> not roman.
            if re.fullmatch(r'^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$', first):
                # It is a valid roman numeral sequence.
                # Remove it?
                # One edge case: "I" (The word 'I' in English? No tagalog 'Ay'?)
                # Risk is low.
                # Strip it.
                current = " ".join(parts[1:])
    
    # Step 4: Uppercase
    current = current.upper()
    
    if current in FOREIGN_TITLES:
        # Don't map words
        if current != original:
            return current, "Formatting/Cleaning only (Foreign preserved)"
        return current, "Unchanged"

    # Step 5: Explicit Mapping
    words = current.split()
    new_words = []
    changes = []
    
    for w in words:
        clean_w = w.strip('.,;:"\'?![]()') # Handle punctuation
        prefix = ""
        suffix = ""
        # Preserve punctuation existence for reconstruction
        # Simple heuristic: map the core word.
        # e.g. "VISPERA" -> core VISPERA.
        # "CATUWIRA'T" -> core CATUWIRA'T.
        
        # Check if w is in map directly
        if w in EXPLICIT_MAPPINGS:
            new_words.append(EXPLICIT_MAPPINGS[w])
            changes.append(f"{w}->{EXPLICIT_MAPPINGS[w]}")
            continue
            
        # Try stripping punct
        # Just use simple regex replacement for the word in the string? No, words might repeat.
        # Reconstruct token by token.
        
        # Check mapping for clean_w
        if clean_w in EXPLICIT_MAPPINGS:
            # Reconstruct with punct
            # Easy way: replace clean_w inside w with mapped.
            mapped = EXPLICIT_MAPPINGS[clean_w]
            new_w = w.replace(clean_w, mapped)
            new_words.append(new_w)
            changes.append(f"{clean_w}->{mapped}")
        else:
            new_words.append(w)
            
    final_title = " ".join(new_words)
    
    note = ""
    if final_title != original:
        note = "Normalized"
        if changes:
             note += f": {', '.join(changes)}"
        else:
             note += " (Formatting/Artifacts)"
             
    return final_title, note


def process_dataset(name, input_path, output_path, log_path, normalized_list_path):
    print(f"Processing {name}...")
    
    titles_map = {} # old -> new to write distinct list
    
    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8', newline='') as f_out, \
         open(log_path, 'w', encoding='utf-8', newline='') as f_log:
         
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        
        log_writer = csv.writer(f_log)
        log_writer.writerow(['chapter_number', 'original_title', 'normalized_title', 'notes'])
        
        # We need to process chapter-by-chapter, but title is in every row.
        # We should compute title once per chapter to ensure consistency?
        # Or just row by row? Row by row is fine, checking consistency is implicit.
        
        # Actually, let's track unique titles encountered to produce the normalized list
        
        processed_rows = 0
        
        for row in reader:
            original = row['chapter_title']
            chap = row['chapter_number']
            
            normalized, note = clean_title(original, chap)
            
            row['chapter_title'] = normalized
            writer.writerow(row)
            
            # Log distinct titles
            if original not in titles_map:
                titles_map[original] = (normalized, note, chap)
                if normalized != original:
                    log_writer.writerow([chap, original, normalized, note])
            
            processed_rows += 1
            
    print(f"Finished {name}. Rows: {processed_rows}. Unique Titles: {len(titles_map)}")
    
    # Write Normalized Titles List
    with open(normalized_list_path, 'w', encoding='utf-8', newline='') as f_norm:
        writer = csv.writer(f_norm)
        writer.writerow(['chapter_number', 'original_title', 'normalized_title', 'notes'])
        # Sort by chapter (try to parse int)
        sorted_titles = sorted(titles_map.items(), key=lambda x: int(x[1][2]) if x[1][2].isdigit() else 9999)
        
        for orig, (norm, note, chap) in sorted_titles:
            writer.writerow([chap, orig, norm, note])

    return titles_map

def main():
    for name, path in INPUT_FILES.items():
        if os.path.exists(path):
            process_dataset(
                name, 
                path, 
                OUTPUT_FILES[name], 
                LOG_FILES[name], 
                NORMALIZED_TITLES_FILES[name]
            )
        else:
            print(f"Skipping {name}, input not found.")

if __name__ == "__main__":
    main()
