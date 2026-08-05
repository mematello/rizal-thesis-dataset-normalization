import os
from pathlib import Path

# Base directories
ROOT_DIR = Path(__file__).parent.resolve()
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
FINAL_DIR = DATA_DIR / "final"
INTERMEDIATE_DIR = DATA_DIR / "intermediate"

P1_EXTRACTION = INTERMEDIATE_DIR / "01_extraction"
P2_ORTHO = INTERMEDIATE_DIR / "02_ortho_norm"
P3_SEG = INTERMEDIATE_DIR / "03_segmentation"
P4_TITLES = INTERMEDIATE_DIR / "04_titles"
P5_LEXICAL = INTERMEDIATE_DIR / "05_lexical"

LOGS_DIR = ROOT_DIR / "logs"
LOGS_ORTHO = LOGS_DIR / "ortho"
LOGS_TITLES = LOGS_DIR / "titles"
LOGS_LEXICAL = LOGS_DIR / "lexical"

EXPERIMENTS_DIR = ROOT_DIR / "experiments"

# --- Raw Files ---
NOLI_RAW_HTML = RAW_DIR / "Noli Me Tangere - Project Gutenberg.html"
ELFILI_RAW_HTML = RAW_DIR / "Ang _Filibusterismo_, by José Rizal_ A Project Gutenberg eBook.html"
ELFILI_EXTRACTED_RAW = RAW_DIR / "elfili_extracted_raw.txt"

# --- Final Deliverables ---
NOLI_FINAL_V2 = FINAL_DIR / "noli_chapter_sentences_FINAL_v2.csv"
ELFILI_FINAL_V2 = FINAL_DIR / "elfili_chapter_sentences_FINAL_v2.csv"

# --- Experimental ---
NOLI_FINAL_V3 = EXPERIMENTS_DIR / "noli_chapter_sentences_FINAL_v3.csv"
ELFILI_FINAL_V3 = EXPERIMENTS_DIR / "elfili_chapter_sentences_FINAL_v3.csv"
NOLI_MODERN_CSV = EXPERIMENTS_DIR / "noli_chapter_sentences_modern.csv"

# --- Phase 1: Extraction ---
NOLI_EXTRACTION_CSV = P1_EXTRACTION / "noli_extraction.csv"
ELFILI_EXTRACTION_CSV = P1_EXTRACTION / "elfili_extraction.csv"

# --- Phase 2: Ortho Normalization ---
NOLI_EXTRACTION_NORMALIZED = P2_ORTHO / "noli_extraction_normalized.csv"
ELFILI_EXTRACTION_NORMALIZED = P2_ORTHO / "elfili_extraction_normalized.csv"
NOLI_NORMALIZED_ORTHO_TXT = P2_ORTHO / "noli_normalized_ortho.txt"
ELFILI_NORMALIZED_ORTHO_TXT = P2_ORTHO / "elfili_normalized_ortho.txt"
NORMALIZATION_LOG_TXT = LOGS_ORTHO / "normalization_log.txt"
NORMALIZATION_LOG_NOLI_TXT = LOGS_ORTHO / "normalization_log_noli.txt"
NORMALIZATION_SUMMARY_TXT = LOGS_ORTHO / "normalization_summary.txt"
CHANGE_LOG_CSV = LOGS_ORTHO / "change_log.csv"

# --- Phase 3: Segmentation ---
NOLI_CHAPTER_SENTENCES = P3_SEG / "noli_chapter_sentences.csv"
ELFILI_CHAPTER_SENTENCES = P3_SEG / "elfili_chapter_sentences.csv"
CORPUS_PROFILE = LOGS_LEXICAL / "corpus_profile.txt"
ALL_TOKENS_INVENTORY = P3_SEG / "all_tokens_inventory.csv"
PROTECTED_TERMS = DATA_DIR / "protected_terms.txt"
HUMAN_REVIEW_LIST = DATA_DIR / "human_review_list.txt"
LEXICON_CANDIDATES = P3_SEG / "lexicon_candidates.csv"
RESIDUAL_CANDIDATES = P3_SEG / "residual_candidates.csv"
MAPPING_PROPOSAL = DATA_DIR / "mapping_proposal.csv"

# --- Phase D (Lexical Intermediates) ---
NOLI_EXTRACTION_MODERNIZED = P5_LEXICAL / "noli_extraction_modernized.csv"
ELFILI_EXTRACTION_MODERNIZED = P5_LEXICAL / "elfili_extraction_modernized.csv"
NOLI_CHAPTER_SENTENCES_MODERNIZED = P5_LEXICAL / "noli_chapter_sentences_modernized.csv"
ELFILI_CHAPTER_SENTENCES_MODERNIZED = P5_LEXICAL / "elfili_chapter_sentences_modernized.csv"
PHASE_D_MAPPING_MASTER = P5_LEXICAL / "phase_d_mapping_master.csv"

# Phase D2
NOLI_CHAPTER_SENTENCES_MODERNIZED_V2 = P5_LEXICAL / "noli_chapter_sentences_modernized_v2.csv"
ELFILI_CHAPTER_SENTENCES_MODERNIZED_V2 = P5_LEXICAL / "elfili_chapter_sentences_modernized_v2.csv"
PHASE_D_MAPPING_MASTER_V2 = P5_LEXICAL / "phase_d_mapping_master_v2.csv"
PHASE_D2_CANDIDATES = P5_LEXICAL / "phase_d2_candidates.csv"

# Phase D3
RESIDUAL_C_INVENTORY = P5_LEXICAL / "residual_c_inventory.csv"
RESIDUAL_C_CLASSIFIED = P5_LEXICAL / "residual_c_classified.csv"

# --- Phase 4: Titles ---
NOLI_CHAPTER_TITLES_NORMALIZED = P4_TITLES / "noli_chapter_titles_normalized.csv"
ELFILI_CHAPTER_TITLES_NORMALIZED = P4_TITLES / "elfili_chapter_titles_normalized.csv"
NOLI_CHAPTER_SENTENCES_TITLES_FIXED = P4_TITLES / "noli_chapter_sentences_titles_fixed.csv"
ELFILI_CHAPTER_SENTENCES_TITLES_FIXED = P4_TITLES / "elfili_chapter_sentences_titles_fixed.csv"
PHASE_T_TITLE_MAPPING_V2 = P4_TITLES / "phase_t_title_mapping_v2.csv"

NOLI_CHAPTER_SENTENCES_TITLES_FIXED_V2 = P4_TITLES / "noli_chapter_sentences_titles_fixed_v2.csv"
ELFILI_CHAPTER_SENTENCES_TITLES_FIXED_V2 = P4_TITLES / "elfili_chapter_sentences_titles_fixed_v2.csv"
NOLI_CHAPTER_SENTENCES_TITLES_FIXED_V3 = P4_TITLES / "noli_chapter_sentences_titles_fixed_v3.csv"

# --- Phase D (Final) ---
NOLI_FINAL = P5_LEXICAL / "noli_chapter_sentences_FINAL.csv"
ELFILI_FINAL = P5_LEXICAL / "elfili_chapter_sentences_FINAL.csv"

PHASE_D5_CANDIDATES = P5_LEXICAL / "phase_d5_candidates.csv"
PHASE_D6_PROPOSAL = DATA_DIR / "phase_d6_proposal.md"

# --- Logs ---
PHASE_D_LOG_NOLI = LOGS_LEXICAL / "phase_d_log_noli.csv"
PHASE_D_LOG_ELFILI = LOGS_LEXICAL / "phase_d_log_elfili.csv"
PHASE_D_SUMMARY_NOLI = LOGS_LEXICAL / "phase_d_summary_noli.md"
PHASE_D_SUMMARY_ELFILI = LOGS_LEXICAL / "phase_d_summary_elfili.md"

PHASE_D2_LOG_NOLI = LOGS_LEXICAL / "phase_d2_log_noli.csv"
PHASE_D2_LOG_ELFILI = LOGS_LEXICAL / "phase_d2_log_elfili.csv"
PHASE_D2_SUMMARY_NOLI = LOGS_LEXICAL / "phase_d2_summary_noli.md"
PHASE_D2_SUMMARY_ELFILI = LOGS_LEXICAL / "phase_d2_summary_elfili.md"

PHASE_D4_LOG_NOLI = LOGS_LEXICAL / "phase_d4_log_noli.csv"
PHASE_D4_LOG_ELFILI = LOGS_LEXICAL / "phase_d4_log_elfili.csv"
PHASE_D4_SUMMARY = LOGS_LEXICAL / "phase_d4_summary.md"

PHASE_D5_AUDIT_SUMMARY = LOGS_LEXICAL / "phase_d5_audit_summary.md"

PHASE_D6_LOG_NOLI = LOGS_LEXICAL / "phase_d6_log_noli.csv"
PHASE_D6_LOG_ELFILI = LOGS_LEXICAL / "phase_d6_log_elfili.csv"
PHASE_D6_SUMMARY = LOGS_LEXICAL / "phase_d6_summary.md"

RESIDUAL_C_AUDIT_SUMMARY = LOGS_LEXICAL / "residual_c_audit_summary.md"

PHASE_T_TITLE_LOG_NOLI = LOGS_TITLES / "phase_t_title_log_noli.csv"
PHASE_T_TITLE_LOG_ELFILI = LOGS_TITLES / "phase_t_title_log_elfili.csv"
PHASE_T_TITLE_SUMMARY_NOLI = LOGS_TITLES / "phase_t_title_summary_noli.md"
PHASE_T_TITLE_SUMMARY_ELFILI = LOGS_TITLES / "phase_t_title_summary_elfili.md"

PHASE_T2_TITLE_LOG_NOLI = LOGS_TITLES / "phase_t2_title_log_noli.csv"
PHASE_T2_TITLE_LOG_ELFILI = LOGS_TITLES / "phase_t2_title_log_elfili.csv"
PHASE_T2_TITLE_SUMMARY_NOLI = LOGS_TITLES / "phase_t2_title_summary_noli.md"
PHASE_T2_TITLE_SUMMARY_ELFILI = LOGS_TITLES / "phase_t2_title_summary_elfili.md"

PHASE_T3_NOLI_CORRECTION_SUMMARY = LOGS_TITLES / "phase_t3_noli_correction_summary.md"

VALIDATION_SUMMARY_NOLI = LOGS_LEXICAL / "validation_summary_noli.md"
VALIDATION_SUMMARY_SEG = LOGS_LEXICAL / "validation_summary_segmentation.md"
VALIDATION_SUMMARY_SEG_V2 = LOGS_LEXICAL / "validation_summary_segmentation_v2.md"
