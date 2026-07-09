import json
import os

from groq import Groq

from hybrid_retriever import HybridRetriever
from reranker import Reranker

AGENT_MODEL = "llama-3.3-70b-versatile"
MAX_ITERATIONS = 4

SYSTEM_PROMPT = """Tu es un agent de recherche documentaire. À chaque tour, réponds
UNIQUEMENT avec un JSON parmi :

1. Chercher (tu peux reformuler ou décomposer la question) :
   {"action": "search", "query": "ta requête", "raison": "pourquoi cette requête"}

2. Répondre (seulement quand les passages suffisent) :
   {"action": "answer", "reponse": "réponse complète, appuyée sur les passages",
    "sources": ["id des chunks utilisés"]}

Règles :
- Si les passages déjà récupérés ne répondent pas, reformule ou découpe la
  question en sous-questions (une recherche par sous-question).
- Ne réponds JAMAIS depuis tes connaissances internes : uniquement les passages.
- Si après plusieurs recherches l'information est introuvable, dis-le
  honnêtement dans "reponse".
"""


class AgenticRAG:
    def __init__(self, retriever: HybridRetriever, reranker: Reranker | None = None,
                 api_key: str | None = None):
        self.retriever = retriever
        self.reranker = reranker
        self.client = Groq(api_key=api_key or os.environ["GROQ_API_KEY"])

    def _decide(self, messages: list[dict]) -> dict:
        response = self.client.chat.completions.create(
            model=AGENT_MODEL, messages=messages, temperature=0.2,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Filet de sécurité : on force une réponse au prochain tour
            return {"action": "answer", "reponse": raw, "sources": []}

    def _search_tool(self, query: str) -> list[dict]:
        candidates = self.retriever.search(query, top_k=10)
        if self.reranker:
            candidates = self.reranker.rerank(query, candidates, top_k=4)
        return candidates[:4]

    def run(self, question: str, verbose: bool = True) -> dict:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Question : {question}"},
        ]
        trajectory = []

        for iteration in range(1, MAX_ITERATIONS + 1):
            decision = self._decide(messages)

            if decision.get("action") == "search":
                query = decision.get("query", question)
                results = self._search_tool(query)
                trajectory.append({"iteration": iteration, "query": query,
                                   "n_resultats": len(results)})
                if verbose:
                    print(f"[agent] tour {iteration} — recherche : « {query} » "
                          f"({decision.get('raison', '')}) -> {len(results)} passages")

                passages = "\n\n".join(
                    f"[{r['id']}] {r['text']}" for r in results
                ) or "(aucun résultat)"
                messages.append({"role": "assistant", "content": json.dumps(decision)})
                messages.append({"role": "user",
                                 "content": f"Passages récupérés :\n{passages}\n\n"
                                            "Nouvelle décision ?"})
            else:  # answer
                if verbose:
                    print(f"[agent] tour {iteration} — réponse rendue")
                return {"reponse": decision.get("reponse", ""),
                        "sources": decision.get("sources", []),
                        "trajectoire": trajectory}

        # Budget épuisé : on force la rédaction avec ce qu'on a
        messages.append({"role": "user",
                         "content": "Budget de recherche épuisé : réponds "
                                    "maintenant avec les passages disponibles "
                                    "(action answer obligatoire)."})
        decision = self._decide(messages)
        return {"reponse": decision.get("reponse", ""),
                "sources": decision.get("sources", []),
                "trajectoire": trajectory}
