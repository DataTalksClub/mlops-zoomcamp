# Prototype : système multi-agents MLOps autonome

Socle commun du prototype. Il lance la pipeline taxi NYC (entraînement, registre
MLflow, API de prédiction) et l'infrastructure dont les 5 agents ont besoin
(bus d'événements Redis, journal d'actions Postgres, tableau de bord Grafana).

## Prérequis

- Git
- Python 3.11 ou plus récent
- Docker Desktop (démarré)

## Installation (une seule fois)

Depuis la racine du dépôt, sur la branche `prototype` :

```bash
cd prototype
python -m venv .venv
# Windows (PowerShell) :
.venv\Scripts\activate
# macOS / Linux :
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env      # macOS / Linux : cp .env.example .env
```

## Lancer le prototype

```bash
docker compose up -d --build                     # MLflow, Postgres, Redis, Grafana, API
python -m pipeline.train --year 2023 --month 1   # premier modèle, mis en production
curl -X POST http://localhost:9696/reload        # l'API charge le modèle
```

Le premier entraînement télécharge deux mois de données taxi dans `data/`
(une seule fois, elles sont ensuite lues depuis le disque).

Tester une prédiction :

```bash
curl -X POST http://localhost:9696/predict -H "Content-Type: application/json" -d "{\"PULocationID\": 43, \"DOLocationID\": 151, \"trip_distance\": 1.8}"
```

Arrêter : `docker compose down` (ajouter `-v` pour tout effacer, y compris les modèles).

## Services

| Service | Adresse | Rôle |
| --- | --- | --- |
| MLflow | http://localhost:5000 | Suivi des entraînements et registre des modèles |
| API | http://localhost:9696 | `/predict`, `/health`, `/reload` |
| Grafana | http://localhost:3000 | Tableau de bord (source Postgres déjà configurée) |
| Postgres | localhost:5432 (mlops / mlops) | Journal d'actions et métriques |
| Redis | localhost:6379 | Bus d'événements entre agents |

## Tests

```bash
pytest
```

Les tests utilisent des données synthétiques et un MLflow local : ils ne
téléchargent rien et ne demandent pas Docker.

## Organisation du code

```
prototype/
  common/          # partagé par tous les agents
    config.py      # seuils, budget, adresses (modifiables par variables d'environnement)
    events.py      # contrat d'événements + bus Redis
    action_log.py  # journal d'actions
  pipeline/
    data.py        # chargement des données taxi + préparation des variables
    train.py       # entraînement + enregistrement dans MLflow
    api/app.py     # API de prédiction
  agents/
    cost/          # estimation, suivi des coûts et recommandations de budget
  rules/autonomy.yaml  # ce que les agents font seuls / avec validation
  tests/
```

L'agent coûts écoute `cost_estimate` et `training_completed`, publie des
événements typés définis dans `common/events.py` et journalise ses décisions
dans `common/action_log.py`. Ses tarifs, seuils et budget sont configurables
dans `common/config.py`.

## Règles de travail

- Une branche par agent, créée depuis `prototype`, qui revient par pull request.
- Ne pas modifier les dossiers du cours (01 à 07) : tout le code va dans `prototype/`.
- Toute modification de `common/events.py` se valide en équipe : elle engage les 5 agents.
- Ne jamais commiter `.env`, `data/` ni `models/`.
- Une dépendance ajoutée à `requirements.txt` doit aussi aller dans `requirements-docker.txt` (dépendances de l'image Docker, avec `xgboost-cpu`).