from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

from requests import HTTPError

from evidently.ui.api.models import OrgModel
from evidently.ui.api.models import TeamModel
from evidently.ui.base import Org
from evidently.ui.base import ProjectManager
from evidently.ui.base import Team
from evidently.ui.storage.common import NoopAuthManager
from evidently.ui.type_aliases import ZERO_UUID
from evidently.ui.type_aliases import OrgID
from evidently.ui.type_aliases import TeamID
from evidently.ui.workspace.remote import NoopBlobStorage
from evidently.ui.workspace.remote import NoopDataStorage
from evidently.ui.workspace.remote import RemoteMetadataStorage
from evidently.ui.workspace.view import WorkspaceView

TOKEN_HEADER_NAME = "X-Evidently-Token"


class Cookie(NamedTuple):
    key: str
    description: str
    httponly: bool


ACCESS_TOKEN_COOKIE = Cookie(
    key="app.at",
    description="",
    httponly=True,
)


class CloudMetadataStorage(RemoteMetadataStorage):
    def __init__(self, base_url: str, token: str, token_cookie_name: str):
        self.token = token
        self.token_cookie_name = token_cookie_name
        self._jwt_token: Optional[str] = None
        self._logged_in: bool = False
        super().__init__(base_url=base_url)

    def _get_jwt_token(self):
        return super()._request("/api/users/login", "GET", headers={TOKEN_HEADER_NAME: self.token}).text

    @property
    def jwt_token(self):
        if self._jwt_token is None:
            self._jwt_token = self._get_jwt_token()

        return self._jwt_token

    def _prepare_request(
        self,
        path: str,
        method: str,
        query_params: Optional[dict] = None,
        body: Optional[dict] = None,
        cookies=None,
        headers: Dict[str, str] = None,
    ):
        r = super()._prepare_request(path, method, query_params, body, cookies, headers)
        if path == "/api/users/login":
            return r
        r.cookies[self.token_cookie_name] = self.jwt_token
        return r

    def _request(
        self,
        path: str,
        method: str,
        query_params: Optional[dict] = None,
        body: Optional[dict] = None,
        response_model=None,
        cookies=None,
        headers: Dict[str, str] = None,
    ):
        try:
            res = super()._request(
                path,
                method,
                query_params,
                body,
                response_model,
                cookies=cookies,
                headers=headers,
            )
            self._logged_in = True
            return res
        except HTTPError as e:
            if self._logged_in and e.response.status_code == 401:
                # renew token and retry
                self._jwt_token = self._get_jwt_token()
                cookies[self.token_cookie_name] = self.jwt_token
                return super()._request(
                    path,
                    method,
                    query_params,
                    body,
                    response_model,
                    cookies=cookies,
                    headers=headers,
                )
            raise

    def create_org(self, org: Org) -> OrgModel:
        return self._request("/api/orgs", "POST", body=org.dict(), response_model=OrgModel)

    def list_orgs(self) -> List[OrgModel]:
        return self._request("/api/orgs", "GET", response_model=List[OrgModel])

    def create_team(self, team: Team, org_id: OrgID = None) -> TeamModel:
        return self._request(
            "/api/teams",
            "POST",
            query_params={"name": team.name, "org_id": org_id},
            response_model=TeamModel,
        )


class CloudWorkspace(WorkspaceView):
    token: str
    URL: str = "https://app.evidently.cloud"

    def __init__(
        self,
        token: str,
        url: str = None,
    ):
        self.token = token
        self.url = url if url is not None else self.URL

        # todo: default org if user have only one
        user_id = ZERO_UUID  # todo: get from /me
        meta = CloudMetadataStorage(
            base_url=self.url,
            token=self.token,
            token_cookie_name=ACCESS_TOKEN_COOKIE.key,
        )

        pm = ProjectManager(
            metadata=meta,
            blob=(NoopBlobStorage()),
            data=(NoopDataStorage()),
            auth=(CloudAuthManager()),
        )
        super().__init__(
            user_id,
            pm,
        )

    def create_org(self, name: str) -> Org:
        assert isinstance(self.project_manager.metadata, CloudMetadataStorage)
        return self.project_manager.metadata.create_org(Org(name=name)).to_org()

    def list_orgs(self) -> List[Org]:
        assert isinstance(self.project_manager.metadata, CloudMetadataStorage)
        return [o.to_org() for o in self.project_manager.metadata.list_orgs()]

    def create_team(self, name: str, org_id: OrgID) -> Team:
        assert isinstance(self.project_manager.metadata, CloudMetadataStorage)
        return self.project_manager.metadata.create_team(Team(name=name), org_id).to_team()


class CloudAuthManager(NoopAuthManager):
    def get_team(self, team_id: TeamID) -> Optional[Team]:
        return Team(id=team_id, name="")
