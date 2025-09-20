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

# cli.py


import argparse
import sys
from pathlib import Path
import requests

from .config import OUTPUT_DIR
from .core.registry import get, all_resources  #To trigger registrations via imports

from .resources import tests as _tests
from .resources import alert_rules as _alert_rules 
from .resources import tags as _tags
from .resources import users as _users
from .resources import roles as _roles
from .resources import account_groups as _account_groups


def main():
    parser = argparse.ArgumentParser(
        prog="te2tf",
        description="Generate Terraform import blocks from ThousandEyes resources.",
    )
    parser.add_argument(
        "resource",
        nargs="?",
        default="tests",
        help=f"Resource to import ({', '.join(all_resources())}); default: tests",
    )
    parser.add_argument(
        "--out",
        default=OUTPUT_DIR,
        help=f"Output directory (default: {OUTPUT_DIR})",
    )
    args = parser.parse_args()

    try:
        importer = get(args.resource)

        scope = importer.select_scope()
        payload = importer.fetch(scope)
        rows = importer.extract_minimal(payload)
        if not rows:
            print("No items with required fields found.")
            sys.exit(0)

        written = importer.write_imports(rows, Path(args.out))
        print(f"Wrote {written} import file(s) to {Path(args.out).resolve()}/{args.resource}")

    except requests.HTTPError as e:
        print(f"HTTP error: {e}\nResponse: {getattr(e, 'response', None) and e.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Request error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)
    except NotImplementedError as e:
        print(f"Not ready yet: {e}", file=sys.stderr)
        sys.exit(3)
