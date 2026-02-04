# Rizal Thesis Dataset Normalization

## Project Overview
This project produces high-quality, normalized datasets of Dr. Jose Rizal's two major novels, **Noli Me Tangere** and **El Filibusterismo**, for Natural Language Processing (NLP) tasks. The primary goal is to convert the historical 19th-century Tagalog orthography into a form compatible with modern Filipino language models (specifically XLM-RoBERTa), while strictly preserving sentence segmentation and paragraph structure.

## Processing Pipeline Overview
The raw text undergoes a strict, auditable 4-pipleline process:

1.  **Extraction**: Raw text is parsed from Project Gutenberg HTML source files into a structured CSV format. Front matter (license, title pages, table of contents) is programmatically removed to ensure only narrative text remains.
2.  **Phase A–C (Orthographic Normalization)**:
    *   **Unicode Standardization**: All text is converted to NFC (Normalization Form C).
    *   **Archaic Character Fixes**: Resolution of archaic tilde-g (`g̃` → `g`) and particle variants (`ñg` → `ng`).
    *   **Diacritic Stripping**: Safe removal of combining diacritics (accents) while strictly preserving the distinct letter `ñ` / `Ñ`.
3.  **Sentence Segmentation**: Paragraphs are split into sentences using a custom rule-based splitter that respects abbreviations (e.g., `G.`, `Dr.`) and dialogue punctuation. Chapter metadata is normalized (Chapters sequenced 1–N).
4.  **Phase D (Lexical Modernization)**: A conservative, lexicon-driven modernization step. Common archaic spellings (e.g., `cung`, `guinoo`) are mapped to their modern equivalents (`kung`, `ginoo`) using a high-confidence mapping table. Proper nouns and ambiguous terms are preserved.

## File Inventory

### El Filibusterismo
| File | Phase | Description |
| :--- | :--- | :--- |
| `elfili_extraction.csv` | Extraction | Raw text extracted from HTML. |
| `elfili_extraction_normalized.csv` | Phase A-C | Orthographically normalized text (NFC, no diacritics). |
| `elfili_normalized_ortho.txt` | Phase A-C | Plain text file of narrative paragraphs (reference corpus). |
| `elfili_chapter_sentences.csv` | Segmentation | Sentence-segmented dataset with Phase A-C orthography. |
| `elfili_chapter_sentences_modernized.csv` | Phase D | **Final Modernized Sentence Dataset**. |

### Noli Me Tangere
| File | Phase | Description |
| :--- | :--- | :--- |
| `noli_extraction.csv` | Extraction | Raw text extracted from HTML. |
| `noli_extraction_normalized.csv` | Phase A-C | Orthographically normalized text (NFC, no diacritics). |
| `noli_normalized_ortho.txt` | Phase A-C | Plain text file of narrative paragraphs (reference corpus). |
| `noli_chapter_sentences.csv` | Segmentation | Sentence-segmented dataset with Phase A-C orthography. |
| `noli_chapter_sentences_modernized.csv` | Phase D | **Final Modernized Sentence Dataset**. |

### Configuration & Logs
| File | Description |
| :--- | :--- |
| `phase_d_mapping_master.csv` | The master lexicon table defining all Phase D textual replacements. |
| `phase_d_log_elfili.csv` | Full audit log of every word replacement in *El Filibusterismo*. |
| `phase_d_log_noli.csv` | Full audit log of every word replacement in *Noli Me Tangere*. |
| `phase_d_summary_*.md` | Statistical summaries of the modernization process. |

## Which files should I use?

### For Modern NLP Modeling (Recommended)
Use the **Phase D Modernized** files. These align best with the vocabulary of modern pre-trained models like XLM-RoBERTa.
*   `noli_chapter_sentences_modernized.csv`
*   `elfili_chapter_sentences_modernized.csv`

### For Historical Analysis
Use the **Phase A–C Normalized** files. These retain archaic spellings (`cung`, `saca`) but remove noise (junk diacritics) for cleaner character-level analysis.
*   `noli_chapter_sentences.csv`
*   `elfili_chapter_sentences.csv`

## Reproducibility & alignment
*   **Row-Level Alignment**: Transformation phases strictly preserve row counts. Row $N$ in the "Normalized" CSV corresponds exactly to Row $N$ in the "Modernized" CSV.
*   **Unicode Compliance**: All final outputs are validated to be **NFC** compliant with **0 combining marks**.
*   **Sentence Boundaries**: Sentence segmentation is identical across Normalized and Modernized versions.

## Notes & Constraints
*   **Proper Nouns**: Names (e.g., *Ibarra*, *Maria Clara*) and places are strictly preserved.
*   **No Rewriting**: No AI paraphrasing or grammar correction was applied. Changes are limited to strict 1:1 token substitution based on the mapping table.
*   **Auditable**: Every single character change in Phase D is logged in the `phase_d_log_*.csv` files.
