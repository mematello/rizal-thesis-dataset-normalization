import re
import unicodedata
import sys
import os
from bs4 import BeautifulSoup
from collections import Counter

# Try importing transformers for validation
try:
    from transformers import XLMRobertaTokenizerFast
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers library not found. Tokenization metrics will be skipped.")

# --- Configuration ---
INPUT_FILE = "Ang _Filibusterismo_, by José Rizal_ A Project Gutenberg eBook.html"
OUTPUT_RAW = "elfili_extracted_raw.txt"
OUTPUT_NORMALIZED = "elfili_normalized_ortho.txt"
LOG_FILE = "normalization_log.txt"

class TagalogNormalizer:
    def __init__(self):
        self.log_diacritics_removed = Counter()
        self.log_gtilde_fixed = 0
        self.log_ng_variants_fixed = 0
        self.log_enye_protected = 0

    def normalize_unicode(self, text):
        """Phase A: Unicode Canonicalization (NFC)."""
        return unicodedata.normalize('NFC', text)

    def fix_archaic_g_tilde(self, text):
        """Phase B: Resolve Archaic G-Tilde and ng variants."""
        # Rule 1: Replace g + combining tilde (\u0303) with g
        # We start by counting occurrences for logging
        matches = len(re.findall(r'g\u0303', text, flags=re.IGNORECASE))
        self.log_gtilde_fixed += matches
        
        # Perform replacement
        text = re.sub(r'g\u0303', 'g', text, flags=re.IGNORECASE)

        # Rule 2: Standalone particle variants (ñg, ñg) -> ng
        # Standalone means surrounded by word boundaries.
        # Check for ñg (precomposed ñ) or n + combining tilde + g
        
        # Regex for 'ñg' or 'n\u0303g' as a whole word
        # Note: We must be careful not to match substrings of names.
        
        def replace_ng_variant(match):
            self.log_ng_variants_fixed += 1
            return "ng"
            
        # Matches "ñg" or "n\u0303g" case-insensitively, strictly bounded
        # \b matches word boundary.
        text = re.sub(r'\b(?:ñ|n\u0303)g\b', replace_ng_variant, text, flags=re.IGNORECASE)
        
        return text

    def strip_diacritics_safe(self, text):
        """Phase C: Diacritic Removal with ñ Preservation."""
        
        # Step 1: Protect ñ (U+00F1) and n + tilde (U+006E + U+0303)
        # We use a unique placeholder that won't appear in 19th century text.
        placeholder = "__TEMP_ENYE__"
        placeholder_cap = "__TEMP_ENYE_CAP__"
        
        # Count for logging
        self.log_enye_protected += len(re.findall(r'ñ|n\u0303', text, flags=re.IGNORECASE))
        
        text = text.replace('ñ', placeholder)
        text = text.replace('Ñ', placeholder_cap)
        # Also handle decomposed input if any remained (though we did NFC earlier)
        text = text.replace('n\u0303', placeholder)
        text = text.replace('N\u0303', placeholder_cap)

        # Step 2: Decompose to NFD
        text = unicodedata.normalize('NFD', text)

        # Step 3: Strip non-spacing marks (Mn)
        # We'll also track what we remove for logging purposes
        chars = []
        for c in text:
            if unicodedata.category(c) == 'Mn':
                self.log_diacritics_removed[convert_mark_to_readable(c)] += 1
                continue
            chars.append(c)
        text = "".join(chars)

        # Step 4: Recompose to NFC
        text = unicodedata.normalize('NFC', text)

        # Step 5: Restore ñ
        text = text.replace(placeholder, 'ñ')
        text = text.replace(placeholder_cap, 'Ñ')
        
        return text

    def normalize(self, text):
        # Pipeline execution
        text = self.normalize_unicode(text)
        text = self.fix_archaic_g_tilde(text)
        text = self.strip_diacritics_safe(text)
        # Basic whitespace cleanup
        text = ' '.join(text.split())
        return text

def convert_mark_to_readable(char):
    """Helper to log the name of the removed diacritic."""
    try:
        return unicodedata.name(char)
    except:
        return f"U+{ord(char):04X}"

def extract_text_from_html(filename):
    """Extracts narrative text from the specific Gutenberg HTML format."""
    print(f"Reading {filename}...")
    with open(filename, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    text_div = soup.find('div', id='text')
    if not text_div:
        return []

    lines = []
    
    # Iterate over chapter divs and dedication
    for child in text_div.children:
        if child.name != 'div': continue
        
        div_id = child.get('id', '')
        div_class = child.get('class', [])
        
        # Valid content blocks: chapter, dedication
        if not ('chapter' in div_class or div_id == 'dedication'):
            continue
            
        # Extract paragraphs
        for p in child.find_all('p'):
            # Skip footnotes
            is_footnote = False
            curr = p
            while curr and curr != child:
                if 'footnote' in curr.get('class', []):
                    is_footnote = True
                    break
                curr = curr.parent
            if is_footnote: continue
            
            # Remove page numbers
            for pn in p.find_all('a', class_='pagenum'):
                pn.decompose()
                
            raw_text = p.get_text().strip()
            # Basic cleanup of multiline strings inside p
            raw_text = re.sub(r'\s+', ' ', raw_text)
            
            if raw_text and not set(raw_text) <= {'*', ' '}:
                lines.append(raw_text)
                
    return lines

def analyze_tokenization(lines, label):
    """Computes basic XLM-R tokenization stats."""
    if not TRANSFORMERS_AVAILABLE:
        return {}
    
    print(f"Running XLM-R tokenization analysis on {label}...")
    tokenizer = XLMRobertaTokenizerFast.from_pretrained("xlm-roberta-base")
    
    total_tokens = 0
    unk_count = 0
    
    # Process in batches to show progress/avoid memory spike if huge (unlikely here)
    batch_text = lines 
    # Use tokenizer on list of strings
    # This might use a lot of memory for very large datasets, but for one book it's fine.
    encodings = tokenizer(batch_text, add_special_tokens=False)
    
    for ids in encodings.input_ids:
        total_tokens += len(ids)
        unk_count += ids.count(tokenizer.unk_token_id)
        
    avg_per_line = total_tokens / len(lines) if lines else 0
    
    return {
        "total_tokens": total_tokens,
        "avg_tokens_per_line": avg_per_line,
        "unk_count": unk_count
    }

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Box not found: {INPUT_FILE}")
        return

    # 1. Extract
    raw_lines = extract_text_from_html(INPUT_FILE)
    print(f"Extracted {len(raw_lines)} paragraphs.")
    
    # Save Raw
    with open(OUTPUT_RAW, 'w', encoding='utf-8') as f:
        f.write('\n'.join(raw_lines))
    print(f"Saved raw text to {OUTPUT_RAW}")

    # 2. Normalize
    normalizer = TagalogNormalizer()
    normalized_lines = []
    
    print("Normalizing...")
    for line in raw_lines:
        normalized_lines.append(normalizer.normalize(line))
        
    # Save Normalized
    with open(OUTPUT_NORMALIZED, 'w', encoding='utf-8') as f:
        f.write('\n'.join(normalized_lines))
    print(f"Saved normalized text to {OUTPUT_NORMALIZED}")

    # 3. Log Generation
    print("Generating logs...")
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("Normalization Statistics\n")
        f.write("========================\n\n")
        f.write(f"G-Tilde Fixes (ng~ -> ng): {normalizer.log_gtilde_fixed}\n")
        f.write(f"Particle Variants (ñg -> ng): {normalizer.log_ng_variants_fixed}\n")
        f.write(f"Protected 'ñ' instances: {normalizer.log_enye_protected}\n")
        f.write("\nDiacritics Removed:\n")
        for char_name, count in normalizer.log_diacritics_removed.most_common():
            f.write(f"  {char_name}: {count}\n")
            
        # 4. Validation / Metrics
        if TRANSFORMERS_AVAILABLE:
            f.write("\n\nXLM-RoBERTa Compatibility Analysis\n")
            f.write("==================================\n")
            
            # Analyze Raw
            raw_stats = analyze_tokenization(raw_lines, "Raw Text")
            norm_stats = analyze_tokenization(normalized_lines, "Normalized Text")
            
            f.write(f"\nMetric                  | Raw Text      | Normalized    | Change\n")
            f.write(f"------------------------|---------------|---------------|--------\n")
            
            diff_tokens = norm_stats['total_tokens'] - raw_stats['total_tokens']
            pct_change = (diff_tokens / raw_stats['total_tokens']) * 100 if raw_stats['total_tokens'] else 0
            
            f.write(f"Total Tokens            | {raw_stats['total_tokens']:<13} | {norm_stats['total_tokens']:<13} | {pct_change:.2f}%\n")
            f.write(f"Avg Tokens/Para         | {raw_stats['avg_tokens_per_line']:<13.2f} | {norm_stats['avg_tokens_per_line']:<13.2f} | \n")
            f.write(f"Unknown Tokens (<unk>)  | {raw_stats['unk_count']:<13} | {norm_stats['unk_count']:<13} | \n")
            
    print(f"Logs written to {LOG_FILE}")
    print("Done.")

if __name__ == "__main__":
    main()
