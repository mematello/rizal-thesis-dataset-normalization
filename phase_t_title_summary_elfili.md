# Phase T: El Filibusterismo Title Normalization Summary

**Dataset**: `elfili_chapter_sentences_titles_fixed.csv`
**Total Unique Titles**: 39
**Normalized Count**: 39 (Formatted/Cleaned)

## Key Changes
- **Roman Numeral Removal**:
  - `III`, `IV`, `V`... `XXXIX` stripped from the start of titles.
  - Example: `III MGA ALAMAT` -> `MGA ALAMAT`

- **Formatting**:
  - `MANgA` -> `MGA`
  - `Ng` -> `NG`
  - `PANgARAP` -> `PANGARAP`
  - `IBINUNgA` -> `IBINUNGA`

- **Archaic -> Modern**:
  - `PANgARAP` -> `PANGARAP` (Formatting/Modernization)
  - `MGA` (Standardized from `MANgA`)

- **Preserved Foreign Titles**:
  - `LOS BAÑOS` (Preserved, Numeral stripped: `XI LOS BAÑOS` -> `LOS BAÑOS`)
