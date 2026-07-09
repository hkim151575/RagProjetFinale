"""question_agent.py - Agent reformulateur de questions (multi-query retrieval).

Probleme adresse (observe empiriquement dans ce projet) : le fosse lexical.
"contester un licenciement" ne partage aucun mot avec L.1471-1 qui parle de
"prescription". Solution : reformuler la question en plusieurs variantes
(dont le registre juridique), chercher avec chacune, fusionner par RRF.
Un seul appel LLM : cout et latence maitrises, comportement previsible.
"""

import json
import os

from groq import Groq

from hybrid_retriever import HybridRetriever, reciprocal_rank_fusion

REFORMULATION_MODEL = "llama-3.3-70b-versatile"

REFORMULATION_PROMPT = """Tu es un expert en recherche documentaire juridique.
On te donne une question d'utilisateur. Genere {n} reformulations qui
maximisent les chances de retrouver les passages pertinents dans un corpus
d'articles du Code du travail :
- au moins une variante avec le VOCABULAIRE JURIDIQUE technique probable
  (ex. "contester" -> "prescription", "action en justice", "recours" ;
   "salaire minimum" -> "SMIC" ; "etre vire" -> "licenciement") ;
- au moins une variante en mots-cles nus (sans phrase) ;
- garde le sens exact de la question, n'ajoute pas de sous-questions.

Reponds UNIQUEMENT avec un JSON :
{{"reformulations": ["...", "..."]}}

Question : {question}
"""


class QuestionAgent:
    """Reformule une question puis interroge le retriever avec chaque variante."""

    def __init__(self, retriever: HybridRetriever, api_key: str | None = None,
                 n_reformulations: int = 3):
        self.retriever = retriever
        self.n = n_reformulations
        self.client = Groq(api_key=api_key or os.environ["GROQ_API_KEY"])

    def reformulate(self, question: str) -> list[str]:
        """Renvoie [question originale] + N reformulations generees par le LLM."""
        prompt = REFORMULATION_PROMPT.format(n=self.n, question=question)
        response = self.client.chat.completions.create(
            model=REFORMULATION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```")
        try:
            variantes = json.loads(raw).get("reformulations", [])
        except json.JSONDecodeError:
            variantes = []
        return [question] + [v for v in variantes if isinstance(v, str) and v.strip()]

    def search(self, question: str, top_k: int = 5,
               per_query: int = 10, verbose: bool = True) -> list[dict]:
        """Multi-query retrieval : une recherche hybride par variante, fusion RRF."""
        variantes = self.reformulate(question)
        if verbose:
            print("[reformulation] variantes generees :")
            for v in variantes:
                print(f"  - {v}")

        rankings = [self.retriever.search(v, top_k=per_query) for v in variantes]
        return reciprocal_rank_fusion(rankings)[:top_k]
