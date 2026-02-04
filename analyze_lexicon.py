
import csv
import re
import collections
import os

FILES = [
    'elfili_extraction_normalized.csv',
    'noli_extraction_normalized.csv'
]

OUTPUT_CANDIDATES = 'lexicon_candidates.csv'

def tokenize(text):
    # Simple tokenization: preserve casing for analysis, but we often map lowercase
    return re.findall(r'\b[a-zA-ZñÑ]+\b', text)

def main():
    counter = collections.Counter()
    
    for fname in FILES:
        if not os.path.exists(fname):
            print(f"Skipping {fname} (not found)")
            continue
            
        print(f"Scanning {fname}...")
        with open(fname, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = row.get('text', '')
                tokens = tokenize(text)
                counter.update(tokens)
                
    print(f"Total unique tokens: {len(counter)}")
    
    # Filter for archaic candidates
    # Rules of thumb for Tagalog archaic:
    # - 'c' (hard k or s) -> k / s (e.g. cayo, caya, cinuha)
    # - 'qu' -> k (e.g. quita)
    # - 'gui' -> gi (e.g. guinoo) - wait, 'gui' might be valid 'gitara'? 
    #   Old Tagalog: 'guinoo' -> 'ginoo'. 'guinto' -> 'ginto'.
    # - 'u' vs 'o' is tricky (totoo vs tutuo), usually let's stick to C/Qu/Gui first
    
    candidates = []
    
    for word, count in counter.most_common():
        word_lower = word.lower()
        
        # Heuristics for "archaic-looking"
        has_c = 'c' in word_lower
        has_qu = 'qu' in word_lower
        has_gui = 'gui' in word_lower
        
        # Exclude common allowed words with these patterns if any (e.g. 'comedor' is spanish loan, might keep 'c')
        # We just list them all, user (me) will curate.
        
        if has_c or has_qu or has_gui:
            candidates.append((word, count))
            
    print(f"Found {len(candidates)} archaic candidates.")
    
    with open(OUTPUT_CANDIDATES, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['token', 'count', 'proposed_modern'])
        for word, count in candidates:
            # Simple auto-propose for common patterns to speed up manual review (simulated)
            proposal = ""
            w_lower = word.lower()
            
            # Simple C -> K
            # Avoid changing ch -> h yet? usually walang 'ch' sa old tagalog unless spanish.
            # 'c' -> 'k' if hard? 'c' -> 's' if soft (ce, ci)?
            # El Fili ortho: 'cung' (kung), 'cay' (kay). 'ce' (se? 'cedula').
            
            # This is just for my view, I won't use proposals blindly.
            proposal = word # placeholder
            
            writer.writerow([word, count, proposal])
            
    print(f"Wrote candidates to {OUTPUT_CANDIDATES}")
    
    # Print top 30
    print("Top 30 Candidates:")
    for w, c in candidates[:30]:
        print(f"  {w}: {count}")

if __name__ == '__main__':
    main()
