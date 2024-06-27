import datetime
import json
import uuid
from typing import Callable
from typing import List
from typing import Optional
from typing import Sequence

from litestar import Response
from litestar import Router
from litestar import delete
from litestar import get
from litestar import post
from litestar.exceptions import HTTPException
from litestar.params import Dependency
from litestar.params import Parameter
from typing_extensions import Annotated

from evidently.report.report import METRIC_GENERATORS
from evidently.report.report import METRIC_PRESETS
from evidently.suite.base_suite import Snapshot
from evidently.test_suite.test_suite import TEST_GENERATORS
from evidently.test_suite.test_suite import TEST_PRESETS
from evidently.ui.api.models import DashboardInfoModel
from evidently.ui.api.models import ReportModel
from evidently.ui.api.models import TestSuiteModel
from evidently.ui.base import EntityType
from evidently.ui.base import Permission
from evidently.ui.base import Project
from evidently.ui.base import ProjectManager
from evidently.ui.dashboards.base import DashboardPanel
from evidently.ui.errors import NotEnoughPermissions
from evidently.ui.type_aliases import ZERO_UUID
from evidently.ui.type_aliases import OrgID
from evidently.ui.type_aliases import TeamID
from evidently.ui.type_aliases import UserID
from evidently.utils import NumpyEncoder


@get("/{project_id:uuid}/reports", sync_to_thread=True)
def list_reports(
    project_id: Annotated[uuid.UUID, Parameter(title="id of project")],
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
) -> List[ReportModel]:
    project = project_manager.get_project(user_id, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    reports = [ReportModel.from_snapshot(s) for s in project.list_snapshots(include_test_suites=False) if s.is_report]
    log_event("list_reports", reports_count=len(reports))
    return reports


@get("/", sync_to_thread=True)
def list_projects(
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
    team_id: Annotated[Optional[TeamID], Parameter(title="filter by team")] = None,
    org_id: Annotated[Optional[OrgID], Parameter(title="filter by org")] = None,
) -> Sequence[Project]:
    projects = project_manager.list_projects(user_id, team_id, org_id)
    log_event("list_projects", project_count=len(projects))
    return projects


@get("/{project_id:uuid}/info", sync_to_thread=True)
def get_project_info(
    project_id: Annotated[uuid.UUID, Parameter(title="id of project")],
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
) -> Project:
    project = project_manager.get_project(user_id, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    log_event("get_project_info")
    return project


@get("/search/{project_name:str}", sync_to_thread=True)
def search_projects(
    project_name: Annotated[str, Parameter(title="Name of the project to search")],
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
    team_id: Annotated[Optional[TeamID], Parameter(title="filter by team")] = None,
    org_id: Annotated[Optional[OrgID], Parameter(title="filter by org")] = None,
) -> List[Project]:
    log_event("search_projects")
    return project_manager.search_project(user_id, team_id=team_id, org_id=org_id, project_name=project_name)


@post("/{project_id:uuid}/info", sync_to_thread=True)
def update_project_info(
    project_id: Annotated[uuid.UUID, Parameter(title="id of project")],
    data: Project,
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
) -> Project:
    project = project_manager.get_project(user_id, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    if not project_manager.auth.check_entity_permission(
        user_id, EntityType.Project, project.id, Permission.PROJECT_WRITE
    ):
        raise NotEnoughPermissions()
    project.description = data.description
    project.name = data.name
    project.date_from = data.date_from
    project.date_to = data.date_to
    project.dashboard = data.dashboard
    project.save()
    log_event("update_project_info")
    return project


@get("/{project_id:uuid}/reload", sync_to_thread=True)
def reload_project_snapshots(
    project_id: Annotated[uuid.UUID, Parameter(title="id of project")],
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
) -> None:
    project = project_manager.get_project(user_id, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    project.reload(reload_snapshots=True)
    log_event("reload_project_snapshots")


@get("/{project_id:uuid}/test_suites", sync_to_thread=True)
def list_test_suites(
    project_id: Annotated[uuid.UUID, Parameter(title="id of project")],
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
) -> List[TestSuiteModel]:
    project = project_manager.get_project(user_id, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    log_event("list_test_suites")
    return [TestSuiteModel.from_snapshot(s) for s in project.list_snapshots(include_reports=False) if not s.is_report]


@get(
    "/{project_id:uuid}/{snapshot_id:uuid}/graphs_data/{graph_id:str}",
    sync_to_thread=True,
)
def get_snapshot_graph_data(
    project_id: Annotated[uuid.UUID, Parameter(title="id of project")],
    snapshot_id: Annotated[uuid.UUID, Parameter(title="id of snapshot")],
    graph_id: Annotated[str, Parameter(title="id of graph in snapshot")],
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
) -> Response:
    project = project_manager.get_project(user_id, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    snapshot = project.get_snapshot_metadata(snapshot_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    graph = snapshot.additional_graphs.get(graph_id)
    if graph is None:
        raise HTTPException(status_code=404, detail="Graph not found")
    log_event("get_snapshot_graph_data")
    return Response(media_type="application/json", content=json.dumps(graph, cls=NumpyEncoder))


@get("/{project_id:uuid}/{snapshot_id:uuid}/download", sync_to_thread=True)
def get_snapshot_download(
    project_id: Annotated[uuid.UUID, Parameter(title="id of project")],
    snapshot_id: Annotated[uuid.UUID, Parameter(title="id of snapshot")],
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
    report_format: str = "html",
) -> Response:
    project = project_manager.get_project(user_id, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    snapshot = project.get_snapshot_metadata(snapshot_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    report = snapshot.as_report_base()
    if report_format == "html":
        return Response(
            report.get_html(),
            headers={"content-disposition": f"attachment;filename={snapshot_id}.html"},
        )
    if report_format == "json":
        return Response(
            report.json(),
            headers={"content-disposition": f"attachment;filename={snapshot_id}.json"},
        )
    log_event("get_snapshot_download")
    return Response(f"Unknown format {report_format}", status_code=400)


@get("/{project_id:uuid}/{snapshot_id:uuid}/data", sync_to_thread=True)
def get_snapshot_data(
    project_id: Annotated[uuid.UUID, Parameter(title="id of project")],
    snapshot_id: Annotated[uuid.UUID, Parameter(title="id of snapshot")],
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
) -> Response:
    project = project_manager.get_project(user_id, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    snapshot_meta = project.get_snapshot_metadata(snapshot_id)
    if snapshot_meta is None:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    info = DashboardInfoModel.from_dashboard_info(snapshot_meta.dashboard_info)
    snapshot = snapshot_meta.load()
    log_event(
        "get_snapshot_data",
        snapshot_type="report" if snapshot.is_report else "test_suite",
        metrics=[m.get_id() for m in snapshot.first_level_metrics()],
        metric_presets=snapshot.metadata.get(METRIC_PRESETS, []),
        metric_generators=snapshot.metadata.get(METRIC_GENERATORS, []),
        tests=[t.get_id() for t in snapshot.first_level_tests()],
        test_presets=snapshot.metadata.get(TEST_PRESETS, []),
        test_generators=snapshot.metadata.get(TEST_GENERATORS, []),
    )
    return Response(json.dumps(info.dict(), cls=NumpyEncoder), media_type="application/json")


@get("/{project_id:uuid}/dashboard/panels", sync_to_thread=True)
def list_project_dashboard_panels(
    project_id: Annotated[uuid.UUID, Parameter(title="id of project")],
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
) -> List[DashboardPanel]:
    project = project_manager.get_project(user_id, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    log_event("list_project_dashboard_panels")
    return list(project.dashboard.panels)


@get("/{project_id:uuid}/dashboard", sync_to_thread=True)
def project_dashboard(
    project_id: Annotated[uuid.UUID, Parameter(title="id of project")],
    # TODO: no datetime, as it unable to validate '2023-07-09T02:03'
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
    timestamp_start: Optional[str] = None,
    timestamp_end: Optional[str] = None,
) -> Response:
    timestamp_start_ = datetime.datetime.fromisoformat(timestamp_start) if timestamp_start else None
    timestamp_end_ = datetime.datetime.fromisoformat(timestamp_end) if timestamp_end else None
    project = project_manager.get_project(user_id, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    info = DashboardInfoModel.from_project_with_time_range(
        project,
        timestamp_start=timestamp_start_,
        timestamp_end=timestamp_end_,
    )
    log_event("project_dashboard")
    return Response(content=json.dumps(info.dict(), cls=NumpyEncoder), media_type="application/json")


@post("/", sync_to_thread=True)
def add_project(
    data: Project,
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
    team_id: TeamID = ZERO_UUID,
) -> Project:
    p = project_manager.add_project(data, user_id, team_id)
    log_event("add_project")
    return p


@delete("/{project_id:uuid}", sync_to_thread=True)
def delete_project(
    project_id: Annotated[uuid.UUID, Parameter(title="id of project")],
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
) -> None:
    project_manager.delete_project(user_id, project_id)
    log_event("delete_project")


@post("/{project_id:uuid}/snapshots", sync_to_thread=True)
def add_snapshot(
    project_id: Annotated[uuid.UUID, Parameter(title="id of project")],
    parsed_json: Snapshot,
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
) -> None:
    if project_manager.get_project(user_id, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")

    project_manager.add_snapshot(user_id, project_id, parsed_json)
    log_event("add_snapshot")


@delete("/{project_id:uuid}/{snapshot_id:uuid}", sync_to_thread=True)
def delete_snapshot(
    project_id: Annotated[uuid.UUID, Parameter(title="id of project")],
    snapshot_id: Annotated[uuid.UUID, Parameter(title="id of snapshot")],
    project_manager: Annotated[ProjectManager, Dependency(skip_validation=True)],
    log_event: Callable,
    user_id: UserID,
) -> None:
    project_manager.delete_snapshot(user_id, project_id, snapshot_id)
    log_event("delete_snapshot")


def create_projects_api(guard: Callable) -> Router:
    return Router(
        "/projects",
        route_handlers=[
            Router(
                "",
                route_handlers=[
                    list_projects,
                    list_reports,
                    get_project_info,
                    search_projects,
                    list_test_suites,
                    get_snapshot_graph_data,
                    get_snapshot_data,
                    get_snapshot_download,
                    list_project_dashboard_panels,
                    project_dashboard,
                ],
            ),
            Router(
                "",
                route_handlers=[
                    update_project_info,
                    reload_project_snapshots,
                    add_project,
                    delete_project,
                    add_snapshot,
                    delete_snapshot,
                ],
                guards=[guard],
            ),
        ],
    )
