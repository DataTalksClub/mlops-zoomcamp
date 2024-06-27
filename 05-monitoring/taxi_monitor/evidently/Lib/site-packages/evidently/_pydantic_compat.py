from typing import TYPE_CHECKING

import pydantic

v = 1 if pydantic.__version__.startswith("1") else 2

if v == 2:
    from pydantic.v1 import UUID4
    from pydantic.v1 import BaseConfig
    from pydantic.v1 import BaseModel
    from pydantic.v1 import Extra
    from pydantic.v1 import Field
    from pydantic.v1 import PrivateAttr
    from pydantic.v1 import SecretStr
    from pydantic.v1 import ValidationError
    from pydantic.v1 import parse_obj_as
    from pydantic.v1 import validator
    from pydantic.v1.fields import SHAPE_DICT
    from pydantic.v1.fields import SHAPE_LIST
    from pydantic.v1.fields import SHAPE_SET
    from pydantic.v1.fields import SHAPE_TUPLE
    from pydantic.v1.fields import ModelField
    from pydantic.v1.main import ModelMetaclass
    from pydantic.v1.utils import import_string
    from pydantic.v1.validators import _VALIDATORS

    if TYPE_CHECKING:
        from pydantic.v1.main import AbstractSetIntStr
        from pydantic.v1.main import MappingIntStrAny
        from pydantic.v1.main import Model
        from pydantic.v1.typing import DictStrAny

else:
    from pydantic import UUID4
    from pydantic import BaseConfig
    from pydantic import BaseModel
    from pydantic import Extra
    from pydantic import Field
    from pydantic import PrivateAttr
    from pydantic import SecretStr
    from pydantic import ValidationError
    from pydantic import parse_obj_as
    from pydantic import validator
    from pydantic.fields import SHAPE_DICT  # type: ignore[attr-defined,no-redef]
    from pydantic.fields import SHAPE_LIST  # type: ignore[attr-defined,no-redef]
    from pydantic.fields import SHAPE_SET  # type: ignore[attr-defined,no-redef]
    from pydantic.fields import SHAPE_TUPLE  # type: ignore[attr-defined,no-redef]
    from pydantic.fields import ModelField  # type: ignore[attr-defined,no-redef]
    from pydantic.main import ModelMetaclass  # type: ignore[attr-defined,no-redef]
    from pydantic.utils import import_string  # type: ignore[attr-defined,no-redef]
    from pydantic.validators import _VALIDATORS  # type: ignore[attr-defined,no-redef]

    if TYPE_CHECKING:
        from pydantic.main import AbstractSetIntStr  # type: ignore[attr-defined,no-redef]
        from pydantic.main import MappingIntStrAny  # type: ignore[attr-defined,no-redef]
        from pydantic.main import Model  # type: ignore[attr-defined,no-redef]
        from pydantic.typing import DictStrAny  # type: ignore[attr-defined,no-redef]


__all__ = [
    "UUID4",
    "BaseConfig",
    "BaseModel",
    "Field",
    "ValidationError",
    "parse_obj_as",
    "validator",
    "SecretStr",
    "SHAPE_DICT",
    "SHAPE_LIST",
    "SHAPE_SET",
    "SHAPE_TUPLE",
    "ModelField",
    "ModelMetaclass",
    "import_string",
    "_VALIDATORS",
    "Model",
    "MappingIntStrAny",
    "AbstractSetIntStr",
    "DictStrAny",
    "PrivateAttr",
    "Extra",
]
