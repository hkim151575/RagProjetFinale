import re

from rank_bm25 import BM25Okapi

from corpus_loader import Chunk


def tokenize(text: str) -> list[str]:
    """Tokenisation simple, robuste aux identifiants type 'L.1235-3'."""
    return re.findall(r"[a-zà-ÿ0-9][a-zà-ÿ0-9.\-]*", text.lower())


class LexicalStore:
    def __init__(self):
        self.chunks: list[Chunk] = []
        self.bm25: BM25Okapi | None = None

    def index(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        self.bm25 = BM25Okapi([tokenize(c.text) for c in chunks])
        print(f"[bm25] {len(chunks)} chunks indexés (lexical)")

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        if self.bm25 is None:
            raise RuntimeError("Index BM25 non construit : appelez index() d'abord.")
        scores = self.bm25.get_scores(tokenize(query))
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [
            {
                "id": self.chunks[i].id,
                "text": self.chunks[i].text,
                "score": float(scores[i]),
                "metadata": self.chunks[i].metadata,
            }
            for i in ranked
            if scores[i] > 0
        ]
