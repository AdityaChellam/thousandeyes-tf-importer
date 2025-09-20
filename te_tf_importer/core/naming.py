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
