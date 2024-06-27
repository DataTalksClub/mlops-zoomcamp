"""Additional types, classes, dataclasses, etc."""

from typing import Any
from typing import ClassVar
from typing import Dict
from typing import Optional
from typing import Union

from evidently.pydantic_utils import ExcludeNoneMixin
from evidently.pydantic_utils import FrozenBaseModel

Numeric = Union[float, int]

# type for distributions - list of tuples (value, count)
ColumnDistribution = Dict[Any, Numeric]


class ApproxValue(FrozenBaseModel, ExcludeNoneMixin):
    """Class for approximate scalar value calculations"""

    class Config:
        smart_union = True

    DEFAULT_RELATIVE: ClassVar = 1e-6
    DEFAULT_ABSOLUTE: ClassVar = 1e-12

    value: Numeric
    relative: Numeric
    absolute: Numeric

    def __init__(self, value: Numeric, relative: Optional[Numeric] = None, absolute: Optional[Numeric] = None):
        if relative is not None and relative <= 0:
            raise ValueError("Relative value for approx should be greater than 0")

        if relative is None:
            relative = self.DEFAULT_RELATIVE

        if absolute is None:
            absolute = self.DEFAULT_ABSOLUTE

        super().__init__(value=value, relative=relative, absolute=absolute)

    @property
    def tolerance(self) -> Numeric:
        relative_value = abs(self.value) * self.relative
        return max(relative_value, self.absolute)

    def __format__(self, format_spec):
        return f"{format(self.value, format_spec)} ± {format(self.tolerance, format_spec)}"

    def __repr__(self):
        return f"{self.value} ± {self.tolerance}"

    def __eq__(self, other):
        tolerance = self.tolerance
        return (self.value - tolerance) <= other <= (self.value + tolerance)

    def __lt__(self, other):
        return self.value + self.tolerance < other

    def __le__(self, other):
        return self.value - self.tolerance <= other

    def __gt__(self, other):
        return self.value - self.tolerance > other

    def __ge__(self, other):
        return self.value + self.tolerance >= other


NumericApprox = Union[int, float, ApproxValue]
