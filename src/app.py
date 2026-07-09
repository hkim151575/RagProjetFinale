"""
Interface web (bonus, en plus du CLI demandé par le sujet).

Lance un petit serveur Flask qui :
- sert la page HTML/JS (static/index.html)
- expose une route POST /api/ask qui appelle le pipeline RAG existant
  (retrieval.search + generation.generate_answer) et retourne du JSON.

Usage : python main.py --web
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask, request, jsonify, send_from_directory

from retrieval import search
from generation import generate_answer
from config import TOP_K

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Question vide."}), 400

    try:
        chunks = search(question, k=TOP_K)
        resultat = generate_answer(question, chunks)
    except Exception as e:
        # On ne renvoie jamais la trace complète au client, mais on log côté serveur.
        print(f"Erreur lors du traitement de la question : {e}")
        return jsonify({"error": "Une erreur est survenue côté serveur."}), 500

    return jsonify(
        {
            "reponse": resultat["reponse"],
            "articles_sources": resultat["articles_sources"],
        }
    )


def lancer_serveur(port: int = 5000) -> None:
    print(f"Interface disponible sur http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    lancer_serveur()
