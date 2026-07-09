"""
Jalon 5 — Interface en ligne de commande.

Boucle : saisie de la question -> retrieval -> génération -> affichage
de la réponse, des articles sources et de l'avertissement.
"""
from retrieval import search
from generation import generate_answer
from config import TOP_K

COMMANDES_SORTIE = {"quit", "exit", "q"}


def afficher_bienvenue() -> None:
    print("=" * 60)
    print("Assistant Code du travail (RAG)")
    print("Pose ta question sur le droit du travail français.")
    print(f"(tape 'quit' pour sortir)")
    print("=" * 60)


def boucle_interactive() -> None:
    afficher_bienvenue()

    while True:
        question = input("\n> ").strip()

        if question.lower() in COMMANDES_SORTIE:
            print("À bientôt !")
            break

        if not question:
            continue

        chunks = search(question, k=TOP_K)
        resultat = generate_answer(question, chunks)

        print(f"\n{resultat['reponse']}")

        if resultat["articles_sources"]:
            print(f"\nArticles sources : {', '.join(resultat['articles_sources'])}")


if __name__ == "__main__":
    boucle_interactive()
