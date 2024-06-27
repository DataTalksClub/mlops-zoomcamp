import abc
from typing import List
from typing import Optional

from evidently.report import Report
from evidently.suite.base_suite import Snapshot
from evidently.test_suite import TestSuite
from evidently.ui.base import Project
from evidently.ui.type_aliases import STR_UUID
from evidently.ui.type_aliases import OrgID
from evidently.ui.type_aliases import TeamID


class WorkspaceBase(abc.ABC):
    @abc.abstractmethod
    def create_project(self, name: str, description: Optional[str] = None, team_id: TeamID = None) -> Project:
        raise NotImplementedError

    @abc.abstractmethod
    def add_project(self, project: Project, team_id: TeamID = None) -> Project:
        raise NotImplementedError

    @abc.abstractmethod
    def get_project(self, project_id: STR_UUID) -> Optional[Project]:
        raise NotImplementedError

    @abc.abstractmethod
    def delete_project(self, project_id: STR_UUID):
        raise NotImplementedError

    @abc.abstractmethod
    def list_projects(self, team_id: Optional[TeamID] = None, org_id: Optional[OrgID] = None) -> List[Project]:
        raise NotImplementedError

    def add_report(self, project_id: STR_UUID, report: Report):
        self.add_snapshot(project_id, report.to_snapshot())

    def add_test_suite(self, project_id: STR_UUID, test_suite: TestSuite):
        self.add_snapshot(project_id, test_suite.to_snapshot())

    @abc.abstractmethod
    def add_snapshot(self, project_id: STR_UUID, snapshot: Snapshot):
        raise NotImplementedError

    @abc.abstractmethod
    def delete_snapshot(self, project_id: STR_UUID, snapshot_id: STR_UUID):
        raise NotImplementedError

    @abc.abstractmethod
    def search_project(
        self, project_name: str, team_id: Optional[TeamID] = None, org_id: Optional[OrgID] = None
    ) -> List[Project]:
        raise NotImplementedError
