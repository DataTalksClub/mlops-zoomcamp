import uuid
from typing import ClassVar
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from evidently.ui.base import AuthManager
from evidently.ui.base import DefaultRole
from evidently.ui.base import EntityType
from evidently.ui.base import Org
from evidently.ui.base import Permission
from evidently.ui.base import Role
from evidently.ui.base import Team
from evidently.ui.base import User
from evidently.ui.base import UserWithRoles
from evidently.ui.base import get_default_role_permissions
from evidently.ui.type_aliases import ZERO_UUID
from evidently.ui.type_aliases import EntityID
from evidently.ui.type_aliases import OrgID
from evidently.ui.type_aliases import ProjectID
from evidently.ui.type_aliases import TeamID
from evidently.ui.type_aliases import UserID

EVIDENTLY_SECRET_ENV = "EVIDENTLY_SECRET"
SECRET_HEADER_NAME = "evidently-secret"


class NoUser(User):
    id: UserID = ZERO_UUID
    name: str = ""


class NoTeam(Team):
    id: TeamID = ZERO_UUID
    name = ""


class NoOrg(Org):
    id: OrgID = ZERO_UUID
    name = ""


NO_USER = NoUser()
NO_TEAM = NoTeam()
NO_ORG = NoOrg()


class NoopAuthManager(AuthManager):
    user: ClassVar[User] = NO_USER
    team: ClassVar[Team] = NO_TEAM
    org: ClassVar[Org] = NO_ORG

    def create_org(self, owner: UserID, org: Org):
        return self.org

    def get_org(self, org_id: OrgID) -> Optional[Org]:
        return self.org

    def get_default_role(self, default_role: DefaultRole, entity_type: Optional[EntityType]) -> Role:
        return Role(
            id=0,
            name=default_role.value,
            entity_type=entity_type,
            permissions=get_default_role_permissions(default_role, entity_type)[1],
        )

    def update_role(self, role: Role):
        return role

    def _grant_entity_role(self, entity_type: EntityType, entity_id: EntityID, user_id: UserID, role: Role):
        pass

    def _revoke_entity_role(self, entity_type: EntityType, entity_id: EntityID, user_id: UserID, role: Role):
        pass

    def get_available_project_ids(
        self, user_id: UserID, team_id: Optional[TeamID], org_id: Optional[OrgID]
    ) -> Optional[Set[ProjectID]]:
        return None

    def check_entity_permission(
        self, user_id: UserID, entity_type: EntityType, entity_id: uuid.UUID, permission: Permission
    ) -> bool:
        return True

    def create_user(self, user_id: UserID, name: Optional[str]) -> User:
        return self.user

    def get_user(self, user_id: UserID) -> Optional[User]:
        return self.user

    def get_default_user(self) -> User:
        return self.user

    def _create_team(self, author: UserID, team: Team, org_id: OrgID) -> Team:
        return self.team

    def get_team(self, team_id: TeamID) -> Optional[Team]:
        return self.team

    def list_user_teams(self, user_id: UserID, org_id: Optional[OrgID]) -> List[Team]:
        return []

    def _delete_team(self, team_id: TeamID):
        pass

    def _list_entity_users(
        self, entity_type: EntityType, entity_id: EntityID, read_permission: Permission
    ) -> List[User]:
        return []

    def _list_entity_users_with_roles(
        self, entity_type: EntityType, entity_id: EntityID, read_permission: Permission
    ) -> List[UserWithRoles]:
        return []

    def _delete_org(self, org_id: OrgID):
        pass

    def list_user_orgs(self, user_id: UserID):
        return []

    def list_user_entity_permissions(
        self, user_id: UserID, entity_type: EntityType, entity_id: EntityID
    ) -> Set[Permission]:
        return set(Permission)

    def list_user_entity_roles(
        self, user_id: UserID, entity_type: EntityType, entity_id: EntityID
    ) -> List[Tuple[EntityType, EntityID, Role]]:
        return [(entity_type, entity_id, self.get_default_role(DefaultRole.OWNER, None))]

    def list_roles(self, entity_type: Optional[EntityType]) -> List[Role]:
        return [self.get_default_role(DefaultRole.OWNER, None)]
