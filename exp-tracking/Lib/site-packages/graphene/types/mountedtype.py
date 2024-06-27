from ..utils.orderedtype import OrderedType
from .unmountedtype import UnmountedType


class MountedType(OrderedType):
    @classmethod
    def mounted(cls, unmounted):  # noqa: N802
        """
        Mount the UnmountedType instance
        """
        assert isinstance(
            unmounted, UnmountedType
        ), f"{cls.__name__} can't mount {repr(unmounted)}"

        return cls(
            unmounted.get_type(),
            *unmounted.args,
            _creation_counter=unmounted.creation_counter,
            **unmounted.kwargs,
        )
