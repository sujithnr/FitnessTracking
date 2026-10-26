import json
import os
from urllib.parse import urlencode, urlparse, parse_qs

import requests
from auth import TOKENS

def main():
    url = "https://www.strava.com/oauth/authorize?" + urlencode({
        "client_id": os.environ["STRAVA_CLIENT_ID"],
        "redirect_uri": "http://localhost/exchange_token",
        "response_type": "code",
        "approval_prompt": "auto",
        "scope": "activity:read_all",
    })
    print("Open this URL:\n" + url)
    redirected = input("\nPaste redirected URL or code: ").strip()
    code = parse_qs(urlparse(redirected).query).get("code", [redirected])[0]
    response = requests.post("https://www.strava.com/oauth/token", data={
        "client_id": os.environ["STRAVA_CLIENT_ID"],
        "client_secret": os.environ["STRAVA_CLIENT_SECRET"],
        "grant_type": "authorization_code",
        "code": code,
    }, timeout=30)
    response.raise_for_status()
    TOKENS.write_text(json.dumps(response.json(), indent=2) + "\n")
    TOKENS.chmod(0o600)
    print("Tokens saved locally.")

if __name__ == "__main__":
    main()
