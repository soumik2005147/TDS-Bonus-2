# Auto PPT Generator

A tiny web app that turns bulk text/markdown into a PowerPoint presentation **styled like a user-uploaded PPTX/POTX template**. Users can (optionally) bring an LLM API key to help split the text into slides and generate speaker notes.

> Built to match your college task brief: accept text + guidance + user-supplied LLM key + PPT template and output a new `.pptx` that follows the template’s look & feel (colors, fonts, images) with slides created from your content.

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
The app converts long-form text into a slide plan using either an LLM or a deterministic fallback. When an LLM key is provided, the server calls the selected provider (OpenAI/Anthropic/Gemini) with your text and brief guidance. The response is parsed and mapped into slides, then styled using the uploaded template. If no key is given, a rule-based parser splits the input into slides using Markdown headers, delimiters, and bullet points.

---
# Slide Parsing and Template Application

## Parsing Input Text and Mapping to Slides

The app begins by accepting a structured input text, typically formatted with headings, bullet points, or explicit slide delimiters. The parsing engine scans the input, identifying key sections such as titles, subtitles, and content blocks by detecting patterns—like Markdown headers (`#`, `##`), line breaks, or special markers (e.g., `---` for slide separation). Each detected section is mapped to a slide: headings become slide titles, while subsequent lines or bullet points are assigned as body text or list items. If images or media links are present, the parser recognizes them using standard syntax (like `![Image](url)` in Markdown) and tags these for media placement. The parser ensures that each slide object contains all relevant content types: title, body, images, and additional metadata, preserving order and hierarchy from the original text.

## Applying Template Visual Style and Assets

Once slides are generated, the app applies the selected template’s visual style and assets to each slide. Templates define consistent elements such as fonts, color schemes, background graphics, and default layouts for text and images. During rendering, the app assigns fonts and colors according to template specifications, ensuring uniformity across all slides. Images and media are positioned in pre-defined areas, and transitions or animations are added as dictated by the template. Logo, watermark, and any decorative assets specified in the template are included automatically. This process ensures that every slide adheres to the chosen style, resulting in a cohesive, visually-appealing presentation that matches the template’s branding and aesthetic.

---

## Notes / Limits
- Template limit defaults to 15 MB; adjust in `app.py` if needed.
- If your provider/model is slow or blocked, use the **No LLM** fallback.
- We do **not** generate images with AI.
- API keys are not stored or printed in logs.

## License

This repository is for educational purposes.