"""
Jalon 3 — Recherche seule.

Avant de brancher le LLM, on valide que le bon article remonte bien
dans le top-k pour un jeu de questions connues (voir tests/test_retrieval.py).
"""
import chromadb
from sentence_transformers import SentenceTransformer

from config import DB_DIR, EMBEDDING_MODEL_NAME, COLLECTION_NAME, TOP_K
from indexation import verifier_coherence_modele

_modele = None
_collection = None


def _get_modele() -> SentenceTransformer:
    global _modele
    if _modele is None:
        _modele = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _modele


def _get_collection():
    global _collection
    if _collection is None:
        verifier_coherence_modele()
        client = chromadb.PersistentClient(path=str(DB_DIR))
        _collection = client.get_collection(name=COLLECTION_NAME)
    return _collection


def search(question: str, k: int = TOP_K) -> list[dict]:
    """
    Retourne les k chunks les plus pertinents pour une question.

    Chaque résultat : {"texte": ..., "num_article": ..., "theme": ...,
    "source": ..., "score": ...}
    Le score retourné est une similarité (1 - distance), plus il est
    proche de 1, plus le chunk est pertinent.
    """
    modele = _get_modele()
    collection = _get_collection()

    embedding_question = modele.encode([question]).tolist()

    resultats = collection.query(
        query_embeddings=embedding_question,
        n_results=k,
    )

    chunks = []
    for i in range(len(resultats["ids"][0])):
        distance = resultats["distances"][0][i]
        chunks.append(
            {
                "texte": resultats["documents"][0][i],
                "num_article": resultats["metadatas"][0][i]["num_article"],
                "theme": resultats["metadatas"][0][i]["theme"],
                "source": resultats["metadatas"][0][i]["source"],
                "score": 1 - distance,  # similarité approx. (dépend de la métrique Chroma)
            }
        )
    return chunks


if __name__ == "__main__":
    # Petit test manuel rapide
    question = "Combien de jours de congés payés par an ?"
    for chunk in search(question, k=3):
        print(f"[{chunk['score']:.3f}] {chunk['num_article']} - {chunk['texte'][:80]}...")
