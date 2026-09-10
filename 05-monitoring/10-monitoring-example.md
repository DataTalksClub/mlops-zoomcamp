---
code:
  - label: "Monitoring services"
    path: docker-compose.yml
  - label: "Evidently metric calculation"
    path: evidently_metrics_calculation.py
  - label: "Debugging notebook"
    path: debugging_nyc_taxi_data.ipynb
---

# Monitoring Example

Use the local Docker Compose example to combine the monitoring pieces. The example uses the model and reference artifacts from the previous units, stores metrics in PostgreSQL, and displays them in Grafana.

## Prerequisites

Install Docker and Docker Compose, then create a Python environment and install the requirements from `requirements.txt`.

Run `baseline_model_nyc_taxi_data.ipynb` to download the datasets, train a model, and create the reference dataset. The generated data and model files stay under the ignored `data/` and `models/` directories.

## Start the services

From the module directory, run `docker-compose up`. The stack starts PostgreSQL for metric storage, Adminer for database inspection, and Grafana for dashboards.

## Send data

Run `python evidently_metrics_calculation.py` to simulate batch monitoring. The script reads a daily slice, calculates Evidently metrics, and inserts a timestamped row into PostgreSQL at a fixed interval.

## Open the dashboard

Open `http://localhost:3000` and sign in with the credentials configured by the Compose example. Navigate to the provisioned dashboard and check the prediction-drift, missing-value, and drifted-column panels.

## Debug a batch

Open `debugging_nyc_taxi_data.ipynb` to run Evidently reports and test suites against a reference and current batch. Use the detailed output to investigate a dashboard alert.

## Stop the services

Run `docker-compose down` when finished, then review the Compose file before choosing whether to remove the local database volume.
