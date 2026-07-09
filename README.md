# Assistant Code du travail (RAG)

Assistant en ligne de commande qui répond à des questions sur le droit du
travail français, en citant systématiquement les articles du Code du
travail sur lesquels il s'appuie.

## Installation

```bash
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# puis éditer .env et renseigner GROQ_API_KEY (console.groq.com)
```

## Utilisation

```bash
# 1. Construire la base vectorielle (une seule fois, ou après modification du corpus)
python main.py --index

# 2. Lancer l'assistant en ligne de commande (interface demandée par le sujet)
python main.py --chat

# 2bis. Ou lancer l'interface web dans le navigateur (bonus, en plus du CLI)
python main.py --web
# puis ouvrir http://127.0.0.1:5000
```

## Choix techniques (réponses aux questions de réflexion)

### Q1 — Granularité du chunking
Choix retenu : **un chunk = un article**. Les articles du Code du travail
sont déjà courts, atomiques, et numérotés — les découper davantage n'aurait
pas de sens, et les regrouper par section ferait perdre la correspondance
directe entre un chunk et le numéro d'article à citer, ce qui est
l'exigence centrale du projet. Limite assumée : un article qui renvoie à
un autre article ("au sens de l'article L1234-5") peut manquer de contexte
si l'article référencé n'est pas aussi remonté par le retrieval — c'est
atténué en pratique par le top-k (plusieurs chunks pertinents remontent
souvent ensemble).

### Q2 — Traçabilité
Le numéro d'article est stocké **dans les métadonnées** de chaque chunk
(champ `num_article`), pas seulement dans le texte embeddé. Le prompt
système numérote explicitement chaque extrait fourni au LLM et lui impose
de citer le numéro correspondant. Mais la garantie forte ne vient pas du
LLM : la liste des "articles sources" affichée à l'utilisateur est
reconstruite depuis les métadonnées du retrieval (voir `generation.py`),
pas depuis ce que le LLM prétend avoir cité — impossible donc d'afficher
un article halluciné.

### Q3 — Fraîcheur
La date du corpus est stockée dans `prompts.py` (`DATE_CORPUS`) et
injectée dans le prompt système, pour que le LLM puisse relativiser sa
réponse si la question porte sur un sujet potentiellement modifié
récemment. [Amélioration possible jalon 6 : afficher cette date également
dans le message d'accueil du CLI.]

### Q4 — Réponses conditionnelles
Le prompt système (règle 4) impose au LLM de donner la règle générale
tout en signalant explicitement que la réponse peut varier selon la
situation (taille d'entreprise, convention collective, ancienneté...),
plutôt que de deviner ou d'ignorer ces variables.

### Q5 — Frontière du conseil juridique
Le prompt système (règle 5) distingue explicitement les questions
factuelles (auxquelles le Code répond directement) des questions
d'interprétation d'une situation personnelle. Dans le second cas, le
système fournit les éléments factuels disponibles mais précise que
l'appréciation de la situation individuelle relève d'un professionnel.

## Structure du projet

```
├── data/corpus.json       # corpus source (voir note ci-dessous)
├── db/                    # base vectorielle persistée (générée, non versionnée)
├── src/
│   ├── config.py           # constantes centralisées
│   ├── extraction.py       # jalon 1
│   ├── indexation.py       # jalon 2
│   ├── retrieval.py        # jalon 3
│   ├── prompts.py          # template de prompt système
│   ├── generation.py       # jalon 4
│   ├── cli.py               # jalon 5 (interface CLI, demandée par le sujet)
│   └── app.py                # serveur Flask pour l'interface web (bonus)
├── static/
│   └── index.html           # interface web (HTML/CSS/JS)
├── tests/
│   ├── questions_test.json # jeu de questions pour valider le retrieval
│   └── test_retrieval.py
└── main.py                 # point d'entrée
```

## ⚠️ Note importante sur le corpus actuel

Le fichier `data/corpus.json` fourni contient un corpus de démarrage
**saisi manuellement à des fins de développement du pipeline**. Les textes
doivent être vérifiés et remplacés par les textes exacts avant la remise
finale — soit en les recopiant depuis legifrance.gouv.fr (Option C,
plafonnée au barème), soit en implémentant l'extraction depuis le dump XML
LEGI dans `src/extraction.py` (Option B, recommandée).

## Modèle d'embedding

`paraphrase-multilingual-MiniLM-L12-v2` (sentence-transformers), tracé
dans `db/meta.json` lors de l'indexation et vérifié avant chaque
recherche pour éviter toute incohérence.

## Amélioration jalon 6

_À compléter selon l'amélioration choisie._
