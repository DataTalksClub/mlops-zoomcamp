import contextlib
import datetime
import json
import uuid
from abc import ABC
from abc import abstractmethod
from enum import Enum
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from evidently._pydantic_compat import UUID4
from evidently._pydantic_compat import BaseModel
from evidently._pydantic_compat import Field
from evidently._pydantic_compat import PrivateAttr
from evidently._pydantic_compat import parse_obj_as
from evidently.model.dashboard import DashboardInfo
from evidently.renderers.notebook_utils import determine_template
from evidently.suite.base_suite import MetadataValueType
from evidently.suite.base_suite import ReportBase
from evidently.suite.base_suite import Snapshot
from evidently.ui.dashboards.base import DashboardConfig
from evidently.ui.dashboards.base import PanelValue
from evidently.ui.dashboards.base import ReportFilter
from evidently.ui.dashboards.test_suites import TestFilter
from evidently.ui.errors import NotEnoughPermissions
from evidently.ui.errors import OrgNotFound
from evidently.ui.errors import ProjectNotFound
from evidently.ui.errors import TeamNotFound
from evidently.ui.type_aliases import ZERO_UUID
from evidently.ui.type_aliases import BlobID
from evidently.ui.type_aliases import DataPoints
from evidently.ui.type_aliases import DataPointsAsType
from evidently.ui.type_aliases import EntityID
from evidently.ui.type_aliases import OrgID
from evidently.ui.type_aliases import PointType
from evidently.ui.type_aliases import ProjectID
from evidently.ui.type_aliases import RoleID
from evidently.ui.type_aliases import SnapshotID
from evidently.ui.type_aliases import TeamID
from evidently.ui.type_aliases import TestResultPoints
from evidently.ui.type_aliases import UserID
from evidently.utils import NumpyEncoder
from evidently.utils.dashboard import TemplateParams


class BlobMetadata(BaseModel):
    id: BlobID
    size: Optional[int]


class SnapshotMetadata(BaseModel):
    id: UUID4
    name: Optional[str] = None
    timestamp: datetime.datetime
    metadata: Dict[str, MetadataValueType]
    tags: List[str]
    is_report: bool
    blob: "BlobMetadata"

    _project: "Project" = PrivateAttr(None)
    _dashboard_info: "DashboardInfo" = PrivateAttr(None)
    _additional_graphs: Dict[str, dict] = PrivateAttr(None)

    @property
    def project(self):
        return self._project

    def load(self) -> Snapshot:
        return self.project.project_manager.load_snapshot(self.project._user_id, self.project.id, self.id)

    def as_report_base(self) -> ReportBase:
        value = self.load()
        return value.as_report() if value.is_report else value.as_test_suite()

    def bind(self, project: "Project"):
        self._project = project
        return self

    @classmethod
    def from_snapshot(cls, snapshot: Snapshot, blob: "BlobMetadata") -> "SnapshotMetadata":
        return SnapshotMetadata(
            id=snapshot.id,
            name=snapshot.name,
            timestamp=snapshot.timestamp,
            metadata=snapshot.metadata,
            tags=snapshot.tags,
            is_report=snapshot.is_report,
            blob=blob,
        )

    @property
    def dashboard_info(self):
        if self._dashboard_info is None:
            _, self._dashboard_info, self._additional_graphs = self.as_report_base()._build_dashboard_info()
        return self._dashboard_info

    @property
    def additional_graphs(self):
        if self._additional_graphs is None:
            _, self._dashboard_info, self._additional_graphs = self.as_report_base()._build_dashboard_info()
        return self._additional_graphs


class EntityType(Enum):
    Project = "project"
    Team = "team"
    Org = "org"


class Entity(BaseModel):
    entity_type: ClassVar[EntityType]
    id: EntityID


class Org(Entity):
    entity_type: ClassVar[EntityType] = EntityType.Org
    id: OrgID = Field(default_factory=uuid.uuid4)
    name: str


class Team(Entity):
    entity_type: ClassVar[EntityType] = EntityType.Team
    id: TeamID = Field(default_factory=uuid.uuid4)
    name: str


UT = TypeVar("UT", bound="User")


class User(BaseModel):
    id: UserID = Field(default_factory=uuid.uuid4)
    name: str
    email: str = ""

    def merge(self: UT, other: "User") -> UT:
        kwargs = {f: getattr(other, f, None) or getattr(self, f) for f in self.__fields__}
        return self.__class__(**kwargs)


def _default_dashboard():
    from evidently.ui.dashboards import DashboardConfig

    return DashboardConfig(name="", panels=[])


class Project(Entity):
    entity_type: ClassVar[EntityType] = EntityType.Project

    class Config:
        underscore_attrs_are_private = True

    id: ProjectID = Field(default_factory=uuid.uuid4)
    name: str
    description: Optional[str] = None
    dashboard: "DashboardConfig" = Field(default_factory=_default_dashboard)

    team_id: Optional[TeamID]

    date_from: Optional[datetime.datetime] = None
    date_to: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = Field(default=None)
    # Field(default=datetime.datetime.fromisoformat("1900-01-01T00:00:00"))

    _project_manager: "ProjectManager" = PrivateAttr(None)
    _user_id: UserID = PrivateAttr(None)

    def bind(self, project_manager: Optional["ProjectManager"], user_id: Optional[UserID]):
        # todo: better typing (add optional or forbid optional)
        self._project_manager = project_manager  # type: ignore[assignment]
        self._user_id = user_id  # type: ignore[assignment]
        return self

    @property
    def project_manager(self) -> "ProjectManager":
        if self._project_manager is None:
            raise ValueError("Project is not binded")
        return self._project_manager

    def save(self):
        self.project_manager.update_project(self._user_id, self)
        return self

    def load_snapshot(self, snapshot_id: SnapshotID) -> Snapshot:
        return self.project_manager.load_snapshot(self._user_id, self.id, snapshot_id)

    def add_snapshot(self, snapshot: Snapshot):
        self.project_manager.add_snapshot(self._user_id, self.id, snapshot)

    def delete_snapshot(self, snapshot_id: Union[str, SnapshotID]):
        if isinstance(snapshot_id, str):
            snapshot_id = uuid.UUID(snapshot_id)
        self.project_manager.delete_snapshot(self._user_id, self.id, snapshot_id)

    def list_snapshots(self, include_reports: bool = True, include_test_suites: bool = True) -> List[SnapshotMetadata]:
        return self.project_manager.list_snapshots(self._user_id, self.id, include_reports, include_test_suites)

    def get_snapshot_metadata(self, id: SnapshotID) -> SnapshotMetadata:
        return self.project_manager.get_snapshot_metadata(self._user_id, self.id, id)

    def build_dashboard_info(
        self, timestamp_start: Optional[datetime.datetime], timestamp_end: Optional[datetime.datetime]
    ) -> DashboardInfo:
        return self.dashboard.build(self.project_manager.data, self.id, timestamp_start, timestamp_end)

    def show_dashboard(
        self, timestamp_start: Optional[datetime.datetime] = None, timestamp_end: Optional[datetime.datetime] = None
    ):
        dashboard_info = self.build_dashboard_info(timestamp_start, timestamp_end)
        template_params = TemplateParams(
            dashboard_id="pd_" + str(uuid.uuid4()).replace("-", ""),
            dashboard_info=dashboard_info,
            additional_graphs={},
        )
        # pylint: disable=import-outside-toplevel
        try:
            from IPython.display import HTML

            return HTML(determine_template("inline")(params=template_params))
        except ImportError as err:
            raise Exception("Cannot import HTML from IPython.display, no way to show html") from err

    def reload(self, reload_snapshots: bool = False):
        # fixme: reload snapshots
        project = self.project_manager.get_project(self._user_id, self.id)
        self.__dict__.update(project.__dict__)

        if reload_snapshots:
            self.project_manager.reload_snapshots(self._user_id, self.id)


class MetadataStorage(ABC):
    @abstractmethod
    def add_project(self, project: Project, user: User, team: Team) -> Project:
        raise NotImplementedError

    @abstractmethod
    def get_project(self, project_id: ProjectID) -> Optional[Project]:
        raise NotImplementedError

    @abstractmethod
    def delete_project(self, project_id: ProjectID):
        raise NotImplementedError

    @abstractmethod
    def list_projects(self, project_ids: Optional[Set[ProjectID]]) -> List[Project]:
        raise NotImplementedError

    @abstractmethod
    def add_snapshot(self, project_id: ProjectID, snapshot: Snapshot, blob: "BlobMetadata"):
        raise NotImplementedError

    @abstractmethod
    def delete_snapshot(self, project_id: ProjectID, snapshot_id: SnapshotID):
        raise NotImplementedError

    @abstractmethod
    def search_project(self, project_name: str, project_ids: Optional[Set[ProjectID]]) -> List[Project]:
        raise NotImplementedError

    @abstractmethod
    def list_snapshots(
        self, project_id: ProjectID, include_reports: bool = True, include_test_suites: bool = True
    ) -> List[SnapshotMetadata]:
        raise NotImplementedError

    @abstractmethod
    def get_snapshot_metadata(self, project_id: ProjectID, snapshot_id: SnapshotID) -> SnapshotMetadata:
        raise NotImplementedError

    @abstractmethod
    def update_project(self, project: Project) -> Project:
        raise NotImplementedError

    @abstractmethod
    def reload_snapshots(self, project_id: ProjectID):
        raise NotImplementedError


class BlobStorage(ABC):
    @abstractmethod
    @contextlib.contextmanager
    def open_blob(self, id: BlobID):
        raise NotImplementedError

    def put_blob(self, blob_id: str, obj):
        raise NotImplementedError

    def get_snapshot_blob_id(self, project_id: ProjectID, snapshot: Snapshot) -> BlobID:
        raise NotImplementedError

    def put_snapshot(self, project_id: ProjectID, snapshot: Snapshot) -> BlobMetadata:
        id = self.get_snapshot_blob_id(project_id, snapshot)
        self.put_blob(id, json.dumps(snapshot.dict(), cls=NumpyEncoder))
        return self.get_blob_metadata(id)

    def get_blob_metadata(self, blob_id: BlobID) -> BlobMetadata:
        raise NotImplementedError


class DataStorage(ABC):
    @abstractmethod
    def extract_points(self, project_id: ProjectID, snapshot: Snapshot):
        raise NotImplementedError

    def load_points(
        self,
        project_id: ProjectID,
        filter: "ReportFilter",
        values: List["PanelValue"],
        timestamp_start: Optional[datetime.datetime],
        timestamp_end: Optional[datetime.datetime],
    ) -> DataPoints:
        return self.load_points_as_type(float, project_id, filter, values, timestamp_start, timestamp_end)

    @staticmethod
    def parse_value(cls: Type[PointType], value: Any) -> PointType:
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            value = json.loads(value)
        return parse_obj_as(cls, value)

    @abstractmethod
    def load_test_results(
        self,
        project_id: ProjectID,
        filter: "ReportFilter",
        test_filters: List["TestFilter"],
        time_agg: Optional[str],
        timestamp_start: Optional[datetime.datetime],
        timestamp_end: Optional[datetime.datetime],
    ) -> TestResultPoints:
        raise NotImplementedError

    @abstractmethod
    def load_points_as_type(
        self,
        cls: Type[PointType],
        project_id: ProjectID,
        filter: "ReportFilter",
        values: List["PanelValue"],
        timestamp_start: Optional[datetime.datetime],
        timestamp_end: Optional[datetime.datetime],
    ) -> DataPointsAsType[PointType]:
        raise NotImplementedError


class Permission(Enum):
    GRANT_ROLE = "all_grant_role"
    REVOKE_ROLE = "all_revoke_role"

    ORG_READ = "org_read"
    ORG_WRITE = "org_write"
    ORG_CREATE_TEAM = "org_create_team"
    ORG_DELETE = "org_delete"

    TEAM_READ = "team_read"
    TEAM_WRITE = "team_write"
    TEAM_CREATE_PROJECT = "team_create_project"
    TEAM_DELETE = "team_delete"

    PROJECT_READ = "project_read"
    PROJECT_WRITE = "project_write"
    PROJECT_DELETE = "project_delete"
    PROJECT_SNAPSHOT_ADD = "project_snapshot_add"
    PROJECT_SNAPSHOT_DELETE = "project_snapshot_delete"


class Role(BaseModel):
    id: RoleID
    name: str
    entity_type: Optional[EntityType]
    permissions: Set[Permission]


class DefaultRole(Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


DEFAULT_ROLE_PERMISSIONS: Dict[Tuple[DefaultRole, Optional[EntityType]], Set[Permission]] = {
    (DefaultRole.OWNER, None): set(Permission),
    (DefaultRole.EDITOR, EntityType.Org): {
        Permission.ORG_READ,
        Permission.ORG_CREATE_TEAM,
        Permission.TEAM_READ,
        Permission.TEAM_WRITE,
        Permission.TEAM_CREATE_PROJECT,
        Permission.PROJECT_READ,
        Permission.PROJECT_WRITE,
        Permission.PROJECT_SNAPSHOT_ADD,
    },
    (DefaultRole.EDITOR, EntityType.Team): {
        Permission.TEAM_READ,
        Permission.TEAM_WRITE,
        Permission.TEAM_CREATE_PROJECT,
        Permission.PROJECT_READ,
        Permission.PROJECT_WRITE,
        Permission.PROJECT_SNAPSHOT_ADD,
    },
    (DefaultRole.EDITOR, EntityType.Project): {
        Permission.PROJECT_READ,
        Permission.PROJECT_WRITE,
        Permission.PROJECT_SNAPSHOT_ADD,
    },
    (DefaultRole.VIEWER, EntityType.Org): {Permission.ORG_READ},
    (DefaultRole.VIEWER, EntityType.Team): {Permission.TEAM_READ, Permission.PROJECT_READ},
    (DefaultRole.VIEWER, EntityType.Project): {Permission.PROJECT_READ},
}

ENTITY_READ_PERMISSION = {
    EntityType.Org: Permission.ORG_READ,
    EntityType.Team: Permission.TEAM_READ,
    EntityType.Project: Permission.PROJECT_READ,
}

ENTITY_NOT_FOUND_ERROR = {
    EntityType.Org: OrgNotFound,
    EntityType.Team: TeamNotFound,
    EntityType.Project: ProjectNotFound,
}


def get_default_role_permissions(
    default_role: DefaultRole, entity_type: Optional[EntityType]
) -> Tuple[Optional[EntityType], Set[Permission]]:
    res = DEFAULT_ROLE_PERMISSIONS.get((default_role, entity_type))
    if res is None:
        entity_type = None
        res = DEFAULT_ROLE_PERMISSIONS.get((default_role, None))
    if res is None:
        raise ValueError(f"No default role for ({default_role}, {entity_type}) pair")
    return entity_type, res


class UserWithRoles(NamedTuple):
    user: User
    roles: List[Role]


class AuthManager(ABC):
    allow_default_user: bool = True

    def refresh_default_roles(self):
        for (default_role, entity_type), permissions in DEFAULT_ROLE_PERMISSIONS.items():
            role = self.get_default_role(default_role, entity_type)
            if role.permissions != permissions:
                role.permissions = permissions
                self.update_role(role)

    @abstractmethod
    def update_role(self, role: Role):
        raise NotImplementedError

    @abstractmethod
    def get_available_project_ids(
        self, user_id: UserID, team_id: Optional[TeamID], org_id: Optional[OrgID]
    ) -> Optional[Set[ProjectID]]:
        raise NotImplementedError

    @abstractmethod
    def check_entity_permission(
        self, user_id: UserID, entity_type: EntityType, entity_id: EntityID, permission: Permission
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create_user(self, user_id: UserID, name: Optional[str]) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_user(self, user_id: UserID) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def get_default_user(self) -> User:
        raise NotImplementedError

    def get_or_create_user(self, user_id: UserID) -> User:
        user = self.get_user(user_id)
        if user is None:
            user = self.create_user(user_id, str(user_id))
        return user

    @abstractmethod
    def _create_team(self, author: UserID, team: Team, org_id: OrgID) -> Team:
        raise NotImplementedError

    def create_team(self, author: UserID, team: Team, org_id: OrgID) -> Team:
        if not self.check_entity_permission(author, EntityType.Org, org_id, Permission.ORG_CREATE_TEAM):
            raise NotEnoughPermissions()
        return self._create_team(author, team, org_id)

    @abstractmethod
    def get_team(self, team_id: TeamID) -> Optional[Team]:
        raise NotImplementedError

    def get_team_or_error(self, team_id: TeamID) -> Team:
        team = self.get_team(team_id)
        if team is None:
            raise TeamNotFound()
        return team

    @abstractmethod
    def create_org(self, owner: UserID, org: Org):
        raise NotImplementedError

    @abstractmethod
    def get_org(self, org_id: OrgID) -> Optional[Org]:
        raise NotImplementedError

    def delete_org(self, user_id: UserID, org_id: OrgID):
        if not self.check_entity_permission(user_id, EntityType.Org, org_id, Permission.ORG_DELETE):
            raise NotEnoughPermissions()
        self._delete_org(org_id)

    @abstractmethod
    def _delete_org(self, org_id: OrgID):
        raise NotImplementedError

    def get_org_or_error(self, org_id: OrgID) -> Org:
        org = self.get_org(org_id)
        if org is None:
            raise OrgNotFound()
        return org

    def get_or_default_user(self, user_id: UserID) -> User:
        return self.get_or_create_user(user_id) if user_id is not None else self.get_default_user()

    @abstractmethod
    def _delete_team(self, team_id: TeamID):
        raise NotImplementedError

    def delete_team(self, user_id: UserID, team_id: TeamID):
        if not self.check_entity_permission(user_id, EntityType.Team, team_id, Permission.TEAM_DELETE):
            raise NotEnoughPermissions()
        self._delete_team(team_id)

    @abstractmethod
    def get_default_role(self, default_role: DefaultRole, entity_type: Optional[EntityType]) -> Role:
        raise NotImplementedError

    @abstractmethod
    def _grant_entity_role(self, entity_type: EntityType, entity_id: EntityID, user_id: UserID, role: Role):
        raise NotImplementedError

    def grant_entity_role(
        self,
        manager: UserID,
        entity_type: EntityType,
        entity_id: EntityID,
        user_id: UserID,
        role: Role,
        skip_permission_check: bool = False,
    ):
        if not skip_permission_check and not self.check_entity_permission(
            manager, entity_type, entity_id, Permission.GRANT_ROLE
        ):
            raise NotEnoughPermissions()
        self._grant_entity_role(entity_type, entity_id, user_id, role)

    @abstractmethod
    def _revoke_entity_role(self, entity_type: EntityType, entity_id: EntityID, user_id: UserID, role: Role):
        raise NotImplementedError

    def revoke_entity_role(
        self, manager: UserID, entity_type: EntityType, entity_id: EntityID, user_id: UserID, role: Role
    ):
        if not self.check_entity_permission(manager, entity_type, entity_id, Permission.REVOKE_ROLE):
            raise NotEnoughPermissions()
        if manager == user_id:
            raise NotEnoughPermissions()
        self._revoke_entity_role(entity_type, entity_id, user_id, role)

    @abstractmethod
    def _list_entity_users(
        self, entity_type: EntityType, entity_id: EntityID, read_permission: Permission
    ) -> List[User]:
        raise NotImplementedError

    def list_entity_users(self, user_id: UserID, entity_type: EntityType, entity_id: EntityID):
        if not self.check_entity_permission(user_id, entity_type, entity_id, ENTITY_READ_PERMISSION[entity_type]):
            raise ENTITY_NOT_FOUND_ERROR[entity_type]()
        return self._list_entity_users(entity_type, entity_id, ENTITY_READ_PERMISSION[entity_type])

    @abstractmethod
    def _list_entity_users_with_roles(
        self, entity_type: EntityType, entity_id: EntityID, read_permission: Permission
    ) -> List[UserWithRoles]:
        raise NotImplementedError

    def list_entity_users_with_roles(self, user_id: UserID, entity_type: EntityType, entity_id: EntityID):
        if not self.check_entity_permission(user_id, entity_type, entity_id, ENTITY_READ_PERMISSION[entity_type]):
            raise ENTITY_NOT_FOUND_ERROR[entity_type]()
        return self._list_entity_users_with_roles(entity_type, entity_id, ENTITY_READ_PERMISSION[entity_type])

    @abstractmethod
    def list_user_teams(self, user_id: UserID, org_id: Optional[OrgID]) -> List[Team]:
        raise NotImplementedError

    @abstractmethod
    def list_user_orgs(self, user_id: UserID) -> List[Org]:
        raise NotImplementedError

    @abstractmethod
    def list_user_entity_permissions(
        self, user_id: UserID, entity_type: EntityType, entity_id: EntityID
    ) -> Set[Permission]:
        raise NotImplementedError

    @abstractmethod
    def list_user_entity_roles(
        self, user_id: UserID, entity_type: EntityType, entity_id: EntityID
    ) -> List[Tuple[EntityType, EntityID, Role]]:
        raise NotImplementedError

    @abstractmethod
    def list_roles(self, entity_type: Optional[EntityType]) -> List[Role]:
        raise NotImplementedError


class ProjectManager:
    def __init__(self, metadata: MetadataStorage, blob: BlobStorage, data: DataStorage, auth: AuthManager):
        self.metadata: MetadataStorage = metadata
        self.blob: BlobStorage = blob
        self.data: DataStorage = data
        self.auth: AuthManager = auth

    def create_project(
        self,
        name: str,
        user_id: UserID,
        team_id: TeamID,
        description: Optional[str] = None,
    ) -> Project:
        from evidently.ui.dashboards import DashboardConfig

        project = self.add_project(
            Project(
                name=name, description=description, dashboard=DashboardConfig(name=name, panels=[]), team_id=team_id
            ),
            user_id,
            team_id,
        )
        return project

    def add_project(self, project: Project, user_id: UserID, team_id: TeamID) -> Project:
        user = self.auth.get_or_default_user(user_id)
        team = self.auth.get_team_or_error(team_id)
        if not self.auth.check_entity_permission(user.id, EntityType.Team, team.id, Permission.TEAM_CREATE_PROJECT):
            raise NotEnoughPermissions()
        project.team_id = team_id if team_id != ZERO_UUID else None
        project.created_at = project.created_at or datetime.datetime.now()
        project = self.metadata.add_project(project, user, team).bind(self, user.id)
        self.auth.grant_entity_role(
            user.id,
            EntityType.Project,
            project.id,
            user.id,
            self.auth.get_default_role(DefaultRole.OWNER, EntityType.Project),
            skip_permission_check=True,
        )
        return project

    def update_project(self, user_id: UserID, project: Project):
        user = self.auth.get_or_default_user(user_id)
        if not self.auth.check_entity_permission(user.id, EntityType.Project, project.id, Permission.PROJECT_WRITE):
            raise ProjectNotFound()
        return self.metadata.update_project(project)

    def get_project(self, user_id: UserID, project_id: ProjectID) -> Optional[Project]:
        user = self.auth.get_or_default_user(user_id)
        if not self.auth.check_entity_permission(user.id, EntityType.Project, project_id, Permission.PROJECT_READ):
            raise ProjectNotFound()
        project = self.metadata.get_project(project_id)
        if project is None:
            return None
        return project.bind(self, user.id)

    def delete_project(self, user_id: UserID, project_id: ProjectID):
        user = self.auth.get_or_default_user(user_id)
        if not self.auth.check_entity_permission(user.id, EntityType.Project, project_id, Permission.PROJECT_DELETE):
            raise ProjectNotFound()
        return self.metadata.delete_project(project_id)

    def list_projects(self, user_id: UserID, team_id: Optional[TeamID], org_id: Optional[OrgID]) -> List[Project]:
        user = self.auth.get_or_default_user(user_id)
        project_ids = self.auth.get_available_project_ids(user.id, team_id, org_id)
        return [p.bind(self, user.id) for p in self.metadata.list_projects(project_ids)]

    def add_snapshot(self, user_id: UserID, project_id: ProjectID, snapshot: Snapshot):
        user = self.auth.get_or_default_user(user_id)
        if not self.auth.check_entity_permission(
            user.id, EntityType.Project, project_id, Permission.PROJECT_SNAPSHOT_ADD
        ):
            raise ProjectNotFound()  # todo: better exception
        blob = self.blob.put_snapshot(project_id, snapshot)
        self.metadata.add_snapshot(project_id, snapshot, blob)
        self.data.extract_points(project_id, snapshot)

    def delete_snapshot(self, user_id: UserID, project_id: ProjectID, snapshot_id: SnapshotID):
        user = self.auth.get_or_default_user(user_id)
        if not self.auth.check_entity_permission(
            user.id, EntityType.Project, project_id, Permission.PROJECT_SNAPSHOT_DELETE
        ):
            raise ProjectNotFound()  # todo: better exception
        # todo
        # self.data.remove_points(project_id, snapshot_id)
        # self.blob.delete_snapshot(project_id, snapshot_id)
        self.metadata.delete_snapshot(project_id, snapshot_id)

    def search_project(
        self, user_id: UserID, project_name: str, team_id: Optional[TeamID], org_id: Optional[OrgID]
    ) -> List[Project]:
        user = self.auth.get_or_default_user(user_id)
        project_ids = self.auth.get_available_project_ids(user.id, team_id, org_id)
        return [p.bind(self, user.id) for p in self.metadata.search_project(project_name, project_ids)]

    def list_snapshots(
        self, user_id: UserID, project_id: ProjectID, include_reports: bool = True, include_test_suites: bool = True
    ) -> List[SnapshotMetadata]:
        if not self.auth.check_entity_permission(user_id, EntityType.Project, project_id, Permission.PROJECT_READ):
            raise NotEnoughPermissions()
        snapshots = self.metadata.list_snapshots(project_id, include_reports, include_test_suites)
        for s in snapshots:
            s.project.bind(self, user_id)
        return snapshots

    def load_snapshot(
        self, user_id: UserID, project_id: ProjectID, snapshot: Union[SnapshotID, SnapshotMetadata]
    ) -> Snapshot:
        if isinstance(snapshot, SnapshotID):
            snapshot = self.get_snapshot_metadata(user_id, project_id, snapshot)
        with self.blob.open_blob(snapshot.blob.id) as f:
            return parse_obj_as(Snapshot, json.load(f))

    def get_snapshot_metadata(
        self, user_id: UserID, project_id: ProjectID, snapshot_id: SnapshotID
    ) -> SnapshotMetadata:
        if not self.auth.check_entity_permission(user_id, EntityType.Project, project_id, Permission.PROJECT_READ):
            raise NotEnoughPermissions()
        meta = self.metadata.get_snapshot_metadata(project_id, snapshot_id)
        meta.project.bind(self, user_id)
        return meta

    def reload_snapshots(self, user_id: UserID, project_id: ProjectID):
        if not self.auth.check_entity_permission(user_id, EntityType.Project, project_id, Permission.PROJECT_READ):
            raise NotEnoughPermissions()
        self.metadata.reload_snapshots(project_id)
