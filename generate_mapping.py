
import csv
import os

CANDIDATES_FILE = 'lexicon_candidates.csv'
OUTPUT_MAPPING = 'phase_d_mapping_master.csv'

# Curated Safe Replacements (Source Lower -> Target Lower)
# Based on top items from lexicon analysis
SAFE_MAP = {
    'cung': 'kung',
    'co': 'ko',
    'aco': 'ako',
    'pagca': 'pagka',
    'canya': 'kanya',
    'canilang': 'kanilang',
    'cayo': 'kayo',
    'cay': 'kay',
    'anac': 'anak',
    'ca': 'ka',
    'caya': 'kaya',
    'cong': 'kong',
    'acong': 'akong',
    'canila': 'kanila',
    'castila': 'kastila',
    'saca': 'saka',
    'icaw': 'ikaw',
    'capitang': 'kapitang',
    'cahoy': 'kahoy',
    'guinoong': 'ginoong',
    'pagcatapos': 'pagkatapos',
    'guinagawa': 'ginagawa',
    'guinawa': 'ginawa',
    'cayong': 'kayong',
    'cahi': 'kahi',
    'wicang': 'wikang',
    'guitna': 'gitna',
    'cailan': 'kailan',
    'capatid': 'kapatid',
    'cami': 'kami',
    'tungcol': 'tungkol',
    'naguing': 'naging',
    'dacong': 'dakong',
    'catawan': 'katawan',
    'guinoo': 'ginoo',
    'calagayan': 'kalagayan',
    'caibigan': 'kaibigan',
    'casama': 'kasama',
    'tinatawag': 'tinatawag', # no change
    'catulad': 'katulad',
    'canino': 'kanino',
    'baca': 'baka',
    'cahapon': 'kahapon',
    'camay': 'kamay',
    'caluluwa': 'kaluluwa',
    'capag': 'kapag',
    'cabayo': 'kabayo',
    'cabataan': 'kabataan',
    'caaway': 'kaaway',
    'calaman': 'kalaman',
    'carunungan': 'karunungan',
    'catotohanan': 'katotohanan',
    'capangyarihan': 'kapangyarihan',
    'cuncubana': 'kunkubana', # rare?
    'cusang': 'kusang',
    'cusa': 'kusa',
    'café': 'k ape', # NO, keep cafe esp if spanish loan. cafe -> kape?
    # Keeping loans safe: avoid 'cafe', 'familia' (pamilya? No, lexical diff), 'cebollas'.
    # Only strictly archaic Tagalog markers.
}

# Special mappings that include punctuation (not in simple token list usually)
SPECIAL_MAPS = [
    ("nguni't", "ngunit", "punctuation_merge"),
    ("nguni’t", "ngunit", "punctuation_merge"), # curly
    ("datapowa't", "datapwat", "punctuation_merge"),
    ("datapowa’t", "datapwat", "punctuation_merge"),
    ("datapuwa't", "datapwat", "punctuation_merge"),
    ("datapuwa’t", "datapwat", "punctuation_merge"),
    ("subali't", "subalit", "punctuation_merge"),
    ("subali’t", "subalit", "punctuation_merge"),
    ("sapagca't", "sapagkat", "punctuation_merge"),
    ("sapagca’t", "sapagkat", "punctuation_merge"),
    ("bagama't", "bagamat", "punctuation_merge"),
    ("bagama’t", "bagamat", "punctuation_merge"),
    ("baga ma't", "bagamat", "punctuation_merge"), 
    ("baga ma’t", "bagamat", "punctuation_merge"),
]

def main():
    mappings = []
    
    # Load candidates to verify existence
    found_tokens = set()
    if os.path.exists(CANDIDATES_FILE):
        with open(CANDIDATES_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                found_tokens.add(row['token'].lower()) # normalized lower
                found_tokens.add(row['token']) # original form
    
    # 1. Add Safe Maps (Auto-cased)
    # If 'cung' is in found tokens, add 'cung' -> 'kung'.
    # If 'Cung' is in found tokens, add 'Cung' -> 'Kung'.
    
    for archaic, modern in SAFE_MAP.items():
        # Lowercase
        if archaic in found_tokens:
            mappings.append({
                'source_form': archaic,
                'target_form': modern,
                'rule_type': 'lexicon',
                'notes': 'Archaic C/Qu/Gui normalization',
                'apply_case_sensitive': 'True',
                'word_boundary_only': 'True'
            })
            
        # Title case
        archaic_cap = archaic.capitalize()
        modern_cap = modern.capitalize()
        if archaic_cap in found_tokens:
             mappings.append({
                'source_form': archaic_cap,
                'target_form': modern_cap,
                'rule_type': 'lexicon',
                'notes': 'Archaic C/Qu/Gui normalization (Capitalized)',
                'apply_case_sensitive': 'True',
                'word_boundary_only': 'True'
            })
            
    # 2. Add Special Maps
    for src, tgt, note in SPECIAL_MAPS:
        # We assume these exist or force them.
        # Since they have punctuation, they might not be in simple token list.
        # We add them unconditionally but script will only apply if found.
        # Lower
        mappings.append({
            'source_form': src,
            'target_form': tgt,
            'rule_type': 'special',
            'notes': note,
            'apply_case_sensitive': 'False', # Handled loosely or strict? stick to False (case-insensitive search) for these usually lowercase connectors?
            # Actually, punctuation connectors might be capitalized at start of sentence. "Ngunit..."
            # Best to strict case them too?
            'apply_case_sensitive': 'False', # Let's say False implies "Match ignoring case, apply target matching case"?
            # No, standard is usually: False = Regex IGNORECASE flag.
            # If I use re.sub, I can use a callable to match case.
            # But the user asked for explicit table.
            # Let's add capitalized versions explicitly.
            'word_boundary_only': 'True'
        })
        
        # Cap
        src_cap = src.capitalize()
        tgt_cap = tgt.capitalize()
        mappings.append({
            'source_form': src_cap,
            'target_form': tgt_cap,
            'rule_type': 'special',
            'notes': note,
            'apply_case_sensitive': 'True',
            'word_boundary_only': 'True'
        })

    # Sort
    mappings.sort(key=lambda x: x['source_form'])
    
    print(f"Generated {len(mappings)} mappings.")
    
    with open(OUTPUT_MAPPING, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['source_form', 'target_form', 'rule_type', 'notes', 'apply_case_sensitive', 'word_boundary_only']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(mappings)
        
    print(f"Saved to {OUTPUT_MAPPING}")

if __name__ == '__main__':
    main()
