import abc
import logging
from typing import Dict
from typing import Generic
from typing import Optional
from typing import TypeVar

import pandas as pd

from evidently import ColumnMapping
from evidently.base_metric import GenericInputData
from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.calculation_engine.engine import Engine
from evidently.calculation_engine.metric_implementation import MetricImplementation
from evidently.features.generated_features import GeneratedFeature
from evidently.utils.data_preprocessing import DataDefinition
from evidently.utils.data_preprocessing import create_data_definition


class PythonInputData(InputData):
    pass


TMetric = TypeVar("TMetric", bound=Metric)


class PythonEngine(Engine["PythonMetricImplementation", PythonInputData]):
    def convert_input_data(self, data: GenericInputData) -> PythonInputData:
        if not isinstance(data.current_data, pd.DataFrame) or (
            data.reference_data is not None and not isinstance(data.reference_data, pd.DataFrame)
        ):
            raise ValueError("PandasEngine works only with pd.DataFrame input data")
        return PythonInputData(
            data.reference_data,
            data.current_data,
            current_additional_features=None,
            reference_additional_features=None,
            column_mapping=data.column_mapping,
            data_definition=data.data_definition,
            additional_data=data.additional_data,
        )

    def get_data_definition(
        self,
        current_data,
        reference_data,
        column_mapping: ColumnMapping,
        categorical_features_cardinality: Optional[int] = None,
    ):
        if not isinstance(current_data, pd.DataFrame) or (
            reference_data is not None and not isinstance(reference_data, pd.DataFrame)
        ):
            raise ValueError("PandasEngine works only with pd.DataFrame input data")
        return create_data_definition(reference_data, current_data, column_mapping, categorical_features_cardinality)

    def generate_additional_features(self, data: PythonInputData):
        curr_additional_data = None
        ref_additional_data = None
        features = {}
        for metric, calculation in self.get_metric_execution_iterator():
            try:
                required_features = metric.required_features(data.data_definition)
            except Exception as e:
                logging.error(f"failed to get features for {type(metric)}: {e}", exc_info=e)
                continue
            for feature in required_features:
                params = feature.get_parameters()
                if params is not None:
                    _id = (type(feature), params)
                    if _id in features:
                        continue
                    features[_id] = feature
                feature_data = feature.generate_feature(data.current_data, data.data_definition)
                feature_data.columns = [f"{feature.__class__.__name__}.{old}" for old in feature_data.columns]
                if curr_additional_data is None:
                    curr_additional_data = feature_data
                else:
                    curr_additional_data = curr_additional_data.join(feature_data)
                if data.reference_data is None:
                    continue
                ref_feature_data = feature.generate_feature(data.reference_data, data.data_definition)
                ref_feature_data.columns = [f"{feature.__class__.__name__}.{old}" for old in ref_feature_data.columns]

                if ref_additional_data is None:
                    ref_additional_data = ref_feature_data
                else:
                    ref_additional_data = ref_additional_data.join(ref_feature_data)
        data.current_additional_features = curr_additional_data
        data.reference_additional_features = ref_additional_data
        return features

    def get_metric_implementation(self, metric):
        impl = super().get_metric_implementation(metric)
        if impl is None and isinstance(metric, Metric):

            class _Wrapper(PythonMetricImplementation):
                def calculate(self, context, data: PythonInputData):
                    return self.metric.calculate(data)

            return _Wrapper(self, metric)
        return impl

    def form_datasets(
        self,
        data: Optional[PythonInputData],
        features: Optional[Dict[tuple, GeneratedFeature]],
        data_definition: DataDefinition,
    ):
        if data is None:
            return None, None
        if features is not None:
            rename = {x.feature_name().name: x.feature_name().display_name for x in features.values()}
        else:
            rename = {}
        current = data.current_data
        if data.current_additional_features is not None:
            current = data.current_data.join(data.current_additional_features)

        current = current.rename(columns=rename)
        reference = data.reference_data
        if data.reference_data is not None and data.reference_additional_features is not None:
            reference = data.reference_data.join(data.reference_additional_features)

        if reference is not None:
            reference = reference.rename(columns=rename)

        return reference, current


class PythonMetricImplementation(Generic[TMetric], MetricImplementation):
    def __init__(self, engine: PythonEngine, metric: TMetric):
        self.engine = engine
        self.metric = metric

    @abc.abstractmethod
    def calculate(self, context, data: PythonInputData):
        raise NotImplementedError

    @classmethod
    def supported_engines(cls):
        return (PythonEngine,)
