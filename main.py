# main.py
import json
import re
import sys
from collections import defaultdict
import requests

BASE_URL = "https://api.thousandeyes.com/v7"
TOKEN = "TOKEN"

HEADERS = {
    "Accept": "application/hal+json",
    "Authorization": f"Bearer {TOKEN}",
}

# Mapping ThousandEyes API test types to Terraform resource suffixes
TYPE_MAP = {
    #web
    "api": "thousandeyes_api",
    "web-transactions": "thousandeyes_web_transaction",
    "page-load": "thousandeyes_page_load",
    "http-server": "thousandeyes_http_server",
    "ftp-server": "thousandeyes_ftp_server",
    
    #Voice
    "sip-server": "thousandeyes_sip_server",
    "voice": "thousandeyes_voice",

    #Network
    "agent-to-agent": "thousandeyes_agent_to_agent",
    "agent-to-server": "thousandeyes_agent_to_server",
    
    #DNS
    "dns-server": "thousandeyes_dns_server",
    "dns-trace": "thousandeyes_dns_trace",
    "dnssec": "thousandeyes_dnssec",

    #Routing
    "bgp": "thousandeyes_bgp",
    
}

def te_get(path: str, **params):
    url = f"{BASE_URL}{path}"
    r = requests.get(url, headers=HEADERS, params=params or None, timeout=30)
    r.raise_for_status()
    return r.json()

def terraformize_name(name: str) -> str:
    s = (name or "").strip().lower()
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_{2,}", "_", s).strip("_")
    if not s or not re.match(r"^[a-z_]", s):
        s = f"_{s}" if s else "_test"
    return s[:128]

def terraformize_type(t: str) -> str:
    """
    Convert TE test 'type' to Terraform resource suffix.
    1) Use explicit TYPE_MAP when known.
    2) Fallback: lowercase, replace non [a-z0-9_] with '_', collapse '_'.
    """
    if not t:
        return "test"
    if t in TYPE_MAP:
        return TYPE_MAP[t]
    s = t.strip().lower()
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_{2,}", "_", s).strip("_")
    return s or "test"

def ensure_unique(names):
    counts = defaultdict(int)
    out = []
    for n in names:
        c = counts[n]
        out.append(n if c == 0 else f"{n}_{c}")
        counts[n] += 1
    return out

def choose_account_group():
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
        return groups[0]

    while True:
        try:
            choice = int(input("\nSelect an account group by number: ").strip())
            if 0 <= choice < len(groups):
                return groups[choice]
        except ValueError:
            pass
        print("Invalid choice. Try again.")

def main():
    group = choose_account_group()
    aid = group.get("aid") or group.get("accountGroupId") or group.get("id")
    if not aid:
        print("Selected group is missing an AID.")
        sys.exit(1)

    raw = te_get("/tests", aid=str(aid))
    tests = raw.get("tests") or raw.get("items") or raw
    if not isinstance(tests, list):
        print("No tests list found in response.")
        sys.exit(1)

    minimal = []
    for t in tests:
        test_id = t.get("testId") or t.get("testID") or t.get("id")
        test_name = t.get("testName") or t.get("name")
        test_type = t.get("type") or t.get("testType")
        if not (test_id and test_name and test_type):
            continue
        minimal.append(
            {
                "testId": str(test_id),
                "testName": str(test_name),
                "type": str(test_type),
            }
        )

    if not minimal:
        print("No tests with required fields found.")
        sys.exit(0)

    normalized_names = [terraformize_name(m["testName"]) for m in minimal]
    unique_names = ensure_unique(normalized_names)

    result = []
    for m, tf_name in zip(minimal, unique_names):
        tf_type = terraformize_type(m["type"])
        result.append(
            {
                "testId": m["testId"],
                "testName": m["testName"],
                "type": m["type"],
                "tf_type": tf_type,
                "tf_resource_name": tf_name,
            }
        )

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as e:
        print(f"HTTP error: {e}\nResponse: {getattr(e, 'response', None) and e.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Request error: {e}", file=sys.stderr)
        sys.exit(1)
