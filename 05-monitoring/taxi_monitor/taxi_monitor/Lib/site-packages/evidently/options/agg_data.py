from typing import Optional

from evidently.options.option import Option


class RenderOptions(Option):
    raw_data: bool = False


class DataDefinitionOptions(Option):
    categorical_features_cardinality: Optional[int] = None
