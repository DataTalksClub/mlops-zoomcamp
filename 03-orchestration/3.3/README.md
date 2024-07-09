## 3.3 Observability: Monitoring and alerting


## 1. Pipeline health monitoring

1. [sklearn training pipeline health](https://youtu.be/jwte-x3VwFE)

---

## 2. Explainability

### Videos

1. [Customize layout](https://youtu.be/Skr-WnxiQ8I)
1. [XGBoost explainability dashboard](https://youtu.be/BvGZTl-UUQY)

### Code

-   [`custom/dashboard_data_source.py`](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/custom/dashboard_data_source.py):
    this is used to produce the output needed to generate the SHAP values and chart them.
-   [SHAP values](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/charts/shap_values.py)
-   [SHAP values bar chart](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/charts/shap_values_bar.py)
-   [SHAP values force plot](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/charts/shap_values_force_chart.py)

---

## 3. Model performance dashboard

### Videos

1. [Overview dashboard for entire project](https://youtu.be/ScFZPSaOWK4)
1. [RMSE and MSE using time series chart](https://youtu.be/6kqHoxAL0DY)
1. [RMSE distribution using a histogram](https://youtu.be/GQMgCzI-Qrg)
1. [Training runs by model using bar chart](https://youtu.be/q4Quk6GeVRk)
1. [Training runs by model using pie chart](https://youtu.be/I5qR3OtASXs)

### Code

-   [Time series RMSE](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/charts/training_metrics__rmse_.py)
-   [Time series MSE](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/charts/time_series__mse_.py)
-   [Histogram](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/charts/distribution_of_performance_metrics.py)
-   [Runs by model](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/charts/total_runs_by_model.py)
-   [`data.py`](https://github.com/mage-ai/mlops/blob/master/mlops/utils/analytics/data.py)

---

## 4. Alerting

### Videos

1. [Setup email to send alerts](https://youtu.be/DjtE3webtjE)
1. [Setup pipeline alerting](https://youtu.be/H6D7zyqSQMw)

### Code

-   [Project `metadata.yaml`](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/metadata.yaml)

---

## Code

1. [sklearn training pipeline health](https://github.com/mage-ai/mlops/blob/master/mlops/presenters/pipelines/xgboost_training/dashboard/block_layout.yaml)
1. [XGBoost explainability dashboard](https://github.com/mage-ai/mlops/blob/master/mlops/presenters/pipelines/sklearn_training/dashboard/block_layout.yaml)
1. [Model performance dashboard configuration](https://github.com/mage-ai/mlops/blob/master/mlops/presenters/overview/dashboard/block_layout.yaml)

---

## Resources

1. [How to interpret ML models using SHAP values](https://www.mage.ai/blog/how-to-interpret-explain-machine-learning-models-using-shap-values)

1. [Customize dashboards for your project and pipelines](https://docs.mage.ai/visualizations/dashboards)

1. [Confusion matrix](https://www.mage.ai/blog/guide-to-model-metrics-p1-matrix-performance)

1. Set up alerts for pipeline run statuses:
    1. [Email](https://docs.mage.ai/integrations/observability/alerting-email)
    1. [Opsgenie](https://docs.mage.ai/integrations/observability/alerting-opsgenie)
    1. [Slack](https://docs.mage.ai/integrations/observability/alerting-slack)
    1. [Teams](https://docs.mage.ai/integrations/observability/alerting-teams)
    1. [Discord](https://docs.mage.ai/integrations/observability/alerting-discord)
    1. [Telegram](https://docs.mage.ai/integrations/observability/alerting-telegram)
