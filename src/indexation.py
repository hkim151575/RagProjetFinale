"""
Jalon 2 — Chunking et indexation.

Stratégie de chunking retenue (à documenter dans le README, Q1) :
un chunk = un article. C'est le choix le plus adapté à ce corpus car
les articles sont déjà courts et atomiques, et parce que la citation
d'article (exigence forte du projet) doit correspondre exactement à
un chunk — pas à un fragment de section.

Contrainte du jalon : au redémarrage, on recharge la base existante
sans réindexer (voir main.py / la fonction `base_existe`).
"""
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from config import (
    CORPUS_PATH,
    DB_DIR,
    DB_META_PATH,
    EMBEDDING_MODEL_NAME,
    COLLECTION_NAME,
)
from extraction import charger_corpus


def base_existe() -> bool:
    """Vérifie si une base vectorielle a déjà été construite sur disque."""
    return DB_DIR.exists() and any(DB_DIR.iterdir())


def sauvegarder_meta_modele() -> None:
    """Trace le nom du modèle d'embedding utilisé, exigé par le sujet
    pour garantir qu'on ne mélange jamais deux modèles différents
    entre l'indexation et la recherche."""
    DB_META_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_META_PATH, "w", encoding="utf-8") as f:
        json.dump({"embedding_model": EMBEDDING_MODEL_NAME}, f, ensure_ascii=False, indent=2)


def verifier_coherence_modele() -> None:
    """Avant toute recherche, vérifie que le modèle d'embedding configuré
    correspond bien à celui utilisé lors de l'indexation."""
    if not DB_META_PATH.exists():
        return
    with open(DB_META_PATH, encoding="utf-8") as f:
        meta = json.load(f)
    if meta.get("embedding_model") != EMBEDDING_MODEL_NAME:
        raise RuntimeError(
            f"Incohérence : la base a été indexée avec "
            f"'{meta.get('embedding_model')}' mais config.py pointe vers "
            f"'{EMBEDDING_MODEL_NAME}'. Réindexe ou corrige la config."
        )


def construire_index(force: bool = False) -> None:
    """Construit la base vectorielle depuis data/corpus.json et la persiste sur disque."""
    if base_existe() and not force:
        print("Base déjà indexée, rien à faire (utilise --force pour réindexer).")
        return

    print(f"Chargement du modèle d'embedding : {EMBEDDING_MODEL_NAME}")
    modele = SentenceTransformer(EMBEDDING_MODEL_NAME)

    corpus = charger_corpus(CORPUS_PATH)
    print(f"{len(corpus)} documents à indexer (1 chunk = 1 article).")

    # Vérification qualité : aucun article ne doit être vide ou coupé
    for doc in corpus:
        if not doc["texte"].strip():
            print(f"ATTENTION : article {doc['id']} a un texte vide.")

    client = chromadb.PersistentClient(path=str(DB_DIR))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    textes = [doc["texte"] for doc in corpus]
    ids = [doc["id"] for doc in corpus]
    metadonnees = [
        {
            "num_article": doc["num_article"],
            "titre_section": doc["titre_section"],
            "theme": doc["theme"],
            "source": doc["source"],
        }
        for doc in corpus
    ]

    print("Calcul des embeddings...")
    embeddings = modele.encode(textes, show_progress_bar=True).tolist()

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=textes,
        metadatas=metadonnees,
    )

    sauvegarder_meta_modele()
    print(f"Index construit et persisté dans {DB_DIR}")


if __name__ == "__main__":
    import sys

    force = "--force" in sys.argv
    construire_index(force=force)
