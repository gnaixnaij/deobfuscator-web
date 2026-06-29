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
    for line in lines[:5]:
        if line.strip().lower().startswith(('function ', 'sub ', 'end sub', 'end function', 'dim ', 'attribute ')):
            return "vba"
        if '$' in line and any(kw in line.lower() for kw in ['iex', 'invoke', 'write-host', 'get-']):
            return "powershell"
        if 'function ' in line.lower() and '{' in line:
            return "javascript"

    ps_score = sum(1 for kw in ['$', '|', '-e ', '-enc ', 'iex', 'invoke-expression'] if kw in script.lower())
    vba_score = sum(1 for kw in ['sub ', 'function ', 'dim ', 'set ', 'chrw', 'chrd'] if kw.lower() in script.lower())
    js_score = sum(1 for kw in ['function(', 'var ', 'let ', 'const ', 'eval(', 'document'] if kw in script.lower())

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
