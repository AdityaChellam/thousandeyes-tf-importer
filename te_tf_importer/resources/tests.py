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

# resources/tests.py

from pathlib import Path
import sys
import re
from typing import List

from ..client import te_get
from ..config import OUTPUT_DIR
from ..core.naming import terraformize_name, ensure_unique
from ..core.files import ensure_dir, write_text
from ..core.render_tests import import_block
from ..core.registry import register

# ThousandEyes API test type to Terraform resource name
TYPE_MAP = {
    # Web
    "api": "thousandeyes_api",
    "web-transactions": "thousandeyes_web_transaction",
    "page-load": "thousandeyes_page_load",
    "http-server": "thousandeyes_http_server",
    "ftp-server": "thousandeyes_ftp_server",
    # Voice
    "sip-server": "thousandeyes_sip_server",
    "voice": "thousandeyes_voice",
    # Network
    "agent-to-agent": "thousandeyes_agent_to_agent",
    "agent-to-server": "thousandeyes_agent_to_server",
    # DNS
    "dns-server": "thousandeyes_dns_server",
    "dns-trace": "thousandeyes_dns_trace",
    "dnssec": "thousandeyes_dnssec",
    # Routing
    "bgp": "thousandeyes_bgp",
}

def terraformize_type(t: str) -> str:
    if not t:
        return "thousandeyes_test"
    if t in TYPE_MAP:
        return TYPE_MAP[t]
    s = t.strip().lower()
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_{2,}", "_", s).strip("_")
    return f"thousandeyes_{s or 'test'}"

class TestsImporter:
    name = "tests"

    def select_scope(self) -> dict:
        # Prompt to choose account group
        data = te_get("/account-groups")
        groups = data.get("accountGroups") or data.get("items") or []
        if not groups:
            print("No account groups found.")
            sys.exit(1)

        print("\nAccount Groups:")
        for i, g in enumerate(groups):
            name = g.get("accountGroupName") or g.get("name") or "Unnamed"
            aid = g.get("aid") or g.get("accountGroupId") or g.get("id")
            print(f"[{i}] {name}  (aid={aid})")

        if len(groups) == 1:
            print("Only one account group found; selecting it.")
            return {"aid": str(groups[0].get("aid") or groups[0].get("accountGroupId") or groups[0].get("id"))}

        while True:
            try:
                choice = int(input("\nSelect an account group by number: ").strip())
                if 0 <= choice < len(groups):
                    g = groups[choice]
                    aid = g.get("aid") or g.get("accountGroupId") or g.get("id")
                    return {"aid": str(aid)}
            except ValueError:
                pass
            print("Invalid choice. Try again.")

    def fetch(self, scope: dict):
        return te_get("/tests", **scope)

    def extract_minimal(self, payload) -> List[dict]:
        tests = payload.get("tests") or payload.get("items") or payload
        if not isinstance(tests, list):
            return []
        rows = []
        for t in tests:
            test_id = t.get("testId") or t.get("testID") or t.get("id")
            test_name = t.get("testName") or t.get("name")
            test_type = t.get("type") or t.get("testType")
            if test_id and test_name and test_type:
                rows.append({
                    "id": str(test_id),
                    "name": str(test_name),
                    "type": str(test_type),
                })
        return rows

    def write_imports(self, rows: List[dict], out_dir: Path) -> int:
        out_dir = ensure_dir(out_dir / "tests")
        tf_names = ensure_unique([terraformize_name(r["name"]) for r in rows])

        enriched = []
        for r, tf_name in zip(rows, tf_names):
            tf_type = terraformize_type(r["type"])
            enriched.append((tf_type, tf_name, r["id"]))

        enriched.sort(key=lambda x: (x[0], x[1]))

        count = 0
        for tf_type, tf_name, rid in enriched:
            file_path = out_dir / f"import_{tf_type}_{tf_name}.tf"
            write_text(file_path, import_block(tf_type, tf_name, rid) + "\n")
            count += 1
        return count

# Register on import
register(TestsImporter())
