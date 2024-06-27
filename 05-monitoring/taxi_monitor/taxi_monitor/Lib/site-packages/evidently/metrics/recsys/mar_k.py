from evidently.metrics.recsys.base_top_k import TopKMetric
from evidently.metrics.recsys.base_top_k import TopKMetricRenderer
from evidently.renderers.base_renderer import default_renderer


class MARKMetric(TopKMetric):
    def key(self):
        return "mar"


@default_renderer(wrap_type=MARKMetric)
class MARKMetricRenderer(TopKMetricRenderer):
    yaxis_name = "mar@k"
    header = "MAR"
