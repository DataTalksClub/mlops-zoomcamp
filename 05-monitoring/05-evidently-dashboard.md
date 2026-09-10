---
video_url: "https://www.youtube.com/watch?v=zjvYhDPzFlY&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK"
code:
  - label: "Baseline model notebook"
    path: baseline_model_nyc_taxi_data.ipynb
  - label: "Grafana Compose stack"
    path: docker-compose.yml
---

# Evidently Monitoring Dashboard

An Evidently report is useful for one comparison. A monitoring dashboard makes the same measurements visible over time and gives the team a place to look at recent batches.

## Create a project and workspace

The Evidently dashboard example creates a project, adds reports to a workspace, and previews the result before publishing it. Start with a small report so you can verify the column mapping and metric values before adding more panels.

![The notebook creating an Evidently dashboard project](images/05-evidently-dashboard-01-project.jpg)

Add reports for the reference and current batches. The workspace stores the report history, while the dashboard presents selected metrics such as prediction drift, missing values, and the number of drifted columns.

![An Evidently report added to the workspace](images/05-evidently-dashboard-02-report.jpg)

## Select useful panels

Use these panel types to answer an operational question:

- a trend panel that shows whether a metric is changing.
- a counter that shows the current number of drifted columns.
- a data-quality panel that highlights missing or invalid values.

![Data-quality information in the Evidently dashboard](images/05-evidently-dashboard-03-data-quality.jpg)

The dashboard complements Grafana rather than replacing it. Evidently keeps the comparison details, while Grafana is a convenient place to combine monitoring metrics with database-backed alerting.
