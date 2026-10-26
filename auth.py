import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
TOKENS = ROOT / "tokens.json"
API = "https://www.strava.com/api/v3"


def access_token():
    if not TOKENS.exists():
        raise RuntimeError("Run python init_auth.py first")
    data = json.loads(TOKENS.read_text())
    if data.get("expires_at", 0) > datetime.now(timezone.utc).timestamp() + 120:
        return data["access_token"]
    response = requests.post("https://www.strava.com/oauth/token", data={
        "client_id": os.environ["STRAVA_CLIENT_ID"],
        "client_secret": os.environ["STRAVA_CLIENT_SECRET"],
        "grant_type": "refresh_token",
        "refresh_token": data["refresh_token"],
    }, timeout=30)
    response.raise_for_status()
    data = response.json()
    TOKENS.write_text(json.dumps(data, indent=2) + "\n")
    TOKENS.chmod(0o600)
    return data["access_token"]
