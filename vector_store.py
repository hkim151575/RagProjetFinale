import chromadb
from sentence_transformers import SentenceTransformer

from corpus_loader import Chunk

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class VectorStore:
    def __init__(self, collection_name: str = "rag_avance", persist_dir: str = "./chroma_db"):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def index(self, chunks: list[Chunk], batch_size: int = 64) -> None:
        """Indexe les chunks (idempotent : upsert)."""
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            embeddings = self.model.encode(
                [c.text for c in batch], show_progress_bar=False
            ).tolist()
            self.collection.upsert(
                ids=[c.id for c in batch],
                documents=[c.text for c in batch],
                embeddings=embeddings,
                metadatas=[c.metadata or {"_": "none"} for c in batch],
            )
        print(f"[vector] {len(chunks)} chunks indexés (dense)")

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """Renvoie [{id, text, score, metadata}], score = similarité (1 - distance)."""
        embedding = self.model.encode([query]).tolist()
        res = self.collection.query(query_embeddings=embedding, n_results=top_k)
        results = []
        for id_, doc, dist, meta in zip(
            res["ids"][0], res["documents"][0], res["distances"][0], res["metadatas"][0]
        ):
            results.append(
                {"id": id_, "text": doc, "score": 1.0 - dist, "metadata": meta}
            )
        return results
