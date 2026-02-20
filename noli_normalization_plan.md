# Noli Me Tangere — Text Normalization Plan for Antigravity

## Goal

Convert `noli_extraction.csv` into a clean, normalized CSV file named `noli_chapter_sentences_new.csv` with the following schema (matching the elfili reference):

```
book_title, chapter_number, chapter_title, sentence_number, sentence_text
```

---

## Step 1 — Restructure the CSV (Pre-processing, Before LLM Normalization)

This step is pure structural/scripted work. Do it in code before sending anything to an LLM.

### 1a. Map chapter_index to chapter_number

The source file uses `chapter_index` (0–39). Real chapters are numbered 1–39 based on the `chapter_number` text_type rows. The mapping is:

- `chapter_index = 0` → **SKIP** (front matter: dedications, table of contents, preface — not real chapters)
- `chapter_index = 1` → `chapter_number = 1`, title = `ISANG PAGCACAPISAN`
- `chapter_index = 2` → `chapter_number = 2`, title = `CRISOSTOMO IBARRA`
- ... (continues normally through index 38)
- `chapter_index = 39` → **SPLIT** (see 1b below — this index contains chapters 39–63+ due to a scraping bug)

### 1b. Re-split chapter_index 39 into real chapters

The HTML scraper collapsed all remaining chapters (39 through end, plus MGA TALABABA footnotes) into a single `chapter_index=39`. You must re-split using the `chapter_title` column, which **does** track the correct title changes:

| chapter_title in source | Assign chapter_number |
|---|---|
| ANG PROCESION. | 39 |
| SI DONA CONSOLACION. | 40 |
| ANG CATUWIRA'T ANG LACAS. | 41 |
| DALAWANG PANAUHIN. | 42 |
| ANG MAG-ASAWANG DE ESPADAÑA. | 43 |
| MGA PANUCALA. | 44 |
| PAGSISIYASAT NG CONCIENCIA. | 45 |
| ANG MGA PINAG-UUSIG. | 46 |
| SABUNGAN. | 47 |
| ANG DALAWANG GUINOONG BABAE. | 48 |
| ANG HINDI MAGCURO | 49 |
| ANG TINGIG NG MGA PINAG-UUSIG. | 50 |
| ANG MAG-ANAK NI ELIAS. | 51 |
| MGA PAGBABAGO. | 52 |
| ANG SULAT NG MGA PATAY AT ANG MGA ANINO. | 53 |
| IL BUON DI SI CONOSCE DA MATTINA. | 54 |
| ANG CAPAHAMACAN. | 55 (LIV+LV are the same chapter, LV = ANG CAPAHAMACAN) |
| ANG SABIHANAN AT ANG INAACALA. | 56 |
| ¡VAE VICTIS! | 57 |
| ANG SINUMPA. | 58 |
| ANG KINAGUISNANG BAYAN AT ANG MGA PAG-AARI. | 59 |
| MAG-AASAWA SI MARIA CLARA. | 60 |
| ANG PANGHUHULI SA DAGATAN. | 61 |
| PAGPAPALIWANAG NI PARI DAMASO. | 62 |
| ANG GABING SINUSUNDAN NG PASCO NG PANGANGANGANAC. | 63 |
| PANGWACAS NA BAHAGUI. | 64 |
| WACAS NG PAGSASAYSAY. | 65 |
| MGA TALABABA: | **SKIP** (footnotes, not a real chapter) |

> **Note:** Roman numeral rows (XL., XLI., etc.) are `text_type = chapter_number` rows — skip them, they are just chapter markers not content.

### 1c. Filter rows to keep

Only keep rows where `text_type = 'paragraph'`. Drop:
- `text_type = 'chapter_title'`
- `text_type = 'chapter_number'`
- `chapter_index = 0` (front matter)
- Any row whose `chapter_title = 'MGA TALABABA:'` (footnotes)

### 1d. Split paragraphs into sentences

Each row in the source is a paragraph (can contain multiple sentences). Split each paragraph into individual sentences to match the elfili output format. Use sentence boundary detection on Filipino/Spanish text:
- Split on `.`, `!`, `?`, `¡`, `¿` (but be careful with abbreviations like "Dr.", "Sr.", "P.H.P.")
- Each sentence gets its own row with an incrementing `sentence_number` (per chapter, restarting at 1)

### 1e. Set book_title

Set `book_title = "Noli Me Tangere"` for all rows.

---

## Step 2 — Text Normalization (LLM Task for Antigravity)

After restructuring, run each `sentence_text` value through the LLM normalizer. Below are all the transformations needed.

---

## Full Normalization Rules

### Rule 1 — C → K (Most Frequent Change)

The archaic Tagalog orthography uses `c` where modern Filipino uses `k`. Apply this **only to Tagalog/Filipino words**, not Spanish or Latin loanwords.

**Do NOT change `c` in:**
- Spanish proper nouns and words: `Clara`, `Cura`, `Capitan` (when referring to a title), `convento`, `cancer`, `civil`, `Castila`, `Victorina`, `alcalde`, `voces`
- Latin phrases: `Noli Me Tangere`, `Vae Victis`, `sic`, etc.
- Italian phrases: `Il Buon Di Si Conosce Da Mattina`
- Names: `Crisostomo`, `Consolacion`, `Clarita`

**DO change `c → k` in Tagalog words:**

| Archaic | Modern |
|---|---|
| canya, canyá, canyáng | kanya, kanyang |
| co, có | ko |
| acó, acóng | ako, akong |
| ca, cá | ka |
| cung | kung |
| cay | kay |
| cayó, cayóng, cayo | kayo, kayong |
| canilá, caniláng, canila, canilang | kanila, kanilang |
| pagca, pagcá | pagka |
| pagcatapos | pagkatapos |
| cahulugán, cahulug | kahulogan, kahulug |
| cahoy | kahoy |
| caibigan | kaibigan |
| calagayan | kalagayan |
| cailan | kailan |
| casama | kasama |
| dacong | daong / dakong |
| sacali | sakali |
| anác, anac | anak |
| camáy | kamay |
| caya | kaya |
| wicang, wicà, wica | wikang, wika |
| catagalugan | katagatugan |
| calayaan | kalayaan |
| catuwirang, catuwiran | katuwiran |
| catotohanan, catoto | katotohanan, katoto |
| canilag | kanilag |
| kinacailangan | kinakailangan |
| casamaan | kasamaan |
| cabulagan | kabulagan |
| capahamakan | kapahakaman |
| macapangyarihan | makapangyarihan |
| macaimic, maka-imic | maka-imik |
| nacapagpapalaman | nakapagpapalaman |
| nacamamatay | nakamamatay |
| caugalian | kaugalian |
| calolowa | kalolowa |
| casaysayan | kasaysayan |
| capitang (as Filipino word) | kapitang |
| carikitan | kariktan |
| cabria | kabria |
| layang-caisipan | layang-kaisipan |
| pagcain | pagkain |
| cakilakilabot | kakila-kilabot |

**Pattern rule:** For any other Tagalog word with `c` followed by `a`, `o`, `u`, `i`, `e` where it sounds like /k/, replace `c → k`.

---

### Rule 2 — Old NG Tilde (g̃) → Modern ng

The source text uses `g̃` (g with combining tilde) to represent `ng` in certain positions, and `mg̃` to represent `mga`. Replace:

| Archaic | Modern |
|---|---|
| `ng̃` | `ng` |
| `mg̃` | `mga` |
| `g̃` (standalone) | `ng` |

Examples:
- `mg̃a` → `mga`
- `ng̃` (in the middle of a word like `salang̃in`) → `sanlangin` (reconstruct the full word)
- `ng̃uni't` → `ngunit`

---

### Rule 3 — "MANGA" / "MANG̃A" → "MGA"

The archaic word for "mga" is sometimes spelled `manga`, `mang̃a`, or `mang̃`. Replace all with `mga`.

- `manga` → `mga` (when clearly used as a plural marker, not the fruit)
- `mang̃a` → `mga`

---

### Rule 4 — "huag" → "huwag"

| Archaic | Modern |
|---|---|
| `huag` | `huwag` |
| `HUAG` | `HUWAG` |

---

### Rule 5 — "wica" → "wika"

Already covered in Rule 1 (c → k), but make explicit:

| Archaic | Modern |
|---|---|
| `wicang` | `wikang` |
| `wicà` | `wika` |
| `wica` | `wika` |

---

### Rule 6 — "nang" vs "ng"

The source inconsistently uses `nang` where modern Filipino uses `ng` (as a ligature/linker). **This is one of the hardest rules** — defer to context:
- `nang` as a conjunction (temporal: "nang dumating siya") → keep as `nang`
- `nang` used as a linker/marker → `ng`

> **For Antigravity:** Use context to determine correct usage. When uncertain, keep `nang` as-is to avoid incorrect changes.

---

### Rule 7 — Remove Accent Marks

The reference elfili CSV has **zero accent marks**. Remove all diacritics from Tagalog words:

| Remove | Examples |
|---|---|
| Acute accents | `á → a`, `é → e`, `í → i`, `ó → o`, `ú → u` |
| Grave accents | `à → a`, `è → e`, `ì → i`, `ò → o`, `ù → u` |

**Do NOT remove accents from:**
- Spanish loanwords that are conventionally accented in Filipino writing (use judgment): `Señor`, `José`
- Keep proper nouns as culturally appropriate

> **Simpler rule for Antigravity:** Strip ALL accent marks from all text uniformly. This matches the elfili reference approach (0 accented characters in elfili output).

---

### Rule 8 — Normalize Chapter Titles

Apply the same C→K, g̃→ng, MANGA→MGA rules to chapter titles too:

| Original Title | Normalized Title |
|---|---|
| HUAG ACONG SALANG̃IN NINO MAN | HUWAG AKONG SALANGIN NINO MAN |
| ISANG PAGCACAPISAN | ISANG PAGKAKAPIS AN |
| CRISOSTOMO IBARRA | CRISOSTOMO IBARRA (proper name — keep) |
| MANGA ALAALA | MGA ALAALA |
| MANGA CAUGALIAN NG BAYANG ITO | MGA KAUGALIAN NG BAYANG ITO |
| ANG MANG̃A MACAPANGYARIHAN | ANG MGA MAKAPANGYARIHAN |
| MANG̃A SULAT | MGA SULAT |
| CASAYSAYAN NANG BUHAY NANG ISANG INA | KASAYSAYAN NG BUHAY NG ISANG INA |
| MGA CALOLOWANG NAGHIHIRAP | MGA KALOLOWANG NAGHIHIRAP |
| MGA KINASAPITAN NG ISANG MAESTRO SA ESCUELA | MGA KINASAPITAN NG ISANG MAESTRO SA ESCUELA |
| LAYANG-CAISIPAN | LAYANG-KAISIPAN |
| ANG PAGCAIN | ANG PAGKAIN |
| MGA SALISALITAAN | MGA SALISALITAAN |
| PANGWACAS NA BAHAGUI | PANGWAKAS NA BAHAGI |
| WACAS ÑG PAGSASAYSAY | WAKAS NG PAGSASAYSAY |
| ANG CATUWIRA'T ANG LACAS | ANG KATUWIRAN AT ANG LAKAS |
| ANG CAPAHAMACAN | ANG KAPAHAKAMAN |

---

### Rule 9 — Normalize "wacas" → "wakas" and similar

Other common archaic spellings:

| Archaic | Modern |
|---|---|
| `wacas` | `wakas` |
| `bahagui` | `bahagi` |
| `capahamacan` | `kapahakaman` |
| `lacas` | `lakas` |
| `curo` | `kuro` |
| `icáw`, `icaw` | `ikaw` |
| `doon` | `doon` (keep) |
| `iyon` | `iyon` (keep) |
| `niyón` | `niyon` |

---

### Rule 10 — Spanish/Foreign Words — Keep As-Is

Do NOT normalize these types of words:
- Proper names: `Ibarra`, `Clara`, `Damaso`, `Elias`, `Maria`, `Jose`, `Rizal`, `Victorina`, `Consolacion`
- Spanish words retained in text: `convento`, `alcalde`, `fiesta`, `vispera`, `azotea`, `filosofo`, `maestro`, `escuela`, `sermon`, `gobernador`, `procesion`, `filibustero`, `civilizacion`
- Latin: `Noli Me Tangere`, `Vae Victis`, `Sic`, `cancer`
- Italian: `Il Buon Di Si Conosce Da Mattina`

---

## Antigravity Prompt

Below is the prompt to use for each `sentence_text` row. Send one sentence at a time (or batch in groups of 10–20 for efficiency).

---

```
You are a Filipino language expert specializing in modernizing 19th-century Tagalog orthography from José Rizal's era into standard modern Filipino spelling.

I will give you a sentence from the Tagalog translation of "Noli Me Tangere" (circa 1909 by Pascual H. Poblete). Your task is to normalize the spelling to modern Filipino while preserving the exact meaning, word order, and style.

Apply these rules IN ORDER:

1. REMOVE ALL ACCENT MARKS (á→a, é→e, í→i, ó→o, ú→u, à→a, è→e, ì→i, ò→o, ù→u). Remove them from every word uniformly.

2. REPLACE G-TILDE: Replace all instances of "g̃" with "ng", and "mg̃" with "mga". Examples: "ng̃" → "ng", "mg̃a" → "mga", "salang̃in" → "salangin".

3. REPLACE "manga" / "mang̃a": When used as a plural marker (equivalent to "mga"), replace with "mga". Do NOT change "mangga" (the fruit).

4. C → K IN TAGALOG WORDS: Replace "c" with "k" in native Tagalog words where it represents the /k/ sound. Common examples:
   - canya/canyáng → kanya/kanyang
   - co → ko | acó → ako | ca → ka | cung → kung
   - cay → kay | cayó → kayo | canilá → kanila
   - pagca → pagka | anac → anak | cahoy → kahoy
   - caibigan → kaibigan | wica/wicang → wika/wikang
   - casaysayan → kasaysayan | catotohanan → katotohanan
   - calayaan → kalayaan | calagayan → kalagayan
   - dacong → dakong | sacali → sakali
   - icaw → ikaw | nacamamatay → nakamamatay
   - kinacailangan → kinakailangan | capahamacan → kapahakaman
   - caugalian → kaugalian | calolowa → kalolowa
   - macapangyarihan → makapangyarihan
   DO NOT change "c" in Spanish/Latin words or proper names: Clara, Cura, Capitan (as name), convento, cancer, civil, Crisostomo, Consolacion, alcalde, etc.

5. REPLACE "huag" → "huwag" (and "HUAG" → "HUWAG").

6. REPLACE "wacas" → "wakas", "bahagui" → "bahagi", "lacas" → "lakas".

7. NORMALIZE "nang" vs "ng": Use "nang" only as a temporal conjunction ("nang dumating"). Use "ng" as a linker/marker. When uncertain, keep "nang" unchanged.

8. DO NOT change: proper names, Spanish words kept in the text (convento, azotea, fiesta, alcalde, gobernador, filosofo, etc.), Latin/Italian phrases.

9. OUTPUT: Return ONLY the normalized sentence. No explanations, no quotation marks, no extra text. Just the normalized sentence as plain text.

Input sentence: {sentence_text}
```

---

## Step 3 — Output CSV Assembly

After normalization, assemble the final CSV with these exact columns:

```
book_title,chapter_number,chapter_title,sentence_number,sentence_text
```

Rules:
- `book_title` = `Noli Me Tangere` (consistent capitalization, no accents)
- `chapter_number` = integer (1–65, excluding front matter and footnotes)
- `chapter_title` = normalized chapter title (apply same rules as sentence_text to titles)
- `sentence_number` = resets to 1 at each new chapter
- `sentence_text` = the LLM-normalized sentence

**Encoding:** UTF-8, no BOM. Use standard CSV quoting (quote fields that contain commas or newlines).

---

## Summary Checklist for Antigravity

| Step | Task | Method |
|---|---|---|
| 1 | Filter: keep only `text_type=paragraph` rows | Script |
| 2 | Skip chapter_index=0 (front matter) and MGA TALABABA | Script |
| 3 | Re-split chapter_index=39 into chapters 39–65 using chapter_title changes | Script |
| 4 | Split paragraphs into individual sentences | Script (NLP sentence splitter) |
| 5 | Send each sentence to LLM with the prompt above | LLM (Antigravity) |
| 6 | Apply same normalization to chapter titles | LLM or script |
| 7 | Assemble final CSV with correct column schema | Script |
| 8 | Validate: check no g̃ remains, no accent chars remain, no "manga " remains as plural | Script QA |

---

## QA Validation Script Logic

After generating the output, run these checks:

```python
import csv, re

with open('noli_chapter_sentences_new.csv') as f:
    rows = list(csv.DictReader(f))

errors = []
for i, r in enumerate(rows):
    t = r['sentence_text']
    # Check for leftover archaic patterns
    if 'g̃' in t: errors.append(f"Row {i}: g̃ found")
    if re.search(r'[áéíóúàèìòùÁÉÍÓÚ]', t): errors.append(f"Row {i}: accent found")
    if re.search(r'\bmanga\b', t, re.I): errors.append(f"Row {i}: 'manga' as plural")
    if re.search(r'\bhuag\b', t, re.I): errors.append(f"Row {i}: 'huag' not normalized")
    if re.search(r'\bcanya\b|\bcung\b|\bcó\b|\bacó\b', t): errors.append(f"Row {i}: archaic c-word found")
    if re.search(r'\bwica\b', t, re.I): errors.append(f"Row {i}: 'wica' not normalized")

print(f"Total errors: {len(errors)}")
for e in errors[:20]:
    print(e)
```

---

*Reference: elfili_chapter_sentences_FINAL_v3.csv was used as the target format. It has 0 accent marks, 0 g̃ characters, uses modern Filipino orthography throughout, and follows the schema: book_title, chapter_number, chapter_title, sentence_number, sentence_text.*