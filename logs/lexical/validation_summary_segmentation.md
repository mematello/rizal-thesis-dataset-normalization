
# Validation Summary: El Filibusterismo Sentence Segmentation

**Input**: `elfili_extraction_normalized.csv` (2,456 rows)
**Output**: `elfili_chapter_sentences.csv`

## Statistics
- **Total Chapters**: 40
- **Total Sentences**: 5,577
- **Average Sentences per Chapter**: 139.4

## Sample Verification

### Chapter 1 (ALAALA) - First 5 Sentences
1. `sa mga paring G. Mariano GOMEZ (85 taon) Jose BURGOS (30 taon) at Jacinto ZAMORA (35 taon) na binitay sa Bagumbayan ng ika 28[A] ng Febrero ng taong 1872.`
2. `Sa di pagsang-ayon ng Relihion na alisan kayo ng karangalan sa pagkapari ay inilagay sa alinlangan ang kasalanang ibinintang sa inyo; sa pagbabalot ng hiwaga’t kadiliman sa inyong usap ng Pamahalaan ay nagpakilala ng isang pagkakamaling nagawa sa isang masamang sandali, at ang boong Pilipinas, sa paggalang sa inyong alaala at pagtawag na kayo’y mga PINAGPALA, ay hindi kinikilalang lubos ang inyong pagkakasala.`
3. `Samantala ngang hindi naipakikilalang maliwanag ang inyong pagkakalahok sa kaguluhan, naging bayani kayo o di man, nagkaroon o di man kayo ng hilig sa pagtatanggol ng katwiran, nagkaroon ng hilig sa kalayaan, ay may karapatan akong ihandog sa inyo, na bilang ginahis ng kasamaang ibig kong bakahin, ang aking gawa.`
4. `At samantalang inaantay namin na kilalanin sa balang araw ng España ang inyong kabutihan at hindi makipanagot sa pagkakapatay sa inyo, ay maging putong na dahong tuyo na lamang ng inyong mga liblib na libingan ang mga dahong ito ng aklat, at lahat niyong walang katunayang maliwanag na umupasala sa inyong alaala, ay mabahiran nawa ng inyong dugo ang kanilang mga kamay.`
5. `J. Rizal.`

> **Observation**: Abbreviations like `G.` (Ginoo) were correctly protected from splitting.

### Final Chapter (WAKAS) - Last 5 Sentences
1. `—¡Itago ka ng Kalikasan sa kailaliman na kasama ng mga korales at mga perlas ng kaniyang walang pagkapawing mga dagat!`
2. `—ang sabi ng klerigo na iniunat ang kamay.`
3. `—Kapag sa isang banal at mataas na layon ay kakailanganin ka ng mga tao, ay matututuhan kang kunin ng Dios sa sinapupunan ng mga alon....`
4. `Samantala, diyan ay hindi ka makagagawa ng kasamaan, hindi mo ililiko ang katwiran, hindi ka mag-uudyok sa kasakiman!....`
5. `Wakas ng “Ang Filibusterismo”.`

> **Observation**: Dialogue markers and punctuation (¡, ...) were handled correctly.

## Integrity Checks
- **Paragraphs Processed**: All narrative paragraphs from the normalized source were included.
- **Normalization**: Text remains NFC, no combining marks.
- **Segmentation**: Splits occur only on valid sentence terminators (. ! ?), excluding known abbreviations.
