
# Validation Summary: El Filibusterismo Sentence Segmentation (Corrected)

**Input**: `elfili_extraction_normalized.csv` (2,456 rows)
**Output**: `elfili_chapter_sentences.csv`

## Statistics
- **Total Chapters**: 39 (Sequential 1-39)
- **Total Rows (Sentences)**: 5,572
- **Removed**: 'ALAALA' section (Front matter)

## Chapter Metadata Verification

| Chapter | Title Found | Expected | Status |
| :--- | :--- | :--- | :--- |
| **1** | `Sa Ibabaw ng Kubyerta` | `Sa Ibabaw ng Kubyerta` | ✅ Correct |
| **2** | `Sa Ilalim ng Kubyerta` | `Sa Ilalim ng Kubyerta` | ✅ Correct |
| **39** | `XXXIX KATAPUSAN` | `XXXIX KATAPUSAN` | ✅ Correct |

## Content Checks

### Chapter 1 start (After removing ALAALA)
1. `Sic itur ad astra.`
2. `Isang umaga ng Disiembre ay hirap na sumasalunga sa palikolikong linalakaran ng ilog Pasig ang bapor Tabo, na may lulang maraming tao, na tungo sa Lalaguna.`
3. `Ang bapor ay may anyong bagol, halos bilog na wari’y tabo na siyang pinanggalingan ng kaniyang pangalan; napakarumi kahit na may nasa siyang maging maputi, malumanay at waring nagmamalaki dahil sa kaniyang banayad na lakad.`

### Chapter 39 End (Final sentences of the novel)
1. `—Kapag sa isang banal at mataas na layon ay kakailanganin ka ng mga tao, ay matututuhan kang kunin ng Dios sa sinapupunan ng mga alon....`
2. `Samantala, diyan ay hindi ka makagagawa ng kasamaan, hindi mo ililiko ang katwiran, hindi ka mag-uudyok sa kasakiman!....`
3. `Wakas ng “Ang Filibusterismo”.`
