import pandas as pd
import re
import sys

# Configuration
INVENTORY_FILE = "all_tokens_inventory.csv"
PROTECTED_TERMS_FILE = "protected_terms.txt"
CANDIDATES_FILE = "residual_candidates.csv"
REVIEW_FILE = "human_review_list.txt"

def load_protected():
    try:
        with open(PROTECTED_TERMS_FILE, 'r') as f:
            protected = set(line.strip() for line in f)
        print(f"Loaded {len(protected)} protected terms.")
        return protected
    except FileNotFoundError:
        print("Protected terms file not found.")
        return set()

def load_inventory():
    return pd.read_csv(INVENTORY_FILE)

def apply_patterns(token):
    # Returns (pattern_name, suggestion) or (None, None)
    
    # 1. C -> K (Hard C)
    # Regex: starts with c followed by a,o,u OR contains c inside followed by a,o,u
    # But wait, original Tagalog uses 'c' for 'k' sound before a,o,u. 
    # 'qu' for 'k' sound before e,i.
    
    if re.search(r'\bc[aou]', token, re.IGNORECASE) or re.search(r'[a-z]c[aou]', token, re.IGNORECASE):
        # specific replacement logic for c -> k
        # replace all hard c's
        suggestion = re.sub(r'c([aou])', r'k\1', token, flags=re.IGNORECASE)
        # handle case where C was capital
        if token[0].isupper():
            suggestion = suggestion.capitalize() # simple heuristic
            if token.isupper(): suggestion = suggestion.upper()
        
        if suggestion != token:
            return "C_TO_K", suggestion

    # 2. QU -> K
    # before e, i
    if "qu" in token.lower():
        suggestion = re.sub(r'qu([ei])', r'k\1', token, flags=re.IGNORECASE)
        # also qui -> ki, que -> ke
        if suggestion != token:
            return "QU_TO_K", suggestion

    # 3. NG Tilde
    if "ñg" in token:
        suggestion = token.replace("ñg", "ng")
        return "NG_TILDE", suggestion
    if "n͠g" in token:
        suggestion = token.replace("n͠g", "ng")
        return "NG_TILDE", suggestion

    # 4. U -> O
    # Skip common valid words with 'uo'
    common_uo = {'buong', 'suot', 'tuod', 'puon', 'uod', 'buo', 'tuos'}
    if "uo" in token.lower() and token.lower() not in common_uo:
        suggestion = re.sub(r'uo', 'o', token, flags=re.IGNORECASE)
        # Check if length change implies we just deleted a char.
        if suggestion != token:
             return "UO_TO_O", suggestion

    # 5. Prefix pag-ca-
    if token.lower().startswith("pag-ca-"):
        suggestion = re.sub(r'^pag-ca-', 'pagka-', token, flags=re.IGNORECASE)
        return "PREFIX_PAGKA", suggestion
    if "pagca" in token.lower() and "pagkai" not in token.lower(): # simple check
        suggestion = re.sub(r'pagca', 'pagka', token, flags=re.IGNORECASE)
        return "PREFIX_PAGKA", suggestion

    # 6. Hyphenation regular
    # ma-ganda -> maganda (remove hyphen)
    # nag-aral -> nag-aral (keep hyphen)
    # Rule: Keep hyphen if prefix ends in consonant and root starts in vowel? 
    # Or simplified: archaic is usually CV-CV (ma-ganda, pa-laca). Modern is maganda.
    # Modern keeps hyphen for nag-aral, mag-alis, pag-ibig.
    if "-" in token and len(token) > 3:
        # Check for specific archaic prefixes with hyphen
        # ma-, pa-, na-, ca- followed by consonant
        if re.match(r'^(ma|pa|na|ca|ga)-[bcdfghjklmnpqrstvwxyz]', token, re.IGNORECASE):
             suggestion = token.replace("-", "")
             return "HYPHEN_REMOVAL", suggestion
        
        # what about pag-ca-? Handled above.
        # what about in-a-...?
        # If straightforward removal works?
        # Let's be conservative. Only replace if specifically matching the archaic style.


    return None, None

def classify_candidates(df, protected):
    candidates = []
    
    for _, row in df.iterrows():
        token = str(row['token'])
        
        # Skip if protected
        if token in protected:
            continue
            
        # Skip if very short or just symbols
        if len(token) < 2:
            continue
            
        pattern, suggestion = apply_patterns(token)
        
        if pattern and suggestion:
            freq = row['frequency']
            sample_contexts = row['sample_contexts']
            
            # Confidence Logic
            confidence = "MEDIUM"
            auto_action = "REVIEW"
            
            # Heuristics for Confidence
            if pattern == "NG_TILDE":
                confidence = "HIGH"
                auto_action = "SAFE"
            elif pattern == "PREFIX_PAGKA":
                confidence = "HIGH"
                auto_action = "SAFE"
            elif pattern == "C_TO_K":
                # High if frequent and not capitalized often?
                if row['capitalized_count'] == 0:
                    confidence = "HIGH" 
                # If freq is high, might be a common word
                if freq > 5:
                    auto_action = "SAFE"
            elif pattern == "QU_TO_K":
                if row['capitalized_count'] == 0:
                     confidence = "HIGH"
                     if freq > 5:
                         auto_action = "SAFE"
            
            # Check if suggestion is in protected list (e.g. valid word)
            # Actually we want to know if suggestion is a VALID modern word. 
            # We don't have a modern dictionary loaded easily.
            # But if suggestion is already in our corpus with higher frequency?
            # That would be a strong signal.
            
            candidates.append({
                'token': token,
                'frequency': freq,
                'capitalized_count': row['capitalized_count'],
                'pattern_match': pattern,
                'modern_suggestion': suggestion,
                'confidence': confidence,
                'auto_action': auto_action,
                'sample_contexts': sample_contexts
            })
            
    return pd.DataFrame(candidates)

def main():
    print("Loading resources...")
    protected = load_protected()
    df_inv = load_inventory()
    
    print("Classifying candidates...")
    candidates_df = classify_candidates(df_inv, protected)
    
    # Sort by frequency desc
    candidates_df = candidates_df.sort_values('frequency', ascending=False)
    
    print(f"Found {len(candidates_df)} candidates.")
    candidates_df.to_csv(CANDIDATES_FILE, index=False)
    print(f"Saved to {CANDIDATES_FILE}")
    
    # Generate Review List (Top 50 Review items)
    review_df = candidates_df[candidates_df['auto_action'] == 'REVIEW'].head(50)
    
    with open(REVIEW_FILE, 'w') as f:
        f.write("HUMAN REVIEW LIST (Top 50)\n")
        f.write("==========================\n\n")
        
        for _, row in review_df.iterrows():
            f.write(f"TOKEN: {row['token']}  ->  SUGGESTION: {row['modern_suggestion']}\n")
            f.write(f"Pattern: {row['pattern_match']}, Freq: {row['frequency']}, Conf: {row['confidence']}\n")
            f.write("Contexts:\n")
            # Parse context string representation if needed or just print
            # It's stored as string representation of list in CSV usually, but here likely list object if not reloaded
            # But we are in same script so it is a list
            # wait, inventory loaded from CSV, so sample_contexts is a string like "['1: ...', ...]"
            # We need to eval it or print as is.
            f.write(f"  {row['sample_contexts']}\n")
            f.write("-" * 40 + "\n")
            
    print(f"Generated {REVIEW_FILE}")

if __name__ == "__main__":
    main()
