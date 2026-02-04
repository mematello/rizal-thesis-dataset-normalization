
import csv
import collections
import random
import unicodedata
import os

LOG_FILES = {
    'El Filibusterismo': 'phase_d_log_elfili.csv',
    'Noli Me Tangere': 'phase_d_log_noli.csv'
}

FILES = {
    'El Filibusterismo': {
        'orig': 'elfili_extraction_normalized.csv',
        'mod': 'elfili_extraction_modernized.csv',
        'sent_orig': 'elfili_chapter_sentences.csv',
        'sent_mod': 'elfili_chapter_sentences_modernized.csv',
        'summary': 'phase_d_summary_elfili.md'
    },
    'Noli Me Tangere': {
        'orig': 'noli_extraction_normalized.csv',
        'mod': 'noli_extraction_modernized.csv',
        'sent_orig': 'noli_chapter_sentences.csv',
        'sent_mod': 'noli_chapter_sentences_modernized.csv',
        'summary': 'phase_d_summary_noli.md'
    }
}

def analyze_logs(log_file):
    stats = collections.Counter()
    examples = []
    
    if not os.path.exists(log_file):
        return stats, examples, 0
        
    with open(log_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    total = len(rows)
    for row in rows:
        key = f"{row['source_form']} -> {row['target_form']}"
        stats[key] += 1
        
    if rows:
        examples = random.sample(rows, min(20, len(rows)))
        
    return stats, examples, total

def validate_csv(orig_file, mod_file):
    with open(orig_file, 'r', encoding='utf-8') as f:
        orig_rows = len(list(csv.reader(f)))
    
    mn_count = 0
    mod_rows = 0
    
    with open(mod_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        mod_rows_data = list(reader)
        mod_rows = len(mod_rows_data) + 1 # header
        
        for row in mod_rows_data:
            # Check text column only
            text_col = 'text' if 'text' in row else 'sentence_text'
            content = row.get(text_col, '')
            for c in content:
                if unicodedata.category(c) == 'Mn':
                    mn_count += 1
                
    return orig_rows == mod_rows, orig_rows, mod_rows, mn_count

def generate_report(title, file_map, log_file):
    print(f"Generating report for {title}...")
    
    stats, examples, total_replacements = analyze_logs(log_file)
    
    # Validation
    valid_extract, extract_orig_len, extract_mod_len, extract_mn = validate_csv(file_map['orig'], file_map['mod'])
    valid_sent, sent_orig_len, sent_mod_len, sent_mn = validate_csv(file_map['sent_orig'], file_map['sent_mod'])
    
    status_icon = "✅" if (valid_extract and valid_sent and extract_mn == 0 and sent_mn == 0) else "❌"
    
    md = f"""# Phase D Modernization Summary: {title}

**Status**: {status_icon} Validation {'Passed' if status_icon == '✅' else 'Failed'}

## 1. Statistics
- **Total Replacements Applied**: {total_replacements}
- **Top 30 Mappings**:
"""
    
    for k, v in stats.most_common(30):
        md += f"  - `{k}`: {v}\n"
        
    md += f"""
## 2. Validation Metrics
| Metric | Extraction CSV | Sentence CSV |
| :--- | :--- | :--- |
| **Row Count Preservation** | {extract_orig_len} -> {extract_mod_len} ({'PASS' if valid_extract else 'FAIL'}) | {sent_orig_len} -> {sent_mod_len} ({'PASS' if valid_sent else 'FAIL'}) |
| **Unicode Cleanliness (Mn=0)** | {extract_mn} | {sent_mn} |

## 3. Sample Replacements
"""
    for i, ex in enumerate(examples):
        md += f"**{i+1}.** `{ex['source_form']}` -> `{ex['target_form']}`\n"
        md += f"> ...{ex['context_snippet']}...\n\n"
        
    with open(file_map['summary'], 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"Wrote {file_map['summary']}")

def main():
    for title, file_map in FILES.items():
        log_file = LOG_FILES[title]
        generate_report(title, file_map, log_file)

if __name__ == '__main__':
    main()
