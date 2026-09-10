---
video_url: "https://www.youtube.com/watch?v=OVUPIX88q88&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK"
code:
  - label: "Duration prediction notebook"
    path: duration-prediction.ipynb
---

# Model Management

Experiment tracking covers the trials that create models. After we select a candidate, we keep its model and lineage together. We also keep the parameters and metrics so another person can evaluate and deploy it.

## From experiments to a model

The ML lifecycle moves from tuning to a decision about which model is ready for further use. At that point, we need to know which data and code produced it. We also need the parameters, evaluation results, and files that belong to it.

![Model management connecting experiments, parameters, metrics, and artifacts](images/04-model-management-01-lifecycle.jpg)

MLflow can log parameters, metrics, artifacts, and models. Its autologging integrations add common information for supported libraries, which reduces the amount of manual logging in a training script.

## Use autologging carefully

Autologging is useful when the library integration records the values you need. Check the resulting run instead of assuming that every important input was captured. Add explicit parameters for values such as data paths or preprocessing choices when they affect the result.

![MLflow autologging a model training run](images/04-model-management-02-autolog.jpg)

## Preserve lineage

The run should lead to the exact model artifact used later. Store the training and validation data references in one run. Add the model parameters, evaluation metric, and model file there as well. This gives deployment enough information to understand what it's serving.

![A model artifact and its recorded run information](images/04-model-management-03-artifact.jpg)
