from getpass import getpass
from pathlib import Path

from ncclient import manager
from ncclient.operations.errors import OperationError
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import TransportError


HOST = "devnetsandboxiosxec9k.cisco.com"
USERNAME = "keianman"
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
LOG_FILE = REPO_ROOT / "logs" / "lab5.log"

HOSTNAME_FILTER = """
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
  <hostname/>
</native>
"""

INTERFACES_FILTER = """
<interfaces xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-interfaces-oper"/>
"""


def log(message):
    print(message)
    with LOG_FILE.open("a", encoding="utf-8") as log_file:
        log_file.write(f"{message}\n")


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    password = getpass("Sandbox password: ")
    successful_rpcs = 0

    try:
        with manager.connect(
            host=HOST,
            port=830,
            username=USERNAME,
            password=password,
            hostkey_verify=False,  # Lab sandbox only.
            timeout=10,
        ) as session:
            log("CONNECT_OK: NETCONF")
            session.timeout = 10
            queries = (
                ("hostname", session.get_config, {
                    "source": "running",
                    "filter": ("subtree", HOSTNAME_FILTER),
                }),
                ("interfaces", session.get, {
                    "filter": ("subtree", INTERFACES_FILTER),
                }),
            )
            for name, rpc, arguments in queries:
                output_file = DATA_DIR / f"netconf_{name}.xml"
                try:
                    reply = rpc(**arguments)
                    output_file.write_text(reply.xml + "\n", encoding="utf-8")
                except (RPCError, OperationError, TransportError, OSError) as error:
                    log(f"NETCONF_RPC_FAIL:{name}")
                    print(f"{name}: {error}")
                    continue

                log(f"NETCONF_RPC_OK:{name}")
                log(f"RAW_SAVED={output_file.name}")
                successful_rpcs += 1
    except (RPCError, OperationError, TransportError, OSError) as error:
        print(f"NETCONF session error for {HOST}:830: {error}")
        return 1

    return 0 if successful_rpcs == 2 else 1


if __name__ == "__main__":
    raise SystemExit(main())