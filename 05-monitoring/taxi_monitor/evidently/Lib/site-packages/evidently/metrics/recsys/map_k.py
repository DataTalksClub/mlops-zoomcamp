from evidently.metrics.recsys.base_top_k import TopKMetric
from evidently.metrics.recsys.base_top_k import TopKMetricRenderer
from evidently.renderers.base_renderer import default_renderer


class MAPKMetric(TopKMetric):
    def key(self):
        return "map"


@default_renderer(wrap_type=MAPKMetric)
class MAPKMetricRenderer(TopKMetricRenderer):
    yaxis_name = "map@k"
    header = "MAP"
