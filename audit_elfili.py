import pandas as pd
import re
from collections import Counter
import sys

# Configuration
INPUT_FILE = "/Users/marcusoliver/Desktop/rizal-thesis-dataset-normalization/elfili_chapter_sentences_FINAL_v2.csv"
CORPUS_PROFILE_FILE = "elfili_profile.txt"
ALL_TOKENS_FILE = "elfili_token_inventory.csv"
PROTECTED_TERMS_FILE = "protected_terms_elfili.txt"

# Regex patterns for tokenization (keeping archaic characters)
TOKEN_PATTERN = r"[a-zA-ZñÑáéíóúÁÉÍÓÚüÜ'’\-]+" 

def load_data(filepath):
    try:
        df = pd.read_csv(filepath)
        print(f"Loaded {len(df)} rows from {filepath}")
        return df
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        sys.exit(1)

def tokenize(text):
    if pd.isna(text):
        return []
    return re.findall(TOKEN_PATTERN, str(text))

def profile_corpus(df):
    sentences = df['sentence_text'].dropna().tolist()
    total_sentences = len(sentences)
    
    all_tokens = []
    for s in sentences:
        all_tokens.extend(tokenize(s))
        
    total_tokens = len(all_tokens)
    unique_tokens = len(set(all_tokens))
    
    # Case distribution
    case_dist = Counter()
    for t in all_tokens:
        if t.isupper():
            case_dist['UPPER'] += 1
        elif t.istitle():
            case_dist['Title'] += 1
        elif t.islower():
            case_dist['lower'] += 1
        else:
            case_dist['Mixed'] += 1
            
    # Char inventory
    text_blob = "".join(sentences)
    char_counts = Counter(text_blob)
    
    profile_text = f"""EL FILI CORPUS PROFILE
================
Total Sentences: {total_sentences}
Total Tokens: {total_tokens}
Unique Tokens: {unique_tokens}

Case Distribution:
{case_dist}

Character Inventory (Top 50):
{char_counts.most_common(50)}
"""
    with open(CORPUS_PROFILE_FILE, 'w') as f:
        f.write(profile_text)
    print(f"Generated {CORPUS_PROFILE_FILE}")
    
    return all_tokens

def generate_token_inventory(all_tokens, df):
    # Count frequencies
    counter = Counter(all_tokens)
    
    # Analyze capitalization and context
    token_data = {}
    
    print("Analyzing token contexts...")
    
    for token, freq in counter.items():
        token_data[token] = {
            'token': token,
            'frequency': freq,
            'capitalized_count': 0,
            'lowercase_count': 0,
            'sample_contexts': []
        }

    # Reset counts to be populated by loop
    for t in token_data:
        token_data[t]['capitalized_count'] = 0
        token_data[t]['lowercase_count'] = 0
    
    for idx, row in df.iterrows():
        sent = str(row['sentence_text'])
        tokens = tokenize(sent)
        for t in tokens:
            if t in token_data:
                if t[0].isupper():
                    token_data[t]['capitalized_count'] += 1
                else:
                    token_data[t]['lowercase_count'] += 1
                
                # Grab context if we have fewer than 3
                if len(token_data[t]['sample_contexts']) < 3:
                    token_data[t]['sample_contexts'].append(str(row.get('sentence_number', idx)) + ": " + sent)

    # Convert to DataFrame
    inv_df = pd.DataFrame(token_data.values())
    inv_df.to_csv(ALL_TOKENS_FILE, index=False)
    print(f"Generated {ALL_TOKENS_FILE}")
    return inv_df

def generate_protected_list(inv_df):
    protected = set()
    
    # 1. Capitalization Heuristic: >80% capitalized
    for _, row in inv_df.iterrows():
        total = row['frequency']
        if total < 2: continue
        
        cap_rate = row['capitalized_count'] / total
        if cap_rate > 0.8:
            protected.add(row['token'])
            
    # 2. Known Character Names & Titles (El Fili additions)
    known_proper = [
        "Simoun", "Basilio", "Isagani", "Juli", "Juliana", "Tales", "Cabesang", "Tandang", "Selo",
        "Padre", "Florentino", "Sibyla", "Irene", "Camorra", "Salvi", "Fernandez", "Millon",
        "Custodio", "Ben-Zayb", "Quiroga", "Placido", "Penitente", "Paulita", "Gomez",
        "Victorina", "Tiburcio", "Espadaña", "Doña", "Don", "Capitan", "General",
        "Manila", "Pasig", "Laguna", "San", "Diego", "Tiani", "Los", "Baños",
        "Filipinas", "España", "Amerika", "Carolinas", "Hongkong",
        "Indio", "Chino", "Kastila", "Mestiso", "Fraile", "Klerigo",
        "Maria", "Clara", "Ibarra", "Elias"
    ]
    protected.update(known_proper)
    
    # 3. Spanish Loanwords
    common_spanish = [
        "casa", "calle", "convento", "cura", "cruz", "Cristo", 
        "que", "quien", "cual", "cuando", "porque", "pequeño", "aqui",
        "pero", "para", "por", "cuarto", "cuanto", "con", "contra", 
        "desde", "entre", "hasta", "hacia", "para", "por", "segun", "sin", "sobre", "tras",
        "el", "la", "los", "las", "un", "una", "unos", "unas",
        "y", "o", "u", "e", "ni"
    ]
    protected.update(common_spanish)

    with open(PROTECTED_TERMS_FILE, 'w') as f:
        for term in sorted(protected):
            f.write(term + "\n")
            
    print(f"Generated {PROTECTED_TERMS_FILE} with {len(protected)} terms")

if __name__ == "__main__":
    df = load_data(INPUT_FILE)
    all_tokens = profile_corpus(df)
    inv_df = generate_token_inventory(all_tokens, df)
    generate_protected_list(inv_df)
