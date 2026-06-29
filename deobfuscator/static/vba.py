import re

def resolve_chr(s):
    def replace_chr(m):
        inner = m.group(1) or m.group(2)
        try:
            nums = [int(x.strip()) for x in inner.split(',')]
            return ''.join(chr(n) for n in nums)
        except ValueError:
            return m.group(0)

    s = re.sub(r'Chr\(\s*(\d+)\s*\)', replace_chr, s, flags=re.IGNORECASE)
    return s

def concat_strings(s):
    result = s
    result = re.sub(r'"\s*&\s*"', '', result)
    while re.search(r'[^&\s]\s*&\s*[^&\s]', result):
        result = re.sub(r'([^&\s])\s*&\s*([^&\s])', r'\1\2', result)
    return result

def strip_dead_vars(s):
    s = re.sub(r'(Dim |Static |Public |Private )\s+\w+\s*,\s*\w+.*', '', s)
    s = re.sub(r'^\s*\w+\s*=\s*""\s*$', '', s, flags=re.MULTILINE)
    return s

def collapse_lines(s):
    lines = s.split('\n')
    cleaned = []
    buf = ''
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("'"):
            continue
        if stripped.endswith('_'):
            buf += stripped[:-1].rstrip() + ' '
        else:
            cleaned.append(buf + stripped)
            buf = ''
    if buf:
        cleaned.append(buf)
    return '\n'.join(cleaned)

def deobfuscate(script):
    result = script
    steps = []

    result = collapse_lines(result)
    steps.append("Collapsed continuation lines")

    result = resolve_chr(result)
    steps.append("Resolved Chr() function calls")

    result = concat_strings(result)
    steps.append("Concatenated string fragments")

    result = strip_dead_vars(result)
    steps.append("Stripped dead variable assignments")

    result = re.sub(r'\s+', ' ', result).strip()
    result = re.sub(r'^\s*$\n', '', result, flags=re.MULTILINE)

    return result, steps
