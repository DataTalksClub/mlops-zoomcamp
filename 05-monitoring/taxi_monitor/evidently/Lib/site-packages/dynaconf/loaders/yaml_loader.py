from __future__ import annotations

from pathlib import Path
from warnings import warn

from dynaconf import default_settings
from dynaconf.constants import YAML_EXTENSIONS
from dynaconf.loaders.base import BaseLoader
from dynaconf.utils import object_merge
from dynaconf.utils.parse_conf import try_to_encode
from dynaconf.vendor.ruamel import yaml

# Add support for Dynaconf Lazy values to YAML dumper
yaml.SafeDumper.yaml_representers[None] = (
    lambda self, data: yaml.representer.SafeRepresenter.represent_str(
        self, try_to_encode(data)
    )
)


class AllLoader(BaseLoader):
    """YAML Loader to load multi doc files"""

    @staticmethod
    def _assign_data(data, source_file, content):
        """Helper to iterate through all docs in a file"""
        content = tuple(content)
        if len(content) == 1:
            data[source_file] = content[0]
        elif len(content) > 1:
            for i, doc in enumerate(content):
                data[f"{source_file}[{i}]"] = doc

    def get_source_data(self, files):
        data = {}
        for source_file in files:
            if source_file.endswith(self.extensions):
                try:
                    with open(source_file, **self.opener_params) as open_file:
                        content = self.file_reader(open_file)
                        self.obj._loaded_files.append(source_file)
                        self._assign_data(data, source_file, content)
                except OSError as e:
                    if ".local." not in source_file:
                        warn(
                            f"{self.identifier}_loader: {source_file} "
                            f":{str(e)}"
                        )
            else:
                # for tests it is possible to pass string
                content = self.string_reader(source_file)
                self._assign_data(data, source_file, content)
        return data


def load(obj, env=None, silent=True, key=None, filename=None, validate=False):
    """
    Reads and loads in to "obj" a single key or all keys from source file.

    :param obj: the settings instance
    :param env: settings current env default='development'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in env
    :param filename: Optional custom filename to load
    :return: None
    """
    # Resolve the loaders
    # https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation
    # Possible values are:
    #   `safe_load, full_load, unsafe_load, load, safe_load_all`
    yaml_reader = getattr(
        yaml, obj.get("YAML_LOADER_FOR_DYNACONF"), yaml.safe_load
    )
    if yaml_reader.__name__ == "unsafe_load":  # pragma: no cover
        warn(
            "yaml.unsafe_load is deprecated."
            " Please read https://msg.pyyaml.org/load for full details."
            " Try to use full_load or safe_load."
        )

    _loader = BaseLoader
    if yaml_reader.__name__.endswith("_all"):
        _loader = AllLoader

    loader = _loader(
        obj=obj,
        env=env,
        identifier="yaml",
        extensions=YAML_EXTENSIONS,
        file_reader=yaml_reader,
        string_reader=yaml_reader,
        validate=validate,
    )
    loader.load(
        filename=filename,
        key=key,
        silent=silent,
    )


def write(settings_path, settings_data, merge=True):
    """Write data to a settings file.

    :param settings_path: the filepath
    :param settings_data: a dictionary with data
    :param merge: boolean if existing file should be merged with new data
    :param stdout: boolean if should output to stdout instead of file
    """
    settings_path = Path(settings_path)
    if settings_path.exists() and merge:  # pragma: no cover
        with open(
            str(settings_path), encoding=default_settings.ENCODING_FOR_DYNACONF
        ) as open_file:
            object_merge(yaml.safe_load(open_file), settings_data)

    with open(
        str(settings_path),
        "w",
        encoding=default_settings.ENCODING_FOR_DYNACONF,
    ) as open_file:
        yaml.dump(
            settings_data,
            open_file,
            Dumper=yaml.dumper.SafeDumper,
            explicit_start=True,
            indent=2,
            default_flow_style=False,
        )
