from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

from pendulum.datetime import DateTime
from pendulum.utils._compat import PYPY


if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self


class BaseTraveller:
    def __init__(self, datetime_class: type[DateTime] = DateTime) -> None:
        self._datetime_class: type[DateTime] = datetime_class

    def freeze(self) -> Self:
        raise self._not_implemented()

    def travel_back(self) -> Self:
        raise self._not_implemented()

    def travel(
        self,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        microseconds: int = 0,
    ) -> Self:
        raise self._not_implemented()

    def travel_to(self, dt: DateTime, *, freeze: bool = False) -> Self:
        raise self._not_implemented()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType,
    ) -> None:
        ...

    def _not_implemented(self) -> NotImplementedError:
        return NotImplementedError()


if not PYPY:
    try:
        import time_machine
    except ImportError:
        time_machine = None  # type: ignore[assignment]

    if time_machine is not None:

        class Traveller(BaseTraveller):
            def __init__(self, datetime_class: type[DateTime] = DateTime) -> None:
                super().__init__(datetime_class)

                self._started: bool = False
                self._traveller: time_machine.travel | None = None
                self._coordinates: time_machine.Coordinates | None = None

            def freeze(self) -> Self:
                if self._started:
                    cast(time_machine.Coordinates, self._coordinates).move_to(
                        self._datetime_class.now(), tick=False
                    )
                else:
                    self._start(freeze=True)

                return self

            def travel_back(self) -> Self:
                if not self._started:
                    return self

                cast(time_machine.travel, self._traveller).stop()
                self._coordinates = None
                self._traveller = None
                self._started = False

                return self

            def travel(
                self,
                years: int = 0,
                months: int = 0,
                weeks: int = 0,
                days: int = 0,
                hours: int = 0,
                minutes: int = 0,
                seconds: int = 0,
                microseconds: int = 0,
                *,
                freeze: bool = False,
            ) -> Self:
                self._start(freeze=freeze)

                cast(time_machine.Coordinates, self._coordinates).move_to(
                    self._datetime_class.now().add(
                        years=years,
                        months=months,
                        weeks=weeks,
                        days=days,
                        hours=hours,
                        minutes=minutes,
                        seconds=seconds,
                        microseconds=microseconds,
                    )
                )

                return self

            def travel_to(self, dt: DateTime, *, freeze: bool = False) -> Self:
                self._start(freeze=freeze)

                cast(time_machine.Coordinates, self._coordinates).move_to(dt)

                return self

            def _start(self, freeze: bool = False) -> None:
                if self._started:
                    return

                if not self._traveller:
                    self._traveller = time_machine.travel(
                        self._datetime_class.now(), tick=not freeze
                    )

                self._coordinates = self._traveller.start()

                self._started = True

            def __enter__(self) -> Self:
                self._start()

                return self

            def __exit__(
                self,
                exc_type: type[BaseException] | None,
                exc_val: BaseException | None,
                exc_tb: TracebackType,
            ) -> None:
                self.travel_back()

    else:

        class Traveller(BaseTraveller):  # type: ignore[no-redef]
            def _not_implemented(self) -> NotImplementedError:
                return NotImplementedError(
                    "Time travelling is an optional feature. "
                    'You can add it by installing Pendulum with the "test" extra.'
                )

else:

    class Traveller(BaseTraveller):  # type: ignore[no-redef]
        def _not_implemented(self) -> NotImplementedError:
            return NotImplementedError(
                "Time travelling is not supported on the PyPy Python implementation."
            )
