# Deobfuscator Web

Web interface for the AI-powered script deobfuscator. Paste or upload obfuscated PowerShell, VBA, and JavaScript — get clean readable output.

## Quick start

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

## Deploy

**Render** (free):
- Connect repo → set build command `pip install -r requirements.txt` → start command `gunicorn app:app`

**PythonAnywhere** (free tier works):
- Upload files → configure as Flask app → done

## Optional

Set `OPENAI_API_KEY` env variable to enable LLM-powered deobfuscation.
