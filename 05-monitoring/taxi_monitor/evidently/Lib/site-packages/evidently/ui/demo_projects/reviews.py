from datetime import datetime
from datetime import timedelta

import numpy as np
from sklearn import datasets

from evidently import ColumnMapping
from evidently import descriptors
from evidently import metrics
from evidently.renderers.html_widgets import WidgetSize
from evidently.report import Report
from evidently.ui.dashboards import CounterAgg
from evidently.ui.dashboards import DashboardPanelCounter
from evidently.ui.dashboards import DashboardPanelPlot
from evidently.ui.dashboards import PanelValue
from evidently.ui.dashboards import PlotType
from evidently.ui.dashboards import ReportFilter
from evidently.ui.demo_projects import DemoProject
from evidently.ui.workspace import WorkspaceBase


def create_data():
    reviews_data = datasets.fetch_openml(name="Womens-E-Commerce-Clothing-Reviews", version=2, as_frame="auto")
    reviews = reviews_data.frame
    for name, rs in (("TheOtherStore", 0), ("AMajorCompetitor", 42), ("AwesomeShop", 100)):
        np.random.seed(rs)
        random_index = np.random.choice(reviews.index, 300, replace=False)
        reviews.loc[random_index, "Review_Text"] = (
            reviews.loc[random_index, "Review_Text"] + f" mention competitor {name}"
        )

    np.random.seed(13)
    random_index = np.random.choice(reviews.index, 1000, replace=False)
    reviews.loc[random_index, "Review_Text"] = (
        reviews.loc[random_index, "Review_Text"] + " mention www.someurl.someurl "
    )
    reviews["prediction"] = reviews["Rating"]
    np.random.seed(0)
    random_index = np.random.choice(reviews.index, 2000, replace=False)
    reviews.loc[random_index, "prediction"] = 1
    reference = reviews.sample(n=5000, replace=True, ignore_index=True, random_state=42)
    current = reviews
    column_mapping = ColumnMapping(
        target="Rating",
        prediction="prediction",
        numerical_features=["Age", "Positive_Feedback_Count"],
        categorical_features=["Division_Name", "Department_Name", "Class_Name"],
        text_features=["Review_Text", "Title"],
    )
    return current, reference, column_mapping


def create_report(i: int, data):
    current, reference, column_mapping = data
    text_report = Report(
        metrics=[
            metrics.DatasetSummaryMetric(),
            metrics.DatasetDriftMetric(),
            metrics.ColumnDriftMetric(column_name="prediction"),
            metrics.ColumnDriftMetric(column_name="Rating"),
            metrics.ColumnDriftMetric(column_name="Age"),
            metrics.ColumnDriftMetric(column_name="Positive_Feedback_Count"),
            metrics.ColumnDriftMetric(column_name="Division_Name"),
            metrics.ColumnDriftMetric(column_name="Department_Name"),
            metrics.ColumnDriftMetric(column_name="Class_Name"),
            metrics.ColumnDriftMetric(column_name="Review_Text"),
            metrics.ColumnDriftMetric(column_name="Title"),
            metrics.ClassificationQualityMetric(),
            metrics.ColumnSummaryMetric(column_name=descriptors.OOV(display_name="OOV").for_column("Review_Text")),
            metrics.ColumnSummaryMetric(
                column_name=descriptors.NonLetterCharacterPercentage(
                    display_name="Non Letter Character Percentage"
                ).for_column("Review_Text")
            ),
            metrics.ColumnSummaryMetric(
                column_name=descriptors.Sentiment(display_name="Sentiment").for_column("Review_Text")
            ),
            metrics.ColumnSummaryMetric(
                column_name=descriptors.RegExp(display_name="urls", reg_exp=r".*(http|www)\S+.*").for_column(
                    "Review_Text"
                )
            ),
            metrics.ColumnValueRangeMetric(
                column_name=descriptors.TextLength(display_name="TextLength in the Range").for_column("Review_Text"),
                left=1,
                right=1000,
            ),
            metrics.ColumnCategoryMetric(
                column_name=descriptors.TriggerWordsPresence(
                    display_name="competitors",
                    words_list=["theotherstore", "amajorcompetitor", "awesomeshop"],
                    lemmatize=False,
                ).for_column("Review_Text"),
                category=1,
            ),
            metrics.ColumnCategoryMetric(column_name="Rating", category=1),
            metrics.ColumnCategoryMetric(column_name="Rating", category=5),
        ],
        timestamp=datetime(2023, 1, 29) + timedelta(days=i + 1),
    )
    text_report.set_batch_size("daily")

    if i < 17:
        text_report.run(
            reference_data=reference,
            current_data=current.iloc[1000 * i : 1000 * (i + 1), :],
            column_mapping=column_mapping,
        )
    else:
        text_report.run(
            reference_data=reference, current_data=current[(current.Rating < 5)], column_mapping=column_mapping
        )

    return text_report


def create_project(workspace: WorkspaceBase, name: str):
    project = workspace.create_project(name)
    project.description = "A toy demo project using E-commerce Reviews dataset. Text and tabular data, classification."
    # title
    project.dashboard.add_panel(
        DashboardPanelCounter(
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            agg=CounterAgg.NONE,
            title="Classification of E-commerce User Reviews",
        )
    )
    # counters
    project.dashboard.add_panel(
        DashboardPanelCounter(
            title="Model Calls",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            value=PanelValue(
                metric_id="DatasetSummaryMetric",
                field_path=metrics.DatasetSummaryMetric.fields.current.number_of_rows,
                legend="count",
            ),
            text="count",
            agg=CounterAgg.SUM,
            size=WidgetSize.HALF,
        )
    )
    project.dashboard.add_panel(
        DashboardPanelCounter(
            title="Share of Drifted Features",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            value=PanelValue(
                metric_id="DatasetDriftMetric",
                field_path="share_of_drifted_columns",
                legend="share",
            ),
            text="share",
            agg=CounterAgg.LAST,
            size=WidgetSize.HALF,
        )
    )
    # Precision
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Model Precision",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            values=[
                PanelValue(
                    metric_id="ClassificationQualityMetric",
                    field_path="current.precision",
                    legend="precision",
                ),
            ],
            plot_type=PlotType.LINE,
            size=WidgetSize.FULL,
        )
    )
    # target and prediction drift
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Target and Prediction Drift (Jensen-Shannon distance) ",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            values=[
                PanelValue(
                    metric_id="ColumnDriftMetric",
                    metric_args={"column_name.name": "prediction"},
                    field_path=metrics.ColumnDriftMetric.fields.drift_score,
                    legend="prediction drift score",
                ),
                PanelValue(
                    metric_id="ColumnDriftMetric",
                    metric_args={"column_name.name": "Rating"},
                    field_path=metrics.ColumnDriftMetric.fields.drift_score,
                    legend="target drift score",
                ),
            ],
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )
    # features drift
    # text
    values = []
    for col in ["Title", "Review_Text"]:
        values.append(
            PanelValue(
                metric_id="ColumnDriftMetric",
                metric_args={"column_name.name": col},
                field_path=metrics.ColumnDriftMetric.fields.drift_score,
                legend=col,
            ),
        )
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Data Drift: review texts (domain classifier ROC AUC) ",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            values=values,
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )
    # numerical
    values = []
    for col in ["Age", "Positive_Feedback_Count"]:
        values.append(
            PanelValue(
                metric_id="ColumnDriftMetric",
                metric_args={"column_name.name": col},
                field_path=metrics.ColumnDriftMetric.fields.drift_score,
                legend=f"{col}",
            ),
        )
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Data Drift: numerical features (Wasserstein distance)",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            values=values,
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )
    # categorical
    values = []
    for col in ["Division_Name", "Department_Name", "Class_Name"]:
        values.append(
            PanelValue(
                metric_id="ColumnDriftMetric",
                metric_args={"column_name.name": col},
                field_path=metrics.ColumnDriftMetric.fields.drift_score,
                legend=col,
            ),
        )
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Data Drift: categorical features (Jensen-Shannon distance)",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            values=values,
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )
    # Text quality
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Review Text Quality: % of out-of-vocabulary words",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            values=[
                PanelValue(
                    metric_id="ColumnSummaryMetric",
                    metric_args={"column_name": descriptors.OOV(display_name="OOV").for_column("Review_Text")},
                    field_path="current_characteristics.mean",
                    legend="OOV % (mean)",
                ),
            ],
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Review Text Quality: % of non-letter characters",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            values=[
                PanelValue(
                    metric_id="ColumnSummaryMetric",
                    metric_args={
                        "column_name": descriptors.NonLetterCharacterPercentage(
                            display_name="NonLetterCharacterPercentage"
                        ).for_column("Review_Text")
                    },
                    field_path="current_characteristics.mean",
                    legend="NonLetterCharacter % (mean)",
                ),
            ],
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Review Text Quality: share of non-empty reviews",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            values=[
                PanelValue(
                    metric_id="ColumnValueRangeMetric",
                    field_path="current.share_in_range",
                    legend="Reviews with 1-1000 symbols",
                ),
            ],
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )
    # Average review sentiment
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title=" Review sentiment",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            values=[
                PanelValue(
                    metric_id="ColumnSummaryMetric",
                    metric_args={
                        "column_name": descriptors.Sentiment(display_name="Sentiment").for_column("Review_Text")
                    },
                    field_path="current_characteristics.mean",
                    legend="sentiment (mean)",
                ),
            ],
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )
    # Reviews that mention competitors
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Share of reviews mentioning 'TheOtherStore', 'AMajorCompetitor', 'AwesomeShop'",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            values=[
                PanelValue(
                    metric_id="ColumnCategoryMetric",
                    metric_args={
                        "column_name": descriptors.TriggerWordsPresence(
                            display_name="competitors",
                            words_list=["theotherstore", "amajorcompetitor", "awesomeshop"],
                            lemmatize=False,
                        ).for_column("Review_Text"),
                        "category": 1,
                    },
                    field_path="current.category_ratio",
                    legend="reviews with competitors",
                ),
            ],
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )
    # Reviews that mention url
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Share of reviews with URLs",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            values=[
                PanelValue(
                    metric_id="ColumnSummaryMetric",
                    metric_args={
                        "column_name": descriptors.RegExp(display_name="urls", reg_exp=r".*(http|www)\S+.*").for_column(
                            "Review_Text"
                        )
                    },
                    field_path="current_characteristics.mean",
                    legend="reviews with URLs",
                ),
            ],
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )
    # Rating ratio
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title='Share of reviews ranked "1"',
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            values=[
                PanelValue(
                    metric_id="ColumnCategoryMetric",
                    metric_args={"column_name.name": "Rating", "category": 1},
                    field_path="current.category_ratio",
                    legend='share of "1"',
                ),
            ],
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title='Share of reviews ranked "5"',
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            values=[
                PanelValue(
                    metric_id="ColumnCategoryMetric",
                    metric_args={"column_name.name": "Rating", "category": 5},
                    field_path="current.category_ratio",
                    legend='share of "5"',
                ),
            ],
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )

    project.save()
    return project


reviews_demo_project = DemoProject(
    name="Demo project - Reviews",
    create_data=create_data,
    create_report=create_report,
    create_project=create_project,
    create_test_suite=None,
    count=19,
)

if __name__ == "__main__":
    # create_demo_project("http://localhost:8080")
    reviews_demo_project.create("workspace")
