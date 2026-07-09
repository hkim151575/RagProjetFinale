"""
Point d'entrée du projet.

Usage :
    python main.py --index          # construit la base vectorielle (jalon 2)
    python main.py --index --force  # réindexe même si une base existe déjà
    python main.py --chat           # lance la boucle de questions-réponses en CLI (jalon 5)
    python main.py --web            # lance l'interface web (bonus, dans le navigateur)
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Assistant Code du travail (RAG)")
    parser.add_argument("--index", action="store_true", help="Construit la base vectorielle")
    parser.add_argument("--force", action="store_true", help="Force la réindexation")
    parser.add_argument("--chat", action="store_true", help="Lance la boucle de Q/R en CLI")
    parser.add_argument("--web", action="store_true", help="Lance l'interface web dans le navigateur")
    args = parser.parse_args()

    if args.index:
        from indexation import construire_index

        construire_index(force=args.force)
    elif args.chat:
        from cli import boucle_interactive

        boucle_interactive()
    elif args.web:
        from app import lancer_serveur

        lancer_serveur()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
