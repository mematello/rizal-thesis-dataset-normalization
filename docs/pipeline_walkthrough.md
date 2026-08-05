# Pipeline Walkthrough

This document explains the step-by-step reproducible pipeline for the Rizal Thesis Dataset Normalization project.

## 1. Extraction (Phase 1)
Raw HTML texts from Project Gutenberg (`data/raw/`) are parsed to remove boilerplate and structure the text into rows representing narrative paragraphs. Output goes to `data/intermediate/01_extraction/`. *(For details on the exact Project Gutenberg source files and licensing, see the **Source Material** section in `README.md`.)*

## 2. Orthographic Normalization (Phase A-C)
Intermediate extraction CSVs are passed through Unicode normalization (NFC) and archaic character cleaning (e.g., `g̃` → `g`, `ñg` → `ng`, diacritic stripping). Output goes to `data/intermediate/02_ortho_norm/`.

## 3. Segmentation
Paragraphs are split into sentences using custom rule-based heuristics that respect dialogue and abbreviations. Output goes to `data/intermediate/03_segmentation/`.

## 4. Lexical Modernization (Phase D - Initial)
Initial safe and strictly defined token replacements are applied. Outputs move into `data/intermediate/05_lexical/`. 

## 5. Title Normalization (Phase T)
Chapter titles are frozen, modernized strictly, and joined back onto the sentences. Outputs land in `data/intermediate/04_titles/`.

## 6. Final Audit and Apply (Phase D.2-D.6)
Strictly approved token mappings (Category A) are explicitly audited and applied. The output of Phase D.6 is the **`FINAL_v2.csv`** dataset, stored in `data/final/`.

---

> [!WARNING]
> ## Experimental Branches (Not Core Pipeline)
> The repository contains an `experiments/` directory which houses `modernize_noli.py` and `noli_chapter_sentences_FINAL_v3.csv`. 
> 
> **Important**: `modernize_noli.py` depends on the OpenAI API (`gpt-4`) to perform deep contextual semantic modernization. Because LLM outputs are non-deterministic and reliant on external APIs, this step is **NOT part of the reproducible core pipeline**. `FINAL_v2.csv` remains the definitive, deterministic, and auditable thesis deliverable.
