
import csv
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paths import ELFILI_CHAPTER_SENTENCES_MODERNIZED_V2, NOLI_CHAPTER_SENTENCES_MODERNIZED_V2


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

get_titles(NOLI_CHAPTER_SENTENCES_MODERNIZED_V2, 'Noli Me Tangere')
get_titles(ELFILI_CHAPTER_SENTENCES_MODERNIZED_V2, 'El Filibusterismo')
