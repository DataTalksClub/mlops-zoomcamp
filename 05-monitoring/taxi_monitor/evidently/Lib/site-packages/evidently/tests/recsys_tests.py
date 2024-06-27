import abc
from typing import ClassVar
from typing import List
from typing import Optional
from typing import Union

from evidently.metric_results import HistogramData
from evidently.metrics import DiversityMetric
from evidently.metrics import FBetaTopKMetric
from evidently.metrics import HitRateKMetric
from evidently.metrics import MAPKMetric
from evidently.metrics import MARKMetric
from evidently.metrics import MRRKMetric
from evidently.metrics import NDCGKMetric
from evidently.metrics import NoveltyMetric
from evidently.metrics import PersonalizationMetric
from evidently.metrics import PopularityBias
from evidently.metrics import PrecisionTopKMetric
from evidently.metrics import RecallTopKMetric
from evidently.metrics import ScoreDistribution
from evidently.metrics import SerendipityMetric
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.base_renderer import TestHtmlInfo
from evidently.renderers.base_renderer import TestRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import TabData
from evidently.renderers.html_widgets import plotly_figure
from evidently.renderers.html_widgets import table_data
from evidently.renderers.html_widgets import widget_tabs
from evidently.tests.base_test import BaseCheckValueTest
from evidently.tests.base_test import GroupData
from evidently.tests.base_test import GroupingTypes
from evidently.tests.base_test import TestValueCondition
from evidently.tests.utils import approx
from evidently.utils.types import Numeric
from evidently.utils.visualizations import plot_4_distr
from evidently.utils.visualizations import plot_distr_with_perc_button
from evidently.utils.visualizations import plot_metric_k

RECSYS_GROUP = GroupData("recsys", "Recommendations", "")
GroupingTypes.TestGroup.add_value(RECSYS_GROUP)


BaseTopKRecsysType = Union[
    PrecisionTopKMetric,
    RecallTopKMetric,
    FBetaTopKMetric,
    MAPKMetric,
    MARKMetric,
    NDCGKMetric,
    MRRKMetric,
    HitRateKMetric,
]


class BaseTopkRecsysTest(BaseCheckValueTest, abc.ABC):
    group: ClassVar = RECSYS_GROUP.id
    header: str
    k: int
    min_rel_score: Optional[int]
    no_feedback_users: bool
    _metric: BaseTopKRecsysType

    def __init__(
        self,
        k: int,
        min_rel_score: Optional[int] = None,
        no_feedback_users: bool = False,
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self.k = k
        self.min_rel_score = min_rel_score
        self.no_feedback_users = no_feedback_users
        self._metric = self.get_metric(k, min_rel_score, no_feedback_users)
        super().__init__(
            eq=eq,
            gt=gt,
            gte=gte,
            is_in=is_in,
            lt=lt,
            lte=lte,
            not_eq=not_eq,
            not_in=not_in,
            is_critical=is_critical,
        )

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        metric_result = self.metric.get_result()
        ref_value = metric_result.reference[self.k] if metric_result.reference is not None else None
        if ref_value is not None:
            return TestValueCondition(eq=approx(ref_value, relative=0.1))
        return TestValueCondition(gt=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current[self.k]

    def get_description(self, value: Numeric) -> str:
        header_part = "(no feedback users included)"
        if not self.no_feedback_users:
            header_part = "(no feedback users excluded)"
        return f"{self.header}@{self.k} {header_part} is {value:.3}. The test threshold is {self.get_condition()}"

    @abc.abstractmethod
    def get_metric(self, k, min_rel_score, no_feedback_users) -> BaseTopKRecsysType:
        raise NotImplementedError()

    @property
    def metric(self):
        return self._metric


@default_renderer(wrap_type=BaseTopkRecsysTest)
class BaseTopkRecsysRenderer(TestRenderer):
    yaxis_name: str

    def render_html(self, obj: BaseTopkRecsysTest) -> TestHtmlInfo:
        info = super().render_html(obj)
        result = obj.metric.get_result()
        fig = plot_metric_k(result.current, result.reference, self.yaxis_name)
        info.with_details("", plotly_figure(figure=fig, title=""))
        return info


class TestPrecisionTopK(BaseTopkRecsysTest):
    name: ClassVar = "Precision (top-k)"
    header: str = "Precision"

    def get_metric(self, k, min_rel_score, no_feedback_users) -> BaseTopKRecsysType:
        return PrecisionTopKMetric(k=k, min_rel_score=min_rel_score, no_feedback_users=no_feedback_users)


@default_renderer(wrap_type=TestPrecisionTopK)
class TestPrecisionTopKRenderer(BaseTopkRecsysRenderer):
    yaxis_name = "precision@k"


class TestRecallTopK(BaseTopkRecsysTest):
    name: ClassVar = "Recall (top-k)"
    header: str = "Recall"

    def get_metric(self, k, min_rel_score, no_feedback_users) -> BaseTopKRecsysType:
        return RecallTopKMetric(k=k, min_rel_score=min_rel_score, no_feedback_users=no_feedback_users)


@default_renderer(wrap_type=TestRecallTopK)
class TestRecallTopKRenderer(BaseTopkRecsysRenderer):
    yaxis_name = "recall@k"


class TestFBetaTopK(BaseTopkRecsysTest):
    name: ClassVar = "F_beta (top-k)"
    header: str = "F_beta"

    def get_metric(self, k, min_rel_score, no_feedback_users) -> BaseTopKRecsysType:
        return FBetaTopKMetric(k=k, min_rel_score=min_rel_score, no_feedback_users=no_feedback_users)


@default_renderer(wrap_type=TestFBetaTopK)
class TestFBetaTopKRenderer(BaseTopkRecsysRenderer):
    yaxis_name = "f_beta@k"


class TestMAPK(BaseTopkRecsysTest):
    name: ClassVar = "MAP (top-k)"
    header: str = "MAP"

    def get_metric(self, k, min_rel_score, no_feedback_users) -> BaseTopKRecsysType:
        return MAPKMetric(k=k, min_rel_score=min_rel_score, no_feedback_users=no_feedback_users)


@default_renderer(wrap_type=TestMAPK)
class TestMAPKRenderer(BaseTopkRecsysRenderer):
    yaxis_name = "map@k"


class TestMARK(BaseTopkRecsysTest):
    name: ClassVar = "MAR (top-k)"
    header: str = "MAR"

    def get_metric(self, k, min_rel_score, no_feedback_users) -> BaseTopKRecsysType:
        return MARKMetric(k=k, min_rel_score=min_rel_score, no_feedback_users=no_feedback_users)


@default_renderer(wrap_type=TestMARK)
class TestMARKRenderer(BaseTopkRecsysRenderer):
    yaxis_name = "mar@k"


class TestNDCGK(BaseTopkRecsysTest):
    name: ClassVar = "NDCG (top-k)"
    header: str = "NDCG"

    def get_metric(self, k, min_rel_score, no_feedback_users) -> BaseTopKRecsysType:
        return NDCGKMetric(k=k, min_rel_score=min_rel_score, no_feedback_users=no_feedback_users)


@default_renderer(wrap_type=TestNDCGK)
class TestNDCGKRenderer(BaseTopkRecsysRenderer):
    yaxis_name = "ndcg@k"


class TestHitRateK(BaseTopkRecsysTest):
    name: ClassVar = "Hit Rate (top-k)"
    header: str = "Hit Rate"

    def get_metric(self, k, min_rel_score, no_feedback_users) -> BaseTopKRecsysType:
        return HitRateKMetric(k=k, min_rel_score=min_rel_score, no_feedback_users=no_feedback_users)


@default_renderer(wrap_type=TestHitRateK)
class TestHitRateKRenderer(BaseTopkRecsysRenderer):
    yaxis_name = "hit_rate@k"


class TestMRRK(BaseTopkRecsysTest):
    name: ClassVar = "MRR (top-k)"
    header: str = "MRR"

    def get_metric(self, k, min_rel_score, no_feedback_users) -> BaseTopKRecsysType:
        return MRRKMetric(k=k, min_rel_score=min_rel_score, no_feedback_users=no_feedback_users)


@default_renderer(wrap_type=TestMRRK)
class TestMRRKRenderer(BaseTopkRecsysRenderer):
    yaxis_name = "mrr@k"


BaseNotRankRecsysType = Union[
    PersonalizationMetric,
    NoveltyMetric,
    SerendipityMetric,
    DiversityMetric,
]


class BaseNotRankRecsysTest(BaseCheckValueTest, abc.ABC):
    group: ClassVar = RECSYS_GROUP.id
    header: str
    k: int
    min_rel_score: Optional[int]
    item_features: Optional[List[str]]
    _metric: BaseNotRankRecsysType

    def __init__(
        self,
        k: int,
        min_rel_score: Optional[int] = None,
        item_features: Optional[List[str]] = None,
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self.k = k
        self.min_rel_score = min_rel_score
        self.item_features = item_features
        self._metric = self.get_metric(k, min_rel_score, item_features)
        super().__init__(
            eq=eq,
            gt=gt,
            gte=gte,
            is_in=is_in,
            lt=lt,
            lte=lte,
            not_eq=not_eq,
            not_in=not_in,
            is_critical=is_critical,
        )

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        metric_result = self.metric.get_result()

        ref_value = metric_result.reference_value
        if ref_value is not None:
            return TestValueCondition(eq=approx(ref_value, relative=0.1))
        return TestValueCondition(gt=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current_value

    def get_description(self, value: Numeric) -> str:
        return f"{self.header}@{self.k} is {value:.3}. The test threshold is {self.get_condition()}"

    @abc.abstractmethod
    def get_metric(self, k, min_rel_score, item_features) -> BaseTopKRecsysType:
        raise NotImplementedError()

    @property
    def metric(self):
        return self._metric


@default_renderer(wrap_type=BaseNotRankRecsysTest)
class BaseNotRankRecsysTestRenderer(TestRenderer):
    xaxis_name: str

    def render_html(self, obj: BaseNotRankRecsysTest) -> TestHtmlInfo:
        info = super().render_html(obj)
        result = obj.metric.get_result()
        fig = plot_distr_with_perc_button(
            hist_curr=HistogramData.from_distribution(result.current_distr),
            hist_ref=HistogramData.from_distribution(result.reference_distr),
            xaxis_name=self.xaxis_name,
            yaxis_name="Count",
            yaxis_name_perc="Percent",
            same_color=False,
            color_options=self.color_options,
            subplots=False,
            to_json=False,
        )
        info.with_details("", plotly_figure(figure=fig, title=""))
        return info


class TestNovelty(BaseNotRankRecsysTest):
    name: ClassVar = "Novelty (top-k)"
    header: str = "Novelty"

    def get_metric(self, k, min_rel_score, item_features) -> BaseNotRankRecsysType:
        return NoveltyMetric(k=k)


@default_renderer(wrap_type=TestNovelty)
class TestNoveltyRenderer(BaseNotRankRecsysTestRenderer):
    xaxis_name = "novelty by user"


class TestDiversity(BaseNotRankRecsysTest):
    name: ClassVar = "Diversity (top-k)"
    header: str = "Diversity"

    def get_metric(self, k, min_rel_score, item_features) -> BaseNotRankRecsysType:
        return DiversityMetric(k=k, item_features=item_features)


@default_renderer(wrap_type=TestDiversity)
class TestDiversityRenderer(BaseNotRankRecsysTestRenderer):
    xaxis_name = "intra list diversity by user"


class TestSerendipity(BaseNotRankRecsysTest):
    name: ClassVar = "Serendipity (top-k)"
    header: str = "Serendipity"

    def get_metric(self, k, min_rel_score, item_features) -> BaseNotRankRecsysType:
        return SerendipityMetric(k=k, min_rel_score=min_rel_score, item_features=item_features)


@default_renderer(wrap_type=TestSerendipity)
class TestSerendipityRenderer(BaseNotRankRecsysTestRenderer):
    xaxis_name = "serendipity by user"


class TestPersonalization(BaseNotRankRecsysTest):
    name: ClassVar = "Personalization (top-k)"
    header: str = "Personalization"

    def get_metric(self, k, min_rel_score, item_features) -> BaseNotRankRecsysType:
        return PersonalizationMetric(k=k)


@default_renderer(wrap_type=TestPersonalization)
class TestPersonalizationRenderer(TestRenderer):
    @staticmethod
    def _get_table_stat(dataset_name: str, curr_table: dict, ref_table: Optional[dict]) -> BaseWidgetInfo:
        matched_stat_headers = ["Value", "Count"]
        tabs = [
            TabData(
                title="CURRENT: Top 10 popular items",
                widget=table_data(
                    title="",
                    column_names=matched_stat_headers,
                    data=[(k, v) for k, v in curr_table.items() if v > 0][:10],
                ),
            ),
        ]
        if ref_table is not None:
            tabs.append(
                TabData(
                    title="REFERENCE: Top 10 popular items",
                    widget=table_data(
                        title="",
                        column_names=matched_stat_headers,
                        data=[(k, v) for k, v in ref_table.items() if v > 0][:10],
                    ),
                ),
            )
        return widget_tabs(title="", tabs=tabs)

    def render_html(self, obj: BaseNotRankRecsysTest) -> TestHtmlInfo:
        info = super().render_html(obj)
        result = obj.metric.get_result()
        info.with_details("", self._get_table_stat("", result.current_table, result.reference_table))
        return info


class TestARP(BaseCheckValueTest):
    group: ClassVar = RECSYS_GROUP.id
    name: ClassVar = "ARP (top-k)"
    k: int
    normalize_arp: bool
    _metric: PopularityBias

    def __init__(
        self,
        k: int,
        normalize_arp: bool = False,
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self.k = k
        self.normalize_arp = normalize_arp
        self._metric = PopularityBias(k, normalize_arp=normalize_arp)
        super().__init__(
            eq=eq,
            gt=gt,
            gte=gte,
            is_in=is_in,
            lt=lt,
            lte=lte,
            not_eq=not_eq,
            not_in=not_in,
            is_critical=is_critical,
        )

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        metric_result = self.metric.get_result()
        ref_value = metric_result.reference_apr
        if ref_value is not None:
            return TestValueCondition(eq=approx(ref_value, relative=0.1))
        return TestValueCondition(gt=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current_apr

    def get_description(self, value: Numeric) -> str:
        return f"ARP (top-{self.k}) is {value:.3}. The test threshold is {self.get_condition()}"

    @property
    def metric(self):
        return self._metric


class TestGiniIndex(BaseCheckValueTest):
    group: ClassVar = RECSYS_GROUP.id
    name: ClassVar = "Gini Index (top-k)"
    k: int
    _metric: PopularityBias

    def __init__(
        self,
        k: int,
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self.k = k
        self._metric = PopularityBias(k)
        super().__init__(
            eq=eq,
            gt=gt,
            gte=gte,
            is_in=is_in,
            lt=lt,
            lte=lte,
            not_eq=not_eq,
            not_in=not_in,
            is_critical=is_critical,
        )

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        metric_result = self.metric.get_result()
        ref_value = metric_result.reference_gini
        if ref_value is not None:
            return TestValueCondition(eq=approx(ref_value, relative=0.1))
        return TestValueCondition(lt=1)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current_gini

    def get_description(self, value: Numeric) -> str:
        return f"Gini index (top-{self.k}) is {value:.3}. The test threshold is {self.get_condition()}"

    @property
    def metric(self):
        return self._metric


class TestCoverage(BaseCheckValueTest):
    group: ClassVar = RECSYS_GROUP.id
    name: ClassVar = "Coverage (top-k)"
    k: int
    _metric: PopularityBias

    def __init__(
        self,
        k: int,
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self.k = k
        self._metric = PopularityBias(k)
        super().__init__(
            eq=eq,
            gt=gt,
            gte=gte,
            is_in=is_in,
            lt=lt,
            lte=lte,
            not_eq=not_eq,
            not_in=not_in,
            is_critical=is_critical,
        )

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        metric_result = self.metric.get_result()
        ref_value = metric_result.reference_coverage
        if ref_value is not None:
            return TestValueCondition(eq=approx(ref_value, relative=0.1))
        return TestValueCondition(gt=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current_coverage

    def get_description(self, value: Numeric) -> str:
        return f"Coverage (top-{self.k}) is {value:.3}. The test threshold is {self.get_condition()}"

    @property
    def metric(self):
        return self._metric


@default_renderer(wrap_type=TestARP)
@default_renderer(wrap_type=TestGiniIndex)
@default_renderer(wrap_type=TestCoverage)
class TestPopularityBiasRenderer(TestRenderer):
    def render_html(self, obj: Union[TestARP, TestGiniIndex, TestCoverage]) -> TestHtmlInfo:
        info = super().render_html(obj)
        metric_result = obj.metric.get_result()
        is_normed = ""
        if metric_result.normalize_arp:
            is_normed = " normilized"
        distr_fig = plot_distr_with_perc_button(
            hist_curr=HistogramData.from_distribution(metric_result.current_distr),
            hist_ref=HistogramData.from_distribution(metric_result.reference_distr),
            xaxis_name="item popularity" + is_normed,
            yaxis_name="Count",
            yaxis_name_perc="Percent",
            same_color=False,
            color_options=self.color_options,
            subplots=False,
            to_json=False,
        )
        info.with_details("", plotly_figure(figure=distr_fig, title=""))
        return info


class TestScoreEntropy(BaseCheckValueTest):
    group: ClassVar = RECSYS_GROUP.id
    name: ClassVar = "Score Entropy (top-k)"
    k: int
    _metric: ScoreDistribution

    def __init__(
        self,
        k: int,
        eq: Optional[Numeric] = None,
        gt: Optional[Numeric] = None,
        gte: Optional[Numeric] = None,
        is_in: Optional[List[Union[Numeric, str, bool]]] = None,
        lt: Optional[Numeric] = None,
        lte: Optional[Numeric] = None,
        not_eq: Optional[Numeric] = None,
        not_in: Optional[List[Union[Numeric, str, bool]]] = None,
        is_critical: bool = True,
    ):
        self.k = k
        self._metric = ScoreDistribution(k)
        super().__init__(
            eq=eq,
            gt=gt,
            gte=gte,
            is_in=is_in,
            lt=lt,
            lte=lte,
            not_eq=not_eq,
            not_in=not_in,
            is_critical=is_critical,
        )

    def get_condition(self) -> TestValueCondition:
        if self.condition.has_condition():
            return self.condition
        metric_result = self.metric.get_result()
        ref_value = metric_result.reference_entropy
        if ref_value is not None:
            return TestValueCondition(eq=approx(ref_value, relative=0.1))
        return TestValueCondition(gt=0)

    def calculate_value_for_test(self) -> Numeric:
        return self.metric.get_result().current_entropy

    def get_description(self, value: Numeric) -> str:
        return f"Score Entropy (top-{self.k}) is {value:.3}. The test threshold is {self.get_condition()}"

    @property
    def metric(self):
        return self._metric


@default_renderer(wrap_type=TestScoreEntropy)
class TestScoreEntropyRenderer(TestRenderer):
    def render_html(self, obj: TestScoreEntropy) -> TestHtmlInfo:
        info = super().render_html(obj)
        metric_result = obj.metric.get_result()
        distr_fig = plot_4_distr(
            curr_1=HistogramData.from_distribution(metric_result.current_top_k_distr),
            curr_2=HistogramData.from_distribution(metric_result.current_other_distr),
            ref_1=HistogramData.from_distribution(metric_result.reference_top_k_distr),
            ref_2=HistogramData.from_distribution(metric_result.reference_other_distr),
            name_1="top_k",
            name_2="other",
            xaxis_name="scores",
            color_2="secondary",
        )
        info.with_details("", plotly_figure(figure=distr_fig, title=""))
        return info
