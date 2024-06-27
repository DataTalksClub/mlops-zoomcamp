import uuid
from typing import List
from typing import Optional

from evidently.suite.base_suite import Snapshot
from evidently.ui.base import Project
from evidently.ui.base import ProjectManager
from evidently.ui.type_aliases import STR_UUID
from evidently.ui.type_aliases import ZERO_UUID
from evidently.ui.type_aliases import OrgID
from evidently.ui.type_aliases import TeamID
from evidently.ui.type_aliases import UserID
from evidently.ui.workspace.base import WorkspaceBase


class WorkspaceView(WorkspaceBase):
    def __init__(
        self,
        user_id: Optional[UserID],
        project_manager: ProjectManager,
    ):
        self.project_manager = project_manager
        self.user_id = user_id or ZERO_UUID

    def create_project(self, name: str, description: Optional[str] = None, team_id: TeamID = None) -> Project:
        return self.project_manager.create_project(
            name, user_id=self.user_id, team_id=team_id or ZERO_UUID, description=description
        )

    def add_project(self, project: Project, team_id: TeamID = None) -> Project:
        project = self.project_manager.add_project(project, user_id=self.user_id, team_id=team_id or ZERO_UUID)
        return project

    def get_project(self, project_id: STR_UUID) -> Optional[Project]:
        if isinstance(project_id, str):
            project_id = uuid.UUID(project_id)
        return self.project_manager.get_project(self.user_id, project_id)

    def delete_project(self, project_id: STR_UUID):
        if isinstance(project_id, str):
            project_id = uuid.UUID(project_id)
        self.project_manager.delete_project(self.user_id, project_id)

    def list_projects(self, team_id: Optional[TeamID] = None, org_id: Optional[OrgID] = None) -> List[Project]:
        return self.project_manager.list_projects(self.user_id, team_id or ZERO_UUID, org_id or ZERO_UUID)

    def add_snapshot(self, project_id: STR_UUID, snapshot: Snapshot):
        if isinstance(project_id, str):
            project_id = uuid.UUID(project_id)
        self.project_manager.add_snapshot(self.user_id, project_id, snapshot)

    def delete_snapshot(self, project_id: STR_UUID, snapshot_id: STR_UUID):
        if isinstance(project_id, str):
            project_id = uuid.UUID(project_id)
        if isinstance(snapshot_id, str):
            snapshot_id = uuid.UUID(snapshot_id)
        self.project_manager.delete_snapshot(self.user_id, project_id, snapshot_id)

    def search_project(
        self, project_name: str, team_id: Optional[TeamID] = None, org_id: Optional[OrgID] = None
    ) -> List[Project]:
        return self.project_manager.search_project(
            self.user_id, project_name, team_id or ZERO_UUID, org_id or ZERO_UUID
        )


class LocalWorkspaceView(WorkspaceView):
    def __init__(self, path: str):
        from evidently.ui.storage.local import create_local_project_manager

        self.path = path
        super().__init__(None, create_local_project_manager(path=path, autorefresh=False))

    @classmethod
    def create(cls, path: str):
        return LocalWorkspaceView(path)

    def refresh(self):
        from evidently.ui.storage.local import create_local_project_manager

        self.project_manager = create_local_project_manager(path=self.path, autorefresh=False)


Workspace = LocalWorkspaceView
