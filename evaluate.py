import sys
import time

from corpus_loader import load_corpus
from hybrid_retriever import HybridRetriever
from lexical_store import LexicalStore
from reranker import Reranker
from vector_store import VectorStore


def show(name: str, results: list[dict], elapsed: float, n: int = 3) -> None:
    print(f"\n--- {name} ({elapsed * 1000:.0f} ms) ---")
    for r in results[:n]:
        extrait = r["text"][:110].replace("\n", " ")
        score = r.get("rerank_score", r.get("score", 0.0))
        print(f"  [{r['id']}] score={score:.3f}  {extrait}...")


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    csv_path, questions = sys.argv[1], sys.argv[2:]

    chunks = load_corpus(csv_path)
    vector = VectorStore()
    vector.index(chunks)
    lexical = LexicalStore()
    lexical.index(chunks)
    hybrid = HybridRetriever(vector, lexical)
    reranker = Reranker()

    for question in questions:
        print("\n" + "=" * 70)
        print(f"QUESTION : {question}")
        print("=" * 70)

        t = time.perf_counter()
        show("1. Dense seul (baseline du cours)", vector.search(question, 5),
             time.perf_counter() - t)

        t = time.perf_counter()
        show("2. BM25 seul", lexical.search(question, 5), time.perf_counter() - t)

        t = time.perf_counter()
        show("3. Hybride (RRF)", hybrid.search(question, 5), time.perf_counter() - t)

        t = time.perf_counter()
        candidates = hybrid.search(question, top_k=20)
        reranked = reranker.rerank(question, candidates, top_k=5)
        show("4. Hybride + reranker", reranked, time.perf_counter() - t)


if __name__ == "__main__":
    main()
