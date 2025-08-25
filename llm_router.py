
import json
import re
from typing import Dict, List

import httpx

from utils import fallback_plan_from_text, clamp_slides

# Optional SDKs (installed via requirements). Imported lazily.
def _import_openai():
    from openai import OpenAI
    return OpenAI

def _import_anthropic():
    import anthropic
    return anthropic

def _import_gemini():
    import google.generativeai as genai
    return genai

SYSTEM_PROMPT = """You are a slide architect. Convert the given text into a JSON plan for slides.
Return ONLY valid JSON with this schema:
{
  "slides": [
    {"title": "string", "bullets": ["string", ...], "notes": "string (optional)"}
  ]
}
Bullets should be short, 3-6 per slide. At most 20 slides. Do not include code fences.
"""

def _prompt_for(text: str, guidance: str, gen_notes: bool) -> str:
    parts = [f"GUIDANCE: {guidance.strip()}" if guidance else "GUIDANCE: (none)",
             f"NOTES: {'yes' if gen_notes else 'no'}",
             "TEXT:", text.strip()]
    return "\n\n".join(parts)

async def plan_slides_via_provider(text: str, guidance: str, provider: str, api_key: str, gen_notes: bool) -> Dict:
    if provider == "none" or not api_key:
        plan = fallback_plan_from_text(text, guidance, gen_notes=gen_notes)
        return {"slides": clamp_slides(plan["slides"], max_slides=20)}

    prompt = _prompt_for(text, guidance, gen_notes)

    if provider == "openai":
        OpenAI = _import_openai()
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        content = resp.choices[0].message.content
        return _coerce_to_plan(content)

    if provider == "anthropic":
        anthropic = _import_anthropic()
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            temperature=0.2,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        # Claude returns content as a list of blocks
        content = "".join([b.text for b in msg.content if getattr(b, "type", None) == "text"])
        return _coerce_to_plan(content)

    if provider == "gemini":
        genai = _import_gemini()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content([SYSTEM_PROMPT, prompt])
        content = resp.text
        return _coerce_to_plan(content)

    # Unknown provider -> fallback
    plan = fallback_plan_from_text(text, guidance, gen_notes=gen_notes)
    return {"slides": clamp_slides(plan["slides"], max_slides=20)}

def _coerce_to_plan(raw: str) -> Dict:
    # Strip code fences if the model added them
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE)
    # Try to extract the first {...} JSON object
    m = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if m:
        cleaned = m.group(0)
    data = json.loads(cleaned)
    if "slides" not in data or not isinstance(data["slides"], list):
        raise ValueError("LLM did not return a slides array")
    return data

def safe_parse_json(s: str):
    try:
        return json.loads(s)
    except Exception:
        return None
