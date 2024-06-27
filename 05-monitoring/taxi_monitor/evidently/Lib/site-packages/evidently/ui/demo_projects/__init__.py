from typing import Dict

from .adult import adult_demo_project
from .base import DemoProject
from .bikes import bikes_demo_project
from .reviews import reviews_demo_project
from .simple import simple_demo_project

DEMO_PROJECTS: Dict[str, DemoProject] = {
    "bikes": bikes_demo_project,
    "reviews": reviews_demo_project,
    "adult": adult_demo_project,
}

__all__ = [
    "DemoProject",
    "DEMO_PROJECTS",
    "simple_demo_project",
    "reviews_demo_project",
    "bikes_demo_project",
    "adult_demo_project",
]
