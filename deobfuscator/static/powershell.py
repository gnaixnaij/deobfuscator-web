import base64
import re
import zlib

def decode_base64(s):
    try:
        s = s.strip()
        if s.startswith("'") and s.endswith("'"):
            s = s[1:-1]
        s = s.replace('-', '+').replace('_', '/')
        missing = len(s) % 4
        if missing:
            s += '=' * (4 - missing)
        decoded = base64.b64decode(s)
        return decoded.decode('utf-16-le', errors='replace')
    except Exception:
        return None

def decompress_powershell(data):
    patterns = [
        r'\[System\.Text\.Encoding\]::Unicode\.GetString\(\[System\.Convert\]::FromBase64String\(["\']([^"\']+)["\']\)\)',
        r'FromBase64String\(["\']([^"\']+)["\']\)',
    ]
    for p in patterns:
        match = re.search(p, data, re.IGNORECASE)
        if match:
            decoded = decode_base64(match.group(1))
            if decoded:
                return decoded
    return data

def handle_nested_invoke(data):
    while True:
        m = re.search(r'&\{([^}]+)\}', data)
        if not m:
            break
        data = data.replace(m.group(0), m.group(1).strip())
    return data

def remove_noise(s):
    s = re.sub(r'`[^nrt]', '', s)
    s = re.sub(r'\$[a-zA-Z_]\w*\s*=\s*["\'][^"\']*["\'];?\s*', '', s)
    s = re.sub(r';\s*\$[a-zA-Z_]\w*\s*=\s*["\'][^"\']*["\']', '', s)
    s = re.sub(r'\$[a-zA-Z_]\w*\s*\+\s*=\s*["\'][^"\']*["\'];?\s*', '', s)
    return s

def deobfuscate(script):
    result = script
    steps = []

    result = decompress_powershell(result)

    b64_blocks = re.findall(r'["\']([A-Za-z0-9+/=_-]{40,})["\']', result)
    for block in b64_blocks:
        decoded = decode_base64(block)
        if decoded and any(c in decoded for c in ' .;$|'):
            steps.append(f"Base64 decoded a {len(block)}-char block")
            result = result.replace(f'"{block}"', decoded, 1)
            result = result.replace(f"'{block}'", decoded, 1)

    result = handle_nested_invoke(result)

    iex_patterns = [
        r'[Ii][Ee][Xx]\s+[\(\.]?\s*["\'](.+?)["\']\s*[\)]?',
        r'Invoke-Expression\s+[\(\.]?\s*["\'](.+?)["\']\s*[\)]?',
        r'&?\s*\{\s*["\'](.+?)["\']\s*\}',
    ]
    for p in iex_patterns:
        for m in re.finditer(p, result):
            steps.append(f"Extracted IEX payload ({len(m.group(1))} chars)")

    result = re.sub(
        r'[Ii][Ee][Xx]\s*[\(\.]?\s*["\'][^"\']+["\']\s*[\)]?',
        lambda m: m.group(0).split('"')[0].split("'")[0] if '"' in m.group(0) else m.group(0).split("'")[0] + " <deobfuscated>",
        result
    )

    result = remove_noise(result)
    result = re.sub(r'\s+', ' ', result).strip()

    return result, steps
