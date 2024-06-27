from evidently.metrics.recsys.base_top_k import TopKMetric
from evidently.metrics.recsys.base_top_k import TopKMetricRenderer
from evidently.renderers.base_renderer import default_renderer


class PrecisionTopKMetric(TopKMetric):
    def key(self):
        return "precision"


@default_renderer(wrap_type=PrecisionTopKMetric)
class PrecisionTopKMetricRenderer(TopKMetricRenderer):
    yaxis_name = "precision@k"
    header = "Precision"
