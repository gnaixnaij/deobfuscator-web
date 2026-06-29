def generate_sigma(iocs, title="Suspicious Script Detection"):
    rules = []
    
    if iocs["urls"]:
        rule = f"""title: {title}
status: experimental
description: Detected potential C2 URLs from deobfuscated script analysis
logsource:
    category: proxy
detection:
    selection:
        cs-uri-stem|contains:
{_yaml_list(iocs["urls"])}
    condition: selection
falsepositives:
    - Unknown
level: high"""
        rules.append(("Sigma — Network (URLs)", rule))

    if iocs["domains"]:
        rule = f"""title: {title} - Domain Indicators
status: experimental
description: Detected domains from deobfuscated script analysis
logsource:
    category: dns
detection:
    selection:
        query|value:
{_yaml_list(iocs["domains"])}
    condition: selection
falsepositives:
    - Unknown
level: high"""
        rules.append(("Sigma — DNS (Domains)", rule))

    if iocs["ips"]:
        rule = f"""title: {title} - IP Indicators
status: experimental
description: Detected IP addresses from deobfuscated script analysis
logsource:
    category: network
detection:
    selection:
        destination|ip:
{_yaml_list(iocs["ips"])}
    condition: selection
falsepositives:
    - Unknown
level: high"""
        rules.append(("Sigma — Network (IPs)", rule))

    if iocs["registry_keys"]:
        rule = f"""title: {title} - Registry Indicators
status: experimental
description: Detected registry keys from deobfuscated script analysis
logsource:
    category: registry
detection:
    selection:
        TargetObject|contains:
{_yaml_list(iocs["registry_keys"])}
    condition: selection
falsepositives:
    - Unknown
level: medium"""
        rules.append(("Sigma — Registry", rule))

    if iocs["filepaths"]:
        rule = f"""title: {title} - File Path Indicators
status: experimental
description: Detected file paths from deobfuscated script analysis
logsource:
    category: file_event
detection:
    selection:
        TargetFilename|contains:
{_yaml_list(iocs["filepaths"])}
    condition: selection
falsepositives:
    - Unknown
level: medium"""
        rules.append(("Sigma — File System", rule))

    return rules


def _yaml_list(items):
    seen = set()
    lines = []
    for item in items:
        if item.lower() not in seen:
            seen.add(item.lower())
            lines.append(f"            - '{item}'")
    return "\n".join(lines[:10])
