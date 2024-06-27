from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import TYPE_CHECKING, Any, Callable, Generator, Iterable, Iterator, Mapping, MutableMapping

from litestar.utils.scope.state import CONNECTION_STATE_KEY

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ("ImmutableState", "State")


class ImmutableState(Mapping[str, Any]):
    """An object meant to store arbitrary state.

    It can be accessed using dot notation while exposing dict like functionalities.
    """

    __slots__ = (
        "_state",
        "_deep_copy",
    )

    _state: dict[str, Any]

    def __init__(
        self, state: ImmutableState | Mapping[str, Any] | Iterable[tuple[str, Any]], deep_copy: bool = True
    ) -> None:
        """Initialize an ``ImmutableState`` instance.

        Args:
             state: An object to initialize the state from. Can be a dict, an instance of :class:`ImmutableState`, or a tuple
                of key value paris.
             deep_copy: Whether to 'deepcopy' the passed in state.

        Examples:
            .. code-block:: python

                from litestar.datastructures import ImmutableState

                state_dict = {"first": 1, "second": 2, "third": 3, "fourth": 4}
                state = ImmutableState(state_dict)

                # state implements the Mapping type:
                assert len(state) == 3
                assert "first" in state
                assert not "fourth" in state
                assert state["first"] == 1
                assert [(k, v) for k, v in state.items()] == [("first", 1), ("second", 2), ("third", 3)]

                # state implements __bool__
                assert state  # state is true when it has values.
                assert not State()  # state is empty when it has no values.

                # it has a 'dict' method to retrieve a shallow copy of the underlying dict
                inner_dict = state.dict()
                assert inner_dict == state_dict

                # you can also retrieve a mutable State by calling 'mutable_copy'
                mutable_state = state.mutable_copy()
                del state["first"]
                assert "first" not in state

        """
        if isinstance(state, ImmutableState):
            state = state._state

        if not isinstance(state, dict) and isinstance(state, Iterable):
            state = dict(state)

        super().__setattr__("_deep_copy", deep_copy)
        super().__setattr__("_state", deepcopy(state) if deep_copy else state)

    def __bool__(self) -> bool:
        """Return a boolean indicating whether the wrapped dict instance has values."""
        return bool(self._state)

    def __getitem__(self, key: str) -> Any:
        """Get the value for the corresponding key from the wrapped state object using subscription notation.

        Args:
            key: Key to access.

        Raises:
            KeyError

        Returns:
            A value from the wrapped state instance.
        """
        return self._state[key]

    def __iter__(self) -> Iterator[str]:
        """Return an iterator iterating the wrapped state dict.

        Returns:
            An iterator of strings
        """
        return iter(self._state)

    def __len__(self) -> int:
        """Return length of the wrapped state dict.

        Returns:
            An integer
        """
        return len(self._state)

    def __getattr__(self, key: str) -> Any:
        """Get the value for the corresponding key from the wrapped state object using attribute notation.

        Args:
            key: Key to retrieve

        Raises:
            AttributeError: if the given attribute is not set.

        Returns:
            The retrieved value
        """
        try:
            return self._state[key]
        except KeyError as e:
            raise AttributeError from e

    def __copy__(self) -> Self:
        """Return a shallow copy of the given state object.

        Customizes how the builtin "copy" function will work.
        """
        return self.__class__(self._state, deep_copy=self._deep_copy)  # pyright: ignore

    def mutable_copy(self) -> State:
        """Return a mutable copy of the state object.

        Returns:
            A ``State``
        """
        return State(self._state, deep_copy=self._deep_copy)

    def dict(self) -> dict[str, Any]:
        """Return a shallow copy of the wrapped dict.

        Returns:
            A dict
        """
        return {k: v for k, v in self._state.items() if k != CONNECTION_STATE_KEY}

    @classmethod
    def __get_validators__(
        cls,
    ) -> Generator[Callable[[ImmutableState | dict[str, Any] | Iterable[tuple[str, Any]]], ImmutableState], None, None]:  # type: ignore[valid-type]
        """Pydantic compatible method to allow custom parsing of state instances in a SignatureModel."""
        yield cls.validate

    @classmethod
    def validate(cls, value: ImmutableState | dict[str, Any] | Iterable[tuple[str, Any]]) -> Self:  # type: ignore[valid-type]
        """Parse a value and instantiate state inside a SignatureModel. This allows us to use custom subclasses of
        state, as well as allows users to decide whether state is mutable or immutable.

        Args:
            value: The value from which to initialize the state instance.

        Returns:
            An ImmutableState instance
        """
        deep_copy = value._deep_copy if isinstance(value, ImmutableState) else False
        return cls(value, deep_copy=deep_copy)


class State(ImmutableState, MutableMapping[str, Any]):
    """An object meant to store arbitrary state.

    It can be accessed using dot notation while exposing dict like functionalities.
    """

    __slots__ = ("_lock",)

    _lock: RLock

    def __init__(
        self,
        state: ImmutableState | Mapping[str, Any] | Iterable[tuple[str, Any]] | None = None,
        deep_copy: bool = False,
    ) -> None:
        """Initialize a ``State`` instance with an optional value.

        Args:
             state: An object to initialize the state from. Can be a dict, an instance of 'ImmutableState', or a tuple of key value paris.
             deep_copy: Whether to 'deepcopy' the passed in state.

        .. code-block:: python
            :caption: Examples

            from litestar.datastructures import State

            state_dict = {"first": 1, "second": 2, "third": 3, "fourth": 4}
            state = State(state_dict)

            # state can be accessed using '.' notation
            assert state.fourth == 4
            del state.fourth

            # state implements the Mapping type:
            assert len(state) == 3
            assert "first" in state
            assert not "fourth" in state
            assert state["first"] == 1
            assert [(k, v) for k, v in state.items()] == [("first", 1), ("second", 2), ("third", 3)]

            state["fourth"] = 4
            assert "fourth" in state
            del state["fourth"]

            # state implements __bool__
            assert state  # state is true when it has values.
            assert not State()  # state is empty when it has no values.

            # it has shallow copy
            copied_state = state.copy()
            del copied_state.first
            assert state.first

            # it has a 'dict' method to retrieve a shallow copy of the underlying dict
            inner_dict = state.dict()
            assert inner_dict == state_dict

            # you can get an immutable copy of the state by calling 'immutable_immutable_copy'
            immutable_copy = state.immutable_copy()
            del immutable_copy.first  #  raises AttributeError

        """

        super().__init__(state if state is not None else {}, deep_copy=deep_copy)
        super().__setattr__("_lock", RLock())

    def __delitem__(self, key: str) -> None:
        """Delete the value from the key from the wrapped state object using subscription notation.

        Args:
            key: Key to delete

        Raises:
            KeyError: if the given attribute is not set.

        Returns:
            None
        """

        with self._lock:
            del self._state[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set an item in the state using subscription notation.

        Args:
            key: Key to set.
            value: Value to set.

        Returns:
            None
        """

        with self._lock:
            self._state[key] = value

    def __setattr__(self, key: str, value: Any) -> None:
        """Set an item in the state using attribute notation.

        Args:
            key: Key to set.
            value: Value to set.

        Returns:
            None
        """

        with self._lock:
            self._state[key] = value

    def __delattr__(self, key: str) -> None:
        """Delete the value from the key from the wrapped state object using attribute notation.

        Args:
            key: Key to delete

        Raises:
            AttributeError: if the given attribute is not set.

        Returns:
            None
        """

        try:
            with self._lock:
                del self._state[key]
        except KeyError as e:
            raise AttributeError from e

    def copy(self) -> Self:
        """Return a shallow copy of the state object.

        Returns:
            A ``State``
        """
        return self.__class__(self.dict(), deep_copy=self._deep_copy)  # pyright: ignore

    def immutable_copy(self) -> ImmutableState:
        """Return a shallow copy of the state object, setting it to be frozen.

        Returns:
            A ``State``
        """
        return ImmutableState(self, deep_copy=self._deep_copy)
