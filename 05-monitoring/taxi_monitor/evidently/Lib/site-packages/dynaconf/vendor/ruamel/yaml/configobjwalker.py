import warnings
from.util import configobj_walker as new_configobj_walker
if False:from typing import Any
def configobj_walker(cfg):warnings.warn('configobj_walker has moved to ruamel.yaml.util, please update your code');return new_configobj_walker(cfg)