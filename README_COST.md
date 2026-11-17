# Agent Coûts : intégration

## Fichiers
Copie `agents/cost/` et `tests/test_cost.py` dans ton dépôt (branche agent-cost).
Ajoute `agents/__init__.py` s'il n'existe pas.

## Lancer les tests (sans Docker)
    pip install pytest
    pytest tests/test_cost.py -q

## À adapter à ton socle (prototype/common/)
1. `settings.py` : déplace `CostConfig` dans `common/config.py` si l'équipe veut
   une config unique (tarif, budget, remise spot).
2. `EventBus` : écris un petit adaptateur vers `common/events.py` :

       class RedisBus:
           def publish(self, event_type, payload):
               events.publish(Event(type=event_type, payload=payload))  # ton schéma Pydantic

3. `ActionLog` : adaptateur vers `common/action_log.py` :

       class PgActionLog:
           def write(self, agent, action, details):
               action_log.write(agent=agent, action=action, details=details)

4. Abonnement : dans ta boucle d'écoute Redis, appelle
   `agent.on_event(event.type, event.payload)`.
5. Postgres : `PostgresCostStore(psycopg2.connect(...))` crée la table
   `model_costs` au démarrage.
6. Docker : `DockerStatsCollector()` + un appel périodique (ex. toutes les 60 s) à
   `agent.record_serving_sample("taxi-duration", "<nom du conteneur API>")`.
7. Fin d'entraînement : l'agent Retrain (ou train.py) publie `training_completed`
   avec `{model, cpu_seconds, months}` (mesure avec `time.process_time()`).

## Nouveaux événements à déclarer dans common/events.py (prévenir l'équipe)
- `cost_estimated`      réponse à `cost_estimate`
- `budget_exceeded`     si coût du mois + estimation > budget
- `cost_recommendation` taille de serveur / scale-to-zero (calcul seulement)
- `training_completed`  si l'agent Retrain ne le publie pas déjà

## Requêtes Grafana (source Postgres)
Coût par modèle ce mois-ci :

    SELECT model AS metric, SUM(cost) AS value
    FROM model_costs
    WHERE month = to_char(now(), 'YYYY-MM')
    GROUP BY model;

Coût cumulé dans le temps :

    SELECT $__timeGroupAlias(ts, 1h), model AS metric, SUM(cost) AS value
    FROM model_costs
    WHERE $__timeFilter(ts)
    GROUP BY 1, model ORDER BY 1;

Budget restant (jauge) : `budget - SUM(cost)` avec le budget saisi en constante.

## Règles respectées
- L'agent mesure et estime ; il ne bloque jamais un job (l'Orchestrateur décide).
- Aucun LLM, aucun calcul d'argent hors fonctions pures testées.
- Les recommandations (taille, spot, scale-to-zero) n'agissent pas sur l'infra.
