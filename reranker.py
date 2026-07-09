from sentence_transformers import CrossEncoder

DEFAULT_MODEL = "BAAI/bge-reranker-v2-m3"
# Alternative multilingue de qualitÃ© production :
# DEFAULT_MODEL = "BAAI/bge-reranker-v2-m3"


class Reranker:
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
        if not candidates:
            return []
        pairs = [(query, c["text"]) for c in candidates]
        scores = self.model.predict(pairs)
        for c, s in zip(candidates, scores):
            c["rerank_score"] = float(s)
        return sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)[:top_k]

