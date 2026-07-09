"""
Jalon 4 — Génération avec citations.

Le point critique de ce module : l'avertissement juridique est ajouté
par le CODE, pas seulement demandé au LLM dans le prompt. Ça garantit
qu'il figure dans 100% des réponses, même si le modèle l'oublie.
"""
from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL, LLM_TEMPERATURE
from prompts import construire_prompt_systeme, AVERTISSEMENT_JURIDIQUE

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY manquante. Copie .env.example en .env et "
                "renseigne ta clé (console.groq.com)."
            )
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


def generate_answer(question: str, chunks: list[dict]) -> dict:
    """
    Appelle le LLM avec le contexte retrouvé et retourne un dict :
    {"reponse": str, "articles_sources": list[str]}

    Si aucun chunk n'est trouvé (base vide ou question hors sujet au
    point qu'aucun chunk ne remonte), on court-circuite l'appel LLM.
    """
    if not chunks:
        return {
            "reponse": "Je ne trouve pas cette information dans ma base de connaissances."
            + AVERTISSEMENT_JURIDIQUE,
            "articles_sources": [],
        }

    client = _get_client()
    prompt_systeme = construire_prompt_systeme(chunks)

    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=LLM_TEMPERATURE,
        messages=[
            {"role": "system", "content": prompt_systeme},
            {"role": "user", "content": question},
        ],
    )

    texte_reponse = completion.choices[0].message.content

    # Articles sources = récupérés depuis les métadonnées du retrieval,
    # PAS depuis ce que le LLM prétend avoir cité (source de vérité fiable).
    articles_sources = sorted(set(chunk["num_article"] for chunk in chunks))

    # L'avertissement est ajouté ici, en dur, indépendamment de ce que le
    # LLM a généré : c'est la garantie de fiabilité exigée par le sujet.
    reponse_finale = texte_reponse.strip() + AVERTISSEMENT_JURIDIQUE

    return {
        "reponse": reponse_finale,
        "articles_sources": articles_sources,
    }
