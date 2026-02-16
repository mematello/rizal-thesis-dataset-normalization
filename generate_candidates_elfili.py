import pandas as pd
import re
import sys

# Configuration
INVENTORY_FILE = "elfili_token_inventory.csv"
PROTECTED_TERMS_FILE = "protected_terms_elfili.txt"
CANDIDATES_FILE = "elfili_candidates.csv"

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
    if re.search(r'\bc[aou]', token, re.IGNORECASE) or re.search(r'[a-z]c[aou]', token, re.IGNORECASE):
        suggestion = re.sub(r'c([aou])', r'k\1', token, flags=re.IGNORECASE)
        # handle case where C was capital
        if token[0].isupper():
            suggestion = suggestion.capitalize() # simple heuristic
            if token.isupper(): suggestion = suggestion.upper()
        
        if suggestion != token:
            return "C_TO_K", suggestion

    # 2. QU -> K
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
    
    # 6. GUI -> GI (New for El Fili base on user request)
    # "guinawa" -> "ginawa"
    if "gui" in token.lower():
         suggestion = re.sub(r'gui([aeou])', r'gi\1', token, flags=re.IGNORECASE) # guinawa -> ginawa
         # wait, gui + consonant? or gui + n/l/etc?
         # tagalog: 'gui' -> 'gi' before consonants usually?
         # "guinoo" -> "ginoo"
         # "gui" followed by anything?
         # Actually standard is: gui -> gi before consonants. 
         # But "guing" -> "ging"?
         # Let's try simple replacement for now and let user review.
         suggestion = re.sub(r'gui', 'gi', token, flags=re.IGNORECASE)
         if suggestion != token:
             return "GUI_TO_GI", suggestion

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
                if row['capitalized_count'] == 0:
                    confidence = "HIGH" 
                if freq > 5:
                    auto_action = "SAFE"
            elif pattern == "QU_TO_K":
                if row['capitalized_count'] == 0:
                     confidence = "HIGH"
                     if freq > 5:
                         auto_action = "SAFE"
            elif pattern == "GUI_TO_GI":
                if row['capitalized_count'] == 0:
                    confidence = "HIGH"
            
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

if __name__ == "__main__":
    main()
