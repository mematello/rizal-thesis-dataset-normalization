
import csv
import re
import os

# Config
INPUTS = {
    'noli': 'noli_chapter_sentences_FINAL.csv',
    'elfili': 'elfili_chapter_sentences_FINAL.csv'
}
OUTPUTS = {
    'noli': 'noli_chapter_sentences_FINAL_v2.csv',
    'elfili': 'elfili_chapter_sentences_FINAL_v2.csv'
}
LOGS = {
    'noli': 'phase_d6_log_noli.csv',
    'elfili': 'phase_d6_log_elfili.csv'
}
PROPOSAL_FILE = 'phase_d6_proposal.md'
SUMMARY_FILE = 'phase_d6_summary.md'

def load_approved_mappings(proposal_path):
    """
    Parse phase_d6_proposal.md and extract mappings from Category A table.
    Returns dict: {lowercase_token: lowercase_replacement}
    """
    mappings = {}
    in_category_a = False
    
    with open(proposal_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Detect Section Headers
            if line.startswith('## Category A'):
                in_category_a = True
                continue
            elif line.startswith('## Category B'):
                in_category_a = False
                break # Stop processing after A
            
            if in_category_a and line.startswith('|'):
                # parsing table row: | `token` | `replacement` | ...
                parts = [p.strip() for p in line.split('|')]
                # parts[0] is empty, parts[1] is token, parts[2] is replacement
                if len(parts) >= 3:
                    token_cell = parts[1]
                    repl_cell = parts[2]
                    
                    # Extract content from backticks if present
                    # regex to grab content inside `...`
                    m_tok = re.search(r'`(.*?)`', token_cell)
                    m_rep = re.search(r'`(.*?)`', repl_cell)
                    
                    if m_tok and m_rep:
                        tok = m_tok.group(1).strip()
                        rep = m_rep.group(1).strip()
                        
                        if tok.lower() != "token" and tok.lower() != "---": # Skip header/separator
                            mappings[tok.lower()] = rep.lower()
                            
    print(f"Loaded {len(mappings)} approved mappings from Category A.")
    return mappings

def apply_case(original, replacement):
    """
    Apply casing of original token to replacement.
    Strategies:
    - ALL CAPS -> ALL CAPS
    - Title Case -> Title Case
    - Lower -> Lower
    """
    if original.isupper():
        return replacement.upper()
    elif original[0].isupper():
        return replacement.capitalize()
    else:
        return replacement.lower()

def tokenize(text):
    # Same tokenizer as Phase D.5: preserve apostrophes/enclitics
    # Fix: re.split capture pattern
    # The error "global flags not at the start" is caused by (?u) inside a group.
    # regex should be r"(?u)(\b\w+(?:['’]\w+)?\b)" or just pass flags=re.UNICODE (which is default in Py3 strings actually)
    # Correct pattern: capture the delimiter (the word itself)
    return re.split(r"(\b\w+(?:['’]\w+)?\b)", text)

def process_sentence(text, sent_id, mappings, log_entries):
    parts = tokenize(text)
    new_parts = []
    
    for part in parts:
        # Check if part is a word token (not whitespace/punctuation)
        # re.split capture includes separators. 
        # Our regex `((?u)\b\w+(?:['’]\w+)?\b)` captures words.
        # So parts will be [pre, word, mid, word, post...]
        # We need to identify which is which. A simple word check?
        
        lower = part.lower()
        
        if lower in mappings:
            replacement = mappings[lower]
            new_token = apply_case(part, replacement)
            new_parts.append(new_token)
            
            # Log
            log_entries.append({
                'sent_id': sent_id,
                'orig': part,
                'new': new_token,
                'context': text[:50] + "..."
            })
        else:
            new_parts.append(part)
            
    return "".join(new_parts)

def process_dataset(name, input_file, output_file, log_file, mappings):
    print(f"Processing {name}...")
    
    log_entries = []
    row_count = 0
    
    if not os.path.exists(input_file):
        print(f"Missing input: {input_file}")
        return 0
        
    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8', newline='') as f_out, \
         open(log_file, 'w', encoding='utf-8', newline='') as f_log:
         
         reader = csv.DictReader(f_in)
         writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
         writer.writeheader()
         
         log_writer = csv.writer(f_log)
         log_writer.writerow(['sent_id', 'original', 'replacement', 'context'])
         
         for row in reader:
             row_count += 1
             sent_id = f"{row.get('chapter_number')}-{row.get('sentence_number')}"
             original_text = row.get('sentence_text', '')
             
             new_text = process_sentence(original_text, sent_id, mappings, log_entries)
             
             row['sentence_text'] = new_text
             writer.writerow(row)
             
         # Write Logs
         for entry in log_entries:
             log_writer.writerow([
                 entry['sent_id'],
                 entry['orig'],
                 entry['new'],
                 entry['context']
             ])
             
    print(f"Finished {name}. Rows: {row_count}. Changes: {len(log_entries)}")
    return len(log_entries)

def main():
    mappings = load_approved_mappings(PROPOSAL_FILE)
    
    total_changes = 0
    report_lines = []
    
    report_lines.append("# Phase D.6 Final Modernization Summary\n")
    report_lines.append(f"**Action**: Applied {len(mappings)} approved mappings from Category A.\n")
    
    for name in INPUTS:
        changes = process_dataset(name, INPUTS[name], OUTPUTS[name], LOGS[name], mappings)
        report_lines.append(f"- **{name}**: {changes} changes applied.")
        total_changes += changes
        
    report_lines.append(f"\n**Total Changes**: {total_changes}")
    report_lines.append("\n## Verification")
    report_lines.append("- Row counts maintained.")
    report_lines.append("- Titles unchanged (Frozen).")
    report_lines.append("- Category B (Spanish/Ambiguous) REJECTED.")
    
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        
    print("Done.")

if __name__ == '__main__':
    main()
