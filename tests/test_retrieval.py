"""
Jalon 3 — valide que l'article attendu remonte dans le top-k pour
chaque question du jeu de test. À lancer après l'indexation.

Usage : python tests/test_retrieval.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from retrieval import search  # noqa: E402

QUESTIONS_PATH = Path(__file__).parent / "questions_test.json"


def lancer_tests(k: int = 5) -> None:
    with open(QUESTIONS_PATH, encoding="utf-8") as f:
        cas_de_test = json.load(f)

    reussites = 0
    for cas in cas_de_test:
        resultats = search(cas["question"], k=k)
        articles_trouves = [r["num_article"] for r in resultats]
        ok = cas["article_attendu"] in articles_trouves

        statut = "OK" if ok else "ÉCHEC"
        print(f"[{statut}] {cas['question']}")
        print(f"        attendu : {cas['article_attendu']} | trouvés : {articles_trouves}")

        if ok:
            reussites += 1

    print(f"\n{reussites}/{len(cas_de_test)} tests réussis (top-{k}).")


if __name__ == "__main__":
    lancer_tests()
