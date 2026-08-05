
# Validation Summary: Noli Me Tangere

## 1. Extraction (HTML to CSV)
- **Source**: `Noli Me Tangere | Project Gutenberg.html`
- **Output**: `noli_extraction.csv`
- **Rows Extracted**: 4528
- **Narrative Paragraphs**: 4393
- **Front Matter Dropped**: Page numbers (`span.pagenum`) explicitly removed to preserve word integrity (e.g., `sasaysayin`). License/Boilerplate excluded.

## 2. Orthographic Normalization
- **Output**: `noli_extraction_normalized.csv`
- **Methods**: NFC, Archaic G-tilde (g̃ -> g), ñg -> ng, Diacritic Stripping (Protect-Strip-Restore ñ).
- **Changes**:
  - G-tilde fixed: 24,303
  - Diacritics removed: 45,897
  - Ñ protected/restored: 312
- **Validation**:
  - Remaining G-tilde: 0
  - Remaining Combining Marks (Mn): 0
  - Preserved Ñ count: 312

## 3. Sentence Segmentation & Metadata
- **Output**: `noli_chapter_sentences.csv`
- **Total Valid Chapters**: 63
- **Total Sentences**: 8,833
- **Structure**:
  - **Start**: Chapter 1 starts at "ISANG PAGCACAPISAN." (Front matter "NOLI ME TANGERE", "TALAAN...", "SA AKING..." dropped).
  - **End**: Narrative ends at Chapter 63 ("PANGWACAS NA BAHAGUI"). Footnotes ("MGA TALABABA") excluded.
  - **Numbering**: Sequential 1-63. Roman numeral headers merged with titles.

### Sample Verification

**Chapter 1: ISANG PAGCACAPISAN.**
> 1: Nag-anyaya ng pagpapacain nang isang hapunan, ng magtatapos ang Octubre, si Guinoong Santiago de los Santos, na lalong nakikilala ng bayan sa pamagat na Capitang Tiago, anyayang baga man niyon lamang hapong iyon canyang inihayag, laban sa dati niyang caugalian, gayon ma'y siyang dahil na ng lahat ng mga usap-usapan sa Binundoc, sa iba't ibang mga nayon at hanggang sa loob ng Maynila.
> 2: Ng panahong yao'y lumalagay si Capitang Tiagong isang lalaking siyang lalong maguilas, at talastas ng ang canyang bahay at ang canyang kinamulatang bayan ay hindi nagsasara ng pinto canino man, liban na lamang sa mga calacal o sa ano mang isip na bago o pangahas.
> 3: Cawangis ng kislap ng lintic ang cadalian ng pagcalaganap ng balita sa daigdigan ng mga dapo, mga langaw o mga "colado", na kinapal ng Dios sa canyang walang hanggang cabaitan, at canyang pinararami ng boong pag-irog sa Maynila.

**Final Chapter (63): PANGWACAS NA BAHAGUI.**
> ...
> 84: ng canyang mabalitaan ang nangyaring iyon; tinangca niyang tangkilikin ang ulol na babae caya't hiningi niya ito.
> 85: Ngunit ngayo'y walang humarap na sino mang dalagang cagandagandahang walang umampon, at hindi itinulot ng abadesang dalawin at tingnan ang convento, at sa ganito'y tumutol siya sa pangalan ng Religion at ng mga Santong Cautusan sa Convento.
> 86: Hindi na muling napagsalitaanan pa ang nangyaring iyon, at gayon din ang tungcol sa cahabaghabag na si Maria Clara.
