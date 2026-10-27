import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def config():
    path = ROOT / "shoes.json"
    if not path.exists():
        raise RuntimeError("Copy shoes.example.json to shoes.json and edit it")
    return json.loads(path.read_text())


def classify(name):
    name = (name or "").lower()
    for pattern, label in [
        (r"warm[ -]?up", "warm up"),
        (r"cool[ -]?down", "cool down"),
        (r"marathon[ -]?(workout|pace)", "marathon workout"),
        (r"track|interval", "track workout"),
        (r"tempo|threshold", "tempo run"),
        (r"long[ -]?run", "long run"),
        (r"easy|recovery", "easy run"),
    ]:
        if re.search(pattern, name):
            return label
    return "unknown"


def override(description):
    for line in (description or "").splitlines():
        match = re.match(r"^\s*shoe\s*:\s*(.*?)\s*$", line, re.I)
        if match and match.group(1):
            return match.group(1)
    return None


def attribution(activity, cfg):
    workout = classify(activity.get("name"))
    explicit = override(activity.get("description"))
    shoe = explicit or cfg.get("defaults", {}).get(workout)
    source = "description" if explicit else ("default" if shoe else "unknown")
    run_date = (activity.get("start_date_local") or activity["start_date"])[:10]
    matches = [
        item for item in cfg.get("cycles", [])
        if shoe and item["shoe_name"].casefold() == shoe.casefold()
        and (not item.get("start_date") or item["start_date"] <= run_date)
        and (not item.get("retired_date") or run_date <= item["retired_date"])
    ]
    matches.sort(key=lambda item: item.get("start_date") or "", reverse=True)
    return workout, shoe, source, matches[0]["id"] if matches else None
