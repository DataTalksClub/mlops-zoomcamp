import pathlib
from contextlib import suppress
from types import SimpleNamespace

from .. import readers, _adapters


class TraversableResourcesLoader(_adapters.TraversableResourcesLoader):
    """
    Adapt loaders to provide TraversableResources and other
    compatibility.

    Ensures the readers from importlib_resources are preferred
    over stdlib readers.
    """

    def get_resource_reader(self, name):
        return self._standard_reader() or super().get_resource_reader(name)

    def _standard_reader(self):
        return self._zip_reader() or self._namespace_reader() or self._file_reader()

    def _zip_reader(self):
        with suppress(AttributeError):
            return readers.ZipReader(self.spec.loader, self.spec.name)

    def _namespace_reader(self):
        with suppress(AttributeError, ValueError):
            return readers.NamespaceReader(self.spec.submodule_search_locations)

    def _file_reader(self):
        try:
            path = pathlib.Path(self.spec.origin)
        except TypeError:
            return None
        if path.exists():
            return readers.FileReader(SimpleNamespace(path=path))


def wrap_spec(package):
    """
    Override _adapters.wrap_spec to use TraversableResourcesLoader
    from above. Ensures that future behavior is always available on older
    Pythons.
    """
    return _adapters.SpecLoaderAdapter(package.__spec__, TraversableResourcesLoader)
