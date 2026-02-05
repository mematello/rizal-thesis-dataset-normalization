
import csv
import re
import os

# Input/Output Config
INPUTS = {
    'noli': 'noli_chapter_sentences_titles_fixed_v3.csv',
    'elfili': 'elfili_chapter_sentences_titles_fixed_v2.csv'
}
OUTPUTS = {
    'noli': 'noli_chapter_sentences_FINAL.csv',
    'elfili': 'elfili_chapter_sentences_FINAL.csv'
}
LOGS = {
    'noli': 'phase_d4_log_noli.csv',
    'elfili': 'phase_d4_log_elfili.csv'
}
SUMMARY_FILE = 'phase_d4_summary.md'

# SAFE LIST PROPER MAPPINGS (Case Insensitive)
# Source -> Target
SAFE_MAPPINGS = {
    'canyang': 'kanyang',
    'bulaclac': 'bulaklak',
    'buhoc': 'buhok',
    'lacas': 'lakas',
}

# Filipino Markers that validate "Capitan" -> "Kapitan"
# Preceding tokens
FILIPINO_MARKERS_PRE = {'si', 'ni', 'kay', 'ang', 'ng', 'mga', 'sa'}

# Spanish Markers that FORBID inversion (Preceding)
SPANISH_MARKERS_PRE = {'el', 'del', 'al', 'un'}

def tokenize(text):
    """
    Split text into tokens while preserving separators for reconstruction.
    Returns list of (token, separator) tuples.
    Wait, better to just tokenize words and reconstruction might be tricky if we don't save offsets.
    Let's use re.split capturing delimiters.
    """
    # Split by non-alphanumeric chars (keep them)
    # But wait, apostrophes? "Catowira't".
    # Regex: (\w+) or (\W+)
    parts = re.split(r'([^\w\']+)', text)
    # parts will be [word, sep, word, sep, ...]
    return parts

def process_sentence(text, sent_id, log_entries):
    parts = tokenize(text)
    new_parts = []
    
    # We need context (previous token)
    # Filter parts to get only "word" tokens for analysis?
    # No, we assume even indices are words (0, 2, 4...) if starting with word?
    # parts[0] could be empty if text starts with punct.
    
    for i in range(len(parts)):
        token = parts[i]
        
        # Skip separators (odd indices usually, or just check content)
        # Actually split r'([^\w\']+)' captures separators.
        # If text = "Hello, world!" -> ['Hello', ', ', 'world', '!', '']
        
        # Simple check: is this a word?
        if not re.search(r'[\w]', token):
            new_parts.append(token)
            continue
            
        original = token
        lower = token.lower()
        replacement = None
        reason = ""
        
        # 1. Safe List Check
        if lower in SAFE_MAPPINGS:
            target_lower = SAFE_MAPPINGS[lower]
            # Restore case
            if token.isupper():
                replacement = target_lower.upper()
            elif token[0].isupper():
                replacement = target_lower.capitalize()
            else:
                replacement = target_lower
            reason = f"Safe List: {lower}"

        # 2. Capitan Policy
        elif lower in ['capitan', 'capitang']:
            # Context Check
            # Look at previous *word* token
            prev_word = None
            # Scan backwards from i-1
            for j in range(i-1, -1, -1):
                if re.search(r'[\w]', parts[j]):
                    prev_word = parts[j]
                    break
            
            # Next word (for specific check if needed, e.g. Name? "Capitan Tiago")
            # User said: "or followed by a personal name (e.g., Capitan Tiago)"
            # But checking if next word is a name is hard without NER.
            # Rely on Preceding Filipino Markers.
            
            is_filipino_context = False
            is_spanish_context = False
            
            if prev_word:
                prev_lower = prev_word.lower()
                if prev_lower in FILIPINO_MARKERS_PRE:
                    is_filipino_context = True
                if prev_lower in SPANISH_MARKERS_PRE:
                    is_spanish_context = True
            
            # Also check if it's "Capitan Tiago" -> "Kapitan Tiago" (Tiago is a name)
            # Or "Capitan Tinong".
            # If prev_word is NOT Spanish and NOT Filipino? e.g. Start of sentence?
            # "Capitan Tiago..."
            # If start of sentence, assume Filipino default if not "El Capitan"?
            # User: "followed by a personal name (e.g., Capitan Tiago)"
            # Let's check next word.
            next_word = None
            for j in range(i+1, len(parts)):
                if re.search(r'[\w]', parts[j]):
                    next_word = parts[j]
                    break
            
            if next_word and next_word[0].isupper():
                # Potential name following
                # "Capitan General"? "General" is upper.
                # "El Capitan General" -> Spanish.
                # "Ang Kapitan Heneral" -> Filipino.
                # If "Capitan General" appears alone?
                # "Si Capitan General..." -> Filipino.
                # If prev is none (start), and next is Upper -> Likely Filipino Title usage unless "General" follows?
                pass

            # DECISION LOGIC
            should_replace = False
            
            if is_spanish_context:
                should_replace = False # Forbidden
            elif is_filipino_context:
                should_replace = True
            else:
                # Ambiguous or Start of Sentence.
                # If followed by Name (Upper case word)?
                if next_word and next_word[0].isupper():
                    # Check if next word is "General" (Special case: Capitan General could be Spanish title used in Tagalog context, usually rendered Kapitan Heneral?)
                    # But we are not changing "General" to "Heneral" here (Phase D.4 doesn't replace General).
                    # If text is "Capitan General", and we replace Capitan -> Kapitan, we get "Kapitan General".
                    # Is that acceptable?
                    # User: "Do NOT modify ... Spanish loanwords".
                    # But "Capitan" -> "Kapitan" allowed.
                    # If "Capitan General" is the token sequence.
                    # Let's assume replacement is preferred if not explicitly Spanish "El/Del".
                    should_replace = True
                elif prev_word is None: 
                     # Start of sentence. "Capitan..."
                     # Assume Filipino context for this corpus (Tagalog novels).
                     should_replace = True
            
            if should_replace:
                if lower == 'capitan':
                    replacement = 'Kapitan' if token[0].isupper() else 'kapitan' # rare lowercase?
                    if token.isupper(): replacement = 'KAPITAN'
                elif lower == 'capitang':
                     replacement = 'Kapitang' if token[0].isupper() else 'kapitang'
                     if token.isupper(): replacement = 'KAPITANG'
                reason = "Capitan Policy"

        if replacement and replacement != original:
            new_parts.append(replacement)
            log_entries.append({
                'sent_id': sent_id,
                'orig': original,
                'new': replacement,
                'reason': reason,
                'context': text[:50] + "..." # snippet
            })
        else:
            new_parts.append(original)
            
    return "".join(new_parts)

def process_dataset(name, input_file, output_file, log_file):
    print(f"Processing {name}...")
    if not os.path.exists(input_file):
        print(f"Skipping {name} (Missing input)")
        return
        
    log_entries = []
    processed_rows = 0
    
    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8', newline='') as f_out, \
         open(log_file, 'w', encoding='utf-8', newline='') as f_log:
         
         reader = csv.DictReader(f_in)
         writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
         writer.writeheader()
         
         log_writer = csv.writer(f_log)
         log_writer.writerow(['sentence_id', 'original_token', 'new_token', 'reason', 'context_snippet'])
         
         for row in reader:
             sent_id = f"{row.get('chapter_number')}-{row.get('sentence_number')}"
             text = row.get('sentence_text', '')
             
             # Process
             # Special handling: Don't touch titles. Just text.
             new_text = process_sentence(text, sent_id, log_entries)
             
             row['sentence_text'] = new_text
             writer.writerow(row)
             processed_rows += 1
             
         # Write log buffer
         for entry in log_entries:
             log_writer.writerow([
                 entry['sent_id'],
                 entry['orig'],
                 entry['new'],
                 entry['reason'],
                 entry['context']
             ])
             
    print(f"Finished {name}. Rows: {processed_rows}. Changes: {len(log_entries)}")
    return len(log_entries)

def main():
    total_changes = 0
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f_sum:
        f_sum.write("# Phase D.4 Modernization Summary\n\n")
        
        for name in INPUTS:
            changes = process_dataset(name, INPUTS[name], OUTPUTS[name], LOGS[name])
            f_sum.write(f"- **{name}**: {changes} replacements.\n")
            total_changes += changes
            
        f_sum.write(f"\n**Total Replacements**: {total_changes}")

if __name__ == "__main__":
    main()
