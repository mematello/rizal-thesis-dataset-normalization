
import csv
import re
import os
import sys
from collections import Counter

# Configuration
INPUT_FILES = {
    'elfili': 'elfili_chapter_sentences_modernized.csv',
    'noli': 'noli_chapter_sentences_modernized.csv'
}
MAPPING_MASTER = 'phase_d_mapping_master.csv'

OUTPUT_MAPPING = 'phase_d_mapping_master_v2.csv'
OUTPUT_FILES = {
    'elfili': 'elfili_chapter_sentences_modernized_v2.csv',
    'noli': 'noli_chapter_sentences_modernized_v2.csv'
}
OUTPUT_LOGS = {
    'elfili': 'phase_d2_log_elfili.csv',
    'noli': 'phase_d2_log_noli.csv'
}
OUTPUT_SUMMARIES = {
    'elfili': 'phase_d2_summary_elfili.md',
    'noli': 'phase_d2_summary_noli.md'
}
CANDIDATES_FILE = 'phase_d2_candidates.csv'

# Safe Proper Noun Exceptions (Start with specific ones if needed, otherwise rely on heuristics)
# We won't list all names, but generally will skip capitalized words unless they match specific patterns.
SAFE_CAPS_PREFIXES = ['Pagca', 'Sapagca', 'Boong'] 

def load_csv_data(filepath):
    """Reads CSV into list of dicts."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return [], []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames

def load_mappings(filepath):
    """Loads existing mappings."""
    mappings = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                mappings.append(row)
    return mappings

def get_tokens(text):
    """Simple tokenizer keeping punctuation causing sticking? 
    Better to use regex to find words for candidates."""
    # We want to identify tokens that "contain c" or are "boong".
    # We can split by non-word chars.
    return re.findall(r"\b[\w']+\b", text)

def is_candidate(token):
    """Check if token is a candidate for modernization."""
    # 1. Contains 'c' or 'C'
    if 'c' in token or 'C' in token:
        return True
    # 2. 'boong' / 'boon' variants
    if 'boong' in token.lower():
        return True
    return False

def propose_mapping(token):
    """
    Decide if a token should be mapped.
    Returns (target_form, rule_type, notes) or None.
    """
    original = token
    lower = token.lower()
    
    # Rule 1: 'boong' -> 'buong'
    if lower == 'boong':
        # Preserve Case
        if token == 'Boong': return 'Buong', 'lexicon', 'Archaic oo -> uo (Start)'
        if token == 'boong': return 'buong', 'lexicon', 'Archaic oo -> uo'
        if token == 'BOONG': return 'BUONG', 'lexicon', 'Archaic oo -> uo (Caps)'

    # Specific user-cited fixes
    if lower == 'pagcacasipan':
        return 'pagkakaisipan', 'lexicon', 'Specific fix: pagcacasipan -> pagkakaisipan'
    if lower == 'pagcakapisan':
        return 'pagkakapisán', 'lexicon', 'Specific fix: pagcakapisan -> pagkakapisán'

    # Rule 2: 'pagcaca' prefix (MUST CHECK BEFORE pagca)
    # This handles pagcaca... -> pagkaka...
    # e.g. pagcacapisan -> pagkakapisan
    if 'pagcaca' in lower:
        # Check if it starts with pagcaca
        if lower.startswith('pagcaca'):
             # Replace first occurrence of pagcaca with pagkaka
             # Case handling:
             target_prefix = 'Pagkaka' if token[0].isupper() else 'pagkaka'
             target = target_prefix + token[7:] # 7 chars in pagcaca
             # But wait, what if the rest has 'c'? 
             # e.g. pagcacadlac -> pagkakadlak
             # For now, let's fix the prefix at least. 
             # Better: just replace 'pagcaca' with 'pagkaka' in the string (case matched)
             # But 'replace' might hit middle?
             # User said "pagcaca* forms".
             if lower.startswith('pagcaca'):
                 # Reconstruct
                 prefix_len = 7
                 new_prefix = 'Pagkaka' if token[0] == 'P' else 'pagkaka'
                 target = new_prefix + token[prefix_len:]
                 return target, 'prefix', 'Archaic pagcaca- -> pagkaka-'

    # Rule 3: 'sapagca' prefix
    if lower.startswith('sapagca'):
        # sapagca (7 chars). c is at 5.
        if len(token) >= 7 and token[5].lower() == 'c' and token[6].lower() == 'a':
            target = list(token)
            target[5] = 'k' if token[5] == 'c' else 'K'
            return "".join(target), 'prefix', 'Archaic sapagca- -> sapagka-'

    # Rule 4: 'pagca' prefix (Generic)
    if lower.startswith('pagca'):
        # Replace 'c' with 'k' in the prefix 'pagca' -> 'pagka'
        # Check if it's just 'pagca' or longer
        target = list(token)
        # pagca has 5 chars. indices 0,1,2,3,4. 'c' is at 3.
        if len(token) >= 5 and token[3].lower() == 'c' and token[4].lower() == 'a':
            target[3] = 'k' if token[3] == 'c' else 'K'
            return "".join(target), 'prefix', 'Archaic pagca- -> pagka-'
            
    # Rule 5: 'pumanhic' -> 'pumanhik' (ending in c)
    if lower.endswith('hic'):
        target = token[:-1] + 'k' # replace last c with k
        return target, 'suffix', 'Archaic -hic -> -hik'


    return None

def analyze_candidates(files):
    candidates = {} # token -> {count, chapters, examples}
    
    for fname, path in files.items():
        rows, _ = load_csv_data(path)
        print(f"Scanning {fname} ({len(rows)} rows)...")
        
        for row in rows:
            text = row.get('sentence_text', row.get('text', ''))
            # Find tokens
            tokens = get_tokens(text)
            
            chapter = row.get('chapter_number', 'unknown')
            
            for t in tokens:
                if is_candidate(t):
                    # Filter existing proper nouns logic: 
                    # If Capitalized and NOT in likely archaic list, we tentatively skip from *mapping* but keep in *candidates* log?
                    # The user wants "Candidate discovery... likely archaic".
                    # I'll log everything that matches 'c'/'boong' and filter later/manually or via heuristic.
                    
                    if t not in candidates:
                        candidates[t] = {'count': 0, 'chapters': set(), 'examples': []}
                    
                    c = candidates[t]
                    c['count'] += 1
                    c['chapters'].add(chapter)
                    if len(c['examples']) < 3:
                        c['examples'].append(text[:100] + "...") # Snippet
                        
    return candidates

def generate_new_mappings(candidates, existing_mappings):
    """
    candidates: dict of token -> info
    existing_mappings: list of dicts
    """
    existing_keys = {m['source_form'] for m in existing_mappings}
    
    new_mappings = []
    
    for token, info in candidates.items():
        if token in existing_keys:
            continue
            
        # Filter exclusions
        # 1. Foreign/Proper Noun filter: 
        # If starts with uppercase, and NOT recognized as archaic form -> Skip
        if token[0].isupper() and not any(token.startswith(p) for p in SAFE_CAPS_PREFIXES):
            # Checking if it's "Carlos", "Custodio", "Cristo", etc.
            # We skip.
            continue
        
        # 2. 'ñ' check
        if 'ñ' in token or 'Ñ' in token:
            continue
            
        proposal = propose_mapping(token)
        if proposal:
            target, rtype, notes = proposal
            
            # Additional safety:
            if target == token: continue
            
            new_mappings.append({
                'source_form': token,
                'target_form': target,
                'rule_type': rtype,
                'notes': notes,
                'apply_case_sensitive': 'True',
                'word_boundary_only': 'True'
            })
            
    return new_mappings

class ModernizerV2:
    def __init__(self, mappings):
        self.mappings = mappings
        self.rules = []
        for m in mappings:
            src = m['source_form']
            tgt = m['target_form']
            pattern = r'\b' + re.escape(src) + r'\b'
            # Note: Phase D used Case Sensitive logic mostly.
            # We enforce case sensitive if apply_case_sensitive is True
            # which we set to True for all new mappings.
            # Existing mappings might have it set or not.
            flags = 0 if m.get('apply_case_sensitive', 'True') == 'True' else re.IGNORECASE
            self.rules.append({
                'regex': re.compile(pattern, flags),
                'target': tgt,
                'src': src
            })
            
    def process_text(self, text, log_list, meta):
        current_text = text
        for rule in self.rules:
            # We want to capture replacements for logging
            # This requires a new string construction or callback
            
            def repl(match):
                # Log it
                log_list.append({
                    'chapter_number': meta.get('chapter_number', ''),
                    'sentence_number': meta.get('sentence_number', ''),
                    'source_form': match.group(0),
                    'target_form': rule['target'],
                    'context_snippet': current_text  # Store full text or snippet? User wants audit logs.
                })
                return rule['target']
                
            current_text = rule['regex'].sub(repl, current_text)
            
        return current_text

def main():
    print("Starting Phase D.2 Audit...")
    
    # 1. Candidate Discovery
    candidates = analyze_candidates(INPUT_FILES)
    
    # Save Candidates CSV
    print(f"Saving candidates to {CANDIDATES_FILE}...")
    with open(CANDIDATES_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['token', 'count_total', 'example_contexts', 'chapters_seen'])
        for t, info in sorted(candidates.items(), key=lambda x: x[1]['count'], reverse=True):
            examples = " | ".join(info['examples']).replace('\n', ' ')
            chapters = ",".join(sorted(list(info['chapters'])))
            writer.writerow([t, info['count'], examples, chapters])
            
    # 2. Propose Mappings
    existing = load_mappings(MAPPING_MASTER)
    new_maps = generate_new_mappings(candidates, existing)
    
    print(f"Proposed {len(new_maps)} new mappings.")
    
    # 3. Create V2 Master
    all_mappings = existing + new_maps
    # Dedup by source_form just in case
    seen_src = set()
    final_mappings = []
    for m in all_mappings: # Prefer existing? Or new? Append new at end usually means they cover residuals.
        if m['source_form'] not in seen_src:
            final_mappings.append(m)
            seen_src.add(m['source_form'])
            
    print(f"Writing {OUTPUT_MAPPING} with {len(final_mappings)} total rules...")
    with open(OUTPUT_MAPPING, 'w', encoding='utf-8', newline='') as f:
        if final_mappings:
            fieldnames = list(final_mappings[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(final_mappings)
    
    # 4. Apply
    modernizer = ModernizerV2(final_mappings)
    
    for key, infile in INPUT_FILES.items():
        outfile = OUTPUT_FILES[key]
        logfile = OUTPUT_LOGS[key]
        summaryfile = OUTPUT_SUMMARIES[key]
        
        print(f"Processing {infile} -> {outfile}...")
        rows, fieldnames = load_csv_data(infile)
        
        logs = []
        out_rows = []
        replaced_count = 0
        
        for row in rows:
            text = row.get('sentence_text', row.get('text', ''))
            meta = {
                'chapter_number': row.get('chapter_number', ''),
                'sentence_number': row.get('sentence_number', '')
            }
            
            # Capture logs for this row
            row_logs = []
            new_text = modernizer.process_text(text, row_logs, meta)
            
            if row_logs:
                replaced_count += len(row_logs)
                for l in row_logs:
                    l['dataset'] = key
                    logs.append(l)
            
            row['sentence_text'] = new_text # Update text
            out_rows.append(row)
            
        # Write Output
        with open(outfile, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(out_rows)
            
        # Write Logs
        with open(logfile, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['dataset', 'chapter_number', 'sentence_number', 'source_form', 'target_form', 'context_snippet'])
            writer.writeheader()
            writer.writerows(logs)
            
        # Write Summary
        high_impact = Counter([l['source_form'] for l in logs]).most_common(50)
        
        with open(summaryfile, 'w', encoding='utf-8') as f:
            f.write(f"# Phase D.2 Summary: {key}\n")
            f.write(f"- Input Row Count: {len(rows)}\n")
            f.write(f"- Output Row Count: {len(out_rows)}\n")
            f.write(f"- Total Replacements: {replaced_count}\n")
            f.write(f"\n## Top Mappings Applied\n")
            for src, count in high_impact:
                f.write(f"- {src}: {count}\n")
                
        print(f"Completed {key}. Replacements: {replaced_count}")

if __name__ == '__main__':
    main()
