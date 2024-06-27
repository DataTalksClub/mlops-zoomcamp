from datetime import datetime
from datetime import timedelta

import pandas as pd

from evidently import ColumnMapping
from evidently import metrics
from evidently.renderers.html_widgets import WidgetSize
from evidently.report import Report
from evidently.ui.dashboards import CounterAgg
from evidently.ui.dashboards import DashboardPanelCounter
from evidently.ui.dashboards import PanelValue
from evidently.ui.dashboards import ReportFilter
from evidently.ui.demo_projects import DemoProject
from evidently.ui.workspace.base import WorkspaceBase


def create_data():
    current = reference = pd.DataFrame({"a": [0, 1, 2], "b": [1, 2, 3]})
    column_mapping = ColumnMapping()
    return current, reference, column_mapping


def create_report(i: int, data):
    current, reference, column_mapping = data
    report = Report(
        metrics=[metrics.ColumnDriftMetric("a")],
        timestamp=datetime(2023, 1, 29) + timedelta(days=i + 1),
    )
    report.set_batch_size("daily")

    report.run(reference_data=reference, current_data=current, column_mapping=column_mapping)

    return report


def create_project(workspace: WorkspaceBase, name: str):
    project = workspace.create_project(name)
    project.description = "Simple demo project"
    # title
    project.dashboard.add_panel(
        DashboardPanelCounter(
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            agg=CounterAgg.NONE,
            title="Panels",
        )
    )
    # counters
    project.dashboard.add_panel(
        DashboardPanelCounter(
            title="Model Calls",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            value=PanelValue(
                metric_id="ColumnDriftMetric",
                field_path=metrics.ColumnDriftMetric.fields.drift_detected,
                legend="count",
            ),
            text="count",
            agg=CounterAgg.SUM,
            size=WidgetSize.HALF,
        )
    )
    project.save()
    return project


simple_demo_project = DemoProject(
    name="Demo project - Simple",
    create_data=create_data,
    create_report=create_report,
    create_project=create_project,
    create_test_suite=None,
    count=2,
)

if __name__ == "__main__":
    # create_demo_project("http://localhost:8080")
    simple_demo_project.create("workspace")
