import dataclasses
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

import pandas as pd

from evidently.calculation_engine.engine import Engine
from evidently.calculation_engine.python_engine import PythonEngine
from evidently.calculations import stattests
from evidently.core import ColumnType
from evidently.utils.numpy_encoder import add_type_mapping

StatTestFuncReturns = Tuple[float, bool]
StatTestFuncType = Callable[[pd.Series, pd.Series, ColumnType, float], StatTestFuncReturns]


@dataclasses.dataclass
class StatTestResult:
    drift_score: float
    drifted: bool
    actual_threshold: float


@dataclasses.dataclass
class StatTest:
    name: str
    display_name: str
    allowed_feature_types: List[ColumnType]
    default_threshold: float = 0.05

    def __call__(
        self,
        reference_data: Any,
        current_data: Any,
        feature_type: ColumnType,
        threshold: Optional[float],
        engine: Type[Engine] = PythonEngine,
        **kwargs,
    ) -> StatTestResult:
        actual_threshold = self.default_threshold if threshold is None else threshold
        impl = self._get_impl(engine)
        data = impl.data_type(reference_data=reference_data, current_data=current_data, **kwargs)
        p = impl(data, feature_type, actual_threshold)
        drift_score, drifted = p
        return StatTestResult(drift_score=drift_score, drifted=drifted, actual_threshold=actual_threshold)

    def _get_impl(self, engine: Type[Engine]):
        impl = _impls.get(self, {}).get(engine, None)
        if impl is None:
            raise NotImplementedError(f"'{self.name}' is not implemented for {engine}")
        return impl

    def __hash__(self):
        # hash by name, so stattests with same name would be the same.
        return hash(self.name)

    @property
    def func(self):
        """For backward compatibility"""
        impl = self._get_impl(PythonEngine)
        if isinstance(impl, PythonStatTestWrapper):
            return impl.func
        return AttributeError("StatTest.func is deprecated, please use __call__")


add_type_mapping((StatTest,), lambda obj: get_registered_stattest_name(obj))


@dataclasses.dataclass
class StatTestData:
    reference_data: Any
    current_data: Any


TStatTestData = TypeVar("TStatTestData", bound=StatTestData)
TStatTestEngine = TypeVar("TStatTestEngine", bound=Engine)


class StatTestImpl(Generic[TStatTestData, TStatTestEngine]):
    data_type: ClassVar[Type[TStatTestData]]

    def __call__(self, data: TStatTestData, feature_type: ColumnType, threshold: float) -> StatTestFuncReturns:
        raise NotImplementedError


_impls: Dict[StatTest, Dict[Type[Engine], StatTestImpl]] = {}


@dataclasses.dataclass
class PythonStatTestData(StatTestData):
    reference_data: pd.Series
    current_data: pd.Series


class PythonStatTest(StatTestImpl[PythonStatTestData, PythonEngine]):
    data_type = PythonStatTestData

    def __call__(self, data: PythonStatTestData, feature_type: ColumnType, threshold: float) -> StatTestFuncReturns:
        raise NotImplementedError


PossibleStatTestType = Union[str, StatTestFuncType, StatTest]

_registered_stat_tests: Dict[str, Dict[ColumnType, StatTest]] = {}
_registered_stat_test_funcs: Dict[StatTestFuncType, str] = {}


class PythonStatTestWrapper(PythonStatTest):
    def __init__(self, func: StatTestFuncType):
        self.func = func

    def __call__(self, data: PythonStatTestData, feature_type: ColumnType, threshold: float) -> StatTestFuncReturns:
        return self.func(data.reference_data, data.current_data, feature_type, threshold)


def create_impl_wrapper(func: StatTestFuncType):
    return PythonStatTestWrapper(func)


def register_stattest(stat_test: StatTest, default_impl: StatTestFuncType = None):
    _registered_stat_tests[stat_test.name] = {ft: stat_test for ft in stat_test.allowed_feature_types}
    _impls[stat_test] = {}
    if default_impl is not None:
        _impls[stat_test][PythonEngine] = create_impl_wrapper(default_impl)
        _registered_stat_test_funcs[default_impl] = stat_test.name


def _get_default_stattest(reference_data: pd.Series, current_data: pd.Series, feature_type: ColumnType) -> StatTest:
    n_values = pd.concat([reference_data, current_data]).nunique()
    if feature_type == ColumnType.Text:
        if reference_data.shape[0] > 1000:
            return stattests.abs_text_content_drift_stat_test
        return stattests.perc_text_content_drift_stat_test
    elif reference_data.shape[0] <= 1000:
        if feature_type == ColumnType.Numerical:
            if n_values <= 5:
                return stattests.chi_stat_test if n_values > 2 else stattests.z_stat_test
            elif n_values > 5:
                return stattests.ks_stat_test
        elif feature_type == ColumnType.Categorical:
            return stattests.chi_stat_test if n_values > 2 else stattests.z_stat_test
    elif reference_data.shape[0] > 1000:
        if feature_type == ColumnType.Numerical:
            n_values = pd.concat([reference_data, current_data]).nunique()
            if n_values <= 5:
                return stattests.jensenshannon_stat_test
            elif n_values > 5:
                return stattests.wasserstein_stat_test
        elif feature_type == ColumnType.Categorical:
            return stattests.jensenshannon_stat_test
    raise ValueError(f"Unexpected feature_type {feature_type}")


def get_stattest(
    reference_data: pd.Series,
    current_data: pd.Series,
    feature_type: Union[ColumnType, str],
    stattest_func: Optional[PossibleStatTestType],
) -> StatTest:
    if isinstance(feature_type, str):
        feature_type = ColumnType(feature_type)
    if stattest_func is None:
        return _get_default_stattest(reference_data, current_data, feature_type)
    return get_registered_stattest(stattest_func, feature_type)


def get_registered_stattest(
    stattest_func: Optional[PossibleStatTestType], feature_type: ColumnType = None, engine: Type[Engine] = None
) -> StatTest:
    if isinstance(stattest_func, StatTest):
        return stattest_func
    if callable(stattest_func) and stattest_func not in _registered_stat_test_funcs:
        stat_test = StatTest(
            name="",
            display_name=f"custom function '{stattest_func.__name__}'",
            allowed_feature_types=[],
        )
        add_stattest_impl(stat_test, engine or PythonEngine, create_impl_wrapper(stattest_func))
        return stat_test
    if callable(stattest_func) and stattest_func in _registered_stat_test_funcs:
        stattest_name = _registered_stat_test_funcs[stattest_func]
    elif isinstance(stattest_func, str):
        stattest_name = stattest_func
    else:
        raise ValueError(f"Unexpected type of stattest argument ({type(stattest_func)}), expected: str or Callable")
    funcs = _registered_stat_tests.get(stattest_name, None)
    if funcs is None or feature_type is None:
        raise StatTestNotFoundError(stattest_name)
    func = funcs.get(feature_type)
    if func is None:
        raise StatTestInvalidFeatureTypeError(stattest_name, feature_type)
    return func


def get_registered_stattest_name(stattest_func: Optional[PossibleStatTestType], feature_type: ColumnType = None) -> str:
    stattest_name = get_registered_stattest(stattest_func, feature_type).name
    if stattest_name:
        return stattest_name
    raise StatTestNotFoundError(f"No registered stattest for function {stattest_func}. Please register it")


class StatTestNotFoundError(ValueError):
    def __init__(self, stattest_name: str):
        super().__init__(
            f"No stattest found of name {stattest_name}. " f"Available stattests: {list(_registered_stat_tests.keys())}"
        )


class StatTestInvalidFeatureTypeError(ValueError):
    def __init__(self, stattest_name: str, feature_type: ColumnType):
        super().__init__(
            f"Stattest {stattest_name} isn't applicable to feature of type {feature_type.value}. "
            f"Available feature types: {list(_registered_stat_tests[stattest_name].keys())}"
        )


def add_stattest_impl(stattest: StatTest, engine: Type[Engine], impl: StatTestImpl):
    if stattest not in _impls:
        _impls[stattest] = {}
    _impls[stattest][engine] = impl
