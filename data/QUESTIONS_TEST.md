# Questions de test — corpus NovaTech (data/corpus.csv)

Le corpus décrit une société fictive (NovaTech, objets connectés) et est
construit pour que chaque type de question mette en évidence une approche.

## 1. Correspondance exacte → BM25 doit gagner, le dense peut rater
- « Que signifie le code d'erreur E-4012 ? »
- « Que prévoit l'article L.1235-3 ? »
- « Quelle pile utilise le capteur NT-200 ? »

```powershell
python evaluate.py data/corpus.csv "Que signifie le code d'erreur E-4012 ?"
```

## 2. Question sémantique → le dense s'en sort bien
- « Comment réduire sa facture de chauffage avec des capteurs ? »
- « Pourquoi les clients achètent-ils des capteurs connectés ? »

## 3. Multi-hop → le top-k échoue, le graphe (ou l'agent) réussit
La réponse exige de RELIER des chunks différents :
- « Quel fournisseur de la filiale allemande est aussi client de la filiale
  espagnole ? » (Elektra Bauteile : fournisseur de NovaTech GmbH dans un
  document, client de NovaTech Iberia dans un autre)
- « Qui dirige l'équipe responsable de l'incident du 5 mars 2026, et où est
  hébergé le serveur concerné ? » (incident → équipe infrastructure →
  Sofia Lindgren → Nordic Datacenters)
- « Quel partenaire de la filiale espagnole travaille aussi avec un
  concurrent de NovaTech ? » (SmartCasa → HomeSense)

```powershell
python main.py data/corpus.csv --mode hybride "Quel fournisseur de la filiale allemande est aussi client de la filiale espagnole ?"
python main.py data/corpus.csv --mode graphe  "Quel fournisseur de la filiale allemande est aussi client de la filiale espagnole ?"
python main.py data/corpus.csv --mode agent   "Quel fournisseur de la filiale allemande est aussi client de la filiale espagnole ?"
```

## 4. Question globale → limite assumée du retrieval par chunks
- « Quels sont les grands thèmes de ce corpus ? »
Aucun mode chunk-based n'y répond bien : c'est l'argument des résumés de
communautés (GraphRAG) et de RAPTOR, traités dans la note de synthèse.

## 5. Filtre par métadonnées (piste C, à montrer si le temps le permet)
Le CSV porte des colonnes `source`, `type`, `date` — exploitables pour
filtrer (ex. type=juridique) avant le retrieval.

---

# Questions de test — corpus Code du travail (data/corpus_code_travail.csv)

Générer le corpus depuis le PDF :
```powershell
python pdf_ingest.py data/code_du_travail_extraits.pdf --sortie data/corpus_code_travail.csv
```

## Référence exacte (BM25 / hybride)
- « Que prévoit l'article L.1235-3 ? »
- « Quelle est la différence entre L.1152-1 et L.1153-1 ? »

## Sémantique (dense)
- « Combien de jours de congés par mois de travail ? »        (→ L.3141-3)
- « Ai-je droit à une pause pendant ma journée de travail ? » (→ L.3121-16)
- « Mon patron peut-il me faire travailler 12 heures par jour ? » (→ L.3121-18)

## Multi-hop / renvois entre articles (graphe ou agent)
- « L'indemnité de rupture conventionnelle peut-elle être inférieure à
  l'indemnité de licenciement ? » (L.1237-13 renvoie à L.1234-9)
- « Quel est le délai pour contester un licenciement, et quelle indemnité
  peut obtenir le salarié si le licenciement est injustifié ? »
  (croise L.1471-1 et L.1235-3)

## Question globale (limite du chunk-based, pour l'argumentaire)
- « Quels sont les grands thèmes couverts par ce corpus ? »
