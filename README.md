# Rizal Thesis Dataset Normalization

## Project Overview
This project produces high-quality, normalized datasets of Dr. Jose Rizal's two major novels, **Noli Me Tangere** and **El Filibusterismo**, for Natural Language Processing (NLP) tasks. The primary goal is to convert the historical 19th-century Tagalog orthography into a form compatible with modern Filipino language models (specifically XLM-RoBERTa), while strictly preserving sentence segmentation and paragraph structure.

## Processing Pipeline Overview
The text undergoes a strict, auditable 6-stage pipeline:

1.  **Extraction**: Raw text is parsed from Project Gutenberg HTML source files into a structured CSV format. Front matter is removed.
2.  **Phase A–C (Orthographic Normalization)**:
    *   **Unicode Standardization**: All text is converted to NFC (Normalization Form C).
    *   **Archaic Character Fixes**: Resolution of archaic tilde-g (`g̃` → `g`) and particle variants (`ñg` → `ng`).
    *   **Diacritic Stripping**: Removal of combining diacritics while preserving `ñ`.
3.  **Phase T (Title Normalization)**:
    *   Chapter titles are normalized to a consistent format (UPPERCASE), with Roman numerals removed and Spanish terms modernized (e.g., `EREHE` instead of `HEREJE`).
    *   These titles are **frozen** and strictly preserved in subsequent phases.
4.  **Sentence Segmentation**: Paragraphs are split into sentences using a custom rule-based splitter that respects abbreviations and dialogue punctuation.
5.  **Phase D (Lexical Modernization)**:
    *   **D.2/D.4 (Conservative)**: Initial safe modernization of common tokens (e.g., `cung`→`kung`, `buhoc`→`buhok`).
    *   **D.5 (Deep Audit)**: Comprehensive scanning of all remaining archaic candidates.
    *   **D.6 (Final Approval)**: **Final, strict modernization** based on an explicitly approved list (Category A). Spanish loanwords (Category B) and proper nouns (Category C) are strictly **preserved/rejected** to maintain historical register.
6.  **Final Output**: The pipeline results in "FINAL v2" frozen datasets.

## File Inventory

### **Recommended Final Datasets (Thesis-Ready)**
These are the frozen, normalized, and modernized files approved for final modeling.
| File | Description |
| :--- | :--- |
| **`noli_chapter_sentences_FINAL_v2.csv`** | **Final Noli Me Tangere Dataset**. |
| **`elfili_chapter_sentences_FINAL_v2.csv`** | **Final El Filibusterismo Dataset**. |

### Intermediate Files (For Reference)
| File | Phase | Description |
| :--- | :--- | :--- |
| `*_extraction.csv` | Extraction | Raw text extracted from HTML. |
| `*_extraction_normalized.csv` | Phase A-C | NFC normalized text. |
| `*_chapter_sentences.csv` | Segmentation | Segmented sentences with old orthography (`cung`, `saca`). |
| `*_chapter_sentences_modernized.csv` | Phase D.4 | Intermediate modernized version. |
| `*_chapter_sentences_FINAL.csv` | Phase D.4 | Version with frozen Phase T titles. |

### Configuration & Logs
| File | Description |
| :--- | :--- |
| `phase_d6_proposal.md` | The final proposal document categorizing tokens as Safe (A), Review (B), or Preserve (C). |
| `phase_d6_apply.py` | The script used for the final application of Phase D.6 rules. |
| `phase_d6_log_*.csv` | **Audit Log**: Every change made in the final phase. |
| `walkthrough.md` | Comprehensive chronological log of all technical decisions and phases. |

## Which files should I use?

### For Modern NLP Modeling
Use the **`FINAL_v2.csv`** files. These align best with the vocabulary of modern pre-trained models like XLM-RoBERTa while respecting the historical context of the novels (preserving Spanish loans and names).

### For Historical Analysis
Use the **`*_chapter_sentences.csv`** (Segmentation phase) files. These retain archaic spellings (`cung`, `saca`) but remove noise (junk diacritics) for cleaner character-level analysis.

## Reproducibility & Alignment
*   **Row-Level Alignment**: Transformation phases strictly preserve row counts. Row $N$ in the "raw" extraction corresponds exactly to Row $N$ in the "FINAL_v2" CSV.
*   **Unicode Compliance**: All final outputs are validated to be **NFC** compliant.
*   **Auditability**: Every change in Phase D is logged.

## Constraints Preserved
*   **Proper Nouns**: Names (e.g., *Ibarra*, *Maria Clara*) are strictly preserved.
*   **Spanish Loans**: Terms like *cura*, *campana*, *coche* are preserved in their original spelling (Phase D.6 Decision).
*   **Titles**: Chapter titles are locked to the Phase T specification.
