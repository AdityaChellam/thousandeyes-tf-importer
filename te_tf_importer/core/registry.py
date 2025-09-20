"""
A plugin/registry so each resource (tests, alerts, etc.) can register its importer with a common interface.
"""

from typing import Protocol, Dict, Callable, Any, List
from pathlib import Path

class Importer(Protocol):
    name: str  # e.g. - "tests"
    def select_scope(self) -> dict: ...
    def fetch(self, scope: dict) -> Any: ...
    def extract_minimal(self, payload: Any) -> List[dict]: ...
    def write_imports(self, rows: List[dict], out_dir: Path) -> int: ...

_REGISTRY: Dict[str, Importer] = {}

def register(importer: Importer):
    _REGISTRY[importer.name] = importer

def get(resource_name: str) -> Importer:
    if resource_name not in _REGISTRY:
        raise KeyError(f"Unknown resource '{resource_name}'. Available: {', '.join(sorted(_REGISTRY))}")
    return _REGISTRY[resource_name]

def all_resources():
    return sorted(_REGISTRY.keys())
