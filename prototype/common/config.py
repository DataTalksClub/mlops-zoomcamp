"""Configuration partagée par tous les agents.
Chaque valeur peut être changée par une variable d'environnement (voir .env.example)."""
import os

# Services
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://mlops:mlops@localhost:5432/mlops")
API_URL = os.getenv("API_URL", "http://localhost:9696")

# Modèle
MODEL_NAME = os.getenv("MODEL_NAME", "taxi-duration")
PRODUCTION_ALIAS = "production"
EXPERIMENT_NAME = os.getenv("EXPERIMENT_NAME", "nyc-taxi-experiment")

# Bus d'événements
EVENTS_CHANNEL = os.getenv("EVENTS_CHANNEL", "mlops.events")

# Seuils (à ajuster par l'équipe)
DRIFT_THRESHOLD = float(os.getenv("DRIFT_THRESHOLD", "0.5"))
MIN_IMPROVEMENT = float(os.getenv("MIN_IMPROVEMENT", "0.02"))  # 2 % d'erreur en moins
MAX_ERROR_RATE = float(os.getenv("MAX_ERROR_RATE", "0.05"))
MAX_LATENCY_SECONDS = float(os.getenv("MAX_LATENCY_SECONDS", "1.0"))

# Coûts (tarif fictif pour le prototype)
CPU_HOUR_PRICE = float(os.getenv("CPU_HOUR_PRICE", "0.05"))
MONTHLY_BUDGET = float(os.getenv("MONTHLY_BUDGET", "20.0"))


# --- Fiabilité ---
MONITORED_ENDPOINT = os.getenv("MONITORED_ENDPOINT", "/predict")  # route dont on surveille le SLO
HTTP_TIMEOUT_SECONDS = float(os.getenv("HTTP_TIMEOUT_SECONDS", "3"))  # au-delà, l'API est jugée injoignable
MIN_REQUESTS = int(os.getenv("MIN_REQUESTS", "10"))  # en dessous, le taux d'erreurs n'est pas significatif
HIGH_ERROR_RATE = float(os.getenv("HIGH_ERROR_RATE", "0.20"))
CRITICAL_ERROR_RATE = float(os.getenv("CRITICAL_ERROR_RATE", "0.50"))  # au-delà : critique d'office
HIGH_LATENCY_SECONDS = float(os.getenv("HIGH_LATENCY_SECONDS", "3.0"))
SLO_TARGET = float(os.getenv("SLO_TARGET", "0.99"))  # 99 % de requêtes réussies
SLO_WINDOW_MINUTES = float(os.getenv("SLO_WINDOW_MINUTES", "60"))
SEVERITY_MEDIUM_SCORE = int(os.getenv("SEVERITY_MEDIUM_SCORE", "4"))
SEVERITY_HIGH_SCORE = int(os.getenv("SEVERITY_HIGH_SCORE", "7"))
CRASH_LOOP_RESTARTS = int(os.getenv("CRASH_LOOP_RESTARTS", "3"))  # redémarrages en 10 min = boucle de crash
RESOURCE_MEMORY_PERCENT = float(os.getenv("RESOURCE_MEMORY_PERCENT", "90"))
RESOURCE_CPU_PERCENT = float(os.getenv("RESOURCE_CPU_PERCENT", "95"))
BAD_MODEL_WINDOW_MINUTES = float(os.getenv("BAD_MODEL_WINDOW_MINUTES", "30"))  # modèle promu récemment = suspect
API_CONTAINER_NAME = os.getenv("API_CONTAINER_NAME", "mlops-api")
API_SERVICE_NAME = os.getenv("API_SERVICE_NAME", "api")  # nom du service dans docker-compose.yml
REDIS_CONTAINER_NAME = os.getenv("REDIS_CONTAINER_NAME", "mlops-redis")
MLFLOW_CONTAINER_NAME = os.getenv("MLFLOW_CONTAINER_NAME", "mlops-mlflow")
# Seuls conteneurs que l'agent a le droit de toucher (jamais Postgres)
ALLOWED_CONTAINERS = (API_CONTAINER_NAME, REDIS_CONTAINER_NAME, MLFLOW_CONTAINER_NAME)
ACTION_HTTP_TIMEOUT_SECONDS = float(os.getenv("ACTION_HTTP_TIMEOUT_SECONDS", "30"))  # /reload peut prendre plusieurs secondes