
import csv
import sys
from transformers import XLMRobertaTokenizerFast

# Files
input_filename = "elfili_extraction.csv"
output_filename = "elfili_tokens.csv"

def main():
    print("Loading XLM-RoBERTa tokenizer...")
    try:
        # Use Fast tokenizer to get offset mappings efficiently
        tokenizer = XLMRobertaTokenizerFast.from_pretrained("xlm-roberta-base")
    except Exception as e:
        print(f"Error loading tokenizer: {e}")
        return

    print(f"Reading {input_filename}...")
    
    rows_to_process = []
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['text_type'] == 'paragraph':
                    rows_to_process.append(row)
    except FileNotFoundError:
        print(f"Error: {input_filename} not found.")
        return

    print(f"Processing {len(rows_to_process)} paragraphs...")

    output_rows = []
    total_tokens = 0
    total_paras = 0
    
    # Validation sample storage
    sample_tokens = [] 
    
    for row in rows_to_process:
        text = row['text']
        global_para_index = row['global_para_index']
        chapter_index = row['chapter_index']
        chapter_title = row['chapter_title']
        para_index_in_chapter = row['para_index_in_chapter']
        
        # Tokenize with offsets
        # return_offsets_mapping=True gives (start, end) for each token
        encoding = tokenizer(text, return_offsets_mapping=True, add_special_tokens=False)
        
        tokens = tokenizer.convert_ids_to_tokens(encoding.input_ids)
        offsets = encoding.offset_mapping
        ids = encoding.input_ids
        
        # In some versions/cases, convert_ids_to_tokens might return tokens with the special char.
        # XLM-R uses SPIECE_UNDERLINE (U+2581) to denote whitespace/start of word.
        
        for idx, (token, token_id, (start, end)) in enumerate(zip(tokens, ids, offsets)):
            # Check for SentencePiece word-start marker (U+2581)
            # The character is ' ' (Lower One Eighth Block? No, it's U+2581)
            # We can check if it starts with ' '
            
            is_subword = not token.startswith(' ')
            
            # Create row
            token_row = {
                'global_para_index': global_para_index,
                'chapter_index': chapter_index,
                'chapter_title': chapter_title,
                'para_index_in_chapter': para_index_in_chapter,
                'token_index_in_para': idx,
                'token_text': token,
                'is_subword': is_subword,
                'token_id': token_id,
                'char_start': start,
                'char_end': end,
                'paragraph_text': text
            }
            output_rows.append(token_row)
            
            # Collect sample for specific validation request
            # global_para_index = 2, chapter_index = 0
            if str(global_para_index) == '2' and str(chapter_index) == '0' and len(sample_tokens) < 10:
                sample_tokens.append(token_row)

        total_tokens += len(tokens)
        total_paras += 1

    print(f"Writing {len(output_rows)} token rows to {output_filename}...")
    
    fieldnames = [
        'global_para_index', 'chapter_index', 'chapter_title', 'para_index_in_chapter',
        'token_index_in_para', 'token_text', 'is_subword', 'token_id',
        'char_start', 'char_end', 'paragraph_text'
    ]
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    # Validation Summary
    print("\nTokenization Summary")
    print("--------------------")
    print(f"Total paragraphs tokenized: {total_paras}")
    print(f"Total tokens generated: {total_tokens}")
    avg_tokens = total_tokens / total_paras if total_paras > 0 else 0
    print(f"Average tokens per paragraph: {avg_tokens:.2f}")
    
    print("\nSample Output (First 10 tokens from global_para_index=2, chapter_index=0):")
    for t in sample_tokens:
        print(f"Idx: {t['token_index_in_para']}, Text: '{t['token_text']}', Subword: {t['is_subword']}, ID: {t['token_id']}")

if __name__ == "__main__":
    main()
