---
video_url: "https://www.youtube.com/watch?v=s3G4PMsOMOA&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK"
code:
  - label: "Dummy metric calculation"
    path: dummy_metrics_calculation.py
  - label: "Monitoring Compose stack"
    path: docker-compose.yml
---

# Dummy Monitoring

Before connecting real model metrics, test the storage and dashboard path with synthetic values. Dummy monitoring isolates infrastructure problems from model and data problems.

## Create and populate the table

The example creates a PostgreSQL database and a `dummy_metrics` table. Each iteration generates a timestamp, a numeric value, a UUID string, and a random float. It then inserts the row into PostgreSQL.

![The script that generates dummy monitoring values](images/06-dummy-monitoring-01-script.jpg)

Connect with `psycopg` and use an explicit table schema. Confirm that the database exists and that the insert works before opening Grafana.

![The database setup used by the dummy metrics script](images/06-dummy-monitoring-02-database.jpg)

## Check the dashboard loop

Run the script at a fixed interval and look at the rows in the database. Configure Grafana with PostgreSQL as a data source. Build a panel over the timestamp column, then verify that new points appear without a manual refresh.

![The repeated metric-generation loop](images/06-dummy-monitoring-03-loop.jpg)

Once this path works, replace the synthetic values with Evidently results while keeping the database and dashboard connection stable.
