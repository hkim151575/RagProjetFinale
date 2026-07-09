"""
Configuration centralisée du projet.
Toutes les briques (indexation, retrieval, generation) lisent ces
constantes pour rester cohérentes entre elles.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Chemins ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CORPUS_PATH = DATA_DIR / "corpus.json"
DB_DIR = BASE_DIR / "db" / "chroma"
DB_META_PATH = BASE_DIR / "db" / "meta.json"
TESTS_DIR = BASE_DIR / "tests"

# --- Embedding (local, pas besoin de clé API) ---
# Modèle multilingue, gère bien le français juridique.
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# --- LLM (Groq, nécessite une clé API dans .env) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
LLM_TEMPERATURE = 0.1  # basse température : on veut de la fiabilité, pas de créativité

# --- Retrieval ---
TOP_K = 5  # nombre de chunks envoyés au LLM à chaque question

# --- Nom de la collection ChromaDB ---
COLLECTION_NAME = "code_travail"
