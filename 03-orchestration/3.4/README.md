# 3.4 Triggering: Inference and retraining


## 1. Retraining pipeline

### Videos

1. [Setup pipeline](https://youtu.be/ywzNac-OzFc)
1. [Trigger pipeline to run](https://youtu.be/6kcBWl3E8So)

### Code

-   [`detect_new_data.py`](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/sensors/detect_new_data.py)
-   [`custom/retrain/sklearn.py` block](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/custom/retrain/sklearn.py): trigger training pipeline for sklearn models
-   [`custom/retrain/xgboost.py` block](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/custom/retrain/xgboost.py): trigger training pipeline for XGBoost model

---

## 2. Inference pipeline

### Videos

1. [Make a prediction](https://youtu.be/KZaS2oG9NDc)
1. [Build pipeline](https://youtu.be/mytcFbH_ooY)
1. [Model inference playground part 1](https://youtu.be/JI0dhR7Bnhk)
1. [Model inference playground part 2](https://youtu.be/v2ls-gBBRac)
1. [Get prediction via API](https://youtu.be/J6ckSZczk8M)

### Code

-   [`custom/inference.py` block](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/custom/inference.py)

---

## Code

1. [Retraining pipeline `metadata.yaml`](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/pipelines/automatic_retraining/metadata.yaml)
1. [Inference pipeline `metadata.yaml`](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/pipelines/predict/metadata.yaml)
1. [Playground configuration settings](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/interactions/playground.yaml)

---

## Resources

1. [No-code UI interactions](https://docs.mage.ai/interactions/overview)

1. [Saving triggers in code](https://docs.mage.ai/orchestration/triggers/configure-triggers-in-code)

1. [Trigger another pipeline from a block](https://docs.mage.ai/orchestration/triggers/trigger-pipeline)

1. [Trigger pipeline via API endpoint](https://docs.mage.ai/orchestration/triggers/trigger-pipeline-api)

1. [Run pipelines on a recurring schedule](https://docs.mage.ai/orchestration/triggers/schedule-pipelines)

1. [Improving model performance through retraining](<https://www.mage.ai/blog/how-to-improve-the-performance-of-a-machine-learning-(ML)-model>)
