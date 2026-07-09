"""test_rapide.py - Verifie l'installation et le retrieval SANS cle API."""
import sys

OK, KO = "  [OK]", "  [ECHEC]"

Q_DENSE   = "combien de jours de cong\u00e9s par mois de travail ?"
Q_HYBRIDE = "indemnit\u00e9 pr\u00e9vue par L.1235-3 en cas de licenciement injustifi\u00e9"
Q_RERANK  = "dur\u00e9e l\u00e9gale hebdomadaire de travail \u00e0 temps complet"

def main():
    erreurs = 0

    print("1. Chargement du corpus...")
    from corpus_loader import load_corpus
    chunks = load_corpus("data/corpus.json")
    print(OK if len(chunks) == 49 else KO, f"{len(chunks)} chunks (attendu : 49)")
    erreurs += len(chunks) != 49

    print("\n2. Indexation dense (ChromaDB + sentence-transformers)...")
    from vector_store import VectorStore
    vector = VectorStore(collection_name="test_rapide")
    vector.index(chunks)

    print("\n3. Indexation lexicale (BM25)...")
    from lexical_store import LexicalStore
    lexical = LexicalStore()
    lexical.index(chunks)

    print("\n4. Test BM25 - reference exacte L.1235-3")
    top = lexical.search("article L.1235-3", top_k=1)
    trouve = bool(top) and top[0]["metadata"].get("reference") == "L.1235-3"
    print(OK if trouve else KO, top[0]["text"][:70] if top else "aucun resultat")
    erreurs += not trouve

    print("\n5. Test dense - question semantique sur les conges")
    top = vector.search(Q_DENSE, top_k=3)
    refs = [r["metadata"].get("reference") for r in top]
    trouve = "L.3141-3" in refs
    print(OK if trouve else KO, f"top-3 : {refs} (attendu : L.3141-3 dedans)")
    erreurs += not trouve

    print("\n6. Test entonnoir complet : hybride RRF (rappel) -> reranker (precision)")
    from hybrid_retriever import HybridRetriever
    from reranker import Reranker
    hybrid = HybridRetriever(vector, lexical)
    reranker = Reranker()
    top20 = hybrid.search(Q_HYBRIDE, top_k=20)
    refs20 = [r["metadata"].get("reference") for r in top20]
    rappel = "L.1235-3" in refs20
    print(("  [OK]" if rappel else KO),
          f"rappel : L.1235-3 present dans le top-20 hybride = {rappel}")
    print(f"         (top-5 hybride brut : {refs20[:5]} - RRF favorise les")
    print(f"          articles presents dans les DEUX classements, cf. note)")
    top = reranker.rerank(Q_HYBRIDE, top20, top_k=3)
    refs = [r["metadata"].get("reference") for r in top]
    trouve = "L.1235-3" in refs
    print(OK if trouve else KO, f"precision : top-3 apres reranking = {refs}")
    erreurs += not (rappel and trouve)

    print("\n7. Test reranker seul - duree legale du travail")
    candidats = hybrid.search(Q_RERANK, top_k=20)
    top = reranker.rerank(Q_RERANK, candidats, top_k=3)
    refs = [r["metadata"].get("reference") for r in top]
    trouve = "L.3121-27" in refs
    print(OK if trouve else KO, f"top-3 apres reranking : {refs} (attendu : L.3121-27)")
    erreurs += not trouve

    print("\n8. Cle Groq (optionnelle pour ce test)...")
    import os
    from dotenv import load_dotenv
    load_dotenv()
    if os.environ.get("GROQ_API_KEY", "").startswith("gsk_"):
        print(OK, "cle detectee -> modes graphe/agent/generation disponibles")
    else:
        print("  [INFO] pas de cle -> copier .env.example en .env pour les modes LLM")

    print("\n" + "=" * 55)
    if erreurs == 0:
        print("TOUT EST FONCTIONNEL - le retrieval est pret pour la demo.")
    else:
        print(f"{erreurs} test(s) en echec - verifier les messages ci-dessus.")
        sys.exit(1)

if __name__ == "__main__":
    main()
