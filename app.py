import os
import sys
import tempfile

from flask import Flask, render_template, request, jsonify

sys.path.insert(0, os.path.expanduser("~/ai-deobfuscator"))
from deobfuscator.core import analyze, detect_language
from deobfuscator.llm.deobfuscate import deobfuscate_with_llm

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
