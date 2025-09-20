# main.py
import json
import sys
import requests

BASE_URL = "https://api.thousandeyes.com/v7"
TOKEN = "TOKEN"

HEADERS = {
    "Accept": "application/hal+json",
    "Authorization": f"Bearer {TOKEN}",
}

def te_get(path: str, **params):
    url = f"{BASE_URL}{path}"
    r = requests.get(url, headers=HEADERS, params=params or None, timeout=30)
    r.raise_for_status()
    return r.json()

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

    # Auto-select if only one
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
    name = group.get("accountGroupName") or group.get("name") or str(aid)
    if not aid:
        print("Selected group is missing an AID.")
        sys.exit(1)
    tests = te_get("/tests", aid=str(aid))


if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as e:
        print(f"HTTP error: {e}\nResponse: {getattr(e, 'response', None) and e.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Request error: {e}", file=sys.stderr)
        sys.exit(1)
