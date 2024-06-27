from typing import Any
from typing import Dict

import pandas as pd

from evidently.collector.config import CollectorConfig
from evidently.ui.utils import RemoteClientBase


class CollectorClient(RemoteClientBase):
    def create_collector(self, id: str, collector: CollectorConfig) -> Dict[str, Any]:
        return self._request(f"/{id}", "POST", body=collector.dict()).json()

    def send_data(self, id: str, data: pd.DataFrame) -> Dict[str, Any]:
        return self._request(f"/{id}/data", "POST", body=data.to_dict()).json()

    def set_reference(self, id: str, reference: pd.DataFrame) -> Dict[str, Any]:
        return self._request(f"/{id}/reference", "POST", body=reference.to_dict()).json()
