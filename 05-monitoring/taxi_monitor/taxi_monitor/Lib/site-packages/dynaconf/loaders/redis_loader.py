from __future__ import annotations

from dynaconf.loaders.base import SourceMetadata
from dynaconf.utils import build_env_list
from dynaconf.utils import upperfy
from dynaconf.utils.parse_conf import parse_conf_data
from dynaconf.utils.parse_conf import unparse_conf_data

try:
    from redis import StrictRedis
except ImportError:
    StrictRedis = None

IDENTIFIER = "redis"


def load(obj, env=None, silent=True, key=None, validate=False):
    """Reads and loads in to "settings" a single key or all keys from redis

    :param obj: the settings instance
    :param env: settings env default='DYNACONF'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in env
    :return: None
    """
    if StrictRedis is None:
        raise ImportError(
            "redis package is not installed in your environment. "
            "`pip install dynaconf[redis]` or disable the redis loader with "
            "export REDIS_ENABLED_FOR_DYNACONF=false"
        )

    redis = StrictRedis(**obj.get("REDIS_FOR_DYNACONF"))
    prefix = obj.get("ENVVAR_PREFIX_FOR_DYNACONF")
    # prefix is added to env_list to keep backwards compatibility
    env_list = [prefix] + build_env_list(obj, env or obj.current_env)
    for env_name in env_list:
        holder = f"{prefix.upper()}_{env_name.upper()}"
        try:
            source_metadata = SourceMetadata(IDENTIFIER, "unique", env_name)
            if key:
                value = redis.hget(holder.upper(), key)
                if value:
                    parsed_value = parse_conf_data(
                        value, tomlfy=True, box_settings=obj
                    )
                    if parsed_value:
                        obj.set(
                            key,
                            parsed_value,
                            validate=validate,
                            loader_identifier=source_metadata,
                        )
            else:
                data = {
                    key: parse_conf_data(value, tomlfy=True, box_settings=obj)
                    for key, value in redis.hgetall(holder.upper()).items()
                }
                if data:
                    obj.update(
                        data,
                        loader_identifier=source_metadata,
                        validate=validate,
                    )
        except Exception:
            if silent:
                return False
            raise


def write(obj, data=None, **kwargs):
    """Write a value in to loader source

    :param obj: settings object
    :param data: vars to be stored
    :param kwargs: vars to be stored
    :return:
    """
    if obj.REDIS_ENABLED_FOR_DYNACONF is False:
        raise RuntimeError(
            "Redis is not configured \n"
            "export REDIS_ENABLED_FOR_DYNACONF=true\n"
            "and configure the REDIS_*_FOR_DYNACONF variables"
        )
    client = StrictRedis(**obj.REDIS_FOR_DYNACONF)
    holder = obj.get("ENVVAR_PREFIX_FOR_DYNACONF").upper()
    # add env to holder
    holder = f"{holder}_{obj.current_env.upper()}"

    data = data or {}
    data.update(kwargs)
    if not data:
        raise AttributeError("Data must be provided")
    redis_data = {
        upperfy(key): unparse_conf_data(value) for key, value in data.items()
    }
    client.hset(holder.upper(), mapping=redis_data)
    load(obj)


def delete(obj, key=None):
    """
    Delete a single key if specified, or all env if key is none
    :param obj: settings object
    :param key: key to delete from store location
    :return: None
    """
    client = StrictRedis(**obj.REDIS_FOR_DYNACONF)
    holder = obj.get("ENVVAR_PREFIX_FOR_DYNACONF").upper()
    # add env to holder
    holder = f"{holder}_{obj.current_env.upper()}"

    if key:
        client.hdel(holder.upper(), upperfy(key))
        obj.unset(key)
    else:
        keys = client.hkeys(holder.upper())
        client.delete(holder.upper())
        obj.unset_all(keys)
