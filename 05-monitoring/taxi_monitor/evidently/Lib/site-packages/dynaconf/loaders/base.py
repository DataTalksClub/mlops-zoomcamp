from __future__ import annotations

import warnings
from typing import NamedTuple

from dynaconf.utils import build_env_list
from dynaconf.utils import ensure_a_list
from dynaconf.utils import upperfy
from dynaconf.utils.functional import empty


class BaseLoader:
    """Base loader for dynaconf source files.

    :param obj: {[LazySettings]} -- [Dynaconf settings]
    :param env: {[string]} -- [the current env to be loaded defaults to
      [development]]
    :param identifier: {[string]} -- [identifier ini, yaml, json, py, toml]
    :param extensions: {[list]} -- [List of extensions with dots ['.a', '.b']]
    :param file_reader: {[callable]} -- [reads file return dict]
    :param string_reader: {[callable]} -- [reads string return dict]
    """

    def __init__(
        self,
        obj,
        env,
        identifier,
        extensions,
        file_reader,
        string_reader,
        opener_params=None,
        validate=False,
    ):
        """Instantiates a loader for different sources"""
        self.obj = obj
        self.env = env or obj.current_env
        self.identifier = identifier
        self.extensions = extensions
        self.file_reader = file_reader
        self.string_reader = string_reader
        self.opener_params = opener_params or {
            "mode": "r",
            "encoding": obj.get("ENCODING_FOR_DYNACONF", "utf-8"),
        }
        self.validate = validate

    @staticmethod
    def warn_not_installed(obj, identifier):  # pragma: no cover
        if identifier not in obj._not_installed_warnings:
            warnings.warn(
                f"{identifier} support is not installed in your environment. "
                f"`pip install dynaconf[{identifier}]`"
            )
        obj._not_installed_warnings.append(identifier)

    def load(self, filename=None, key=None, silent=True, merge=empty):
        """
        Reads and loads in to `self.obj` a single key or all keys from source

        :param filename: Optional filename to load
        :param key: if provided load a single key
        :param silent: if load errors should be silenced
        """

        filename = filename or self.obj.get(self.identifier.upper())
        if not filename:
            return

        if not isinstance(filename, (list, tuple)):
            split_files = ensure_a_list(filename)
            if all([f.endswith(self.extensions) for f in split_files]):  # noqa
                files = split_files  # it is a ['file.ext', ...]
            else:  # it is a single config as string
                files = [filename]
        else:  # it is already a list/tuple
            files = filename

        source_data = self.get_source_data(files)

        if self.obj.get("ENVIRONMENTS_FOR_DYNACONF") is False:
            self._envless_load(source_data, silent, key)
        else:
            self._load_all_envs(source_data, silent, key)

    def get_source_data(self, files):
        """Reads each file and returns source data for each file
        {"path/to/file.ext": {"key": "value"}}
        """
        data = {}
        for source_file in files:
            if source_file.endswith(self.extensions):
                try:
                    with open(source_file, **self.opener_params) as open_file:
                        content = self.file_reader(open_file)
                        self.obj._loaded_files.append(source_file)
                        if content:
                            data[source_file] = content
                except OSError as e:
                    if ".local." not in source_file:
                        warnings.warn(
                            f"{self.identifier}_loader: {source_file} "
                            f":{str(e)}"
                        )
            else:
                # for tests it is possible to pass string
                content = self.string_reader(source_file)
                if content:
                    data[source_file] = content
        return data

    def _envless_load(self, source_data, silent=True, key=None):
        """Load all the keys from each file without env separation"""
        for file_name, file_data in source_data.items():
            # is there a `dynaconf_merge` on top level of file?
            file_merge = file_data.get("dynaconf_merge", empty)

            # set source metadata
            source_metadata = SourceMetadata(
                self.identifier, file_name, "default"
            )

            self._set_data_to_obj(
                file_data,
                source_metadata,
                file_merge=file_merge,
                key=key,
            )

    def _load_all_envs(self, source_data, silent=True, key=None):
        """
        Load configs from files separating by each environment
        source_data should have format:
            {
                "path/to/src": {
                    "env": {...},
                    "env2": {...}
                }
            }
        """
        for file_name, file_data in source_data.items():
            # env name is checked in lower
            file_data = {k.lower(): value for k, value in file_data.items()}

            # is there a `dynaconf_merge` on top level of file?
            file_merge = file_data.get("dynaconf_merge", empty)

            # is there a flag disabling dotted lookup on file?
            file_dotted_lookup = file_data.get("dynaconf_dotted_lookup")

            for env in build_env_list(self.obj, self.env):
                env = env.lower()  # lower for better comparison
                # print(self.env, file_data)

                # set source metadata
                source_metadata = SourceMetadata(
                    self.identifier, file_name, env
                )

                try:
                    data = file_data[env] or {}
                except KeyError:
                    if silent:
                        continue
                    raise

                if not data:
                    continue

                self._set_data_to_obj(
                    data,
                    source_metadata,
                    file_merge,
                    key,
                    file_dotted_lookup=file_dotted_lookup,
                )

    def _set_data_to_obj(
        self,
        data,
        identifier: SourceMetadata,
        file_merge=empty,
        key=False,
        file_dotted_lookup=None,
    ):
        """Calls settings.set to add the keys"""
        # data 1st level keys should be transformed to upper case.
        data = {upperfy(k): v for k, v in data.items()}
        if key:
            key = upperfy(key)

        if self.obj.filter_strategy:
            data = self.obj.filter_strategy(data)

        # is there a `dynaconf_merge` inside an `[env]`?
        env_scope_merge = data.pop("DYNACONF_MERGE", None)
        if env_scope_merge is not None:
            file_merge = env_scope_merge

        # If not passed or passed as None,
        # look for inner [env] value, or default settings.
        if file_dotted_lookup is None:
            file_dotted_lookup = data.pop(
                "DYNACONF_DOTTED_LOOKUP",
                self.obj.get("DOTTED_LOOKUP_FOR_DYNACONF"),
            )

        if not key:
            self.obj.update(
                data,
                loader_identifier=identifier,
                merge=file_merge,
                dotted_lookup=file_dotted_lookup,
                validate=self.validate,
            )
        elif key in data:
            self.obj.set(
                key,
                data.get(key),
                loader_identifier=identifier,
                merge=file_merge,
                dotted_lookup=file_dotted_lookup,
                validate=self.validate,
            )


class SourceMetadata(NamedTuple):
    """
    Useful metadata about some loaded source (file, envvar, etc).

    Serve as a unique identifier for data from a specific env
    and a specific source (file, envvar, validationd default, etc)

    Examples:
        SourceMetadata(loader="envvar", identifier="os", env="global")
        SourceMetadata(loader="yaml", identifier="path/to/file.yml", env="dev")
    """

    loader: str
    identifier: str
    env: str = "global"
    merged: bool = False
