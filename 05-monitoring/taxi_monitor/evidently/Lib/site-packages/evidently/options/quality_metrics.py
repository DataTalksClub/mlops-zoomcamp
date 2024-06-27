from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

DEFAULT_CONF_INTERVAL_SIZE = 1
DEFAULT_CLASSIFICATION_THRESHOLD = 0.5


@dataclass
class QualityMetricsOptions:
    conf_interval_n_sigmas: int = DEFAULT_CONF_INTERVAL_SIZE
    classification_threshold: float = DEFAULT_CLASSIFICATION_THRESHOLD
    cut_quantile: Union[None, Tuple[str, float], Dict[str, Tuple[str, float]]] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "conf_interval_n_sigmas": self.conf_interval_n_sigmas,
            "classification_threshold": self.classification_threshold,
            "cut_quantile": self.cut_quantile,
        }

    def get_cut_quantile(self, feature_name: str) -> Optional[Tuple[str, float]]:
        if self.cut_quantile is None:
            return None
        if isinstance(self.cut_quantile, tuple):
            return self.cut_quantile
        if isinstance(self.cut_quantile, dict):
            return self.cut_quantile.get(feature_name, None)
        raise ValueError(
            f"""QualityMetricsOptions.cut_quantile
                                is incorrect type {type(self.cut_quantile)}"""
        )
