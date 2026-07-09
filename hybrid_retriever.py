from lexical_store import LexicalStore
from vector_store import VectorStore

RRF_K = 60


def reciprocal_rank_fusion(rankings: list[list[dict]], k: int = RRF_K) -> list[dict]:
    """Fusionne plusieurs listes de résultats classés en une seule, par RRF."""
    scores: dict[str, float] = {}
    docs: dict[str, dict] = {}
    for ranking in rankings:
        for rank, doc in enumerate(ranking):
            scores[doc["id"]] = scores.get(doc["id"], 0.0) + 1.0 / (k + rank + 1)
            docs[doc["id"]] = doc
    fused = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    return [{**docs[doc_id], "score": rrf_score} for doc_id, rrf_score in fused]


class HybridRetriever:
    """Recherche dense + lexicale en parallèle, fusion RRF, top-k final."""

    def __init__(self, vector_store: VectorStore, lexical_store: LexicalStore):
        self.vector = vector_store
        self.lexical = lexical_store

    def search(self, query: str, top_k: int = 10, candidates_per_index: int = 20) -> list[dict]:
        dense = self.vector.search(query, top_k=candidates_per_index)
        sparse = self.lexical.search(query, top_k=candidates_per_index)
        return reciprocal_rank_fusion([dense, sparse])[:top_k]
