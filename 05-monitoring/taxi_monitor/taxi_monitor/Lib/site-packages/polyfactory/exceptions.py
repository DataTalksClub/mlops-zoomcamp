class FactoryException(Exception):
    """Base Factory error class"""


class ConfigurationException(FactoryException):
    """Configuration Error class - used for misconfiguration"""


class ParameterException(FactoryException):
    """Parameter exception - used when wrong parameters are used"""


class MissingBuildKwargException(FactoryException):
    """Missing Build Kwarg exception - used when a required build kwarg is not provided"""


class MissingDependencyException(FactoryException, ImportError):
    """Missing dependency exception - used when a dependency is not installed"""
