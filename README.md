# Lab 5 — RESTCONF vs NETCONF on Catalyst 8k

**Course:** Software Defined Networking  
**Module:** Network Automation Fundamentals • **Lab #:** 5  
**Estimated Time:** 1.5–2 hours

## Repository structure

```text
Lab-5-RESTCONF-and-NETCONF
├── .devcontainer
│   └── devcontainer.json
├── .gitignore
├── .markdownlint.json
├── .markdownlintignore
├── .pettierrc.yml
├── INSTRUCTIONS.backup.md
├── INSTRUCTIONS.md
├── LICENSE
├── README.backup.md
├── README.md
├── data
│   └── inventory.example.yml
├── lab.yml
├── prettierrc.yml
├── requirements.txt
└── src
    ├── __init__.py
    └── main.py
```


## Lab Topics

### Introduction to Network Device APIs
Modern network devices expose programmable interfaces via RESTCONF and NETCONF, allowing
automation tools to interact with device configurations and state data. This lab explores
both protocols on a Cisco Catalyst 8000v device, comparing their usage and outputs.


### What is RESTCONF?
RESTCONF is a REST-like protocol that provides a programmatic interface for accessing
data defined in YANG, using HTTP methods. It typically returns data in JSON formats. RESTCONF
is stateless and leverages standard HTTP features like authentication, caching, and error handling. You
will use Python's `requests` library to interact with RESTCONF endpoints but can also use tools like Postman or curl.

RESTCONF is defined in RFC 8040 and listens on HTTP/HTTPS ports (often 443). To enable RESTCONF on a Cisco device,
you typically use the `restconf` command in global configuration mode as shown below:


```bash
router(config)# restconf
router(config)# end

```

### What is NETCONF?
NETCONF is a network management protocol that provides mechanisms to install, manipulate,
and delete the configuration of network devices. It uses XML for data encoding and operates
over SSH. NETCONF is stateful and supports transactions, making it suitable for complex
configuration tasks. You will use Python's `ncclient` library to interact with NETCONF, but
tools like `netconf-console` can also be used.

NETCONF is defined in RFC 6241 and typically listens on port 830. To enable NETCONF on a Cisco device,
you usually need to ensure SSH is enabled and the device is configured to accept NETCONF sessions.
On many Cisco devices, NETCONF is enabled by default when SSH is active. However, if you need to explicitly
enable it, you can use the following commands:


```bash
router(config)# netconf-yang
router(config)# end

```

### Comparing RESTCONF and NETCONF
Both RESTCONF and NETCONF are powerful protocols for network device management, each with its
own strengths. RESTCONF's use of HTTP and JSON makes it more accessible for web developers
and easier to integrate with modern web services. In contrast, NETCONF's XML-based approach
and support for transactions make it more suitable for complex configuration tasks in traditional
network management scenarios.

In this lab, you will interact with both protocols on a Cisco Catalyst 8000v device to retrieve
system information, compare the outputs, and understand how YANG models influence both interfaces.

RESTCONF is more suitable for web-based applications and simpler tasks, while NETCONF is often preferred for
complex configurations and environments where transactional integrity is crucial. Device telemetry streaming
is another area where NETCONF excels, as it can efficiently handle large volumes of data and provide real-time updates.


### What is YANG?
YANG is a data modeling language used to define the structure of data that can be managed
by network devices. It provides a way to model configuration and state data in a hierarchical
manner, making it easier to understand and manipulate. YANG models are used by both RESTCONF
and NETCONF to define the data that can be accessed or modified.

In RESTCONF, YANG models are typically exposed as RESTful APIs, allowing clients to interact
with the data using standard HTTP methods. In NETCONF, YANG models are used to define the
XML-based RPC messages that are exchanged between clients and devices.

Understanding YANG is crucial for working with both RESTCONF and NETCONF, as it provides
the foundation for the data structures and operations that these protocols support.

An example of YANG model snippet for system information might look like this:


```yang
module system {
  namespace "http://example.com/system";
  prefix sys;

  container system {
    leaf hostname {
      type string;
    }
    leaf version {
      type string;
    }
  }
}

```

### Cisco Catalyst 8k API Docs
Cisco provides comprehensive API documentation for the Catalyst 8000 series, including
RESTCONF and NETCONF interfaces. You can find the documentation at the following link:

[Cisco Catalyst 8000 Series API Documentation](https://developer.cisco.com/docs/catalyst-8000/)

This documentation includes details on available YANG models, RESTCONF endpoints, and
NETCONF RPCs, along with examples and usage guidelines.

This documentation is an essential resource for understanding how to interact with the
Catalyst 8000 series devices using their APIs.


### Creating a RESTCONF Request with Python `requests`
To create a RESTCONF request using Python's `requests` library, you need to set up the
appropriate headers, authentication, and the URL for the RESTCONF endpoint. Below is an
example of how to perform a GET request to retrieve system information from a Cisco
Catalyst 8000v device.


```python
import requests
from requests.auth import HTTPBasicAuth
import json

# Device details
device_ip = "sandbox-iosxe-latest-1.cisco.com"
restconf_port = 443
username = "developer"
password = "C1sco12345"

# RESTCONF endpoint for system information
url = f"https://{device_ip}:{restconf_port}/restconf/data/Cisco-IOS-XE-native:native/system"

# Headers for RESTCONF
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

# Make the GET request
response = requests.get(url, auth=HTTPBasicAuth(username, password), headers=headers, verify=False)

# Check the response status
if response.status_code == 200:
    system_info = response.json()
    print(json.dumps(system_info, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")

```

### Creating a NETCONF Request with Python `ncclient`
To create a NETCONF request using Python's `ncclient` library, you need to establish
a connection to the device and then send an RPC to retrieve the desired information.
Below is an example of how to perform a GET request to retrieve system information
from a Cisco Catalyst 8000v device.


```python
from ncclient import manager
import xml.etree.ElementTree as ET

# Device details
device_ip = "sandbox-iosxe-latest-1.cisco.com"
netconf_port = 830
username = "developer"
password = "C1sco12345"

# NETCONF filter for system information
filter = """
<filter>
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <system>
    </system>
  </native>
</filter>
"""

# Establish NETCONF connection
with manager.connect(host=device_ip, port=netconf_port, username=username, password=password, hostkey_verify=False) as m:
    # Send the NETCONF RPC
    response = m.get(filter)

    # Parse and print the XML response
    xml_response = ET.fromstring(response.xml)
    print(ET.tostring(xml_response, encoding='unicode', method='xml'))

```



## License
© 2025 Sheldon Swanson — Classroom use.
