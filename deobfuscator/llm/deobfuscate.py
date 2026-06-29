import json
import os
import sys

LLM_AVAILABLE = False

try:
    from openai import OpenAI
    LLM_AVAILABLE = True
except ImportError:
    pass

SYSTEM_PROMPTS = {
    "powershell": """You are a malware analysis expert specializing in PowerShell deobfuscation.
Given an obfuscated PowerShell script, return ONLY a JSON object with:
- "deobfuscated": the fully deobfuscated script (readable, variable names cleaned up, logic preserved)
- "techniques": list of obfuscation techniques you identified
- "summary": brief explanation of what the script does

Do NOT execute any code. Do NOT include anything outside the JSON.""",

    "vba": """You are a malware analysis expert specializing in VBA macro deobfuscation.
Given an obfuscated VBA macro, return ONLY a JSON object with:
- "deobfuscated": the fully deobfuscated macro (cleaned, readable)
- "techniques": list of obfuscation techniques you identified
- "summary": brief explanation of what the macro does

Do NOT execute any code. Do NOT include anything outside the JSON.""",

    "javascript": """You are a malware analysis expert specializing in JavaScript deobfuscation.
Given an obfuscated JavaScript, return ONLY a JSON object with:
- "deobfuscated": the fully deobfuscated script (cleaned, readable)
- "techniques": list of obfuscation techniques you identified
- "summary": brief explanation of what the script does

Do NOT execute any code. Do NOT include anything outside the JSON.""",
}


def deobfuscate_with_llm(script, lang, api_key=None, model="gpt-4o-mini", base_url=None):
    if not LLM_AVAILABLE:
        return None, "openai library not installed. Run: pip install openai"

    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None, "No API key found. Set OPENAI_API_KEY or pass --api-key"

    client = OpenAI(api_key=api_key, base_url=base_url)
    prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["powershell"])

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Deobfuscate this {lang} script:\n\n```{lang}\n{script}\n```"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content
        data = json.loads(content)
        return data, None
    except Exception as e:
        return None, str(e)
