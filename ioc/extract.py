import re
import ipaddress
from urllib.parse import urlparse

def extract_iocs(script):
    iocs = {
        "ips": [],
        "domains": [],
        "urls": [],
        "emails": [],
        "filepaths": [],
        "registry_keys": [],
        "hashes": {
            "md5": [],
            "sha1": [],
            "sha256": [],
        },
        "base64_strings": [],
    }

    seen = set()

    def unique(items):
        result = []
        for item in items:
            if item.lower() not in seen:
                seen.add(item.lower())
                result.append(item)
        return result

    iocs["ips"] = unique(_extract_ips(script))
    iocs["domains"] = unique(_extract_domains(script))
    iocs["urls"] = unique(_extract_urls(script))
    iocs["emails"] = unique(_extract_emails(script))
    iocs["filepaths"] = unique(_extract_filepaths(script))
    iocs["registry_keys"] = unique(_extract_registry(script))
    iocs["hashes"]["md5"] = unique(_extract_md5(script))
    iocs["hashes"]["sha1"] = unique(_extract_sha1(script))
    iocs["hashes"]["sha256"] = unique(_extract_sha256(script))
    iocs["base64_strings"] = unique(_extract_base64(script))

    return iocs


def _extract_ips(text):
    ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
    valid = []
    for ip in ips:
        try:
            addr = ipaddress.ip_address(ip)
            if not addr.is_private and not addr.is_loopback and not addr.is_link_local:
                valid.append(str(addr))
        except ValueError:
            pass
    return valid


def _extract_domains(text):
    domains = re.findall(
        r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b',
        text
    )
    excludes = {"example.com", "test.com", "domain.com", "localhost"}
    return [d for d in domains if d.lower() not in excludes]


def _extract_urls(text):
    urls = re.findall(
        r'https?://[^\s"\'<>\[\]]+',
        text
    )
    return [u.rstrip(".,;:!?)") for u in urls]


def _extract_emails(text):
    emails = re.findall(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
        text
    )
    return [e for e in emails if not e.endswith(".local")]


def _extract_filepaths(text):
    paths = []
    paths.extend(re.findall(r'(?:[Cc]:\\|/)[^\s"\'<>\[\]]+(?:\.\w+)?', text))
    paths = [p for p in paths if len(p) > 5]
    return paths


def _extract_registry(text):
    keys = re.findall(
        r'(?:HK[A-Z_]+|HKEY_[A-Z_]+|REG_[A-Z_]+)\\[A-Za-z0-9_\\]+',
        text, re.IGNORECASE
    )
    return keys


def _extract_md5(text):
    matches = re.findall(r'\b[a-fA-F0-9]{32}\b', text)
    return [m.lower() for m in matches]


def _extract_sha1(text):
    matches = re.findall(r'\b[a-fA-F0-9]{40}\b', text)
    return [m.lower() for m in matches]


def _extract_sha256(text):
    matches = re.findall(r'\b[a-fA-F0-9]{64}\b', text)
    return [m.lower() for m in matches]


def _extract_base64(text):
    b64_candidates = re.findall(r'[A-Za-z0-9+/=]{40,}', text)
    import base64
    valid = []
    for b in b64_candidates:
        try:
            decoded = base64.b64decode(b, validate=True)
            if 8 <= len(decoded) <= 512:
                valid.append(b)
        except Exception:
            pass
    return valid[:10]
