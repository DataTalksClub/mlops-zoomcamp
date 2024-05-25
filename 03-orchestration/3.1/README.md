# 3.1 Data preparation: ETL and feature engineering

<a href="https://youtube.com/playlist?list=PLBpweK9KQBJ5rtIbCikq_FCQhqgkvY3rt&si=S17dKrYkgM2EL5d4">
  <img src="https://github.com/mage-ai/assets/blob/main/mlops/1-data.png?raw=true">
</a>

## 1. Ingest raw data

### Videos

1. [Setup new project](https://youtu.be/7hKrQmoARD8)
1. [Utility helper functions](https://youtu.be/FBh3P19lXj4)
1. [Ingest data block](https://youtu.be/Ttfkry1QQD4)

### Code

-   [`cleaning.py`](https://github.com/mage-ai/mlops/blob/master/mlops/utils/data_preparation/cleaning.py)
-   [`feature_selector.py`](https://github.com/mage-ai/mlops/blob/master/mlops/utils/data_preparation/feature_selector.py)
-   [`splitters.py`](https://github.com/mage-ai/mlops/blob/master/mlops/utils/data_preparation/splitters.py)
-   [`ingest.py`](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/data_loaders/ingest.py)

---

## 2. Prepare data for training

### Videos

1. [Data preparation block](https://youtu.be/TcTMVn3BxeY)
1. [Visualize prepared data](https://youtu.be/j0Hfaoc5wRY)

### Code

-   [`prepare.py`](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/transformers/prepare.py)

---

## 3. Build training sets

### Videos

1. [Encoding functions](https://youtu.be/z8erMV-6joY)
1. [Training set block](https://youtu.be/qSzcfSHjJoY)

### Code

-   [`encoders.py`](https://github.com/mage-ai/mlops/blob/master/mlops/utils/data_preparation/encoders.py)
-   [`build.py`](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/data_exporters/build.py)

---

## 4. Data validations using built-in testing framework

### Videos

1. [Writing data validations](https://youtu.be/tYPAl4Q8kpw)

### Code

-   [`build.py`](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/data_exporters/build.py)

---

## Code

1. [Complete code solution](https://github.com/mage-ai/mlops)
1. [Pipeline configuration](https://github.com/mage-ai/mlops/blob/master/mlops/unit_3_observability/pipelines/data_preparation/metadata.yaml)

---

## Resources

1. [Global Data Products](https://docs.mage.ai/orchestration/global-data-products/overview)

1. [Data validations using built-in testing framework](https://docs.mage.ai/development/data-validation)

1. [Data quality checks with Great Expectations integration](https://docs.mage.ai/development/testing/great-expectations)

1. [Unit tests](https://docs.mage.ai/development/testing/unit-tests)

1. [Feature encoding](https://www.mage.ai/blog/qualitative-data)
