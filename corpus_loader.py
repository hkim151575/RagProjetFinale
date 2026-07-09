import json
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)


def load_corpus(path: str, text_column: str | None = None) -> list[Chunk]:
    """Charge un corpus CSV ou JSON et renvoie une liste de Chunk."""
    if Path(path).suffix.lower() == ".json":
        return _load_json(path)
    return _load_csv(path, text_column)


def _load_json(json_path: str) -> list[Chunk]:
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    items = data["chunks"] if isinstance(data, dict) and "chunks" in data else data

    chunks: list[Chunk] = []
    for i, item in enumerate(items):
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        metadata = item.get("metadata") or {
            k: str(v) for k, v in item.items() if k not in ("id", "text") and v
        }
        chunks.append(Chunk(id=item.get("id", f"chunk_{i}"), text=text,
                            metadata=metadata))
    print(f"[corpus] {len(chunks)} chunks chargés depuis {json_path}")
    return chunks


def _load_csv(csv_path: str, text_column: str | None = None) -> list[Chunk]:
    df = pd.read_csv(csv_path)

    # Détection automatique de la colonne de texte si non précisée
    if text_column is None:
        for candidate in ("text", "chunk", "content", "contenu", "texte"):
            if candidate in df.columns:
                text_column = candidate
                break
        else:
            raise ValueError(
                f"Colonne de texte introuvable. Colonnes disponibles : {list(df.columns)}. "
                "Précisez text_column=..."
            )

    chunks: list[Chunk] = []
    for i, row in df.iterrows():
        text = str(row[text_column]).strip()
        if not text or text.lower() == "nan":
            continue
        metadata = {
            col: str(row[col])
            for col in df.columns
            if col != text_column and pd.notna(row[col])
        }
        chunks.append(Chunk(id=f"chunk_{i}", text=text, metadata=metadata))

    print(f"[corpus] {len(chunks)} chunks chargés depuis {csv_path}")
    return chunks
