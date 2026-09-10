---
video_url: "https://www.youtube.com/watch?v=SQ0jBwd_3kk&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK"
---

# Intro to ML Monitoring

Monitoring starts after a model is deployed. A production model can keep responding while its inputs, outputs, or business value quietly change, so operational metrics alone aren't enough.

## Four groups of monitoring metrics

The course introduces four useful groups of monitoring metrics:

- service health, such as uptime and request failures.
- model performance, such as an error metric when labels arrive.
- data quality and integrity, such as missing or invalid values.
- data drift and concept drift, which describe input changes and changes in the input-target relationship.

![A monitoring checklist for service health and model performance](images/01-ml-monitoring-01-health.jpg)

The exact performance metric depends on the task. Regression uses measures such as mean absolute error or root mean squared error. Classification may use precision, recall, or ranking metrics. Monitoring should use the metric that reflects the product requirement rather than a generic score.

![Metrics for monitoring a model and its data](images/01-ml-monitoring-02-metrics.jpg)

## Compare production with a reference

Many model checks compare a current batch with a reference dataset. We use a reference period in which the model and data behaved acceptably. A large change is evidence to investigate, not proof that the model is wrong.

![A monitoring scheme connecting data, predictions, and dashboards](images/01-ml-monitoring-03-scheme.jpg)

Good monitoring turns a vague concern into an actionable result. Define thresholds, store the measurements, and decide who investigates when a check fails.
