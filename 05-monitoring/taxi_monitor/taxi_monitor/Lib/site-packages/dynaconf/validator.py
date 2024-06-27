from __future__ import annotations

from collections import defaultdict
from itertools import chain
from types import MappingProxyType
from typing import Any
from typing import Callable
from typing import Sequence
from typing import TYPE_CHECKING

from dynaconf import validator_conditions
from dynaconf.utils import ensure_a_list
from dynaconf.utils.functional import empty

if TYPE_CHECKING:
    from dynaconf.base import LazySettings  # noqa: F401
    from dynaconf.base import Settings

EQUALITY_ATTRS = (
    "names",
    "must_exist",
    "when",
    "condition",
    "operations",
    "envs",
)


class ValidationError(Exception):
    """Raised when a validation fails"""

    def __init__(self, message: str, *args, **kwargs):
        self.details = kwargs.pop("details", [])
        super().__init__(message, *args, **kwargs)
        self.message = message


class Validator:
    """Validators are conditions attached to settings variables names
    or patterns::

        Validator('MESSAGE', must_exist=True, eq='Hello World')

    The above ensure MESSAGE is available in default env and
    is equal to 'Hello World'

    `names` are a one (or more) names or patterns::

        Validator('NAME')
        Validator('NAME', 'OTHER_NAME', 'EVEN_OTHER')
        Validator(r'^NAME', r'OTHER./*')

    The `operations` are::

        eq: value == other
        ne: value != other
        gt: value > other
        lt: value < other
        gte: value >= other
        lte: value <= other
        is_type_of: isinstance(value, type)
        is_in:  value in sequence
        is_not_in: value not in sequence
        identity: value is other
        cont: contain value in
        len_eq: len(value) == other
        len_ne: len(value) != other
        len_min: len(value) > other
        len_max: len(value) < other

    `env` is which env to be checked, can be a list or
    default is used.

    `when` holds a validator and its return decides if validator runs or not::

        Validator('NAME', must_exist=True, when=Validator('OTHER', eq=2))
        # NAME is required only if OTHER eq to 2
        # When the very first thing to be performed when passed.
        # if no env is passed to `when` it is inherited

    `must_exist` is alias to `required` requirement. (executed after when)::

       settings.get(value, empty) returns non empty

    condition is a callable to be executed and return boolean::

       Validator('NAME', condition=lambda x: x == 1)
       # it is executed before operations.

    """

    default_messages = MappingProxyType(
        {
            "must_exist_true": "{name} is required in env {env}",
            "must_exist_false": "{name} cannot exists in env {env}",
            "condition": "{name} invalid for {function}({value}) in env {env}",
            "operations": (
                "{name} must {operation} {op_value} "
                "but it is {value} in env {env}"
            ),
            "combined": "combined validators failed {errors}",
        }
    )

    def __init__(
        self,
        *names: str,
        must_exist: bool | None = None,
        required: bool | None = None,  # alias for `must_exist`
        condition: Callable[[Any], bool] | None = None,
        when: Validator | None = None,
        env: str | Sequence[str] | None = None,
        messages: dict[str, str] | None = None,
        cast: Callable[[Any], Any] | None = None,
        default: Any | Callable[[Any, Validator], Any] | None = empty,
        description: str | None = None,
        apply_default_on_none: bool | None = False,
        **operations: Any,
    ) -> None:
        # Copy immutable MappingProxyType as a mutable dict
        self.messages = dict(self.default_messages)
        if messages:
            self.messages.update(messages)

        if when is not None and not isinstance(when, Validator):
            raise TypeError("when must be Validator instance")

        if condition is not None and not callable(condition):
            raise TypeError("condition must be callable")

        self.names = names
        self.must_exist = must_exist if must_exist is not None else required
        self.condition = condition
        self.when = when
        self.cast = cast or (lambda value: value)
        self.operations = operations
        self.default = default
        self.description = description
        self.envs: Sequence[str] | None = None
        self.apply_default_on_none = apply_default_on_none

        # See #585
        self.is_type_of = operations.get("is_type_of")

        if isinstance(env, str):
            self.envs = [env]
        elif isinstance(env, (list, tuple)):
            self.envs = env

    def __or__(self, other: Validator) -> CombinedValidator:
        return OrValidator(self, other, description=self.description)

    def __and__(self, other: Validator) -> CombinedValidator:
        return AndValidator(self, other, description=self.description)

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True

        if type(self).__name__ != type(other).__name__:
            return False

        identical_attrs = (
            getattr(self, attr) == getattr(other, attr)
            for attr in EQUALITY_ATTRS
        )
        if all(identical_attrs):
            return True

        return False

    def validate(
        self,
        settings: Settings,
        only: str | Sequence | None = None,
        exclude: str | Sequence | None = None,
        only_current_env: bool = False,
    ) -> None:
        """Raise ValidationError if invalid"""
        # If only or exclude are not set, this value always passes startswith
        only = ensure_a_list(only or [""])
        if only and not isinstance(only[0], str):
            raise ValueError("'only' must be a string or list of strings.")

        exclude = ensure_a_list(exclude)
        if exclude and not isinstance(exclude[0], str):
            raise ValueError("'exclude' must be a string or list of strings.")

        if self.envs is None:
            self.envs = [settings.current_env]

        if self.when is not None:
            try:
                # inherit env if not defined
                if self.when.envs is None:
                    self.when.envs = self.envs

                self.when.validate(settings, only=only, exclude=exclude)
            except ValidationError:
                # if when is invalid, return canceling validation flow
                return

        if only_current_env:
            if settings.current_env.upper() in map(
                lambda s: s.upper(), self.envs
            ):
                self._validate_items(
                    settings, settings.current_env, only=only, exclude=exclude
                )
            return

        # If only using current_env, skip using_env decoration (reload)
        if (
            len(self.envs) == 1
            and self.envs[0].upper() == settings.current_env.upper()
        ):
            self._validate_items(
                settings, settings.current_env, only=only, exclude=exclude
            )
            return

        for env in self.envs:
            env_settings: Settings = settings.from_env(env)
            self._validate_items(env_settings, only=only, exclude=exclude)
            # merge source metadata into original settings for history inspect
            settings._loaded_by_loaders.update(env_settings._loaded_by_loaders)

    def _validate_items(
        self,
        settings: Settings,
        env: str | None = None,
        only: str | Sequence | None = None,
        exclude: str | Sequence | None = None,
    ) -> None:
        env = env or settings.current_env
        for name in self.names:
            # Skip if only is set and name isn't in the only list
            if only and not any(name.startswith(sub) for sub in only):
                continue

            # Skip if exclude is set and name is in the exclude list
            if exclude and any(name.startswith(sub) for sub in exclude):
                continue

            if self.default is not empty:
                default_value = (
                    self.default(settings, self)
                    if callable(self.default)
                    else self.default
                )
            else:
                default_value = empty

            # THIS IS A FIX FOR #585 in contrast with #799
            # toml considers signed strings "+-1" as integers
            # however existing users are passing strings
            # to default on validator (see #585)
            # The solution we added on #667 introduced a new problem
            # This fix here makes it to work for both cases.
            if (
                isinstance(default_value, str)
                and default_value.startswith(("+", "-"))
                and self.is_type_of is str
            ):
                # avoid TOML from parsing "+-1" as integer
                default_value = f"'{default_value}'"

            value = settings.setdefault(
                name,
                default_value,
                apply_default_on_none=self.apply_default_on_none,
                env=env,
            )

            # is name required but not exists?
            if self.must_exist is True and value is empty:
                _message = self.messages["must_exist_true"].format(
                    name=name, env=env
                )
                raise ValidationError(_message, details=[(self, _message)])

            if self.must_exist is False and value is not empty:
                _message = self.messages["must_exist_false"].format(
                    name=name, env=env
                )
                raise ValidationError(_message, details=[(self, _message)])

            if self.must_exist in (False, None) and value is empty:
                continue

            # value or default value already set
            # by settings.setdefault above
            # however we need to cast it
            # so we call .set again
            value = self.cast(settings.get(name))
            settings.set(name, value, validate=False)

            # is there a callable condition?
            if self.condition is not None:
                if not self.condition(value):
                    _message = self.messages["condition"].format(
                        name=name,
                        function=self.condition.__name__,
                        value=value,
                        env=env,
                    )
                    raise ValidationError(_message, details=[(self, _message)])

            # operations
            for op_name, op_value in self.operations.items():
                op_function = getattr(validator_conditions, op_name)
                op_succeeded = False

                # 'is_type_of' special error handling - related to #879
                if op_name == "is_type_of":
                    # auto transform quoted types
                    if isinstance(op_value, str):
                        op_value = __builtins__.get(  # type: ignore
                            op_value, op_value
                        )

                    # invalid type (not in __builtins__) may raise TypeError
                    try:
                        op_succeeded = op_function(value, op_value)
                    except TypeError:
                        raise ValidationError(
                            f"Invalid type '{op_value}' for condition "
                            "'is_type_of'. Should provide a valid type"
                        )
                else:
                    op_succeeded = op_function(value, op_value)

                if not op_succeeded:
                    _message = self.messages["operations"].format(
                        name=name,
                        operation=op_function.__name__,
                        op_value=op_value,
                        value=value,
                        env=env,
                    )
                    raise ValidationError(_message, details=[(self, _message)])


class CombinedValidator(Validator):
    def __init__(
        self,
        validator_a: Validator,
        validator_b: Validator,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Takes 2 validators and combines the validation"""
        self.validators = (validator_a, validator_b)
        super().__init__(*args, **kwargs)
        for attr in EQUALITY_ATTRS:
            if not getattr(self, attr, None):
                value = tuple(
                    getattr(validator, attr) for validator in self.validators
                )
                setattr(self, attr, value)

    def validate(
        self,
        settings: Any,
        only: str | Sequence | None = None,
        exclude: str | Sequence | None = None,
        only_current_env: bool = False,
    ) -> None:  # pragma: no cover
        raise NotImplementedError(
            "subclasses OrValidator or AndValidator implements this method"
        )


class OrValidator(CombinedValidator):
    """Evaluates on Validator() | Validator()"""

    def validate(
        self,
        settings: Any,
        only: str | Sequence | None = None,
        exclude: str | Sequence | None = None,
        only_current_env: bool = False,
    ) -> None:
        """Ensure at least one of the validators are valid"""
        errors = []
        for validator in self.validators:
            try:
                validator.validate(
                    settings,
                    only=only,
                    exclude=exclude,
                    only_current_env=only_current_env,
                )
            except ValidationError as e:
                errors.append(e)
                continue
            else:
                return

        _message = self.messages["combined"].format(
            errors=" or ".join(
                str(e).replace("combined validators failed ", "")
                for e in errors
            )
        )
        raise ValidationError(_message, details=[(self, _message)])


class AndValidator(CombinedValidator):
    """Evaluates on Validator() & Validator()"""

    def validate(
        self,
        settings: Any,
        only: str | Sequence | None = None,
        exclude: str | Sequence | None = None,
        only_current_env: bool = False,
    ) -> None:
        """Ensure both the validators are valid"""
        errors = []
        for validator in self.validators:
            try:
                validator.validate(
                    settings,
                    only=only,
                    exclude=exclude,
                    only_current_env=only_current_env,
                )
            except ValidationError as e:
                errors.append(e)
                continue

        if errors:
            _message = self.messages["combined"].format(
                errors=" and ".join(
                    str(e).replace("combined validators failed ", "")
                    for e in errors
                )
            )
            raise ValidationError(_message, details=[(self, _message)])


class ValidatorList(list):
    def __init__(
        self,
        settings: Settings,
        validators: Sequence[Validator] | None = None,
        *args: Validator,
        **kwargs: Any,
    ) -> None:
        if isinstance(validators, (list, tuple)):
            args = list(args) + list(validators)  # type: ignore
        self._only = kwargs.pop("validate_only", None)
        self._exclude = kwargs.pop("validate_exclude", None)
        super().__init__(args, **kwargs)  # type: ignore
        self.settings = settings

    def register(self, *args: Validator, **kwargs: Validator):
        validators: list[Validator] = list(
            chain.from_iterable(kwargs.values())  # type: ignore
        )
        validators.extend(args)
        for validator in validators:
            if validator and validator not in self:
                self.append(validator)

    def descriptions(self, flat: bool = False) -> dict[str, str | list[str]]:
        if flat:
            descriptions: dict[str, str | list[str]] = {}
        else:
            descriptions = defaultdict(list)

        for validator in self:
            for name in validator.names:
                if isinstance(name, tuple) and len(name) > 0:
                    name = name[0]
                if flat:
                    descriptions.setdefault(name, validator.description)
                else:
                    descriptions[name].append(  # type: ignore
                        validator.description
                    )
        return descriptions

    def validate(
        self,
        only: str | Sequence | None = None,
        exclude: str | Sequence | None = None,
        only_current_env: bool = False,
    ) -> None:
        for validator in self:
            validator.validate(
                self.settings,
                only=only,
                exclude=exclude,
                only_current_env=only_current_env,
            )

    def validate_all(
        self,
        only: str | Sequence | None = None,
        exclude: str | Sequence | None = None,
        only_current_env: bool = False,
    ) -> None:
        errors = []
        details = []
        for validator in self:
            try:
                validator.validate(
                    self.settings,
                    only=only,
                    exclude=exclude,
                    only_current_env=only_current_env,
                )
            except ValidationError as e:
                errors.append(e)
                details.append((validator, str(e)))
                continue

        if errors:
            raise ValidationError(
                "; ".join(str(e) for e in errors), details=details
            )
