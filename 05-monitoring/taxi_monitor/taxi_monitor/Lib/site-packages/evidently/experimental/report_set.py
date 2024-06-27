import datetime
import os
import uuid
from typing import Dict
from typing import Optional

from evidently._pydantic_compat import ValidationError
from evidently.suite.base_suite import Snapshot


def load_snapshots(
    path: str,
    date_from: Optional[datetime.datetime] = None,
    date_to: Optional[datetime.datetime] = None,
    skip_errors: bool = False,
) -> Dict[uuid.UUID, Snapshot]:
    result = {}
    for file in os.listdir(path):
        filepath = os.path.join(path, file)
        try:
            suite = Snapshot.load(filepath)
        except ValidationError:
            if skip_errors:
                continue
            raise
        if date_from is not None and suite.timestamp < date_from:
            continue
        if date_to is not None and suite.timestamp > date_to:
            continue
        result[suite.id] = suite
    return result
