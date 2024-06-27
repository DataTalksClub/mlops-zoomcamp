import os.path
import re
import uuid
from pathlib import Path

from watchdog.events import EVENT_TYPE_CREATED
from watchdog.events import EVENT_TYPE_DELETED
from watchdog.events import EVENT_TYPE_MODIFIED
from watchdog.events import EVENT_TYPE_MOVED
from watchdog.events import FileSystemEvent
from watchdog.events import FileSystemEventHandler

from evidently.ui.storage.common import NO_USER
from evidently.ui.storage.local.base import METADATA_PATH
from evidently.ui.storage.local.base import SNAPSHOTS
from evidently.ui.storage.local.base import LocalState
from evidently.ui.storage.local.base import load_project

uuid4hex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


class WorkspaceDirHandler(FileSystemEventHandler):
    def __init__(self, state: LocalState):
        self.state = state
        self.path = state.location.path

    def dispatch(self, event):
        if self.is_project_event(event):
            self.on_project_event(event)
            return
        if self.is_snapshot_event(event):
            self.on_snapshot_event(event)

    def is_project_event(self, event: FileSystemEvent):
        path = Path(event.src_path)
        f_name = path.name
        if f_name != METADATA_PATH:
            return False
        if not re.fullmatch(uuid4hex, path.parent.name):
            return False
        if not path.parent.parent.samefile(self.path):
            return False
        return True

    def is_snapshot_event(self, event: FileSystemEvent):
        path = Path(event.src_path)
        f_name = path.name
        if not re.fullmatch(uuid4hex + r"\.json", f_name):
            return False
        if path.parent.name != SNAPSHOTS:
            return False
        if not re.fullmatch(uuid4hex, path.parent.parent.name):
            return False
        if not path.parent.parent.parent.samefile(self.path):
            return False
        return True

    def parse_project_id(self, path):
        path = Path(path)
        f_name = path.name
        if f_name != METADATA_PATH:
            return None
        if not re.fullmatch(uuid4hex, path.parent.name):
            return None
        return path.parent.name

    def parse_project_and_snapshot_id(self, path):
        path = Path(path)
        f_name = path.name
        if not re.fullmatch(uuid4hex + r"\.json", f_name):
            return None, None
        snapshot_id = f_name[:-5]
        if path.parent.name != SNAPSHOTS:
            return None, None
        if not re.fullmatch(uuid4hex, path.parent.parent.name):
            return None, None
        if not path.parent.parent.parent.samefile(self.path):
            return None, None
        return path.parent.parent.name, snapshot_id

    def on_project_event(self, event: FileSystemEvent):
        project_id = self.parse_project_id(event.src_path)
        if project_id is None:
            return
        if event.event_type in (EVENT_TYPE_CREATED, EVENT_TYPE_MOVED):
            project = load_project(self.state.location, project_id)
            if project is None:
                return
            self.state.projects[project.id] = project.bind(self.state.project_manager, NO_USER.id)
            if project.id not in self.state.snapshots:
                self.state.snapshots[project.id] = {}
                self.state.snapshot_data[project.id] = {}
        if event.event_type in (EVENT_TYPE_MODIFIED,):
            project = load_project(self.state.location, project_id)
            if project is None:
                return
            self.state.projects[project.id] = project.bind(self.state.project_manager, NO_USER.id)
        if event.event_type == EVENT_TYPE_DELETED:
            pid = uuid.UUID(project_id)
            del self.state.projects[pid]
            del self.state.snapshots[pid]
            del self.state.snapshot_data[pid]

    def on_snapshot_event(self, event):
        project_id, snapshot_id = self.parse_project_and_snapshot_id(event.src_path)
        if project_id is None or snapshot_id is None:
            return
        pid = uuid.UUID(project_id)
        sid = uuid.UUID(snapshot_id)
        project = self.state.projects.get(pid)
        if project is None:
            return
        if (event.event_type in (EVENT_TYPE_MODIFIED, EVENT_TYPE_CREATED, EVENT_TYPE_MOVED)) and os.path.exists(
            event.src_path
        ):
            self.state.reload_snapshot(project, sid)
        if (
            event.event_type == EVENT_TYPE_DELETED
            or event.event_type == EVENT_TYPE_MOVED
            and not os.path.exists(event.src_path)
        ):
            del self.state.snapshots[pid][sid]
            del self.state.snapshot_data[pid][sid]
