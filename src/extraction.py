"""
Jalon 1 — Préparation des données.

État actuel : le corpus de démarrage (data/corpus.json) a été saisi
manuellement (équivalent Option C) pour faire tourner le pipeline
rapidement. Pour la version finale, remplace ce fichier par un vrai
script d'extraction du dump XML LEGI (Option B), en suivant le
squelette ci-dessous.

Structure attendue en sortie (data/corpus.json) : une liste de dict
avec au minimum les clés id, num_article, titre_section, theme,
texte, source.
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from config import CORPUS_PATH, DATA_DIR


def nettoyer_texte(texte: str) -> str:
    """Supprime les scories courantes d'un texte juridique extrait de XML :
    espaces multiples, retours à la ligne parasites, balises résiduelles."""
    if not texte:
        return ""
    texte = re.sub(r"\s+", " ", texte)
    texte = texte.strip()
    return texte


def extraire_article_depuis_xml(fichier_xml: Path) -> dict | None:
    """
    TODO (Option B) : à adapter une fois que tu as téléchargé le dump LEGI
    depuis data.gouv.fr et ouvert un fichier d'article dans un éditeur pour
    voir sa structure réelle.

    Piste : chaque article LEGI est typiquement un fichier XML avec des
    balises comme <NUM>, <TITRE_TXT>, <BLOC_TEXTUEL>, <CONTENU>.
    Utilise `xml.etree.ElementTree` pour parser et `.find()` / `.text`
    pour extraire chaque champ.

    Exemple de squelette (à vérifier/adapter à la vraie structure du XML) :

        tree = ET.parse(fichier_xml)
        root = tree.getroot()
        num = root.find(".//NUM").text
        contenu_elem = root.find(".//BLOC_TEXTUEL//CONTENU")
        texte = "".join(contenu_elem.itertext())
        return {
            "id": num,
            "num_article": num,
            "titre_section": ...,   # à déterminer via l'arborescence de dossiers
            "theme": ...,           # à mapper depuis le titre de section
            "texte": nettoyer_texte(texte),
            "source": "Code du travail, partie législative (LEGI, data.gouv.fr)",
        }
    """
    raise NotImplementedError(
        "Complète cette fonction une fois le dump XML LEGI téléchargé et "
        "sa structure examinée. En attendant, data/corpus.json contient "
        "un corpus de démarrage saisi manuellement."
    )


def construire_corpus_depuis_dossier(dossier_xml: Path) -> list[dict]:
    """Parcourt un dossier de fichiers XML LEGI et construit le corpus complet."""
    documents = []
    for fichier in dossier_xml.glob("**/*.xml"):
        doc = extraire_article_depuis_xml(fichier)
        if doc:
            documents.append(doc)
    return documents


def sauvegarder_corpus(documents: list[dict], chemin: Path = CORPUS_PATH) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    print(f"{len(documents)} documents sauvegardés dans {chemin}")


def charger_corpus(chemin: Path = CORPUS_PATH) -> list[dict]:
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def controle_qualite(documents: list[dict], n: int = 10) -> None:
    """Affiche n documents au hasard pour relecture manuelle (demandé au jalon 1)."""
    import random

    echantillon = random.sample(documents, min(n, len(documents)))
    for doc in echantillon:
        print(f"\n--- {doc['num_article']} ({doc['theme']}) ---")
        print(doc["texte"][:200], "...")


if __name__ == "__main__":
    # Pour l'instant, on se contente de valider le corpus de démarrage existant.
    corpus = charger_corpus()
    print(f"Corpus chargé : {len(corpus)} documents")
    themes = sorted(set(d["theme"] for d in corpus))
    print(f"Thèmes couverts ({len(themes)}) : {', '.join(themes)}")
    controle_qualite(corpus, n=3)
