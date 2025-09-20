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

# core/naming.py


import re
from collections import defaultdict

def terraformize_name(name: str) -> str:
    s = (name or "").strip().lower()
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_{2,}", "_", s).strip("_")
    if not s or not re.match(r"^[a-z_]", s):
        s = f"_{s}" if s else "_item"
    return s[:128]

def ensure_unique(names):
    counts = defaultdict(int)
    out = []
    for n in names:
        c = counts[n]
        out.append(n if c == 0 else f"{n}_{c}")
        counts[n] += 1
    return out
