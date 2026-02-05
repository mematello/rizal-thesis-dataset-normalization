
import csv
import re

def get_titles(filename, label):
    titles = {} # num -> title
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                num = row.get('chapter_number', '0')
                title = row.get('chapter_title', '')
                # normalize num for sorting
                try:
                    num_val = int(num)
                except:
                    num_val = 9999
                
                if num_val not in titles:
                    titles[num_val] = title
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return

    print(f"\n### {label} Chapter Titles")
    for num in sorted(titles.keys()):
        if num == 9999: continue
        print(f"{num}: {titles[num]}")

get_titles('noli_chapter_sentences_modernized_v2.csv', 'Noli Me Tangere')
get_titles('elfili_chapter_sentences_modernized_v2.csv', 'El Filibusterismo')
