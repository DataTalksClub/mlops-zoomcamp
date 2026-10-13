"""Règles d'autonomie de l'orchestrateur, lues dans rules/autonomy.yaml."""
from __future__ import annotations

from pathlib import Path

import yaml

AUTONOMY_FILE = Path(__file__).resolve().parents[2] / "rules" / "autonomy.yaml"

AUTO = "auto"            # l'orchestrateur agit seul
APPROVAL = "approval"    # il demande d'abord à un humain
FORBIDDEN = "forbidden"  # jamais


class Rules:
    def __init__(self, rules: dict[str, str] | None = None, path: Path = AUTONOMY_FILE):
        if rules is None:
            with open(path, encoding="utf-8") as f:
                rules = yaml.safe_load(f) or {}
        self.rules = rules

    def can(self, action: str) -> str:
        """auto, approval ou forbidden. Une action inconnue demande une validation humaine."""
        rule = self.rules.get(action, APPROVAL)
        return rule if rule in (AUTO, APPROVAL, FORBIDDEN) else APPROVAL