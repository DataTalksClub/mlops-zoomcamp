"""For backward compatibility with evidently <= 4.9"""

import warnings

from evidently.ui.workspace import RemoteWorkspace

__all__ = ["RemoteWorkspace"]

warnings.warn(
    "Importing RemoteWorkspace from evidently.ui.remote is deprecated. Please import from evidently.ui.workspace",
    DeprecationWarning,
)
