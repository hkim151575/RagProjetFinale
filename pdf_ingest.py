import argparse
import json
import csv
import re
from pathlib import Path

from pypdf import PdfReader

# Majuscule obligatoire : ne matche que les en-têtes « Article L.XXXX-X »,
# pas les renvois internes du type « ...prévue à l'article L.1234-9 ».
ARTICLE_PATTERN = re.compile(r"Article\s+(L\.\d{4}-\d+)")


def extract_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    print(f"[pdf] {len(pages)} pages extraites de {pdf_path}")
    return "\n".join(pages)


def chunk_par_article(text: str, source: str) -> list[dict]:
    """1 article de loi = 1 chunk ; la référence part en métadonnée."""
    matches = list(ARTICLE_PATTERN.finditer(text))
    chunks = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        ref = m.group(1)
        body = text[m.end():end].strip().replace("\n", " ")
        body = re.sub(r"\s+", " ", body)
        # On garde la référence DANS le texte : c'est elle que BM25 doit trouver
        chunks.append({
            "text": f"Article {ref} — {body}",
            "source": source,
            "type": "article_de_loi",
            "reference": ref,
        })
    return chunks


def chunk_par_taille(text: str, source: str, taille: int = 800,
                     recouvrement: int = 150) -> list[dict]:
    """Fenêtre glissante avec recouvrement, coupée de préférence sur une phrase."""
    text = re.sub(r"\s+", " ", text).strip()
    chunks, start = [], 0
    while start < len(text):
        end = min(start + taille, len(text))
        # Reculer jusqu'à la fin de phrase la plus proche si possible
        cut = text.rfind(". ", start, end)
        if cut > start + taille // 2:
            end = cut + 1
        chunks.append({
            "text": text[start:end].strip(),
            "source": source,
            "type": "extrait_pdf",
            "reference": "",
        })
        start = end - recouvrement if end < len(text) else end
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", help="Chemin du PDF à ingérer")
    parser.add_argument("--sortie", default="data/corpus.csv")
    parser.add_argument("--strategie", choices=["auto", "article", "taille"],
                        default="auto")
    args = parser.parse_args()

    text = extract_text(args.pdf)
    source = Path(args.pdf).name

    strategie = args.strategie
    if strategie == "auto":
        strategie = "article" if len(ARTICLE_PATTERN.findall(text)) >= 5 else "taille"
        print(f"[pdf] stratégie détectée : {strategie}")

    chunks = (chunk_par_article if strategie == "article" else chunk_par_taille)(text, source)

    if Path(args.sortie).suffix.lower() == ".json":
        payload = [
            {"id": f"chunk_{i}", "text": c["text"],
             "metadata": {k: v for k, v in c.items() if k != "text" and v}}
            for i, c in enumerate(chunks)
        ]
        with open(args.sortie, "w", encoding="utf-8") as f:
            json.dump({"corpus": Path(args.pdf).name, "chunks": payload},
                      f, ensure_ascii=False, indent=2)
    else:
        with open(args.sortie, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["text", "source", "type", "reference"])
            writer.writeheader()
            writer.writerows(chunks)

    print(f"[pdf] {len(chunks)} chunks écrits dans {args.sortie}")
    print(f"      exemple : {chunks[0]['text'][:90]}...")


if __name__ == "__main__":
    main()
