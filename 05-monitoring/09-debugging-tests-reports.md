---
video_url: "https://www.youtube.com/watch?v=sNSk3ojISh8&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK"
code:
  - label: "Debugging notebook"
    path: debugging_nyc_taxi_data.ipynb
---

# Debugging with Test Suites and Reports

Monitoring tells us that something changed. Debugging uses reports and test suites to narrow down what changed and whether the difference crosses an agreed threshold.

## Look at the dashboard metric

Start with the metric that triggered the investigation. Prediction drift, the number of drifted columns, and missing-value share can show different problems. Check the time window and compare it with deployments or upstream data changes.

![The debugging notebook and Grafana view](images/09-debugging-01-suite.jpg)

## Run a test suite

Evidently test suites turn expectations into pass or fail results. A data-drift preset can check several columns, while individual tests can focus on a known risk. Run the suite with the same reference and current data used by the monitoring job.

![Individual monitoring tests in the debugging workflow](images/09-debugging-02-tests.jpg)

The report gives more detail than a single time-series point. Use it to identify which column or distribution failed, then check the raw batch and the feature-preparation code.

![A debugging report with test results](images/09-debugging-03-report.jpg)

Keep the test thresholds versioned. A threshold change is a monitoring-policy change and should be reviewable alongside model or data-pipeline changes.
