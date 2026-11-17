# autonomous-mlops-agents

Projet étudiant (6 personnes, méthode Design Thinking, étape Prototype).
But : un système multi-agents qui surveille une pipeline MLOps, décide et corrige seul,
sous contrôle humain.

## Contexte
- Le dépôt est une copie du cours MLOps Zoomcamp (DataTalksClub).
- Cas d'usage : prédiction de la durée des trajets de taxi NYC (green taxi, régression).
- Tout le code du projet est dans prototype/ (voir prototype/README.md).
- Ne pas modifier les dossiers du cours (01 à 07, cohorts).
- Ne jamais activer .github/workflows/cd-deploy.yml (déploiement AWS payant).

## Architecture
5 agents : orchestrator, quality, retrain, reliability, cost (prototype/agents/).
Ils communiquent uniquement par événements JSON (Redis pub/sub), définis dans
prototype/common/events.py. Toute action est écrite dans le journal d'actions
(prototype/common/action_log.py). Ce qu'un agent peut faire seul est décrit dans
prototype/rules/autonomy.yaml.
Les décisions critiques (promotion, rollback, budget) sont des règles déterministes ;
le LLM sert seulement à expliquer et à comprendre les commandes chat.
Le modèle s'appelle "taxi-duration" dans MLflow ; la version servie porte l'alias "production".

## Conventions
- Python 3.11+, un dossier par agent, tests pytest dans prototype/tests/.
- Seuils et budget dans prototype/common/config.py, jamais en dur.
- Infrastructure locale : `docker compose up -d` depuis prototype/.
- Lancer `pytest` depuis prototype/ avant chaque pull request.