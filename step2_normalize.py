import csv
import re
import unicodedata

INPUT_CSV = 'noli_step1_sentences.csv'
OUTPUT_CSV = 'noli_chapter_sentences_new.csv'

# Predefined explicit Tagalog archaic maps (must match exactly)
EXPLICIT_C_MAP = {
    'canya': 'kanya', 'canyang': 'kanyang', 'caniyang': 'kaniyang', 'caniya': 'kaniya',
    'co': 'ko', 'aco': 'ako', 'acong': 'akong', 'cong': 'kong',
    'ca': 'ka', 'cang': 'kang', 'cung': 'kung', 'cay': 'kay',
    'cayo': 'kayo', 'cayong': 'kayong',
    'canila': 'kanila', 'canilang': 'kanilang',
    'pagca': 'pagka', 'pagcatapos': 'pagkatapos',
    'cahulugan': 'kahulugan', 'cahoy': 'kahoy',
    'caibigan': 'kaibigan', 'caibigang': 'kaibigang', 'calagayan': 'kalagayan',
    'cailan': 'kailan', 'casama': 'kasama',
    'dacong': 'dakong', 'sacali': 'sakali',
    'anac': 'anak', 'camay': 'kamay', 'caya': 'kaya',
    'wica': 'wika', 'wicang': 'wikang',
    'catagalugan': 'katagalugan', 'calayaan': 'kalayaan',
    'catuwiran': 'katuwiran', 'catuwirang': 'katuwirang',
    'catotohanan': 'katotohanan', 'catoto': 'katoto',
    'canilag': 'kanilag',
    'kinacailangan': 'kinakailangan', 'casamaan': 'kasamaan',
    'cabulagan': 'kabulagan', 'capahamacan': 'kapahamakan', 
    'macapangyarihan': 'makapangyarihan', 'macaimic': 'makaimik',
    'nacapagpapalaman': 'nakapagpapalaman', 'nacamamatay': 'nakamamatay',
    'caugalian': 'kaugalian', 'calolowa': 'kaluluwa',
    'casaysayan': 'kasaysayan', 'capitang': 'kapitang',
    'carikitan': 'kariktan', 'cabria': 'kabria',
    'pagcain': 'pagkain', 'cakilakilabot': 'kakila-kilabot',
    'huag': 'huwag', 'wacas': 'wakas', 'bahagui': 'bahagi', 'lacas': 'lakas',
    'cami': 'kami', 'caming': 'kaming', 
    'capuwa': 'kapuwa', 'capwa': 'kapwa',
    'cun': 'kun', 'cundi': 'kundi', 'pacundangan': 'pakundangan',
    'cagalingan': 'kagalingan', 'cagaling': 'kagaling', 'casalanan': 'kasalanan',
    'catapusan': 'katapusan', 'cailangan': 'kailangan', 'cailang': 'kailang',
    'icaw': 'ikaw', 'curo': 'kuro', 'capitana': 'kapitana',
    'saca': 'saka', 'cahi': 'kahi', 'caaway': 'kaaway', 'catungculan': 'katungkulan',
    'catungculang': 'katungkulang',
    'nauucol': 'nauukol', 'ucol': 'ukol', 'cawacasa': 'wakas', # Note the map
    'acala': 'akala', 'acalang': 'akalang', 'inaacala': 'inaakala',
    'magcaroon': 'magkaroon', 'cawang': 'kawang', 'camahalan': 'kamahalan',
    'bulaclac': 'bulaklak', 'culang': 'kulang', 'culay': 'kulay', 'catulad': 'katulad',
    'catahimican': 'katahimikan', 'calooban': 'kalooban', 'capatid': 'kapatid',
    'cagalanggalang': 'kagalanggalang', 'carapatdapat': 'karapatdapat', 'tacot': 'takot',
    'paglacad': 'paglakad', 'lacad': 'lakad', 'pumasoc': 'pumasok', 'pumapasoc': 'pumapasok',
    'macaraan': 'makaraan', 'sucat': 'sukat', 'caunti': 'kaunti', 'caunting': 'kaunting',
    'catawan': 'katawan', 'cadahilanan': 'kadahilanan', 'sapagca': 'sapagka', 'cawayan': 'kawayan',
    'casayahan': 'kasayahan', 'canino': 'kanino', 'icagagaling': 'ikagagaling', 'casabay': 'kasabay',
    'caculang': 'kakulang', 'nacacaalam': 'nakakaalam', 'caramihang': 'karamihang', 'caraniwan': 'karaniwan',
    'caraniwang': 'karaniwang', 'cayamanan': 'kayamanan', 'baca': 'baka', 'magcagayo': 'magkagayo',
    'macatuwid': 'makatuwid', 'cabataan': 'kabataan', 'tumacas': 'tumakas', 'canicanilang': 'kanikanilang',
    'capang': 'kapang', 'caguluhan': 'kaguluhan', 'caayaayang': 'kaayaayang', 'nagcacailang': 'nagkakailang',
    'cagandahan': 'kagandahan', 'nagcaroon': 'nagkaroon', 'cahihiyan': 'kahihiyan', 'cumikilos': 'kumikilos',
    'licuran': 'likuran', 'pagcakita': 'pagkakita', 'caisipan': 'kaisipan', 'capayapaan': 'kapayapaan',
    'cahabaghabag': 'kahabaghabag', 'cakilala': 'kakilala', 'magcabicabilang': 'magkabikabilang',
    'macapag': 'makapag', 'calugodlugod': 'kalugodlugod', 'cabuluhan': 'kabuluhan',
    'casam': 'kasam', 'daco': 'dako', 'cabanalan': 'kabanalan', 'bucas': 'bukas', 'camatayan': 'kamatayan',
    'umiiyac': 'umiiyak', 'calungcutan': 'kalungkutan', 'cata': 'kata', 'imic': 'imik',
    'casangcapan': 'kasangkapan', 'causap': 'kausap', 'cahaling': 'kahaling', 'cumilos': 'kumilos',
    'cababayan': 'kababayan', 'cusang': 'kusang', 'kinabucasan': 'kinabukasan', 'umiimic': 'umiimik',
    'carunung': 'karunung', 'camag': 'kamag', 'cumain': 'kumain', 'balicat': 'balikat', 'casalucuyang': 'kasalukuyang',
    'caninang': 'kaninang', 'capalaran': 'kapalaran', 'capit': 'kapit', 'bucod': 'bukod', 'magpacailan': 'magpakailan',
    'suloc': 'sulok', 'macapang': 'makapang', 'cabooan': 'kabuuan'
}

# Substrings that explicitly remain Spanish
PROTECTED_SPANISH = {
    'cura', 'clara', 'alcalde', 'victorina', 'convento', 'civil', 'franciscano', 'sacerdote', 
    'lucas', 'doctor', 'coche', 'coches', 'cruz', 'castila', 'castilang', 'escuela', 'victoria', 'dominico', 
    'tiburcio', 'francisco', 'chocolate', 'justicia', 'jesucristo', 'indulgencia', 
    'cristal', 'conservador', 'cristiano', 'corresponsal', 'cuartel', 'gobernadorcillo',
    'sacristan', 'crispin', 'capitan', 'capitanes', 'capitana', 'crisostomo', 'consolacion', 'clarita',
    'jose', 'santiago', 'tiago', 'paco', 'marcos', 'macaraig', 'carlos', 'carmen',
    'corbata', 'cruzado', 'cerveza', 'cigarrillo', 'cristo', 'conciencia', 'cuarto', 'capilla',
    'catolico', 'celda', 'capitulo', 'blanco', 'franco', 'chico', 'chica', 'medico', 'banco',
    'rico', 'poco', 'loco', 'noli', 'tangere', 'vae', 'victis', 'sic', 'buon', 'conosce', 'mattina',
    'rizal', 'elias', 'maria', 'damaso', 'fiesta', 'vispera', 'azotea', 'filosofo', 'maestro',
    'sermon', 'gobernador', 'procesion', 'filibustero', 'civilizacion', 'dios', 'domingo',
    'general', 'teniente', 'guardia', 'tribunal', 'san', 'diego', 'guevara', 'peninsula', 'europa',
    'ermita', 'santa', 'pascual', 'baylon', 'antonio', 'padua', 'niño', 'jesus', 'vicente', 'pedro',
    'martir', 'malco', 'luis', 'felipe', 'amadeo', 'catorce', 'diez', 'seis', 'segundo', 'primero',
    'doña', 'don', 'poblete', 'gutenberg', 'fernandez', 'paz', 'sta', 'evangelio', 'schiller', 'shakespeare',
    'sra', 'sr', 'dr', 'fr', 'coadjutor', 'cuarta', 'candilang'
}

PROTECTED_GUI = {
    'guitarra', 'guia', 'guirnalda'
}

def remove_accents(text):
    # Temporarily hide enye
    text = text.replace("ñ", "___enye___").replace("Ñ", "___ENYE___")
    # Decompose
    text = unicodedata.normalize('NFD', text)
    # Strip Mark, Nonspacing
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    # Recombine
    text = unicodedata.normalize('NFC', text)
    # Restore enye
    text = text.replace("___enye___", "ñ").replace("___ENYE___", "Ñ")
    return text

def normalize_text(text):
    # Rule 2: g-tilde & variants
    text = re.sub(r'mg\u0303a', 'mga', text, flags=re.IGNORECASE)
    text = re.sub(r'mg\u0303', 'mga', text, flags=re.IGNORECASE)
    text = re.sub(r'ng\u0303', 'ng', text, flags=re.IGNORECASE)
    text = re.sub(r'n\u0303g', 'ng', text, flags=re.IGNORECASE)
    text = re.sub(r'g\u0303', 'ng', text, flags=re.IGNORECASE)

    # Convert standalone ñg to ng
    text = re.sub(r'\bñg\b', 'ng', text, flags=re.IGNORECASE)
    
    # Rule 1: Accents uniformly removed
    text = remove_accents(text)
    
    # Rule 3: manga / mang̃a (already converted to manga above) -> mga
    # Case insensitive exact word replacements
    text = re.sub(r'\bmanga\b', 'mga', text)
    text = re.sub(r'\bManga\b', 'Mga', text)
    text = re.sub(r'\bMANGA\b', 'MGA', text)
    
    # Rule 5 & 6 & Custom: Explicit archaic word replace
    explicit = {
        'huag': 'huwag', 'HUAG': 'HUWAG', 'Huag': 'Huwag',
        'wacas': 'wakas', 'Wacas': 'Wakas', 'WACAS': 'WAKAS',
        'bahagui': 'bahagi', 'Bahagui': 'Bahagi', 'BAHAGUI': 'BAHAGI',
        'lacas': 'lakas', 'Lacas': 'Lakas', 'LACAS': 'LAKAS',
        'boong': 'buong', 'Boong': 'Buong', 'BOONG': 'BUONG',
        'kabooan': 'kabuuan', 'Kabooan': 'Kabuuan', 'KABOOAN': 'KABUUAN',
        'pilac': 'pilak', 'Pilac': 'Pilak', 'PILAC': 'PILAK'
    }
    for old, new in explicit.items():
        text = re.sub(rf'\b{old}\b', new, text)

    # Custom rule: gui -> gi
    def gui_to_gi_replacer(match):
        word = match.group(0)
        word_lower = word.lower()
        if word_lower in PROTECTED_GUI:
            return word
        rep = re.sub(r'gui', 'gi', word)
        rep = re.sub(r'Gui', 'Gi', rep)
        rep = re.sub(r'GUI', 'GI', rep)
        return rep
    text = re.sub(r'\b[A-Za-zñÑ]*[gG][uU][iI][A-Za-zÑñ]*\b', gui_to_gi_replacer, text)

    # Rule 4: c -> k in Tagalog words
    def c_to_k_replacer(match):
        word = match.group(0)
        word_lower = word.lower()
        
        if word_lower in PROTECTED_SPANISH:
            return word
            
        if word_lower in EXPLICIT_C_MAP:
            rep = EXPLICIT_C_MAP[word_lower]
            if word.istitle(): return rep.capitalize()
            if word.isupper(): return rep.upper()
            return rep
            
        # Generalized C->K for remaining unidentified words
        # Only replace 'c' -> 'k' if NOT followed by 'h' (ch is maintained, e.g. coche)
        # also not preceding 'i' or 'e' if we strictly want only a,o,u, but Tagalog C->K can happen anywhere if not Spanish.
        # "Pattern rule: For any other Tagalog word with c followed by a, o, u, i, e where it sounds like /k/, replace c -> k"
        rep = re.sub(r'c(?!h)', 'k', word)
        rep = re.sub(r'C(?!h|H)', 'K', rep)
        return rep

    text = re.sub(r'\b[A-Za-zñÑ]*[cC][A-Za-zñÑ]*\b', c_to_k_replacer, text)
    return text

def main():
    rows = []
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            normalized_sentence = normalize_text(row['sentence_text'])
            normalized_title = normalize_text(row['chapter_title'])
            
            rows.append({
                'book_title': 'Noli Me Tangere',
                'chapter_number': row['chapter_number'],
                'chapter_title': normalized_title.upper(),
                'sentence_number': row['sentence_number'],
                'sentence_text': normalized_sentence
            })
            
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['book_title', 'chapter_number', 'chapter_title', 'sentence_number', 'sentence_text'])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Normalized {len(rows)} sentences to {OUTPUT_CSV}")

    # QA Validation Script Logic
    print("\n--- QA Validation ---")
    errors = []
    for i, r in enumerate(rows):
        t = r['sentence_text']
        if 'g̃' in t: errors.append(f"Row {i}: g̃ found")
        if re.search(r'[áéíóúàèìòùÁÉÍÓÚ]', t): errors.append(f"Row {i}: accent found")
        if re.search(r'\bmanga\b', t, re.I): errors.append(f"Row {i}: 'manga' as plural")
        if re.search(r'\bhuag\b', t, re.I): errors.append(f"Row {i}: 'huag' not normalized")
        if re.search(r'\bcanya\b|\bcung\b|\bcó\b|\bacó\b', t): errors.append(f"Row {i}: archaic c-word found")
        if re.search(r'\bwica\b', t, re.I): errors.append(f"Row {i}: 'wica' not normalized")
        
        # New checks
        gui_matches = re.findall(r'\b[A-Za-zñÑ]*gui[A-Za-zñÑ]*\b', t, re.I)
        unprotected_gui = [m for m in gui_matches if m.lower() not in PROTECTED_GUI]
        if unprotected_gui: errors.append(f"Row {i}: unprotected 'gui' found: {unprotected_gui}")
        
        if re.search(r'\bboong\b', t, re.I): errors.append(f"Row {i}: 'boong' found")
        if re.search(r'\bpilac\b', t, re.I): errors.append(f"Row {i}: 'pilac' found")
        if re.search(r'\bkabooan\b', t, re.I): errors.append(f"Row {i}: 'kabooan' found")

    print(f"Total errors: {len(errors)}")
    for e in errors[:20]:
        print(e)

if __name__ == '__main__':
    main()
