import json
from getpass import getpass
from pathlib import Path

import requests


BASE_URL = "https://devnetsandboxiosxec9k.cisco.com/restconf/data/"
USERNAME = "keianman"
HEADERS = {"Accept": "application/yang-data+json"}
ENDPOINTS = {
    "hostname": "Cisco-IOS-XE-native:native/hostname",
    "interfaces": "ietf-interfaces:interfaces",
}

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
LOG_FILE = REPO_ROOT / "logs" / "lab5.log"


def log(message):
    print(message)
    with LOG_FILE.open("a", encoding="utf-8") as log_file:
        log_file.write(f"{message}\n")


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    password = getpass("Sandbox password: ")
    successful_requests = 0

    for name, endpoint in ENDPOINTS.items():
        url = f"{BASE_URL}{endpoint}"
        output_file = DATA_DIR / f"restconf_{name}.json"

        try:
            response = requests.get(
                url,
                auth=(USERNAME, password),
                headers=HEADERS,
                timeout=10,
                verify=False,  # Lab sandbox only.
            )
            response.raise_for_status()
            payload = response.json()
            output_file.write_text(
                json.dumps(payload, indent=2) + "\n", encoding="utf-8"
            )
        except (requests.RequestException, OSError) as error:
            log(f"RESTCONF_REQ_FAIL:{name}")
            print(f"{url}\n{error}")
            continue

        if successful_requests == 0:
            log("CONNECT_OK: RESTCONF")
        log(f"RESTCONF_REQ_OK:{name}")
        log(f"RAW_SAVED={output_file.name}")
        successful_requests += 1

    return 0 if successful_requests == len(ENDPOINTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())