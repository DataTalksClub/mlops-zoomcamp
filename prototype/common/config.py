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
COST_PER_CPU_SECOND = float(os.getenv("COST_PER_CPU_SECOND", "0.0005"))
COST_SPOT_DISCOUNT = float(os.getenv("COST_SPOT_DISCOUNT", "0.6"))
DEFAULT_CPU_SECONDS_PER_MONTH_OF_DATA = float(
    os.getenv("DEFAULT_CPU_SECONDS_PER_MONTH_OF_DATA", "600.0")
)
COST_IDLE_MINUTES = float(os.getenv("COST_IDLE_MINUTES", "30.0"))
COST_SIZE_HEADROOM = float(os.getenv("COST_SIZE_HEADROOM", "0.3"))
COST_HOURS_PER_MONTH = float(os.getenv("COST_HOURS_PER_MONTH", "730.0"))