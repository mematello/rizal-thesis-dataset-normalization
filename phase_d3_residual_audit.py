
import csv
import re
import os
import sys
from collections import Counter

# Parsing
INPUT_FILES = {
    'elfili': 'elfili_chapter_sentences_modernized_v2.csv',
    'noli': 'noli_chapter_sentences_modernized_v2.csv'
}
OUTPUT_INVENTORY = 'residual_c_inventory.csv'
OUTPUT_CLASSIFIED = 'residual_c_classified.csv'
OUTPUT_SUMMARY = 'residual_c_audit_summary.md'

# Heuristics
# B = Spanish Suffixes/Patterns
SPANISH_SUFFIXES = ['cion', 'cia', 'za', 'co', 'ca', 'do', 'da', 'ro', 'ra', 'lo', 'la', 'no', 'na', 'mo', 'ma', 'to', 'ta', 'so', 'sa', 'ivo', 'iva', 'al', 'ar', 'er', 'ir', 'ez', 'es']

def load_data(files):
    data = []
    for fname, path in files.items():
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['dataset'] = fname
                    data.append(row)
    return data

def get_c_tokens(text):
    tokens = re.findall(r"\b[\w']+\b", text)
    return [t for t in tokens if 'c' in t or 'C' in t]

def classify_token(token):
    """
    Classify token into A, B, C, D, E.
    A = Archaic Tagalog
    B = Spanish loanword
    C = Proper noun
    D = Foreign quotation
    E = Uncertain
    """
    original = token
    lower = token.lower()
    
    # Rule 1: Capitalized -> Proper Noun (C) or Title
    # Note: Some archaic tagalog might be capitalized (e.g. at start of sentence), but without robust NLP, 
    # assuming capitalized = Proper/Title is safer than assuming Archaic.
    # Exception: if it appears lowercase elsewhere? We process per token type here, not token instance (though we sum counts).
    # If the token is 'Canyang' (capitalized), it counts as C here. 
    # But wait, 'Canyang' is just 'Kanyang'. If we mark it C, we won't modernize it.
    # Check if commonly archaic even if capitalized.
    
    is_capitalized = token[0].isupper()

    # Rule 2: Explicit Spanish/Foreign indicators (ce, ci, ch, ñ, -cion) -> B or C
    if 'ce' in lower or 'ci' in lower:
        if is_capitalized: return 'C', 'Proper/Spanish', None
        return 'B', 'Spanish/Foreign pattern (ce/ci)', None
    if 'ch' in lower:
        if is_capitalized: return 'C', 'Proper/Foreign (ch)', None
        return 'B', 'Spanish/Foreign (ch)', None
    if 'ñ' in lower:
        if is_capitalized: return 'C', 'Proper (ñ)', None
        return 'B', 'Spanish (ñ)', None

    # Rule 3: Archaic Lookup (High Confidence)
    # Handle capitalized variants for these too
    archaic_lookup = {
        'canyang': 'kanyang',
        'cang': 'kang',
        'cayo': 'kayo',
        'canila': 'kanila',
        'capowa': 'kapuwa',
        'capuwa': 'kapuwa',
        'casi': 'kasi',
        'caya': 'kaya',
        'co': 'ko',
        'cu': 'ku',
        'acala': 'akala',
        'inocol': 'inukol',
        'inocul': 'inukol',
        'uica': 'wika',
        'wica': 'wika',
        'wicas': 'wakas',
        'bulaclac': 'bulaklak',
        'calolowa': 'kaluluwa',
        'caluluwa': 'kaluluwa',
        'caniya': 'kaniya', 
        'canino': 'kanino',
        'catotohanan': 'katotohanan',
        'caunti': 'kaunti',
        'culay': 'kulay',
        'lacas': 'lakas',
        'buhoc': 'buhok',
        'insik': 'intsik',
        'insic': 'intsik',
        'camay': 'kamay',
        'casalanan': 'kasalanan',
        'capitan': 'kapitan', # Common noun usage
        'sacali': 'sakali',
        'sacaling': 'sakaling',
        'cailan': 'kailan',
        'cailangan': 'kailangan',
        'baca': 'baka',
        'bucas': 'bukas',
        'cahit': 'kahit',
        'cauauang': 'kawawang',
        'cagayat': 'kagayat',
        'cabilang': 'kabilang'
    }
    
    if lower in archaic_lookup:
        modern = archaic_lookup[lower]
        # Restore case
        if is_capitalized:
            modern = modern.capitalize()
            # If strictly archaic, we map it to A.
            # But if capitalized, we previously said C.
            # 'Canyang' -> 'Kanyang'. Should be modernized.
            return 'A', f'Specific Archaic: {lower}', modern
        return 'A', f'Specific Archaic: {lower}', modern

    # Explicit Spanish Allowlist (to prevent B being flagged as A below)
    spanish_common = ['cura', 'cruz', 'cristiano', 'cristo', 'carlos', 'cabesa', 'cabeza', 'calle', 'cocina', 'coche', 'civil', 'comedia', 'colegio', 'convento', 'cuarto', 'cajon', 'calesa', 'carta', 'caso', 'cosa', 'cuenta', 'cuento', 'cuerpo', 'cuadro', 'curiosidad']
    if lower in spanish_common:
         if is_capitalized: return 'C', 'Proper/Spanish Common', None
         return 'B', 'Common Spanish Loan', None

    # Rule 4: Prefix/Affix Logic
    # Archaic Tagalog often uses c for k.
    # Patterns: ca-, co-, cu- followed by Tagalog consonants or general usage.
    # Affixes: nagc-, magc-, nac-, cum-, -c (suffix)
    
    if lower.startswith(('cum', 'nagc', 'magc', 'nac', 'pagc')):
        proposal = token.replace('c', 'k').replace('C', 'K')
        return 'A', 'Archaic Affix (cum/nagc/magc/nac/pagc)', proposal

    if 'qu' in lower:   
        if 'aquing' in lower: return 'A', 'Archaic aquing->aking', token.replace('qu', 'k')
        if 'iquao' in lower: return 'A', 'Archaic iquao->ikaw', 'ikaw'

    # General Startswith ca/co/cu -> Likely A if not in Spanish list
    # But risky if we don't know the word.
    # However, given we are in Phase D.3 audit, we want to FIND these.
    # Let's be aggressive in classifying A for ca/co/cu if not analyzed as B/C.
    if lower.startswith(('ca', 'co', 'cu')):
        # Proposal: simple replacement
        proposal = token.replace('c', 'k').replace('C', 'K')
        confidence = 'Medium'
        if is_capitalized:
            # If capitalized and not in lookup, likely Proper (C).
            # e.g. 'Calamba', 'Cavite'.
            return 'C', 'Proper Noun (Capitalized ca/co/cu)', None
        else:
            return 'A', 'Archaic ca/co/cu start', proposal

    # Endswith 'c' -> 'k'
    if lower.endswith('c'):
        if lower in ['frac', 'zinc', 'chic']:
             return 'B', 'Foreign ending in c', None
        proposal = token.replace('c', 'k').replace('C', 'K')
        return 'A', 'Archaic ending -c', proposal
        
    # Contains 'c' (mid word)
    # e.g. 'acala', 'bacit'
    if 'c' in lower:
        if is_capitalized:
             return 'C', 'Proper Noun (Contains c)', None
        # Check adjacent vowels?
        # a-c-a -> k
        # e.g. 'acala'
        if re.search(r'[aeiou]c[aeiou]', lower):
            proposal = token.replace('c', 'k').replace('C', 'K')
            return 'A', 'Archaic intervocalic c', proposal

    return 'E', 'Uncertain', None

def analyze():
    print("Loading data...")
    rows = load_data(INPUT_FILES)
    print(f"Loaded {len(rows)} rows.")
    
    inventory = {} # token -> {count, contexts, chapters}
    
    print("Extracting 'c' tokens...")
    for row in rows:
        text = row.get('sentence_text', '')
        tokens = get_c_tokens(text)
        chap = row.get('chapter_number', '?')
        dset = row.get('dataset', '')
        
        for t in tokens:
            if t not in inventory:
                inventory[t] = {'count': 0, 'contexts': [], 'chapters': set()}
            
            inv = inventory[t]
            inv['count'] += 1
            inv['chapters'].add(f"{dset}:{chap}")
            if len(inv['contexts']) < 3:
                inv['contexts'].append(text)
                
    # Output Inventory
    print(f"Writing {OUTPUT_INVENTORY}...")
    sorted_inv = sorted(inventory.items(), key=lambda x: x[1]['count'], reverse=True)
    with open(OUTPUT_INVENTORY, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['token', 'count', 'example_contexts', 'chapters'])
        for t, data in sorted_inv:
            ctx = " | ".join(data['contexts']).replace('\n', ' ')
            chaps = ",".join(list(data['chapters'])[:10]) # Truncate chapters
            writer.writerow([t, data['count'], ctx, chaps])
            
    # Classify
    print("Classifying...")
    classified_data = [] # list of dicts
    
    # Counters for summary
    counts = Counter()
    
    for t, data in sorted_inv:
        cat, notes, prop = classify_token(t)
        counts[cat] += 1
        classified_data.append({
            'token': t,
            'count': data['count'],
            'category': cat,
            'proposed_modern_form': prop if prop else '',
            'confidence': 'High' if cat in ['C'] else 'Medium',
            'notes': notes
        })
        
    print(f"Writing {OUTPUT_CLASSIFIED}...")
    with open(OUTPUT_CLASSIFIED, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['token', 'count', 'category', 'proposed_modern_form', 'confidence', 'notes'])
        writer.writeheader()
        writer.writerows(classified_data)
        
    # Summary
    print(f"Writing {OUTPUT_SUMMARY}...")
    with open(OUTPUT_SUMMARY, 'w', encoding='utf-8') as f:
        f.write("# Phase D.3 Residual 'c' Audit Summary\n\n")
        f.write(f"- **Total Unique Tokens with 'c'**: {len(sorted_inv)}\n")
        f.write("- **Breakdown by Category**:\n")
        for cat in sorted(counts.keys()):
            f.write(f"  - {cat}: {counts[cat]}\n")
            
        f.write("\n## Top 20 Most Frequent Residuals (with Classification)\n")
        for item in classified_data[:20]:
            f.write(f"- **{item['token']}** ({item['count']}) -> [{item['category']}] {item['proposed_modern_form']}\n")
            
        f.write("\n## Preserved Token Examples (Category C/B/D)\n")
        # Grab some C/B examples
        preserved = [x['token'] for x in classified_data if x['category'] in ['C', 'B', 'D']][:10]
        for p in preserved:
            f.write(f"- {p}\n")
            
        f.write("\n\n**Note**: No blind replacements were applied. This is an analytical report.\n")
        
    print("Done.")

if __name__ == '__main__':
    analyze()
