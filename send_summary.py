import os
import subprocess
import sys

from dotenv import load_dotenv
from auth import ROOT
from summary import build_summary

load_dotenv(ROOT / ".env")


def main():
    recipient = os.getenv("IMESSAGE_RECIPIENT")
    if not recipient:
        raise SystemExit("Set IMESSAGE_RECIPIENT in .env")
    message = build_summary()
    script = '''
    on run argv
        tell application "Messages"
            set targetService to first service whose service type = iMessage
            set targetBuddy to buddy (item 1 of argv) of targetService
            send (item 2 of argv) to targetBuddy
        end tell
    end run
    '''
    subprocess.run(["osascript", "-e", script, recipient, message], check=True)
    print("iMessage summary sent.")


if __name__ == "__main__":
    main()
