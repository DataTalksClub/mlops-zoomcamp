import abc
import functools
import logging
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from evidently import ColumnMapping
from evidently.base_metric import ErrorResult
from evidently.base_metric import GenericInputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.calculation_engine.metric_implementation import MetricImplementation
from evidently.features.generated_features import GeneratedFeature
from evidently.utils.data_preprocessing import DataDefinition

TMetricImplementation = TypeVar("TMetricImplementation", bound=MetricImplementation)
TInputData = TypeVar("TInputData")


class Engine(Generic[TMetricImplementation, TInputData]):
    def __init__(self):
        self.metrics = []
        self.tests = []

    def set_metrics(self, metrics):
        self.metrics = metrics

    def set_tests(self, tests):
        self.tests = tests

    def execute_metrics(self, context, data: GenericInputData):
        calculations: Dict[Metric, Union[ErrorResult, MetricResult]] = {}
        converted_data = self.convert_input_data(data)
        context.features = self.generate_additional_features(converted_data)
        context.data = converted_data
        for metric, calculation in self.get_metric_execution_iterator():
            if calculation not in calculations:
                logging.debug(f"Executing {type(calculation)}...")
                try:
                    calculations[metric] = calculation.calculate(context, converted_data)
                except BaseException as ex:
                    calculations[metric] = ErrorResult(exception=ex)
            else:
                logging.debug(f"Using cached result for {type(calculation)}")
            context.metric_results[metric] = calculations[metric]

    @abc.abstractmethod
    def convert_input_data(self, data: GenericInputData) -> TInputData:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_data_definition(
        self,
        current_data,
        reference_data,
        column_mapping: ColumnMapping,
        categorical_features_cardinality: Optional[int] = None,
    ):
        raise NotImplementedError()

    @abc.abstractmethod
    def generate_additional_features(self, data: TInputData):
        raise NotImplementedError

    def get_metric_implementation(self, metric):
        """
        Get engine specific metric implementation.
        """
        impl = _ImplRegistry.get(type(self), {}).get(type(metric))
        if impl is None:
            return None
        return impl(self, metric)

    def get_metric_execution_iterator(self) -> List[Tuple[Metric, TMetricImplementation]]:
        aggregated: Dict[Type[Metric], List[Metric]] = functools.reduce(_aggregate_metrics, self.metrics, {})
        metric_to_calculations = {}
        for metric_type, metrics in aggregated.items():
            metrics_by_parameters: Dict[tuple, List[Metric]] = functools.reduce(_aggregate_by_parameters, metrics, {})

            for metric in metrics:
                parameters = metric.get_parameters()
                if parameters is None:
                    metric_to_calculations[metric] = metric
                else:
                    metric_to_calculations[metric] = metrics_by_parameters[parameters][0]

        return [(metric, self.get_metric_implementation(metric_to_calculations[metric])) for metric in self.metrics]

    def form_datasets(
        self,
        data: Optional[TInputData],
        features: Optional[Dict[tuple, GeneratedFeature]],
        data_definition: DataDefinition,
    ):
        raise NotImplementedError()


def _aggregate_metrics(agg, item):
    agg[type(item)] = agg.get(type(item), []) + [item]
    return agg


def _aggregate_by_parameters(agg: dict, metric: Metric) -> dict:
    agg[metric.get_parameters()] = agg.get(metric.get_parameters(), []) + [metric]
    return agg


_ImplRegistry: Dict[Type, Dict[Type, Type]] = dict()


def metric_implementation(metric_cls):
    """
    Decorate metric implementation class, as a implementation for specific metric.
    """

    def wrapper(cls: Type[MetricImplementation]):
        _add_implementation(metric_cls, cls)
        return cls

    return wrapper


def _add_implementation(metric_cls, cls):
    engines = cls.supported_engines()
    for engine in engines:
        engine_impls = _ImplRegistry.get(engine, {})
        if metric_cls in engine_impls:
            raise ValueError(
                f"Multiple impls of metric {metric_cls}: {engine_impls[metric_cls]}"
                f" already set, but trying to set {cls}"
            )
        engine_impls[metric_cls] = cls
        _ImplRegistry[engine] = engine_impls
    return cls
