import re


def generate_yara(iocs, rule_name="DecodedMalwareIOC"):
    strings = []
    conditions = []
    idx = 0

    for url in iocs["urls"]:
        if len(url) > 4:
            escaped = _escape_yara(url)
            strings.append(f"    $url_{idx} = \"{escaped}\"")
            conditions.append(f"$url_{idx}")
            idx += 1

    for domain in iocs["domains"]:
        if len(domain) > 3:
            escaped = _escape_yara(domain)
            strings.append(f"    $domain_{idx} = \"{escaped}\"")
            conditions.append(f"$domain_{idx}")
            idx += 1

    for ip in iocs["ips"]:
        strings.append(f"    $ip_{idx} = \"{ip}\"")
        conditions.append(f"$ip_{idx}")
        idx += 1

    for htype in ["md5", "sha1", "sha256"]:
        for h in iocs["hashes"].get(htype, []):
            strings.append(f"    $hash_{idx} = \"{h}\"")
            conditions.append(f"$hash_{idx}")
            idx += 1

    if not strings:
        return None

    if len(conditions) == 1:
        condition = f"${conditions[0]}"
    else:
        cond_lines = " or\n        ".join(conditions)
        condition = f"any of ({', '.join(conditions)})"

    rule = f"""rule {rule_name}
{{
    meta:
        description = "Automatically generated from deobfuscated script IOCs"
        author = "deobfuscator-web"
        date = "{_today()}"
        hash = "unknown"

    strings:
{chr(10).join(strings)}

    condition:
        {condition}
}}"""
    return rule


def _escape_yara(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _today():
    from datetime import date
    return date.today().isoformat()
