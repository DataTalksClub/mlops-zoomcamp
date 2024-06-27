import datetime
import uuid
from typing import Dict
from typing import List
from typing import Tuple
from typing import TypeVar
from typing import Union

from evidently.base_metric import Metric
from evidently.tests.base_test import Test
from evidently.tests.base_test import TestStatus

BlobID = str
UserID = uuid.UUID
TeamID = uuid.UUID
OrgID = uuid.UUID
RoleID = int
ProjectID = uuid.UUID
EntityID = uuid.UUID
SnapshotID = uuid.UUID
STR_UUID = Union[str, uuid.UUID]
PanelID = uuid.UUID
TabID = uuid.UUID
ZERO_UUID = uuid.UUID(int=0)

TestResultPoints = Dict[datetime.datetime, Dict[Test, TestStatus]]
PointType = TypeVar("PointType")
DataPointsAsType = List[Dict[Metric, List[Tuple[datetime.datetime, PointType]]]]
DataPoints = DataPointsAsType[float]
