import dataclasses
import datetime
import uuid
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import TypeVar

from evidently._pydantic_compat import BaseModel
from evidently.base_metric import Metric
from evidently.model.dashboard import DashboardInfo
from evidently.report import Report
from evidently.suite.base_suite import MetadataValueType
from evidently.test_suite import TestSuite
from evidently.ui.base import EntityType
from evidently.ui.base import Org
from evidently.ui.base import Project
from evidently.ui.base import Role
from evidently.ui.base import SnapshotMetadata
from evidently.ui.base import Team
from evidently.ui.base import User
from evidently.ui.type_aliases import OrgID
from evidently.ui.type_aliases import RoleID
from evidently.ui.type_aliases import TeamID
from evidently.ui.type_aliases import UserID


class MetricModel(BaseModel):
    id: str

    @classmethod
    def from_metric(cls, metric: Metric):
        return cls(id=metric.get_id())


class ReportModel(BaseModel):
    id: uuid.UUID
    timestamp: datetime.datetime
    metrics: List[MetricModel]
    metadata: Dict[str, MetadataValueType]
    tags: List[str]

    @classmethod
    def from_report(cls, report: Report):
        return cls(
            id=report.id,
            timestamp=report.timestamp,
            metrics=[MetricModel.from_metric(m) for m in report._first_level_metrics],
            metadata=report.metadata,
            tags=report.tags,
        )

    @classmethod
    def from_snapshot(cls, snapshot: SnapshotMetadata):
        return cls(
            id=snapshot.id,
            timestamp=snapshot.timestamp,
            metrics=[],
            metadata=snapshot.metadata,
            tags=snapshot.tags,
        )


class TestSuiteModel(BaseModel):
    id: uuid.UUID
    timestamp: datetime.datetime
    metadata: Dict[str, MetadataValueType]
    tags: List[str]

    @classmethod
    def from_report(cls, report: TestSuite):
        return cls(id=report.id, timestamp=report.timestamp, metadata=report.metadata, tags=report.tags)

    @classmethod
    def from_snapshot(cls, snapshot: SnapshotMetadata):
        return cls(
            id=snapshot.id,
            timestamp=snapshot.timestamp,
            metadata=snapshot.metadata,
            tags=snapshot.tags,
        )


class DashboardInfoModel(BaseModel):
    name: str
    widgets: List[Any]
    min_timestamp: Optional[datetime.datetime] = None
    max_timestamp: Optional[datetime.datetime] = None

    @classmethod
    def from_dashboard_info(cls, dashboard_info: DashboardInfo):
        return cls(**dataclasses.asdict(dashboard_info))

    @classmethod
    def from_project_with_time_range(
        cls,
        project: Project,
        timestamp_start: Optional[datetime.datetime] = None,
        timestamp_end: Optional[datetime.datetime] = None,
    ):
        time_range: Dict[str, Optional[datetime.datetime]]
        snapshots = project.list_snapshots()
        if len(snapshots) == 0:
            time_range = {"min_timestamp": None, "max_timestamp": None}
        else:
            time_range = dict(
                min_timestamp=min(r.timestamp for r in snapshots),
                max_timestamp=max(r.timestamp for r in snapshots),
            )

        info = project.build_dashboard_info(timestamp_start=timestamp_start, timestamp_end=timestamp_end)

        return cls(**dataclasses.asdict(info), **time_range)


class OrgModel(BaseModel):
    id: OrgID
    name: str

    @classmethod
    def from_org(cls, org: Org):
        return OrgModel(id=org.id, name=org.name)

    def to_org(self) -> Org:
        return Org(id=self.id, name=self.name)


class TeamModel(BaseModel):
    id: TeamID
    name: str

    @classmethod
    def from_team(cls, team: Team):
        return TeamModel(id=team.id, name=team.name)

    def to_team(self) -> Team:
        return Team(id=self.id, name=self.name)


UT = TypeVar("UT", bound="UserModel")


class UserModel(BaseModel):
    id: UserID
    name: str
    email: str

    @classmethod
    def from_user(cls, user: User):
        return UserModel(id=user.id, name=user.name, email=user.email)

    def merge(self: UT, other: "UserModel") -> UT:
        kwargs = {f: getattr(other, f, None) or getattr(self, f) for f in self.__fields__}
        return self.__class__(**kwargs)


class RoleModel(BaseModel):
    id: RoleID
    name: str
    entity_type: Optional[EntityType]

    @classmethod
    def from_role(cls, role: Role):
        return RoleModel(id=role.id, name=role.name, entity_type=role.entity_type)
