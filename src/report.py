"""Compare saved RESTCONF and NETCONF replies for Lab 5."""

import json
from pathlib import Path
from xml.parsers.expat import ExpatError
from xml.dom import Node, minidom


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT = DATA_DIR / "reports" / "lab5_report.txt"
LOG = ROOT / "logs" / "lab5.log"


def log(message):
    print(message)
    with LOG.open("a", encoding="utf-8") as stream:
        stream.write(f"{message}\n")


def xml_to_dict(element):
    children = [child for child in element.childNodes if child.nodeType == Node.ELEMENT_NODE]
    if not children:
        return "".join(
            child.data for child in element.childNodes
            if child.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE)
        ).strip()

    result = {}
    for child in children:
        result.setdefault(child.localName, []).append(xml_to_dict(child))
    return result


def values(tree, key):
    if isinstance(tree, dict):
        for name, value in tree.items():
            if name.rsplit(":", 1)[-1] == key:
                yield from value if isinstance(value, list) else [value]
            yield from values(value, key)
    elif isinstance(tree, list):
        for item in tree:
            yield from values(item, key)


def first_text(tree, *keys):
    for key in keys:
        for value in values(tree, key):
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def extract(tree):
    result = {
        "Hostname": first_text(tree, "hostname", "host-name"),
        "Model/platform": first_text(tree, "model-name", "model-number", "model", "platform-name", "pid", "platform"),
        "Version": first_text(tree, "software-version", "os-version", "version"),
    }
    interfaces = set()
    has_interface_data = False
    for container_key, entry_key in (
        ("interfaces", "interface"),
        ("interfaces-state", "interface"),
        ("interfaces", "interface-state"),
    ):
        for container in values(tree, container_key):
            for entry in values(container, entry_key):
                name = first_text(entry, "name")
                if name:
                    interfaces.add(name)
                    has_interface_data = True

    if has_interface_data:
        result["Interfaces returned"] = len(interfaces)
    return {key: value for key, value in result.items() if value is not None}


def load_xml(path):
    with minidom.parse(str(path)) as document:
        root = document.documentElement
        return {root.localName: xml_to_dict(root)}


def collect(prefix, extension, marker, load):
    summary = {}
    for path in sorted(DATA_DIR.glob(f"{prefix}_*.{extension}")):
        try:
            fields = extract(load(path))
        except (OSError, ValueError, ExpatError) as error:
            print(f"Could not parse {path.name}: {error}")
            continue

        if not fields:
            print(f"No comparable fields found in {path.name}")
            continue

        for field, value in fields.items():
            summary.setdefault(field, value)
        name = path.stem.removeprefix(f"{prefix}_")
        log(f"{marker}:{name}")

    return summary


def main():
    LOG.parent.mkdir(parents=True, exist_ok=True)
    restconf = collect(
        "restconf", "json", "PARSE_JSON_OK",
        lambda path: json.loads(path.read_text(encoding="utf-8")),
    )
    netconf = collect("netconf", "xml", "PARSE_XML_OK", load_xml)
    if not restconf or not netconf:
        print("Run Steps 3 and 4 first. A report requires usable captures from both protocols.")
        return 1

    missing = "Unavailable in capture"
    lines = ["Lab 5 RESTCONF and NETCONF comparison", ""]
    for field in ("Hostname", "Model/platform", "Version", "Interfaces returned"):
        rest_value = restconf.get(field, missing)
        net_value = netconf.get(field, missing)
        if field not in restconf or field not in netconf:
            comparison = "Comparison unavailable"
        elif rest_value == net_value:
            comparison = "Match"
        else:
            comparison = "Different"
        lines.append(f"{field}: RESTCONF = {rest_value} | NETCONF = {net_value} | {comparison}")

    lines.extend([
        "",
        "Interface counts reflect names in each reply. Configuration and operational views may return different sets.",
    ])
    report = "\n".join(lines) + "\n"
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(report, end="")
    log(f"REPORT_SAVED={REPORT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
