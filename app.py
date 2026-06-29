import os

from flask import Flask, render_template, request, jsonify
from deobfuscator.core import analyze, detect_language
from deobfuscator.llm.deobfuscate import deobfuscate_with_llm
from ioc.extract import extract_iocs
from ioc.sigma import generate_sigma
from ioc.yara import generate_yara

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20MB for batch

LANG_MAP = {
    "powershell": "powershell",
    "vba": "vba",
    "javascript": "javascript",
    "ps1": "powershell",
    "bas": "vba",
    "vbs": "vba",
    "js": "javascript",
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/detect", methods=["POST"])
def detect():
    data = request.get_json()
    script = data.get("script", "")
    lang = detect_language(script)
    return jsonify({"language": lang})

@app.route("/api/deobfuscate", methods=["POST"])
def deobfuscate():
    script = request.form.get("script", "")
    lang = request.form.get("lang", "")
    use_llm = request.form.get("use_llm", "false") == "true"

    if not script.strip():
        return jsonify({"error": "No script provided"}), 400

    if lang and lang in LANG_MAP:
        lang = LANG_MAP[lang]
    else:
        lang = detect_language(script)

    if lang == "unknown":
        return jsonify({"error": "Could not detect language. Try specifying it manually."}), 400

    result = analyze(script, lang=lang)

    response = {
        "language": lang,
        "static_steps": result.get("static_steps", []),
        "deobfuscated": result.get("deobfuscated", ""),
        "changed": result.get("deobfuscated", "").strip() != script.strip(),
    }

    if use_llm:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            response["llm_error"] = "OPENAI_API_KEY not set on the server"
        else:
            llm_result, llm_error = deobfuscate_with_llm(script, lang, api_key=api_key)
            if llm_error:
                response["llm_error"] = llm_error
            else:
                response["llm"] = llm_result

    return jsonify(response)

@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    script = f.read().decode("utf-8", errors="replace")
    ext = os.path.splitext(f.filename)[1].lstrip(".").lower()
    lang = LANG_MAP.get(ext, detect_language(script))

    if lang == "unknown":
        lang = "powershell"

    result = analyze(script, lang=lang)

    return jsonify({
        "language": lang,
        "filename": f.filename,
        "static_steps": result.get("static_steps", []),
        "deobfuscated": result.get("deobfuscated", ""),
        "changed": result.get("deobfuscated", "").strip() != script.strip(),
    })

@app.route("/api/analyze-iocs", methods=["POST"])
def analyze_iocs():
    data = request.get_json()
    script = data.get("script", "")
    if not script.strip():
        return jsonify({"error": "No script provided"}), 400

    iocs = extract_iocs(script)
    sigma_rules = generate_sigma(iocs)
    yara_rule = generate_yara(iocs)

    has_iocs = any(v for k, v in iocs.items() if k != "base64_strings" for v in (v if isinstance(v, list) else v.values()))

    return jsonify({
        "iocs": iocs,
        "has_iocs": bool(has_iocs),
        "sigma_rules": [{"title": t, "rule": r} for t, r in sigma_rules],
        "yara_rule": yara_rule,
    })


@app.route("/api/analyze-batch", methods=["POST"])
def analyze_batch():
    if "files" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist("files")
    if not files or all(f.filename == "" for f in files):
        return jsonify({"error": "No files selected"}), 400

    results = []
    for f in files[:20]:
        if f.filename == "":
            continue
        try:
            script = f.read().decode("utf-8", errors="replace")
        except Exception:
            results.append({"filename": f.filename, "error": "Could not read file"})
            continue

        if not script.strip():
            results.append({"filename": f.filename, "error": "Empty file"})
            continue

        ext = os.path.splitext(f.filename)[1].lstrip(".").lower()
        lang = LANG_MAP.get(ext, detect_language(script))
        if lang == "unknown":
            lang = "powershell"

        deobf_result = analyze(script, lang=lang)
        deobfuscated = deobf_result.get("deobfuscated", "")
        changed = deobfuscated.strip() != script.strip()

        iocs = extract_iocs(deobfuscated or script)
        ioc_count = sum(
            len(v) if isinstance(v, list) else sum(v.values()) if isinstance(v, dict) else 0
            for v in iocs.values()
        )

        results.append({
            "filename": f.filename,
            "language": lang,
            "size": len(script),
            "deobfuscated": deobfuscated[:500] if deobfuscated else "",
            "changed": changed,
            "ioc_count": ioc_count,
            "error": None,
        })

    return jsonify({"results": results, "total": len(results)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
