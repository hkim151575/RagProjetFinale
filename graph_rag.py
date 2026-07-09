import json
import os

import networkx as nx
from groq import Groq

from corpus_loader import Chunk

EXTRACTION_MODEL = "llama-3.1-8b-instant"

EXTRACTION_PROMPT = """Tu extrais un graphe de connaissances depuis un texte.
Réponds UNIQUEMENT avec un JSON de la forme :
{"triplets": [{"source": "...", "relation": "...", "cible": "..."}]}
Règles : entités courtes et normalisées (minuscules), relations en 1-3 mots,
maximum 8 triplets, pas de commentaire hors JSON.

Texte :
"""

QUERY_ENTITY_PROMPT = """Extrait les entités mentionnées dans cette question.
Réponds UNIQUEMENT avec un JSON : {"entites": ["...", "..."]} (minuscules).

Question :
"""


def _parse_json(raw: str) -> dict:
    """Parse tolérant : retire d'éventuelles fences markdown."""
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


class GraphRAG:
    def __init__(self, api_key: str | None = None):
        self.client = Groq(api_key=api_key or os.environ["GROQ_API_KEY"])
        self.graph = nx.Graph()
        self.chunks_by_id: dict[str, Chunk] = {}

    def _llm(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=EXTRACTION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content

    # ----------------------------- indexation -----------------------------

    def index(self, chunks: list[Chunk], max_chunks: int | None = None) -> None:
        """Construit le graphe. max_chunks permet de limiter le coût en démo."""
        subset = chunks[:max_chunks] if max_chunks else chunks
        for i, chunk in enumerate(subset):
            self.chunks_by_id[chunk.id] = chunk
            data = _parse_json(self._llm(EXTRACTION_PROMPT + chunk.text))
            for t in data.get("triplets", []):
                src, rel, dst = (
                    t.get("source", "").strip().lower(),
                    t.get("relation", "").strip().lower(),
                    t.get("cible", "").strip().lower(),
                )
                if not src or not dst:
                    continue
                if self.graph.has_edge(src, dst):
                    self.graph[src][dst]["chunks"].add(chunk.id)
                    self.graph[src][dst]["relations"].add(rel)
                else:
                    self.graph.add_edge(src, dst, chunks={chunk.id}, relations={rel})
            if (i + 1) % 10 == 0:
                print(f"[graph] {i + 1}/{len(subset)} chunks traités "
                      f"({self.graph.number_of_nodes()} noeuds, "
                      f"{self.graph.number_of_edges()} arêtes)")
        print(f"[graph] terminé : {self.graph.number_of_nodes()} noeuds, "
              f"{self.graph.number_of_edges()} arêtes")

    # ------------------------------- requête ------------------------------

    def search(self, query: str, hops: int = 2, top_k: int = 8) -> list[dict]:
        """Retrieval par voisinage de graphe -> chunks sources."""
        data = _parse_json(self._llm(QUERY_ENTITY_PROMPT + query))
        entities = [e.strip().lower() for e in data.get("entites", [])]

        # Rattacher chaque entité de la question à un noeud du graphe
        # (correspondance exacte ou par inclusion — volontairement simple).
        seeds = set()
        for entity in entities:
            for node in self.graph.nodes:
                if entity == node or entity in node or node in entity:
                    seeds.add(node)

        if not seeds:
            return []

        # Voisinage à `hops` sauts + collecte des chunks des arêtes traversées
        chunk_ids: set[str] = set()
        frontier, visited = set(seeds), set(seeds)
        for _ in range(hops):
            next_frontier = set()
            for node in frontier:
                for neighbor in self.graph.neighbors(node):
                    chunk_ids |= self.graph[node][neighbor]["chunks"]
                    if neighbor not in visited:
                        next_frontier.add(neighbor)
                        visited.add(neighbor)
            frontier = next_frontier

        results = [
            {"id": cid, "text": self.chunks_by_id[cid].text,
             "score": 1.0, "metadata": self.chunks_by_id[cid].metadata}
            for cid in chunk_ids if cid in self.chunks_by_id
        ]
        return results[:top_k]
