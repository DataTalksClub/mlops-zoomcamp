# Module 5: Model Monitoring

We define production monitoring metrics and calculate Evidently results. We store them in PostgreSQL, then expose them through Grafana dashboards and debugging reports.

## 5.1 [Intro to ML Monitoring](01-ml-monitoring.md)

Separate service health, model performance, data quality, and drift indicators.

## 5.2 [Environment Setup](02-monitoring-environment.md)

Create the Python and Docker Compose environment for metric calculation, PostgreSQL, Adminer, and Grafana.

## 5.3 [Prepare Reference and Model](03-reference-model.md)

Train a baseline model and save the reference dataset used for later comparisons.

## 5.4 [Evidently Metrics Calculation](04-evidently-metrics.md)

Compare reference and current batches, then persist selected metrics for time-series monitoring.

## 5.5 [Evidently Monitoring Dashboard](05-evidently-dashboard.md)

Create a workspace for reports and model/data behavior.

## 5.6 [Dummy Monitoring](06-dummy-monitoring.md)

Test the database and dashboard path with repeatable synthetic values before adding model metrics.

## 5.7 [Data Quality Monitoring](07-data-quality.md)

Add data-quality checks, schedule metric calculations, and choose thresholds with model owners.

## 5.8 [Save Grafana Dashboard](08-save-grafana-dashboard.md)

Provision a saved Grafana dashboard from versioned JSON and configuration files.

## 5.9 [Debugging with Test Suites and Reports](09-debugging-tests-reports.md)

Use Evidently reports and test suites to investigate a monitoring metric.

## 5.10 [Monitoring Example](10-monitoring-example.md)

Run the local end-to-end monitoring stack with Docker Compose, PostgreSQL, and Grafana.

## Homework

More information is available in the [Module 5 homework](https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/cohorts/2025/05-monitoring/homework.md).

## Code and resources

The current requirements set Evidently to 0.6.7. Compare this code with the [Evidently 0.7 example](post-evidently-0.7) when updating the API.

- [Monitoring services](docker-compose.yml)
- [Metric calculation](evidently_metrics_calculation.py)
- [Dummy metric calculation](dummy_metrics_calculation.py)
- [Baseline model notebook](baseline_model_nyc_taxi_data.ipynb)
- [Debugging notebook](debugging_nyc_taxi_data.ipynb)

## Community Notes

Share community notes and resources below.

* [Week 5 notes by M. Ayoub C.](https://gist.github.com/Qfl3x/aa6b1bec35fb645ded0371c46e8aafd1)
* [Week 5 monitoring notes by Ayoub B.](https://github.com/ayoub-berdeddouch/mlops-journey/blob/main/monitoring-05.md)
* [Week 5 notes from 2023](https://github.com/dimzachar/mlops-zoomcamp/tree/master/notes/Week_5)
* [Why monitor models after deployment? by Hongfan](https://github.com/Muhongfan/MLops/blob/main/05-monitoring/README.md)
* [Week 5 detailed notes by Muhammad Shifa](https://github.com/MuhammadShifa/mlops-zoomcamp2025/blob/main/05-monitoring/README.md)
* Send a PR, add your notes above this line
