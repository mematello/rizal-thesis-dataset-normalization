
import csv
import re
import os

# Input/Output Files
INPUT_FILES = {
    'elfili': 'elfili_chapter_sentences_titles_fixed.csv',
    'noli': 'noli_chapter_sentences_titles_fixed.csv'
}
OUTPUT_FILES = {
    'elfili': 'elfili_chapter_sentences_titles_fixed_v2.csv',
    'noli': 'noli_chapter_sentences_titles_fixed_v2.csv'
}
LOG_FILES = {
    'elfili': 'phase_t2_title_log_elfili.csv',
    'noli': 'phase_t2_title_log_noli.csv'
}
MAPPING_FILE = 'phase_t_title_mapping_v2.csv'
SUMMARY_FILES = {
    'elfili': 'phase_t2_title_summary_elfili.md',
    'noli': 'phase_t2_title_summary_noli.md'
}

# Explicit Mappings (UPPERCASE Source -> Target)
# These override everything.
EXPLICIT_MAPPINGS = {
    'HEREJE': 'EREHE',
    'FILIBUSTERO': 'PILIBUSTERO',
    'CAPITANG': 'KAPITANG',
    'TIAGO': 'TIAGO', # Keep
    'AZOTEA': 'ASOTEA',
    'MANGA': 'MGA',
    'CAUGALIAN': 'KAUGALIAN',
    'MACAPANGYARIHAN': 'MAKAPANGYARIHAN',
    'SANTO': 'SANTO', # Keep
    'SACRISTAN': 'SAKRISTAN',
    'CALOLOWANG': 'KALULUWANG',
    'ESCUELA': 'ESKWELA',
    'CASAYSAYAN': 'KASAYSAYAN',
    'VISPERA': 'BISPERA',
    'FIESTA': 'PIYESTA',
    'CABRIA': 'KABRYA',
    'LAYANG-CAISIPAN': 'LAYANG-KAISIPAN', # Hyphenated handling
    'CAISIPAN': 'KAISIPAN', # Fallback if split
    'PAGCAIN': 'PAGKAIN',
    'SALISALITAAN': 'SALISALITAAN', # Keep
    'GOBERNADOR': 'GOBERNADOR', # Keep
    'GENERAL': 'HENERAL',
    'PROCESION': 'PROSESYON',
    'CONSOLACION': 'CONSOLACION', # Name
    'CATUWIRA\'T': 'KATUWIRA\'T',
    'LACAS': 'LAKAS',
    'PANUCALA': 'PANUKALA',
    'CONCIENCIA': 'KONSENSYA',
    'GUINOONG': 'GINOONG',
    'MAGCURO': 'MAGKURO',
    'PASCO': 'PASKO',
    'PANGANANGANAC': 'PANGANANGANAK',
    'PANGWACAS': 'PANGWAKAS',
    'BAHAGUI': 'BAHAGI',
    'PERIYA': 'PERYA',
    'INSIK': 'INTSIK',
    'KOTSERO': 'KUTSERO',
    'TATAKUT': 'TATAKOT',
    'CAPAHAMACAN': 'KAPAHAMAKAN', # Noli 54. "ANG CAPAHAMACAN"
    'SINUMPA': 'SINUMPA',
    'KINAGUISNANG': 'KINAGISNANG',
    'PAGCACAPISAN': 'PAGKAKAPISAN'
}

# Strictly Preserved Titles (Full String Match)
PRESERVED_TITLES = [
    'CRISOSTOMO IBARRA',
    'MARIA CLARA',
    'IL BUON DI SI CONOSCE DA MATTINA.',
    '¡VAE VICTIS!',
    'DE ESPADAÑA', # Usually part of "ANG MAG-ASAWANG DE ESPADAÑA" - handled by word logic hopefully? 
    # "DE ESPADAÑA" is not a full title. "ANG MAG-ASAWANG DE ESPADAÑA." is.
    # So we need to handle "DE" and "ESPADAÑA" as words that shouldn't change.
    # They are not in mapping, so safe.
    'ELIAS',
    'SISA',
    'BASILIO',
    'TASIO',
    'SIMOUN',
    'PILATO',
    'LOS BAÑOS', # Need to ensure LOS doesn't change?
    'PLACIDO PENITENTE',
    'BEN-ZAYB',
    'NOCHE BUENA', # "ANG NOCHE BUENA NG..."
]

# Words to specifically IGNORE/Keep (Foreign/Names not in mapping)
IGNORE_WORDS = {
    'DE', 'ESPADAÑA', 'ELIAS', 'SISA', 'BASILIO', 'TASIO', 'SIMOUN', 'PILATO', 
    'LOS', 'BAÑOS', 'PLACIDO', 'PENITENTE', 'BEN-ZAYB', 'NOCHE', 'BUENA',
    'CRISOSTOMO', 'IBARRA', 'MARIA', 'CLARA', 'IL', 'BUON', 'DI', 'SI', 
    'CONOSCE', 'DA', 'MATTINA', 'VAE', 'VICTIS', 'LIV', 'III', 'IV'
}

def modernize_title(title):
    """
    Apply Phase T.2 modernization.
    Returns: (new_title, list_of_changes)
    """
    original = title.strip()
    
    # 1. Check Full Title Preservation
    # Remove puntuation for check? "¡VAE VICTIS!"
    # Exact match check
    if original in PRESERVED_TITLES:
        return original, []
    
    # Check if title contains preserved phrases?
    # e.g. "ANG NOCHE BUENA NG..." -> NOCHE BUENA preserved.
    # This is handled by default if "NOCHE" and "BUENA" are not in explicit mappings.
    # But just in case we map "BUENA" -> "MAGANDA"? No, we only map EXPLICIT_MAPPINGS.
    # So if it's not in EXPLICIT_MAPPINGS, it stays.
    
    # Tokenize (split by space, strip punct for lookup)
    # We need to preserve punctuation in output.
    
    words = original.split()
    new_words = []
    changes = []
    
    for i, w in enumerate(words):
        # Separation of punctuation
        # e.g. "TIAGO," -> "TIAGO" , ","
        # e.g. "CATUWIRA'T" -> "CATUWIRA'T" (Keep apostrophe inside for mapping?)
        
        # Regex to capture: (prefix_punct)(word)(suffix_punct)
        match = re.match(r'^([^\w\']*?)([\w\'-]+)([^\w\']*?)$', w)
        if match:
            prefix, core, suffix = match.groups()
            
            # Check mappings
            target = core
            
            # 1. Hyphenated words? e.g. "LAYANG-CAISIPAN"
            # If explicit mapping exists for full hyphenated word
            if core in EXPLICIT_MAPPINGS:
                target = EXPLICIT_MAPPINGS[core]
                if target != core:
                    changes.append(f"{core}->{target}")
            else:
                # 2. Check parts if hyphenated
                if '-' in core:
                    parts = core.split('-')
                    new_parts = []
                    sub_change = False
                    for p in parts:
                        if p in EXPLICIT_MAPPINGS:
                            new_parts.append(EXPLICIT_MAPPINGS[p])
                            sub_change = True
                        else:
                            new_parts.append(p)
                    if sub_change:
                        target = "-".join(new_parts)
                        changes.append(f"{core}->{target}")
                else:
                    # 3. Normal word
                     pass # Not in mapping -> Keep
            
            new_word = prefix + target + suffix
            new_words.append(new_word)
        else:
            # Fallback for weird tokens (e.g. just punct "...")
            new_words.append(w)
            
    final_title = " ".join(new_words)
    return final_title, changes

def process_files():
    all_mappings = set()
    
    for name, input_path in INPUT_FILES.items():
        output_path = OUTPUT_FILES[name]
        log_path = LOG_FILES[name]
        
        if not os.path.exists(input_path):
            print(f"Skipping {name}, input missing.")
            continue
            
        print(f"Processing {name}...")
        
        with open(input_path, 'r', encoding='utf-8') as f_in, \
             open(output_path, 'w', encoding='utf-8', newline='') as f_out, \
             open(log_path, 'w', encoding='utf-8', newline='') as f_log:
             
            reader = csv.DictReader(f_in)
            writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
            writer.writeheader()
            
            log_writer = csv.writer(f_log)
            log_writer.writerow(['chapter_number', 'original_title', 'modernized_title', 'changes'])
            
            # Track unique mapped for master list
            processed_titles = {} # title -> changes
            
            for row in reader:
                orig_title = row.get('chapter_title', '')
                chap = row.get('chapter_number', '')
                
                new_title, changes = modernize_title(orig_title)
                
                row['chapter_title'] = new_title
                writer.writerow(row)
                
                if changes:
                    # Only log unique changes per chapter? Or every row?
                    # Log if it's the first time we see this exact change for this title
                    title_key = f"{orig_title}"
                    if title_key not in processed_titles:
                        processed_titles[title_key] = changes
                        log_writer.writerow([chap, orig_title, new_title, "; ".join(changes)])
                        for c in changes:
                            all_mappings.add(c)
                            
        # Create Summary
        summary_path = SUMMARY_FILES[name]
        with open(summary_path, 'w', encoding='utf-8') as f_sum:
            f_sum.write(f"# Phase T.2 Summary: {name}\n\n")
            f_sum.write("## Changes\n")
            # Reload log to summarize? Or just use processed_titles
            if not processed_titles:
                 f_sum.write("No changes made.\n")
            else:
                 for title, ch in processed_titles.items():
                     f_sum.write(f"- **{title}** -> **{modernize_title(title)[0]}**\n")
                     f_sum.write(f"  - Changes: {', '.join(ch)}\n")

    # Generate Master Mapping File
    with open(MAPPING_FILE, 'w', encoding='utf-8', newline='') as f_map:
        writer = csv.writer(f_map)
        writer.writerow(['source', 'target'])
        for m in sorted(list(all_mappings)):
             src, tgt = m.split('->')
             writer.writerow([src, tgt])
             
    print("Done.")

if __name__ == '__main__':
    process_files()
