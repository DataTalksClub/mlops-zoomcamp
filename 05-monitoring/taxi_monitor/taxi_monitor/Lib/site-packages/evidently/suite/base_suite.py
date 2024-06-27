import abc
import copy
import dataclasses
import json
import logging
import uuid
from datetime import datetime
from typing import IO
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

import ujson

import evidently
from evidently import ColumnMapping
from evidently._pydantic_compat import UUID4
from evidently._pydantic_compat import BaseModel
from evidently._pydantic_compat import parse_obj_as
from evidently.base_metric import ErrorResult
from evidently.base_metric import GenericInputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.calculation_engine.engine import Engine
from evidently.core import IncludeOptions
from evidently.features.generated_features import GeneratedFeature
from evidently.options.base import AnyOptions
from evidently.options.base import Options
from evidently.renderers.base_renderer import DEFAULT_RENDERERS
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import RenderersDefinitions
from evidently.renderers.base_renderer import TestRenderer
from evidently.renderers.notebook_utils import determine_template
from evidently.tests.base_test import Test
from evidently.tests.base_test import TestParameters
from evidently.tests.base_test import TestResult
from evidently.tests.base_test import TestStatus
from evidently.utils import NumpyEncoder
from evidently.utils.dashboard import SaveMode
from evidently.utils.dashboard import SaveModeMap
from evidently.utils.dashboard import TemplateParams
from evidently.utils.dashboard import save_data_file
from evidently.utils.dashboard import save_lib_files
from evidently.utils.data_preprocessing import DataDefinition

USE_UJSON = False


@dataclasses.dataclass
class State:
    name: str


class States:
    Init = State("Init")
    AdditionalFeatures = State("AdditionalFeatures")
    Verified = State("Verified")
    Calculated = State("Calculated")
    Tested = State("Tested")


def find_test_renderer(obj, renderers: RenderersDefinitions) -> TestRenderer:
    predefined = renderers.typed_renderers.get(obj, None)
    if predefined:
        return predefined
    if issubclass(obj, Test) and renderers.default_html_test_renderer:
        return renderers.default_html_test_renderer
    raise KeyError(f"No renderer found for {obj}")


def find_metric_renderer(obj, renderers: RenderersDefinitions) -> MetricRenderer:
    predefined = renderers.typed_renderers.get(obj, None)
    if predefined:
        return predefined
    if renderers.default_html_metric_renderer:
        return renderers.default_html_metric_renderer
    raise KeyError(f"No renderer found for {obj}")


def _discover_dependencies(test: Union[Metric, Test]) -> Iterator[Tuple[str, Union[Metric, Test]]]:
    if hasattr(test, "__evidently_dependencies__"):
        yield from test.__evidently_dependencies__()  # type: ignore[union-attr]
        return
    for field_name, field in test.__dict__.items():
        if issubclass(type(field), (Metric, Test)):
            yield field_name, field


@dataclasses.dataclass
class Context:
    """Pipeline execution context tracks pipeline execution and lifecycle"""

    engine: Optional[Engine]
    metrics: list
    tests: list
    metric_results: Dict[Metric, Union[MetricResult, ErrorResult]]
    test_results: Dict[Test, TestResult]
    state: State
    renderers: RenderersDefinitions
    data: Optional[GenericInputData] = None
    features: Optional[Dict[tuple, GeneratedFeature]] = None
    options: Options = Options()
    data_definition: Optional["DataDefinition"] = None

    def get_data_definition(
        self,
        current_data,
        reference_data,
        column_mapping: ColumnMapping,
        categorical_features_cardinality: Optional[int] = None,
    ) -> DataDefinition:
        if self.data_definition is None:
            if self.engine is None:
                raise ValueError("Cannot create data definition when engine is not set")
            self.data_definition = self.engine.get_data_definition(
                current_data, reference_data, column_mapping, categorical_features_cardinality
            )
        return self.data_definition

    def get_datasets(self):
        return self.engine.form_datasets(self.data, self.features, self.data_definition)


class ContextPayload(BaseModel):
    metrics: List[Metric]
    metric_results: List[Union[MetricResult, ErrorResult]]
    tests: List[Test]
    test_results: List[TestResult]
    options: Options = Options()
    data_definition: Optional[DataDefinition]

    @classmethod
    def from_context(cls, context: Context):
        return cls(
            metrics=list(context.metric_results.keys()),
            metric_results=list(context.metric_results.values()),
            tests=list(context.test_results.keys()),
            test_results=list(context.test_results.values()),
            options=context.options,
            data_definition=context.data_definition,
        )

    def to_context(self) -> Context:
        ctx = Context(
            None,
            metrics=self.metrics,
            tests=self.tests,
            metric_results={m: mr for m, mr in zip(self.metrics, self.metric_results)},
            test_results={t: tr for t, tr in zip(self.tests, self.test_results)},
            state=States.Calculated,
            renderers=DEFAULT_RENDERERS,
            options=self.options,
            data_definition=self.data_definition,
        )
        for m in ctx.metrics:
            m.set_context(ctx)
            for _, dep in _discover_dependencies(m):
                dep.set_context(ctx)
        for t in ctx.tests:
            t.set_context(ctx)
            for _, dep in _discover_dependencies(t):
                dep.set_context(ctx)
        return ctx


class ExecutionError(Exception):
    pass


class Display:
    @abc.abstractmethod
    def _build_dashboard_info(self):
        raise NotImplementedError()

    def _repr_html_(self):
        dashboard_id, dashboard_info, graphs = self._build_dashboard_info()
        template_params = TemplateParams(
            dashboard_id=dashboard_id,
            dashboard_info=dashboard_info,
            additional_graphs=graphs,
        )
        return self._render(determine_template("auto"), template_params)

    def show(self, mode="auto"):
        """
        Keyword arguments:
        `mode` - Deprecated.

        Now you should call
        this function without any args, like: `.show()`
        """
        dashboard_id, dashboard_info, graphs = self._build_dashboard_info()
        template_params = TemplateParams(
            dashboard_id=dashboard_id,
            dashboard_info=dashboard_info,
            additional_graphs=graphs,
        )
        # pylint: disable=import-outside-toplevel
        try:
            from IPython.display import HTML

            return HTML(self._render(determine_template(mode), template_params))
        except ImportError as err:
            raise Exception("Cannot import HTML from IPython.display, no way to show html") from err

    def get_html(self):
        dashboard_id, dashboard_info, graphs = self._build_dashboard_info()
        template_params = TemplateParams(
            dashboard_id=dashboard_id,
            dashboard_info=dashboard_info,
            additional_graphs=graphs,
        )
        return self._render(determine_template("inline"), template_params)

    def save_html(self, filename: Union[str, IO], mode: Union[str, SaveMode] = SaveMode.SINGLE_FILE):
        dashboard_id, dashboard_info, graphs = self._build_dashboard_info()
        if isinstance(mode, str):
            _mode = SaveModeMap.get(mode)
            if _mode is None:
                raise ValueError(f"Unexpected save mode {mode}. Expected [{','.join(SaveModeMap.keys())}]")
            mode = _mode
        if mode == SaveMode.SINGLE_FILE:
            template_params = TemplateParams(
                dashboard_id=dashboard_id,
                dashboard_info=dashboard_info,
                additional_graphs=graphs,
            )
            render = self._render(determine_template("inline"), template_params)
            if isinstance(filename, str):
                with open(filename, "w", encoding="utf-8") as out_file:
                    out_file.write(render)
            else:
                filename.write(render)
        else:
            if not isinstance(filename, str):
                raise ValueError("Only singlefile save mode supports streams")
            font_file, lib_file = save_lib_files(filename, mode)
            data_file = save_data_file(filename, mode, dashboard_id, dashboard_info, graphs)
            template_params = TemplateParams(
                dashboard_id=dashboard_id,
                dashboard_info=dashboard_info,
                additional_graphs=graphs,
                embed_lib=False,
                embed_data=False,
                embed_font=False,
                font_file=font_file,
                include_js_files=[lib_file, data_file],
            )
            with open(filename, "w", encoding="utf-8") as out_file:
                out_file.write(self._render(determine_template("inline"), template_params))

    @abc.abstractmethod
    def as_dict(
        self,
        include_render: bool = False,
        include: Dict[str, IncludeOptions] = None,
        exclude: Dict[str, IncludeOptions] = None,
        **kwargs,
    ) -> dict:
        raise NotImplementedError

    def _get_json_content(
        self,
        include_render: bool = False,
        include: Dict[str, IncludeOptions] = None,
        exclude: Dict[str, IncludeOptions] = None,
        **kwargs,
    ) -> dict:
        """Return all data for json representation"""
        result = {"version": evidently.__version__}
        result.update(self.as_dict(include_render=include_render, include=include, exclude=exclude, **kwargs))
        return result

    def json(
        self,
        include_render: bool = False,
        include: Dict[str, IncludeOptions] = None,
        exclude: Dict[str, IncludeOptions] = None,
        **kwargs,
    ) -> str:
        return json.dumps(
            self._get_json_content(include_render=include_render, include=include, exclude=exclude, **kwargs),
            cls=NumpyEncoder,
            allow_nan=True,
        )

    def save_json(
        self,
        filename,
        include_render: bool = False,
        include: Dict[str, IncludeOptions] = None,
        exclude: Dict[str, IncludeOptions] = None,
    ):
        with open(filename, "w", encoding="utf-8") as out_file:
            json.dump(
                self._get_json_content(include_render=include_render, include=include, exclude=exclude),
                out_file,
                cls=NumpyEncoder,
            )

    def _render(self, temple_func, template_params: TemplateParams):
        return temple_func(params=template_params)


class Suite:
    context: Context

    def __init__(self, options: Options):
        self.context = Context(
            engine=None,
            metrics=[],
            tests=[],
            metric_results={},
            test_results={},
            state=States.Init,
            renderers=DEFAULT_RENDERERS,
            options=options,
        )

    def set_engine(self, engine: Engine):
        self.context.engine = engine

    def add_test(self, test: Test):
        test.set_context(self.context)
        for field_name, dependency in _discover_dependencies(test):
            if isinstance(dependency, Metric):
                self.add_metric(dependency)

            if isinstance(dependency, Test):
                dependency_copy = copy.copy(dependency)
                test.__setattr__(field_name, dependency_copy)
                self.add_test(dependency_copy)
        self.context.tests.append(test)
        self.context.state = States.Init

    def add_metric(self, metric: Metric):
        metric.set_context(self.context)

        for field_name, dependency in _discover_dependencies(metric):
            if isinstance(dependency, Metric):
                self.add_metric(dependency)

            if isinstance(dependency, Test):
                dependency_copy = copy.copy(dependency)
                metric.__setattr__(field_name, dependency_copy)
                self.add_test(dependency_copy)
        self.context.metrics.append(metric)
        self.context.state = States.Init

    def verify(self):
        self.context.engine.set_metrics(self.context.metrics)
        self.context.engine.set_tests(self.context.tests)
        self.context.state = States.Verified

    def run_calculate(self, data: GenericInputData):
        if self.context.state in [States.Init]:
            self.verify()

        if self.context.state in [States.Calculated, States.Tested]:
            return

        self.context.metric_results = {}
        if self.context.engine is not None:
            self.context.engine.execute_metrics(self.context, data)

        self.context.state = States.Calculated

    def run_checks(self):
        if self.context.state in [States.Init, States.Verified]:
            raise ExecutionError("No calculation was made, run 'run_calculate' first'")

        test_results = {}

        for test in self.context.tests:
            try:
                logging.debug(f"Executing {type(test)}...")
                test_result = test.check()
                if not test.is_critical and test_result.status == TestStatus.FAIL:
                    test_result.status = TestStatus.WARNING
                test_results[test] = test_result
            except BaseException as ex:
                test_results[test] = TestResult(
                    name=test.name,
                    status=TestStatus.ERROR,
                    group=test.group,
                    description=f"Test failed with exceptions: {ex}",
                    parameters=TestParameters(),
                    exception=ex,
                )

        self.context.test_results = test_results
        self.context.state = States.Tested

    def raise_for_error(self):
        for result in self.context.metric_results.values():
            if isinstance(result, ErrorResult):
                raise result.exception
        for result in self.context.test_results.values():
            if result.exception is not None:
                raise result.exception

    def reset(self):
        self.context = Context(
            engine=None,
            metrics=[],
            tests=[],
            metric_results={},
            test_results={},
            state=States.Init,
            renderers=DEFAULT_RENDERERS,
            options=self.context.options,
        )


MetadataValueType = Union[str, Dict[str, str], List[str]]


class Snapshot(BaseModel):
    id: UUID4
    name: Optional[str] = None
    timestamp: datetime
    metadata: Dict[str, MetadataValueType]
    tags: List[str]
    suite: ContextPayload
    metrics_ids: List[int] = []
    test_ids: List[int] = []
    options: Options

    def save(self, filename):
        with open(filename, "w") as f:
            if USE_UJSON:
                ujson.dump(self.dict(), f, indent=2, default=NumpyEncoder().default)
            else:
                json.dump(self.dict(), f, indent=2, cls=NumpyEncoder)

    @classmethod
    def load(cls, filename):
        with open(filename, "r") as f:
            return parse_obj_as(Snapshot, json.load(f))

    @property
    def is_report(self):
        return len(self.metrics_ids) > 0

    def as_report(self):
        from evidently.report import Report

        return Report._parse_snapshot(self)

    def as_test_suite(self):
        from evidently.test_suite import TestSuite

        return TestSuite._parse_snapshot(self)

    def first_level_metrics(self) -> List[Metric]:
        return [self.suite.metrics[i] for i in self.metrics_ids]

    def first_level_tests(self) -> List[Test]:
        return [self.suite.tests[i] for i in self.test_ids]


T = TypeVar("T", bound="ReportBase")


class ReportBase(Display):
    _inner_suite: Suite
    # collection of all possible common options
    options: Options
    id: uuid.UUID
    name: Optional[str] = None
    timestamp: datetime
    metadata: Dict[str, MetadataValueType] = {}
    tags: List[str] = []

    def __init__(self, options: AnyOptions = None, timestamp: Optional[datetime] = None, name: str = None):
        self.name = name
        self.options = Options.from_any_options(options)
        self.timestamp = timestamp or datetime.now()

    def _get_json_content(
        self,
        include_render: bool = False,
        include: Dict[str, IncludeOptions] = None,
        exclude: Dict[str, IncludeOptions] = None,
        **kwargs,
    ) -> dict:
        res = super()._get_json_content(include_render, include, exclude, **kwargs)
        res["timestamp"] = str(self.timestamp)
        return res

    def _get_snapshot(self) -> Snapshot:
        ctx = self._inner_suite.context
        suite = ContextPayload.from_context(ctx)
        return Snapshot(
            id=self.id,
            name=self.name,
            suite=suite,
            timestamp=self.timestamp,
            metadata=self.metadata,
            tags=self.tags,
            options=self.options,
        )

    @classmethod
    @abc.abstractmethod
    def _parse_snapshot(cls: Type[T], payload: Snapshot) -> T:
        raise NotImplementedError

    def save(self, filename) -> None:
        """Save state to file (experimental)"""
        self._get_snapshot().save(filename)

    @classmethod
    def load(cls: Type[T], filename) -> T:
        """Load state from file (experimental)"""
        return cls._parse_snapshot(Snapshot.load(filename))

    def to_snapshot(self):
        try:
            self._inner_suite.raise_for_error()
        except Exception as e:
            raise ValueError("Cannot create snapshot because of calculation error") from e
        return self._get_snapshot()

    def datasets(self):
        datasets = self._inner_suite.context.get_datasets()
        return datasets
