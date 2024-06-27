#!/usr/bin/env python
# coding: utf-8

from dataclasses import dataclass
from typing import List

from evidently.model.widget import BaseWidgetInfo


@dataclass
class DashboardInfo:
    name: str
    widgets: List[BaseWidgetInfo]
