import logging
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

from evidently.options.data_drift import DataDriftOptions
from evidently.options.quality_metrics import QualityMetricsOptions
from evidently.pipeline.column_mapping import ColumnMapping
from evidently.runner.loader import DataLoader
from evidently.runner.loader import DataOptions
from evidently.runner.loader import SamplingOptions


@dataclass
class RunnerOptions:
    reference_data_path: str
    reference_data_options: DataOptions
    reference_data_sampling: Optional[SamplingOptions]
    current_data_path: Optional[str]
    current_data_options: Optional[DataOptions]
    current_data_sampling: Optional[SamplingOptions]
    column_mapping: ColumnMapping
    options: List[object]
    output_path: str


options_mapping: Dict[str, Type] = {
    "data_drift": DataDriftOptions,
    "quality_metrics": QualityMetricsOptions,
}


def parse_options(raw_dict: Optional[Dict[str, Dict[str, object]]]) -> List[object]:
    if raw_dict is None:
        return []
    result = []
    for key, params in raw_dict.items():
        opt_class = options_mapping.get(key, None)
        if opt_class is None:
            raise ValueError(f"No options with id {key} exists")
        result.append(opt_class(**params))
    return result


class Runner:
    def __init__(self, options: RunnerOptions):
        self.options = options

    def _parse_data(self):
        loader = DataLoader()

        reference_data = loader.load(
            self.options.reference_data_path, self.options.reference_data_options, self.options.reference_data_sampling
        )
        logging.info(f"reference dataset loaded: {len(reference_data)} rows")
        if self.options.current_data_path:
            current_data = loader.load(
                self.options.current_data_path, self.options.current_data_options, self.options.current_data_sampling
            )
            logging.info(f"current dataset loaded: {len(current_data)} rows")
        else:
            current_data = None

        return reference_data, current_data
