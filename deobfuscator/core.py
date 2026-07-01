from .static import powershell, vba, javascript

STATIC_ENGINES = {
    "powershell": powershell,
    "vba": vba,
    "javascript": javascript,
}

LANG_ALIASES = {
    "ps1": "powershell",
    "ps": "powershell",
    "vba": "vba",
    "bas": "vba",
    "js": "javascript",
    ".ps1": "powershell",
    ".vba": "vba",
    ".bas": "vba",
    ".js": "javascript",
}


def detect_language(script, hint=None):
    if hint:
        hint = hint.lower().strip()
        if hint in LANG_ALIASES:
            return LANG_ALIASES[hint]
        if hint in STATIC_ENGINES:
            return hint
        if hint.lstrip(".") in LANG_ALIASES:
            return LANG_ALIASES[hint.lstrip(".")]

    lines = script.strip().split('\n')
    first_lines = [l.strip() for l in lines[:8] if l.strip()]

    # Check for strong PowerShell signals first
    ps_signals = 0
    for line in first_lines:
        if '$' in line and any(kw in line.lower() for kw in ['iex', 'invoke', 'write-host', 'get-', '-enc', 'frombase64']):
            ps_signals += 2
        if line.startswith('function ') and '$' in line:
            ps_signals += 1
    if ps_signals >= 2:
        return "powershell"

    # Check for strong VBA signals
    vba_signals = 0
    for line in first_lines:
        if line.lower().startswith(('sub ', 'end sub', 'end function', 'dim ', 'attribute ')):
            vba_signals += 2
        if 'chrw(' in line.lower() or 'chrd(' in line.lower() or 'chr(' in line.lower():
            vba_signals += 1
    if vba_signals >= 2:
        return "vba"

    # Check for strong JavaScript signals
    js_signals = 0
    for line in first_lines:
        if 'function ' in line.lower() and '{' in line and '$' not in line:
            js_signals += 2
        if line.startswith(('var ', 'let ', 'const ')):
            js_signals += 2
        if 'eval(' in line.lower() or 'atob(' in line.lower():
            js_signals += 1
    if js_signals >= 2:
        return "javascript"

    # Scoring fallback
    ps_score = sum(1 for kw in ['$', '|', '-e ', '-enc ', 'iex'] if kw in script.lower())
    vba_score = sum(1 for kw in ['sub ', 'dim ', 'set ', 'chrw', 'chrd', 'vbhide'] if kw.lower() in script.lower())
    js_score = sum(1 for kw in ['var ', 'let ', 'const ', 'eval(', 'document', 'atob('] if kw in script.lower())

    scores = [("powershell", ps_score), ("vba", vba_score), ("javascript", js_score)]
    best = max(scores, key=lambda x: x[1])
    if best[1] > 0:
        return best[0]
    return "unknown"


def static_deobfuscate(script, lang):
    engine = STATIC_ENGINES.get(lang)
    if not engine:
        return script, ["No static engine for language: {}".format(lang)]
    return engine.deobfuscate(script)


def analyze(script, lang=None, full=False):
    lang = detect_language(script, hint=lang)
    if lang == "unknown":
        return {"language": "unknown", "error": "Could not detect language"}

    deobfuscated, steps = static_deobfuscate(script, lang)

    result = {
        "language": lang,
        "static_steps": steps,
        "deobfuscated": deobfuscated,
    }

    return result
