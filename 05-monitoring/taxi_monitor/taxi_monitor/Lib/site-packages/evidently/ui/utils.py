import json
import urllib.parse
from typing import Any
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

import requests

from evidently._pydantic_compat import BaseModel
from evidently._pydantic_compat import parse_obj_as
from evidently.ui.storage.common import SECRET_HEADER_NAME
from evidently.utils import NumpyEncoder

T = TypeVar("T", bound=BaseModel)


class RemoteClientBase:
    def __init__(self, base_url: str, secret: str = None):
        self.base_url = base_url
        self.secret = secret

    def _request(
        self,
        path: str,
        method: str,
        query_params: Optional[dict] = None,
        body: Optional[dict] = None,
        response_model: Optional[Type[T]] = None,
    ) -> Union[T, requests.Response]:
        # todo: better encoding
        headers = {SECRET_HEADER_NAME: self.secret}
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"

            data = json.dumps(body, allow_nan=True, cls=NumpyEncoder).encode("utf8")

        response = requests.request(
            method, urllib.parse.urljoin(self.base_url, path), params=query_params, data=data, headers=headers
        )
        response.raise_for_status()
        if response_model is not None:
            return parse_obj_as(response_model, response.json())
        return response


def parse_json(body: bytes) -> Any:
    return json.loads(body)
