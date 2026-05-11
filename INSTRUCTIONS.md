# Instructions — Lab 5 — RESTCONF vs NETCONF on Catalyst 8k

## Objectives
- Call at least two RESTCONF endpoints and two NETCONF RPCs on a Catalyst 8k sandbox.
- Use Python `requests` for RESTCONF and `ncclient` for NETCONF.
- Parse RESTCONF JSON and NETCONF XML into Python data structures.
- Extract comparable device facts (e.g., hostname, model, version, interface info).
- Generate a human-readable report using f-strings, saved to the repo.
- Log clear, deterministic markers for autograding and troubleshooting.

## Prerequisites
- Python 3.11 (via the provided dev container)
- Accounts: GitHub
- Devices/Sandboxes: Cisco DevNet Always-On Catalyst 8000v (RESTCONF + NETCONF)
- Technical: - Intermediate Python: functions, modules, exceptions, and logging.
- Basics of HTTP headers and authentication.
- Familiarity with XML/JSON and their Python libraries.
- GitHub Classroom workflow (clone, commit, push, PR).
- Cisco DevNet sandbox credentials and device reachability.

## Table of Contents

1. [Step 1 — Clone the Repository](#step-1--clone-the-repository)
2. [Step 2 — Open Dev Container](#step-2--open-dev-container)
3. [Step 3 — RESTCONF — make ≥2 GET requests](#step-3--restconf--make-2-get-requests)
4. [Step 4 — NETCONF — make ≥2 RPCs](#step-4--netconf--make-2-rpcs)
5. [Step 5 — Parse artifacts & build f-string report](#step-5--parse-artifacts--build-f-string-report)
6. [Step 6 — Finalize & Submit](#step-6--finalize--submit)

## Overview
You will query a Catalyst 8k device via both RESTCONF (HTTP/JSON) and NETCONF (SSH/XML). For RESTCONF, use Python `requests` and proper YANG/JSON Accept headers; for NETCONF, use `ncclient` and standard RPCs. Make at least two calls per interface (2+ RESTCONF endpoints and 2+ NETCONF RPCs), parse outputs into Python, then craft a concise f-string report that compares findings (e.g., hostname, platform/model, version, and one interface/oper state). Save raw artifacts under `data/`, log autograder markers to `logs/lab5.log`, and submit a PR.


> **Before you begin:** Confirm sandbox host/IP, RESTCONF port (often 443) and NETCONF port (830). Open the dev container, verify `requests`, `ncclient`, and `xmltodict` import successfully. Ensure you can write to `data/` and `logs/`.


## Resources

- [Cisco DevNet Sandboxes (Catalyst 8k/IOS-XE)](https://developer.cisco.com/site/sandbox/)
- [RESTCONF — RFC 8040 (concepts)](https://www.rfc-editor.org/rfc/rfc8040)
- [NETCONF — RFC 6241 (concepts)](https://www.rfc-editor.org/rfc/rfc6241)
- [Requests (Python)](https://requests.readthedocs.io/en/latest/)
- [ncclient (Python)](https://ncclient.readthedocs.io/)
- [xmltodict](https://github.com/martinblech/xmltodict)

## Deliverables
- `src/restconf_queries.py` — performs ≥2 RESTCONF GETs, saves raw JSON, logs markers.
- `src/netconf_queries.py` — performs ≥2 NETCONF RPCs, saves raw XML, logs markers.
- `src/report.py` (or integrate into one script) — parses saved artifacts and writes `data/reports/lab5_report.txt` using f-strings.
- `data/restconf_*.json` and `data/netconf_*.xml` raw outputs.
- `data/reports/lab5_report.txt` summary comparing key facts.
- `logs/lab5.log` with all required markers.
- Pull request open to `main` with all artifacts committed.
- Grading: **75 points**

Follow these steps in order.

> **Logging Requirement:** Write progress to `logs/lab5.log` as you complete each step.

## Step 1 — Clone the Repository
**Goal:** Get the starter locally.

**What to do:**  
Clone your Classroom repo and `cd` into it. Create `src/`, `data/raw/`, `data/reports/`, and `logs/` if missing.
Initialize the lab log: `echo 'LAB5_START' >> logs/lab5.log`


**You're done when:**  
- Folders exist and `LAB5_START` appears in `logs/lab5.log`.


**Log marker to add:**  
`[LAB5_START]`

## Step 2 — Open Dev Container
**Goal:** Standardize the toolchain.

**What to do:**  
Reopen in container. Verify imports:
  - `python -c "import requests, ncclient, xmltodict; print('OK')"`
Append `[STEP 2] Dev Container Started` and `PKG_OK: requests`, `PKG_OK: ncclient` to the log.


**You're done when:**  
- Python 3.11+ confirmed; packages import cleanly.
- Log includes the markers.


**Log marker to add:**  
`[[STEP 2] Dev Container Started, PKG_OK: requests, PKG_OK: ncclient]`

## Step 3 — RESTCONF — make ≥2 GET requests
**Goal:** Retrieve JSON via RESTCONF using correct headers.

**What to do:**  
In `src/restconf_queries.py`:
  - Configure base URL (e.g., `https://<host>/restconf/data/`) and basic auth.
  - Set headers e.g., `{'Accept': 'application/yang-data+json'}`.
  - Choose ≥2 endpoints (examples to consider: system/hostname, platform, interfaces summary/oper status).
  - Use `requests.get(..., timeout=10, verify=False)` for sandbox; handle HTTP errors with try/except.
  - Save each response to `data/restconf_<name>.json`.
  - Log `CONNECT_OK: RESTCONF` once and `RESTCONF_REQ_OK:<name>` per successful endpoint; on failure, `RESTCONF_REQ_FAIL:<name>`.
  - Log `RAW_SAVED=restconf_<name>.json` after writing files.


**You're done when:**  
- At least two `RESTCONF_REQ_OK:*` appear and raw JSON files exist.


**Log marker to add:**  
`[CONNECT_OK: RESTCONF, RESTCONF_REQ_OK, RAW_SAVED]`

## Step 4 — NETCONF — make ≥2 RPCs
**Goal:** Retrieve XML via NETCONF with ncclient.

**What to do:**  
In `src/netconf_queries.py`:
  - Use `manager.connect(host=..., port=830, username=..., password=..., hostkey_verify=False, timeout=10)`.
  - Log `CONNECT_OK: NETCONF` on successful session.
  - Issue ≥2 RPCs (e.g., get system/platform info, get interfaces-state). Use appropriate filters.
  - Save each RPC reply XML to `data/netconf_<name>.xml`.
  - Log `NETCONF_RPC_OK:<name>` per successful RPC; on failure, `NETCONF_RPC_FAIL:<name>`.
  - Log `RAW_SAVED=netconf_<name>.xml` after writing files.


**You're done when:**  
- At least two `NETCONF_RPC_OK:*` appear and raw XML files exist.


**Log marker to add:**  
`[CONNECT_OK: NETCONF, NETCONF_RPC_OK, RAW_SAVED]`

## Step 5 — Parse artifacts & build f-string report
**Goal:** Normalize JSON/XML and print a concise comparison.

**What to do:**  
In `src/report.py` (or inside one of your scripts):
  - Load `data/restconf_*.json` with `json`.
  - Load `data/netconf_*.xml` with `xmltodict` (or `minidom`), convert to Python dicts.
  - Extract comparable fields: hostname, model/platform, version, and one interface count/oper-state metric.
  - Log `PARSE_JSON_OK:<name>` and `PARSE_XML_OK:<name>` when extraction succeeds.
  - Compose an f-string report summarizing both interfaces’ results and any differences.
  - Save report to `data/reports/lab5_report.txt` and log `REPORT_SAVED=lab5_report.txt`.


**You're done when:**  
- `data/reports/lab5_report.txt` exists and includes values from both RESTCONF and NETCONF.


**Log marker to add:**  
`[PARSE_JSON_OK, PARSE_XML_OK, REPORT_SAVED=lab5_report.txt]`

## Step 6 — Finalize & Submit
**Goal:** Ensure logs and artifacts are complete; open PR.

**What to do:**  
Review `logs/lab5.log` for all required markers. Append `LAB5_END`.
Commit and push all changes. Open a pull request targeting `main`.


**You're done when:**  
- PR open; artifacts present and markers complete.


**Log marker to add:**  
`[LAB5_END]`


## FAQ
**Q:** RESTCONF returned HTML, not JSON.  
**A:** Set `Accept: application/yang-data+json` and use the exact RESTCONF path.

**Q:** NETCONF keeps failing to connect.  
**A:** Use port 830, correct credentials, and `hostkey_verify=False` for the sandbox.

**Q:** Do I need YANG files locally?  
**A:** Not for these read-only queries; you just need correct paths/RPCs that align with YANG models.


## 🔧 Troubleshooting & Pro Tips
**Timeouts**  
*Symptom:* Long waits or hang on calls.  
*Fix:* Set `timeout=10` and catch `requests.Timeout` or ncclient timeouts.

**File paths**  
*Symptom:* Nothing saved under `data/`.  
*Fix:* Create directories and use repo-relative paths; check write permissions.

**Markers missing**  
*Symptom:* Autograder shows missing tokens.  
*Fix:* Log exact strings from the Autograder section; don’t improvise marker text.


## Grading Breakdown
| Step | Requirement | Points |
|---|---|---|
| Step 2 | Dev container started; packages verified | 5 |
| RESTCONF | ≥2 RESTCONF endpoints succeed (`RESTCONF_REQ_OK:*`, `CONNECT_OK: RESTCONF`) | 12 |
| NETCONF | ≥2 NETCONF RPCs succeed (`NETCONF_RPC_OK:*`, `CONNECT_OK: NETCONF`) | 12 |
| Parsing | JSON and XML parsed; fields extracted (`PARSE_JSON_OK:*`, `PARSE_XML_OK:*`) | 12 |
| Report | F-string report generated and saved (`REPORT_SAVED=lab5_report.txt`) | 12 |
| Artifacts | Raw files saved under `data/` with `RAW_SAVED=*` markers | 7 |
| Error handling & logging | Handled exceptions; consistent logging | 5 |
| Submission | PR open; `LAB5_START` and `LAB5_END` present | 10 |
| **Total** |  | **75** |

## Autograder Notes
- Log file: `logs/lab5.log`
- Required markers: `LAB5_START`, `[STEP 2] Dev Container Started`, `PKG_OK: requests`, `PKG_OK: ncclient`, `CONNECT_OK: RESTCONF`, `CONNECT_OK: NETCONF`, `RESTCONF_REQ_OK`, `NETCONF_RPC_OK`, `RAW_SAVED`, `PARSE_JSON_OK`, `PARSE_XML_OK`, `REPORT_SAVED=lab5_report.txt`, `LAB5_END`

## Submission Checklist
- [ ] `src/restconf_queries.py` and `src/netconf_queries.py` run without unhandled exceptions.
- [ ] `data/restconf_*.json` and `data/netconf_*.xml` exist and are populated.
- [ ] `data/reports/lab5_report.txt` compares fields from both interfaces.
- [ ] `logs/lab5.log` contains all required markers.
- [ ] Pull request open before deadline.
