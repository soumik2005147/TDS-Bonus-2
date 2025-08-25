# Auto PPT Generator

A tiny web app that turns bulk text/markdown into a PowerPoint presentation **styled like a user-uploaded PPTX/POTX template**. Users can (optionally) bring an LLM API key to help split the text into a better slide structure. Keys are **not stored or logged**.

> Built to match your college task brief: accept text + guidance + user-supplied LLM key + PPT template and output a new `.pptx` that follows the template’s look & feel (colors, fonts, images) without generating new images. fileciteturn2file0

---

## Features
- Paste text / markdown
- Optional one-line guidance (e.g. “investor pitch”)
- Select LLM provider (OpenAI / Anthropic / Gemini) or “No LLM (rule-based)"
- Paste your **own** API key (used only for this request)
- Upload `.pptx` / `.potx` template
- Download generated `.pptx`
- (Optional) Generate speaker notes

## Local run
```bash
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
# open http://127.0.0.1:8000
```

## Deploy on Render (Free)
1. Push this repo to GitHub (public).
2. In Render: **New + → Web Service → Build from a repo** → select your repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. After deploy → open the URL and test.
   - No server env vars needed. Users paste their keys per request.
6. (If using GitHub Pages as a separate frontend, enable CORS in `app.py`.)

## Short write-up (≈250 words)
The app converts long-form text into a slide plan using either an LLM or a deterministic fallback. When an LLM key is provided, the server calls the selected provider (OpenAI/Anthropic/Gemini) with a constrained prompt to return **strict JSON** describing slides: each with a title, bullet list, and optional speaker notes. If no key is supplied, a compact rule-based algorithm splits the text into sections: it tries markdown headings first; if none are present, it segments by blank lines and sentence boundaries, assigns a concise title from the first sentence, and trims to 3–6 bullets per slide. The resulting plan is then rendered via `python-pptx` using the **uploaded file as the template** (`Presentation(template_path)`), ensuring master themes, fonts, colors, and layout placeholders are inherited automatically. Slides are created with a “Title and Content” layout when available, falling back to the first layout otherwise. Bullet paragraphs are inserted directly into the body placeholder, and speaker notes are added to each slide if present. Because generation starts from the user’s template, reusable assets (e.g., logos on the master) naturally appear. The app deliberately avoids any AI image creation and never stores sensitive inputs like API keys. It offers basic validation (file type and size) and returns a downloadable `.pptx`. The design emphasizes clarity over perfection: perfect layout inference isn’t required; the focus is on matching style, sensible slide counts, and a clean, reproducible pipeline from text to deck. fileciteturn2file0

## Notes / Limits
- Template limit defaults to 15 MB; adjust in `app.py` if needed.
- If your provider/model is slow or blocked, use the **No LLM** fallback.
- We do **not** generate images with AI.
- API keys are not stored or printed in logs.
