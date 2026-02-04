
import csv
import re
import argparse
import sys
import os

MAPPING_FILE = 'phase_d_mapping_master.csv'

def load_mappings():
    mappings = []
    if not os.path.exists(MAPPING_FILE):
        print(f"Error: {MAPPING_FILE} not found.")
        sys.exit(1)
        
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mappings.append(row)
    return mappings

class Modernizer:
    def __init__(self, mappings, dataset_name):
        self.mappings = mappings
        self.dataset_name = dataset_name
        self.logs = []
        self.replacements_count = 0
        
        # Compile regexes
        # We need a list of (regex, target)
        self.rules = []
        for m in mappings:
            src = m['source_form']
            tgt = m['target_form']
            
            # Escape src just in case (though mostly alphanumeric)
            # handle special punctuation in src (e.g. nguni't)
            escaped_src = re.escape(src)
            
            # Word boundary check
            # if source has punctuation at end/start, \b might not match what we want?
            # e.g. "nguni't" ends with 't' (word char). So \bnguni't\b works.
            # "datapuwa't" -> works.
            # "baga ma't" -> works.
            
            pattern =  r'\b' + escaped_src + r'\b'
            
            # Case sensitivity?
            # Our mapping table has explicit Cased entries.
            # We should respect `apply_case_sensitive`.
            flags = 0
            if m['apply_case_sensitive'] != 'True':
                flags = re.IGNORECASE
                
            regex = re.compile(pattern, flags)
            self.rules.append({'regex': regex, 'target': tgt, 'src': src})

    def process_text(self, text, row_meta):
        # Apply rules sequentially
        # Note: Sequential application might be slow or overlap?
        # "nguni't" vs "nguni". If we have both, order matters.
        # Our mapping generator sorted by alphabetically source_form?
        # Longer matches should probably go first? 
        # But we only have whole words. "nguni" is not in our list (it's "ngunit").
        # "ng" is in list? No.
        # So overlap risk is low.
        
        original_text = text
        current_text = text
        
        # We need to log EVERY replacement.
        # re.sub with callback.
        
        for rule in self.rules:
            
            def replace_callback(match):
                match_str = match.group(0)
                
                # Check consistency if case-sensitive handling is loose
                # But we have explicit cased rules. 
                # e.g. if we match 'cung' using 'Cung' rule (if we had case-insensitive), we'd have issue.
                # But we set apply_case_sensitive=True for almost everything.
                # So 'Cung' rule only matches 'Cung'.
                # 'Special' maps used case_sensitive=True for explicit caps too.
                # So exact match mostly.
                
                # Double check Case Preservation logic meant for "Safe Rules"
                # If we mapped 'cung'->'kung' (lower), and text has 'Cung' (Upper),
                # our regex (if sensitive) won't match.
                # But we added 'Cung'->'Kung' to map explicitly.
                # So 'Cung' rule handles it.
                
                self.replacements_count += 1
                
                # Log
                # Capture context (snippet)
                start = match.start()
                end = match.end()
                snippet_before = current_text[max(0, start-10):end+10]
                
                # Log entry
                self.logs.append({
                    'dataset': self.dataset_name,
                    'chapter_number': row_meta.get('chapter_number', row_meta.get('chapter_index', '')),
                    'sentence_number': row_meta.get('sentence_number', row_meta.get('global_para_index', '')),
                    'source_form': match_str,
                    'target_form': rule['target'],
                    'context_snippet': snippet_before
                })
                
                return rule['target']
                
            current_text = rule['regex'].sub(replace_callback, current_text)
            
        return current_text

def process_file(input_csv, output_csv, dataset_name, modernizer):
    print(f"Processing {input_csv} -> {output_csv}...")
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
        
    out_rows = []
    
    for row in rows:
        text_col = 'text' if 'text' in row else 'sentence_text' # handle sentences csv
        
        orig_text = row[text_col]
        
        # Apply modernization
        # Pass minimal meta for logging
        meta = {
            'chapter_number': row.get('chapter_number', row.get('chapter_index', '')),
            'sentence_number': row.get('sentence_number', ''),
            'global_para_index': row.get('global_para_index', '')
        }
        
        new_text = modernizer.process_text(orig_text, meta)
        
        row[text_col] = new_text
        out_rows.append(row)
        
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)
        
    print(f"Finished {dataset_name}. Total Replacements: {modernizer.replacements_count}")

def main():
    mappings = load_mappings()
    
    # 4 datasets
    tasks = [
        ('elfili_extraction_normalized.csv', 'elfili_extraction_modernized.csv', 'elfili_paragraphs'),
        ('elfili_chapter_sentences.csv', 'elfili_chapter_sentences_modernized.csv', 'elfili_sentences'),
        ('noli_extraction_normalized.csv', 'noli_extraction_modernized.csv', 'noli_paragraphs'),
        ('noli_chapter_sentences.csv', 'noli_chapter_sentences_modernized.csv', 'noli_sentences')
    ]
    
    all_logs = []
    
    for inp, out, name in tasks:
        if not os.path.exists(inp):
            print(f"Skip {inp} (not found)")
            continue
            
        mod = Modernizer(mappings, name)
        process_file(inp, out, name, mod)
        all_logs.extend(mod.logs)
        
    # Write merged logs (or separate? User asked for phase_d_log_elfili.csv etc)
    # I'll separate them now.
    
    logs_elfili = [l for l in all_logs if 'elfili' in l['dataset']]
    logs_noli = [l for l in all_logs if 'noli' in l['dataset']]
    
    for fname, logs in [('phase_d_log_elfili.csv', logs_elfili), ('phase_d_log_noli.csv', logs_noli)]:
        print(f"Writing {fname} ({len(logs)} entries)...")
        with open(fname, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['dataset', 'chapter_number', 'sentence_number', 'source_form', 'target_form', 'context_snippet']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(logs)

if __name__ == '__main__':
    main()
