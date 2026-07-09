# RAG Avancé — Au-delà du RAG classique

Implémentation Python des approches étudiées dans la veille technologique
(M2 MD5 — Data & IA), en extension directe du RAG classique du cours
(ChromaDB + sentence-transformers + Groq).

## Correspondance avec les pistes de la veille

| Module | Piste | Approche |
|---|---|---|
| `vector_store.py` | (baseline) | RAG vectoriel classique : embeddings + ChromaDB + top-k |
| `lexical_store.py` | C | BM25 — correspondances exactes (sigles, références) |
| `hybrid_retriever.py` | C | Fusion RRF des classements dense + lexical |
| `reranker.py` | C | Cross-encoder en seconde passe (entonnoir rappel → précision) |
| `graph_rag.py` | A | Mini-GraphRAG : extraction entités/relations par LLM + parcours de graphe (multi-hop) |
| `agentic_rag.py` | D | Boucle agentique : chercher → évaluer → reformuler → répondre |
| `evaluate.py` | — | Comparaison côte à côte des pipelines (support de la restitution orale) |

Non implémentés volontairement : RAPTOR (piste B, coût de construction élevé
pour une démo) et long contexte/CAG (piste E, dépend du fournisseur de modèle) —
traités dans la note de synthèse.

## Installation (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Clé Groq (gratuite) : console.groq.com -> API Keys -> Create API Key
Copy-Item .env.example .env       # puis coller la clé dans .env
# ou pour la session en cours seulement :
$env:GROQ_API_KEY = "gsk_votre_cle"
```

Placer le corpus CSV (un chunk par ligne, colonne `text` ou `chunk`) dans `data/`.

## Utilisation

```powershell
# Comparer les 4 pipelines de retrieval sur des questions de test (sans LLM)
python evaluate.py data/corpus.csv "question avec référence exacte" "question sémantique"

# Poser une question de bout en bout (retrieval + génération)
python main.py data/corpus.csv --mode classique "votre question"
python main.py data/corpus.csv --mode hybride   "votre question"
python main.py data/corpus.csv --mode rerank    "votre question"
python main.py data/corpus.csv --mode graphe    "votre question"   # coûteux : 1 appel LLM / chunk à l'indexation
python main.py data/corpus.csv --mode agent     "votre question"
```


## Corpus Code du travail (PDF)

Le projet inclut `data/code_du_travail_extraits.pdf` (49 articles clés,
reformulés à des fins pédagogiques — le texte officiel fait foi sur
legifrance.gouv.fr) et un module d'ingestion PDF :

```powershell
# PDF -> corpus JSON (1 article = 1 chunk)
python pdf_ingest.py data/code_du_travail_extraits.pdf --sortie data/corpus.json
# (ou --sortie data/corpus_code_travail.csv pour du CSV : les deux formats sont acceptés partout)

# Puis interroger le code du travail
python evaluate.py data/corpus.json "Que prévoit l'article L.1235-3 ?"
python main.py data/corpus.json --mode rerank "Combien de jours de congés par mois ?"
```

`pdf_ingest.py` fonctionne avec n'importe quel PDF : chunking structurel par
article pour les textes juridiques, fenêtre glissante avec recouvrement sinon.
Pour utiliser le vrai Code du travail complet, télécharger le PDF consolidé
depuis Légifrance et le passer au même script.

## Idées de démonstration pour l'oral

1. **BM25 vs dense** : une question contenant un identifiant exact (code,
   sigle) — le dense la rate, BM25 la trouve, l'hybride garde les deux.
2. **Reranker** : montrer l'ordre des candidats avant/après reranking.
3. **Multi-hop** : une question dont la réponse relie deux chunks distincts —
   comparer `--mode hybride` (échec probable) et `--mode graphe`.
4. **Agent** : afficher la trajectoire (reformulations successives) et le
   surcoût en latence — c'est exactement le compromis décrit dans la note.

## Limites assumées (à dire en soutenance)

- L'extraction d'entités du mini-GraphRAG n'est ni dédupliquée ni normalisée
  sérieusement (alias, homonymes) — c'est précisément le point faible du
  GraphRAG réel documenté dans la veille.
- L'agent est évalué à l'œil : une vraie évaluation exigerait n exécutions
  par question + juge LLM (non-déterminisme).
- Le reranker par défaut (ms-marco-MiniLM) est anglophone ; pour un corpus
  français, remplacer par `BAAI/bge-reranker-v2-m3` dans `reranker.py`.
