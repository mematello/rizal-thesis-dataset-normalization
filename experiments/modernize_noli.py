import csv
import time
import os
from typing import Optional

from openai import OpenAI
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paths import NOLI_FINAL_V2, NOLI_MODERN_CSV



# Configuration
INPUT_CSV = NOLI_FINAL_V2
OUTPUT_CSV = NOLI_MODERN_CSV
TEXT_COLUMN = "sentence_text"            # existing column from your CSV
OUTPUT_COLUMN = "sentence_text_modern"   # new column to add

# You can either set OPENAI_API_KEY in your environment, or put it here.
API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY") or "YOUR_OPENAI_API_KEY_HERE"


SYSTEM_PROMPT = """Ikaw ay tagasalin na nagmo-modernize ng lumang/arkais na Tagalog tungo sa makabagong Filipino (Tagalog).

Mga panuntunan:
- Panatilihin ang orihinal na kahulugan at tono ng pangungusap.
- Panatilihin ang mga pangalan ng tao, lugar, pamagat ng akda, at iba pang terminong makasaysayan (huwag isalin o baguhin ang mga ito).
- Panatilihin hangga't maaari ang bantas at pangkalahatang istruktura, maliban na lamang kung kailangan baguhin para luminaw ang pangungusap.
- Huwag kang magpaliwanag, magdagdag ng paliwanag, o magkomento. Ibalik lamang ang binagong pangungusap.

Sa pagmo-modernize:
- Palitan ang mga lumang ispeling at salitang bihira nang gamitin ng karaniwang gamit ngayon.
- Gamitin ang modernong baybay (Filipino orthography).

Gabay na halimbawang arkais → modernong anyo:
- yao'y, yaon, yao't, iyan, yaon doon → iyon / nandoon / noon (ayon sa konteksto)
- niyaon → noon / ng panahong iyon
- manga → mga
- man~ga → mga
- macapag-, macapan-, maca-, maguiguing, maguiguin → makapag-, makapan-, maka-, magiging
- siya'y, siya'y, siya'y → siya'y / siya ay (piliin ang mas natural sa pangungusap)
- gayon ma'y, gayon ma'y → gayunman / kahit ganoon
- cang, caniya, caniyang → kang, kaniya, kaniyang
- cailan, cailan man → kailan, kailanman
- cahit → kahit
- cay, caya → kay, kaya
- diyan, riya, ria → diyan / riyan / ilog (gamitin ang pinakaangkop)
- sa canya → sa kaniya
- hindi nacacaparis → hindi mapapantayan
- anoman, saan man, sino man → anuman, saanman, sinuman

Kapag may alinlangan, piliin ang pinakakaraniwang anyo sa makabagong Filipino, basta hindi nababago ang kahulugan.
"""


def get_client() -> OpenAI:
    if not API_KEY or API_KEY == "YOUR_OPENAI_API_KEY_HERE":
        raise RuntimeError(
            "OpenAI API key is not set. "
            "Set the OPENAI_API_KEY environment variable or edit API_KEY in this script."
        )
    return OpenAI(api_key=API_KEY)


def modernize_sentence(client: OpenAI, text: str) -> str:
    """Call the model to modernize one sentence."""
    if not text or not text.strip():
        return ""

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="gpt-4.1",  # or "gpt-4.1-mini" if you want it cheaper/faster
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            "Isulat sa makabagong Filipino (Tagalog) ang sumusunod na pangungusap. "
                            "Ibalik lamang ang modernisadong bersiyon, walang paliwanag o dagdag na teksto.\n\n"
                            f"{text}"
                        ),
                    },
                ],
                temperature=0.2,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            print(f"[warning] Error on attempt {attempt + 1} for text: {e}")
            time.sleep(2)

    # If all retries fail, fall back to the original text so the CSV stays aligned.
    return text


def main() -> None:
    client = get_client()

    with open(INPUT_CSV, newline="", encoding="utf-8") as f_in, open(
        OUTPUT_CSV, "w", newline="", encoding="utf-8"
    ) as f_out:
        reader = csv.DictReader(f_in)
        if TEXT_COLUMN not in reader.fieldnames:
            raise KeyError(
                f"TEXT_COLUMN '{TEXT_COLUMN}' not found in CSV headers: {reader.fieldnames}"
            )

        fieldnames = list(reader.fieldnames)
        if OUTPUT_COLUMN not in fieldnames:
            fieldnames.append(OUTPUT_COLUMN)

        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for i, row in enumerate(reader, start=1):
            original = row.get(TEXT_COLUMN, "") or ""
            row[OUTPUT_COLUMN] = modernize_sentence(client, original)
            writer.writerow(row)

            if i % 100 == 0:
                print(f"Processed {i} rows...")

    print(f"Done. Modernized CSV written to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()

