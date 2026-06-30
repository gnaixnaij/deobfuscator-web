<div align="center">
  <h1>🛡️ Deobfuscator Web</h1>
  <p><strong>Paste obfuscated PowerShell, VBA, or JavaScript → get clean readable code + IOCs + detection rules</strong></p>

  <a href="https://deobfuscator-web.onrender.com/">
    <img src="https://img.shields.io/badge/LIVE-deobfuscator--web.onrender.com-58a6ff?style=for-the-badge" alt="Live Site">
  </a>
  <a href="https://ko-fi.com/gnaixnaij">
    <img src="https://img.shields.io/badge/Sponsor-Ko--fi-FF5E5B?style=for-the-badge&logo=ko-fi" alt="Sponsor">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
  </a>
  <a href="https://github.com/gnaixnaij/deobfuscator-web/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/gnaixnaij/deobfuscator-web/lint.yml?branch=main&label=CI&logo=github&style=for-the-badge" alt="CI">
  </a>
</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔓 **Deobfuscate** | Strip layers from PowerShell, VBA, and JavaScript |
| 🔍 **IOC Extraction** | Automatically extract IPs, domains, URLs, hashes, registry keys |
| 🎯 **Sigma Rules** | Ready-to-paste SIEM detection rules |
| 📄 **YARA Rules** | File scanning rules from extracted IOCs |
| 📦 **Batch Upload** | Up to 20 files at once for triage |
| 🧠 **LLM Mode** | Optional OpenAI integration for deeper analysis |

## 🚀 Try it now

👉 **https://deobfuscator-web.onrender.com** 👈

## 🖥 Run locally

### Python

```bash
git clone git@github.com:gnaixnaij/deobfuscator-web.git
cd deobfuscator-web
pip install -r requirements.txt
cp .env.example .env  # Edit with your OpenAI key (optional)
python app.py
# Open http://localhost:5000
```

### Docker

```bash
docker build -t deobfuscator-web .
docker run -p 5000:5000 -e OPENAI_API_KEY=sk-... deobfuscator-web
# Open http://localhost:5000
```

## 🤝 Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome — especially new deobfuscation techniques.

## ⚠️ Disclaimer

This tool is for authorized security testing and education only. See [DISCLAIMER.md](DISCLAIMER.md).

## ☕ Support

If this saves you time in your work, [buy me a coffee](https://ko-fi.com/gnaixnaij). It keeps the project improving.
