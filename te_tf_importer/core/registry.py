# Copyright 2025 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

# core/registry.py

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
