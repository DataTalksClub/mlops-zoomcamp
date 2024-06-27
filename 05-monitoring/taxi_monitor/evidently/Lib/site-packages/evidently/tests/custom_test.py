from typing import Callable
from typing import ClassVar
from typing import List
from typing import Optional
from typing import Union

from evidently.base_metric import InputData
from evidently.metrics.custom_metric import CustomValueMetric
from evidently.tests.base_test import BaseCheckValueTest
from evidently.tests.base_test import GroupData
from evidently.tests.base_test import GroupingTypes
from evidently.utils.types import Numeric
from evidently.utils.types import NumericApprox

CUSTOM_GROUP = GroupData("custom", "Custom", "")
GroupingTypes.TestGroup.add_value(CUSTOM_GROUP)


class CustomValueTest(BaseCheckValueTest):
    name: ClassVar = "Custom Value test"
    group = CUSTOM_GROUP.id

    _metric: CustomValueMetric

    def __init__(
        self,
        func: Callable[[InputData], float],
        title: str = None,
        eq: Optional[NumericApprox] = None,
        gt: Optional[NumericApprox] = None,
        gte: Optional[NumericApprox] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[NumericApprox] = None,
        lte: Optional[NumericApprox] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self._metric = CustomValueMetric(func=func, title=title)
        super().__init__(
            eq=eq,
            gt=gt,
            gte=gte,
            is_in=is_in,
            lt=lt,
            lte=lte,
            not_eq=not_eq,
            not_in=not_in,
            is_critical=is_critical,
        )
        if not self.has_condition():
            raise ValueError("Specify at least one condition")

    def calculate_value_for_test(self) -> Numeric:
        return self._metric.get_result().value

    def get_description(self, value: Numeric) -> str:
        return (
            f"Custom function '{self._metric.title or '<unnamed>'}' value is {self._value or None}. "
            f"The test threshold is {self.get_condition()}"
        )
