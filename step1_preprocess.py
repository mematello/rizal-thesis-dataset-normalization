import csv
import re

INPUT_CSV = 'noli_extraction.csv'
OUTPUT_CSV = 'noli_step1_sentences.csv'

chapter_map = {
    "ANG PROCESION.": 39,
    "SI DONA CONSOLACION.": 40,
    "ANG CATUWIRA'T ANG LACAS.": 41,
    "DALAWANG PANAUHIN.": 42,
    "ANG MAG-ASAWANG DE ESPADAÑA.": 43,
    "MGA PANUCALA.": 44,
    "PAGSISIYASAT NG CONCIENCIA.": 45,
    "ANG MGA PINAG-UUSIG.": 46,
    "SABUNGAN.": 47,
    "ANG DALAWANG GUINOONG BABAE.": 48,
    "ANG HINDI MAGCURO": 49,
    "ANG TINGIG NG MGA PINAG-UUSIG.": 50,
    "ANG TINGIG NG̃ MG̃A PINAG-UUSIG.": 50,
    "ANG MAG-ANAK NI ELIAS.": 51,
    "MGA PAGBABAGO.": 52,
    "ANG SULAT NG MGA PATAY AT ANG MGA ANINO.": 53,
    "ANG SULAT NG̃ MG̃A PATAY AT ANG MG̃A ANINO.": 53,
    "LIV.": 54,
    "IL BUON DI SI CONOSCE DA MATTINA.": 54,
    "ANG CAPAHAMACAN.": 55,
    "ANG SABIHANAN AT ANG INAACALA.": 56,
    "¡VAE VICTIS!": 57,
    "ANG SINUMPA.": 58,
    "ANG KINAGUISNANG BAYAN AT ANG MGA PAG-AARI.": 59,
    "ANG KINAGUISNANG BAYAN AT ANG MG̃A PAG-AARI.": 59,
    "MAG-AASAWA SI MARIA CLARA.": 60,
    "ANG PANGHUHULI SA DAGATAN.": 61,
    "PAGPAPALIWANAG NI PARI DAMASO.": 62,
    "ANG GABING SINUSUNDAN NG PASCO NG PANGANGANGANAC.": 63,
    "ANG GABING SINUSUNDAN NG̃ PASCO NG̃ PANG̃ANG̃ANAC.": 63,
    "PANGWACAS NA BAHAGUI.": 64,
    "WACAS NG PAGSASAYSAY.": 65,
    "WACAS ÑG PAGSASAYSAY.": 65
}

def split_into_sentences(text):
    text = text.strip()
    if not text:
        return []
    
    text = text.replace('Dr.', 'Dr_')
    text = text.replace('Sr.', 'Sr_')
    text = text.replace('Sra.', 'Sra_')
    text = text.replace('Fr.', 'Fr_')
    text = text.replace('P.', 'P_')
    text = text.replace('H.', 'H_')
    
    sentences = []
    # match punctuation + space + Cap
    parts = re.split(r'([.!?]+["\']?)\s+(?=[A-Z¡¿"\'])', text)
    
    current_sentence = parts[0]
    for i in range(1, len(parts), 2):
        punct = parts[i]
        next_part = parts[i+1] if i+1 < len(parts) else ""
        current_sentence += punct
        sentences.append(current_sentence.strip())
        current_sentence = next_part
    
    if current_sentence.strip():
        sentences.append(current_sentence.strip())
        
    for i in range(len(sentences)):
        sentences[i] = sentences[i].replace('Dr_', 'Dr.').replace('Sr_', 'Sr.').replace('Sra_', 'Sra.').replace('Fr_', 'Fr.').replace('P_', 'P.').replace('H_', 'H.')
        
    return sentences

def main():
    out_rows = []
    out_fields = ['book_title', 'chapter_number', 'chapter_title', 'sentence_number', 'sentence_text']
    
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        chapter_sentence_counter = {}
        
        for row in reader:
            c_idx = row['chapter_index'].strip()
            c_title = row['chapter_title'].strip()
            text_type = row['text_type'].strip()
            text = row['text'].strip()
            
            if c_idx == '0':
                continue
            if text_type != 'paragraph':
                continue
            if 'TALABABA' in c_title:
                continue
                
            ch_num = -1
            if int(c_idx) < 39:
                ch_num = int(c_idx)
            else:
                lookup_title = c_title
                matched = False
                for k, v in chapter_map.items():
                    if k in c_title:
                        ch_num = v
                        matched = True
                        break
                if not matched:
                    ch_num = 39
                    print(f"Warning: Could not map title: {c_title}")
                    
            if ch_num not in chapter_sentence_counter:
                chapter_sentence_counter[ch_num] = 1
                
            sentences = split_into_sentences(text)
            
            for s in sentences:
                if not s.strip(): continue
                out_rows.append({
                    'book_title': 'Noli Me Tangere',
                    'chapter_number': ch_num,
                    'chapter_title': c_title,
                    'sentence_number': chapter_sentence_counter[ch_num],
                    'sentence_text': s.strip()
                })
                chapter_sentence_counter[ch_num] += 1
                
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)
        print(f"Wrote {len(out_rows)} sentences to {OUTPUT_CSV}")

if __name__ == '__main__':
    main()
