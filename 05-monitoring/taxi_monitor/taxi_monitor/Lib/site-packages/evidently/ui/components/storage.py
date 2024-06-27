from abc import ABC
from typing import Callable
from typing import ClassVar

from evidently.pydantic_utils import register_type_alias
from evidently.ui.base import BlobStorage
from evidently.ui.base import DataStorage
from evidently.ui.base import MetadataStorage
from evidently.ui.base import ProjectManager
from evidently.ui.components.base import FactoryComponent
from evidently.ui.storage.common import NoopAuthManager
from evidently.ui.storage.local import create_local_project_manager


class StorageComponent(FactoryComponent[ProjectManager], ABC):
    class Config:
        is_base_type = True

    dependency_name: ClassVar = "project_manager"
    use_cache: ClassVar[bool] = True
    sync_to_thread: ClassVar[bool] = False


class LocalStorageComponent(StorageComponent):
    path: str = "workspace"
    autorefresh: bool = True

    def dependency_factory(self) -> Callable[..., ProjectManager]:
        return lambda: create_local_project_manager(self.path, autorefresh=self.autorefresh, auth=NoopAuthManager())


class MetadataStorageComponent(FactoryComponent[MetadataStorage], ABC):
    class Config:
        is_base_type = True

    __section__: ClassVar = "metadata"
    dependency_name: ClassVar = "metadata_storage"
    use_cache: ClassVar[bool] = True
    sync_to_thread: ClassVar[bool] = False


class DataStorageComponent(FactoryComponent[DataStorage], ABC):
    class Config:
        is_base_type = True

    __section__: ClassVar = "data"

    dependency_name: ClassVar = "data_storage"
    use_cache: ClassVar[bool] = True
    sync_to_thread: ClassVar[bool] = False


class BlobStorageComponent(FactoryComponent[BlobStorage], ABC):
    class Config:
        is_base_type = True

    __section__: ClassVar = "blob"

    dependency_name: ClassVar = "blob_storage"
    use_cache: ClassVar[bool] = True
    sync_to_thread: ClassVar[bool] = False


register_type_alias(BlobStorageComponent, "evidently.ui.components.local_storage.FSSpecBlobComponent", "fsspec")
register_type_alias(
    MetadataStorageComponent, "evidently.ui.components.local_storage.JsonMetadataComponent", "json_file"
)
register_type_alias(DataStorageComponent, "evidently.ui.components.local_storage.InmemoryDataComponent", "inmemory")
