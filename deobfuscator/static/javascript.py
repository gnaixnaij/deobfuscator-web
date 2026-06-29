import re

def unpack_charcode_arrays(s):
    pat = r'String\.fromCharCode\(([^)]+)\)'
    def repl(m):
        try:
            nums = [int(x.strip()) for x in m.group(1).split(',')]
            return ''.join(chr(n) for n in nums)
        except ValueError:
            return m.group(0)
    return re.sub(pat, repl, s)

def decode_hex_strings(s):
    def replace_hex(m):
        try:
            return bytes.fromhex(m.group(1).replace('\\x', '')).decode('utf-8', errors='replace')
        except Exception:
            return m.group(0)
    return re.sub(r'(?:\\x[0-9a-fA-F]{2})+', replace_hex, s)

def extract_eval(s):
    while True:
        m = re.search(r'eval\s*\(\s*(["\'])((?:\\?.)*?)\1\s*\)', s, re.DOTALL)
        if not m:
            break
        inner = m.group(2)
        inner = inner.replace('\\x', '\\x').encode().decode('unicode_escape', errors='replace')
        s = s.replace(m.group(0), inner, 1)
    return s

def decode_base64_js(s):
    import base64
    pat = r'atob\(["\']([A-Za-z0-9+/=]+)["\']\)'
    def repl(m):
        try:
            return base64.b64decode(m.group(1)).decode('utf-8', errors='replace')
        except Exception:
            return m.group(0)
    return re.sub(pat, repl, s)

def decode_unicode_escapes(s):
    def repl(m):
        try:
            return chr(int(m.group(1), 16))
        except ValueError:
            return m.group(0)
    return re.sub(r'\\u([0-9a-fA-F]{4})', repl, s)

def deobfuscate(script):
    result = script
    steps = []

    result = extract_eval(result)
    if result != script:
        steps.append("Unwrapped eval() layers")

    result = decode_hex_strings(result)
    steps.append("Decoded hex-escaped strings")

    result = decode_unicode_escapes(result)
    steps.append("Decoded unicode escapes")

    result = decode_base64_js(result)
    steps.append("Decoded base64 strings (atob)")

    result = unpack_charcode_arrays(result)
    steps.append("Unpacked String.fromCharCode() arrays")

    result = re.sub(r'\s+', ' ', result).strip()

    return result, steps
