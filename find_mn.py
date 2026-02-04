
import unicodedata
import csv

FILES = ['elfili_extraction_modernized.csv', 'noli_extraction_modernized.csv']

def check_file(fname):
    print(f"Checking {fname}...")
    with open(fname, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        # Identify columns
        
        row_idx = 1
        found = 0
        for row in reader:
            row_idx += 1
            row_str = "".join(row)
            has_mn = False
            for c in row_str:
                if unicodedata.category(c) == 'Mn':
                    has_mn = True
                    break
            
            if has_mn:
                found += 1
                if found <= 5:
                    # Print which column
                    for i, col in enumerate(row):
                        col_mn = [c for c in col if unicodedata.category(c) == 'Mn']
                        if col_mn:
                            readable = [unicodedata.name(c) for c in col_mn]
                            print(f"Row {row_idx}, Col '{header[i]}': {col} (Mn: {readable})")
        print(f"Total rows with Mn: {found}")

if __name__ == '__main__':
    for f in FILES:
        check_file(f)
