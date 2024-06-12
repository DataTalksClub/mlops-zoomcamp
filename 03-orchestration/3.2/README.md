# 3.2 Training: sklearn models and XGBoost


## 1. Training pipeline for sklearn models

### Videos

1. [GDP training set](https://youtu.be/KP68DuJnk4Q?si=tVHWYLCpZ2RpwuNh)
1. [Sklearn training GDP](https://youtu.be/CbHaZcq_uGo)
1. [Load models](https://youtu.be/zsMHFq2C978)
1. [Utility helper functions for loading models](https://youtu.be/fZnxDhtPxYo)
1. [Hyperparameter tuning](https://youtu.be/zfBB4KoZ7TM)
1. [Train sklearn model](https://youtu.be/P7PtegUFk3k)

### Code

-   [`utils/models/sklearn.py`](https://github.com/mage-ai/mlops/blob/master/mlops/utils/models/sklearn.py)
-   [`custom/load_models.py` block](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/custom/load_models.py): load sklearn models dynamically
-   [`transformers/hyperparameter_tuning/sklearn.py`](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/transformers/hyperparameter_tuning/sklearn.py)
-   [`data_exporters/sklearn.py`](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/data_exporters/sklearn.py)
-   [`hyperparameters/shared.py`](https://github.com/mage-ai/mlops/blob/master/mlops/utils/hyperparameters/shared.py)

---

## 2. Training pipeline for XGBoost model

### Videos

1. [Hyperparameter tuning](https://youtu.be/K_Z2Lm1Cyu4)
1. [Train XGBoost model](https://youtu.be/Y2B-ivm7Mug)

### Code

-   [`utils/models/xgboost.py`](https://github.com/mage-ai/mlops/blob/master/mlops/utils/models/xgboost.py)
-   [`transformers/hyperparameter_tuning/xgboost.py`](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/transformers/hyperparameter_tuning/xgboost.py)
-   [`data_exporters/xgboost.py`](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/data_exporters/xgboost.py)
-   [`hyperparameters/shared.py`](https://github.com/mage-ai/mlops/blob/master/mlops/utils/hyperparameters/shared.py)

---

## Code

1. [Complete code solution](https://github.com/mage-ai/mlops)
1. [sklearn training pipeline configuration](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/pipelines/sklearn_training/metadata.yaml)
1. [XGBoost training pipeline configuration](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/pipelines/xgboost_training/metadata.yaml)

---

## Resources

1. [Accuracy, precision, recall](https://www.mage.ai/blog/definitive-guide-to-accuracy-precision-recall-for-product-developers)

1. [Regression model performance metrics](https://www.mage.ai/blog/product-developers-guide-to-ml-regression-model-metrics)
