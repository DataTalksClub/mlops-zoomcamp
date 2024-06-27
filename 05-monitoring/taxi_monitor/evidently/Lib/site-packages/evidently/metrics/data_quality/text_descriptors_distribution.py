from typing import Dict
from typing import List
from typing import Optional

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.core import ColumnType
from evidently.core import IncludeTags
from evidently.descriptors import OOV
from evidently.descriptors import NonLetterCharacterPercentage
from evidently.descriptors import TextLength
from evidently.features.generated_features import FeatureDescriptor
from evidently.features.generated_features import GeneratedFeature
from evidently.metric_results import Distribution
from evidently.metric_results import HistogramData
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import WidgetSize
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import plotly_figure
from evidently.utils.data_operations import process_columns
from evidently.utils.data_operations import recognize_column_type
from evidently.utils.data_preprocessing import DataDefinition
from evidently.utils.visualizations import get_distribution_for_column
from evidently.utils.visualizations import plot_distr_with_perc_button


class TextDescriptorsDistributionResult(MetricResult):
    class Config:
        pd_include = False
        field_tags = {
            "current": {IncludeTags.Current},
            "reference": {IncludeTags.Reference},
            "column_name": {IncludeTags.Parameter},
        }

    column_name: str
    current: Dict[str, Distribution]
    reference: Optional[Dict[str, Distribution]] = None


class TextDescriptorsDistribution(Metric[TextDescriptorsDistributionResult]):
    """Calculates distribution for the column"""

    column_name: str
    _generated_text_features: Dict[str, GeneratedFeature]
    descriptors: Dict[str, FeatureDescriptor]

    def __init__(
        self, column_name: str, descriptors: Optional[Dict[str, FeatureDescriptor]] = None, options: AnyOptions = None
    ) -> None:
        self.column_name = column_name
        if descriptors:
            self.descriptors = descriptors
        else:
            self.descriptors = {
                "Text Length": TextLength(),
                "Non Letter Character %": NonLetterCharacterPercentage(),
                "OOV %": OOV(),
            }
        super().__init__(options=options)
        self._generated_text_features = {}

    @property
    def generated_text_features(self):
        return self._generated_text_features

    def required_features(self, data_definition: DataDefinition):
        column_type = data_definition.get_column(self.column_name).column_type
        if column_type == ColumnType.Text:
            self._generated_text_features = {
                name: desc.feature(self.column_name) for name, desc in self.descriptors.items()
            }
            return list(self.generated_text_features.values())
        return []

    def get_parameters(self) -> tuple:
        return (self.column_name,)

    def calculate(self, data: InputData) -> TextDescriptorsDistributionResult:
        current_results = {}
        reference_results: Optional[Dict[str, Distribution]] = None
        if data.reference_data is not None:
            reference_results = {}
        if self.column_name not in data.current_data:
            raise ValueError(f"Column '{self.column_name}' was not found in current data.")

        if data.reference_data is not None:
            if self.column_name not in data.reference_data:
                raise ValueError(f"Column '{self.column_name}' was not found in reference data.")

        columns = process_columns(data.current_data, data.column_mapping)
        column_type = recognize_column_type(dataset=data.current_data, column_name=self.column_name, columns=columns)
        if column_type != "text":
            raise ValueError("Text column expected")
        for key, val in self.generated_text_features.items():
            current_column = data.get_current_column(val.feature_name())
            reference_column = None
            if data.reference_data is not None:
                reference_column = data.get_reference_column(val.feature_name())
            current, reference = get_distribution_for_column(
                column_type=val.feature_type.value,
                current=current_column,
                reference=reference_column,
            )
            current_results[key] = current
            if reference_results is not None and reference is not None:
                reference_results[key] = reference

        return TextDescriptorsDistributionResult(
            column_name=self.column_name,
            current=current_results,
            reference=reference_results,
        )


@default_renderer(wrap_type=TextDescriptorsDistribution)
class TextDescriptorsDistributionRenderer(MetricRenderer):
    def render_html(self, obj: TextDescriptorsDistribution) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        result = [header_text(label=f"Distribution for column '{metric_result.column_name}'.")]
        for col in list(metric_result.current.keys()):
            reference = None
            if metric_result.reference is not None:
                reference = metric_result.reference[col]
            distr_fig = plot_distr_with_perc_button(
                hist_curr=HistogramData.from_distribution(metric_result.current[col]),
                hist_ref=HistogramData.from_distribution(reference),
                xaxis_name="",
                yaxis_name="Count",
                yaxis_name_perc="Percent",
                same_color=False,
                color_options=self.color_options,
                subplots=False,
                to_json=False,
            )
            # distr_fig = get_distribution_plot_figure(
            #     current_distribution=metric_result.current[col],
            #     reference_distribution=reference,
            #     color_options=self.color_options,
            # )
            result.append(plotly_figure(title=col, figure=distr_fig, size=WidgetSize.FULL))

        return result
