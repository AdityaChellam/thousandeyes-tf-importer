import requests
from .config import BASE_URL, TOKEN

HEADERS = {
    "Accept": "application/hal+json",
    "Authorization": f"Bearer {TOKEN}",
}

def te_get(path: str, **params):
    url = f"{BASE_URL}{path}"
    r = requests.get(url, headers=HEADERS, params=params or None, timeout=30)
    r.raise_for_status()
    return r.json()
