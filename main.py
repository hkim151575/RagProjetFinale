import argparse
import os

from dotenv import load_dotenv

from corpus_loader import load_corpus
from hybrid_retriever import HybridRetriever
from lexical_store import LexicalStore
from vector_store import VectorStore

load_dotenv()

GENERATION_MODEL = "llama-3.3-70b-versatile"


def generate_answer(question: str, passages: list[dict]) -> str:
    """Génération finale (identique pour les modes non agentiques)."""
    from groq import Groq

    context = "\n\n".join(f"[{p['id']}] {p['text']}" for p in passages)
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {"role": "system",
             "content": "Réponds uniquement à partir des passages fournis, en "
                        "citant les identifiants [chunk_x] utilisés. Si "
                        "l'information manque, dis-le."},
            {"role": "user", "content": f"Passages :\n{context}\n\nQuestion : {question}"},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", help="Chemin du CSV de chunks")
    parser.add_argument("question", help="Question à poser")
    parser.add_argument("--mode", default="hybride",
                        choices=["classique", "hybride", "rerank", "graphe", "agent"])
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    chunks = load_corpus(args.corpus)
    vector = VectorStore()
    vector.index(chunks)

    if args.mode == "classique":
        passages = vector.search(args.question, args.top_k)

    elif args.mode in ("hybride", "rerank", "agent"):
        lexical = LexicalStore()
        lexical.index(chunks)
        hybrid = HybridRetriever(vector, lexical)

        if args.mode == "hybride":
            passages = hybrid.search(args.question, args.top_k)
        elif args.mode == "rerank":
            from reranker import Reranker
            candidates = hybrid.search(args.question, top_k=20)
            passages = Reranker().rerank(args.question, candidates, args.top_k)
        else:  # agent
            from agentic_rag import AgenticRAG
            from reranker import Reranker
            result = AgenticRAG(hybrid, Reranker()).run(args.question)
            print("\n================= RÉPONSE (agent) =================")
            print(result["reponse"])
            print(f"\nSources : {result['sources']}")
            print(f"Trajectoire : {result['trajectoire']}")
            return

    else:  # graphe
        from graph_rag import GraphRAG
        graph = GraphRAG()
        # max_chunks limite le coût de la démo (1 appel LLM par chunk !)
        graph.index(chunks, max_chunks=50)
        passages = graph.search(args.question, top_k=args.top_k)

    print("\n----------------- PASSAGES RETENUS -----------------")
    for p in passages:
        print(f"  [{p['id']}] {p['text'][:100].replace(chr(10), ' ')}...")

    print("\n================= RÉPONSE =================")
    print(generate_answer(args.question, passages))


if __name__ == "__main__":
    main()
