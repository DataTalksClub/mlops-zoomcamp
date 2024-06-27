from __future__ import annotations

import warnings
from collections import ChainMap
from contextlib import suppress

try:
    from flask.config import Config

    flask_installed = True
except ImportError:  # pragma: no cover
    flask_installed = False
    Config = object


from importlib.metadata import EntryPoint

import dynaconf


class FlaskDynaconf:
    """The arguments are.
    app = The created app
    dynaconf_args = Extra args to be passed to Dynaconf (validator for example)

    All other values are stored as config vars specially::

        ENVVAR_PREFIX_FOR_DYNACONF = env prefix for your envvars to be loaded
                            example:
                                if you set to `MYSITE` then
                                export MYSITE_SQL_PORT='@int 5445'

                            with that exported to env you access using:
                                app.config.SQL_PORT
                                app.config.get('SQL_PORT')
                                app.config.get('sql_port')
                                # get is case insensitive
                                app.config['SQL_PORT']

                            Dynaconf uses `@int, @bool, @float, @json` to cast
                            env vars

        SETTINGS_FILE_FOR_DYNACONF = The name of the module or file to use as
                                    default to load settings. If nothing is
                                    passed it will be `settings.*` or value
                                    found in `ENVVAR_FOR_DYNACONF`
                                    Dynaconf supports
                                    .py, .yml, .toml, ini, json

    ATTENTION: Take a look at `settings.yml` and `.secrets.yml` to know the
            required settings format.

    Settings load order in Dynaconf:

    - Load all defaults and Flask defaults
    - Load all passed variables when applying FlaskDynaconf
    - Update with data in settings files
    - Update with data in environment vars `ENVVAR_FOR_DYNACONF_`


    TOML files are very useful to have `envd` settings, lets say,
    `production` and `development`.

    You can also achieve the same using multiple `.py` files naming as
    `settings.py`, `production_settings.py` and `development_settings.py`
    (see examples/validator)

    Example::

        app = Flask(__name__)
        FlaskDynaconf(
            app,
            ENV='MYSITE',
            SETTINGS_FILE='settings.yml',
            EXTRA_VALUE='You can add additional config vars here'
        )

    Take a look at examples/flask in Dynaconf repository

    """

    def __init__(
        self,
        app=None,
        instance_relative_config=False,
        dynaconf_instance=None,
        extensions_list=False,
        **kwargs,
    ):
        """kwargs holds initial dynaconf configuration"""
        if not flask_installed:  # pragma: no cover
            raise RuntimeError(
                "To use this extension Flask must be installed "
                "install it with: pip install flask"
            )
        self.kwargs = {k.upper(): v for k, v in kwargs.items()}
        self.kwargs.setdefault("ENVVAR_PREFIX", "FLASK")
        env_prefix = f"{self.kwargs['ENVVAR_PREFIX']}_ENV"  # FLASK_ENV
        self.kwargs.setdefault("ENV_SWITCHER", env_prefix)
        self.kwargs.setdefault("ENVIRONMENTS", True)
        self.kwargs.setdefault("LOAD_DOTENV", True)
        self.kwargs.setdefault(
            "default_settings_paths", dynaconf.DEFAULT_SETTINGS_FILES
        )

        self.dynaconf_instance = dynaconf_instance
        self.instance_relative_config = instance_relative_config
        self.extensions_list = extensions_list
        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        """kwargs holds initial dynaconf configuration"""
        self.kwargs.update(kwargs)
        self.settings = self.dynaconf_instance or dynaconf.LazySettings(
            **self.kwargs
        )
        dynaconf.settings = self.settings  # rebind customized settings
        app.config = self.make_config(app)
        app.dynaconf = self.settings

        if self.extensions_list:
            if not isinstance(self.extensions_list, str):
                self.extensions_list = "EXTENSIONS"
            app.config.load_extensions(self.extensions_list)

    def make_config(self, app):
        root_path = app.root_path
        if self.instance_relative_config:  # pragma: no cover
            root_path = app.instance_path
        if self.dynaconf_instance:
            self.settings.update(self.kwargs)
        return DynaconfConfig(
            root_path=root_path,
            defaults=app.config,
            _settings=self.settings,
            _app=app,
        )


class DynaconfConfig(Config):
    """
    Replacement for flask.config_class that responds as a Dynaconf instance.
    """

    def __init__(self, _settings, _app, *args, **kwargs):
        """perform the initial load"""
        super().__init__(*args, **kwargs)

        # Bring Dynaconf instance value to Flask Config
        Config.update(self, _settings.store)

        self._settings = _settings
        self._app = _app

    def __contains__(self, item):
        return hasattr(self, item)

    def __getitem__(self, key):
        try:
            return self._settings[key]
        except KeyError:
            return Config.__getitem__(self, key)

    def __setitem__(self, key, value):
        """
        Allows app.config['key'] = 'foo'
        """
        return self._settings.__setitem__(key, value)

    def _chain_map(self):
        return ChainMap(self._settings, dict(dict.items(self)))

    def keys(self):
        return self._chain_map().keys()

    def values(self):
        return self._chain_map().values()

    def items(self):
        return self._chain_map().items()

    def setdefault(self, key, value=None):
        return self._chain_map().setdefault(key, value)

    def __iter__(self):
        return self._chain_map().__iter__()

    def __getattr__(self, name):
        """
        First try to get value from dynaconf then from Flask Config
        """
        with suppress(AttributeError):
            return getattr(self._settings, name)

        with suppress(KeyError):
            return self[name]

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __call__(self, name, *args, **kwargs):
        return self.get(name, *args, **kwargs)

    def get(self, key, default=None):
        """Gets config from dynaconf variables
        if variables does not exists in dynaconf try getting from
        `app.config` to support runtime settings."""
        return self._settings.get(key, Config.get(self, key, default))

    def load_extensions(self, key="EXTENSIONS", app=None):
        """Loads flask extensions dynamically."""
        app = app or self._app
        extensions = app.config.get(key)
        if not extensions:
            warnings.warn(
                f"Settings is missing {key} to load Flask Extensions",
                RuntimeWarning,
            )
            return

        for object_reference in app.config[key]:
            # parse the entry point specification
            entry_point = EntryPoint(
                name=None, group=None, value=object_reference
            )
            # dynamically resolve the entry point
            initializer = entry_point.load()
            # Invoke extension initializer
            initializer(app)
