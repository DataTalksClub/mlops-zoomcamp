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
PREVIOUS_ALIAS = "previous"  # version remplacée, pour un rollback
EXPERIMENT_NAME = os.getenv("EXPERIMENT_NAME", "nyc-taxi-experiment")

# Bus d'événements
EVENTS_CHANNEL = os.getenv("EVENTS_CHANNEL", "mlops.events")

# Seuils (à ajuster par l'équipe)
DRIFT_THRESHOLD = float(os.getenv("DRIFT_THRESHOLD", "0.5"))
MIN_IMPROVEMENT = float(os.getenv("MIN_IMPROVEMENT", "0.02"))  # 2 % d'erreur en moins
RETRAIN_COOLDOWN_MINUTES = float(os.getenv("RETRAIN_COOLDOWN_MINUTES", "60"))  # pause entre deux entraînements
DEFAULT_TRAIN_MONTHS = int(os.getenv("DEFAULT_TRAIN_MONTHS", "1"))  # mois d'entraînement si aucune période
MAX_ERROR_RATE = float(os.getenv("MAX_ERROR_RATE", "0.05"))
MAX_LATENCY_SECONDS = float(os.getenv("MAX_LATENCY_SECONDS", "1.0"))

# Coûts (tarif fictif pour le prototype)
CPU_HOUR_PRICE = float(os.getenv("CPU_HOUR_PRICE", "0.05"))
MONTHLY_BUDGET = float(os.getenv("MONTHLY_BUDGET", "20.0"))

# Qualité des données (agent qualité)
MAX_TRIP_MINUTES = float(os.getenv("MAX_TRIP_MINUTES", "60"))
MAX_PASSENGERS = int(os.getenv("MAX_PASSENGERS", "8"))
MAX_TRIP_DISTANCE = float(os.getenv("MAX_TRIP_DISTANCE", "100"))
CRITICAL_INVALID_SHARE = float(os.getenv("CRITICAL_INVALID_SHARE", "0.05"))

COLUMN_DRIFT_THRESHOLD = float(os.getenv("COLUMN_DRIFT_THRESHOLD", "0.1"))