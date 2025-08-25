
import io
import json
import os
import tempfile
from typing import Optional

from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from llm_router import plan_slides_via_provider, safe_parse_json
from ppt_builder import build_ppt

APP_TITLE = "Auto PPT Generator"
MAX_TEMPLATE_SIZE = 15 * 1024 * 1024  # 15 MB

app = FastAPI(title=APP_TITLE)

# Static and templates
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": APP_TITLE})

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/generate")
async def generate_ppt(
    request: Request,
    text: str = Form(..., description="Raw text or markdown to convert"),
    guidance: Optional[str] = Form(None, description="Optional one-line guidance"),
    provider: str = Form("none", description="LLM provider: openai|anthropic|gemini|none"),
    api_key: Optional[str] = Form(None, description="User-supplied LLM key (never stored)"),
    gen_notes: Optional[bool] = Form(False, description="Generate speaker notes"),
    template: UploadFile = File(..., description=".pptx/.potx template"),
):
    # Validate template
    if not template.filename.lower().endswith(('.pptx', '.potx')):
        raise HTTPException(status_code=400, detail="Template must be a .pptx or .potx file")
    contents = await template.read()
    if len(contents) > MAX_TEMPLATE_SIZE:
        raise HTTPException(status_code=413, detail="Template file too large")

    # Write template to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(template.filename)[1]) as tf:
        tf.write(contents)
        template_path = tf.name

    # Plan slides (LLM or fallback)
    try:
        plan = await plan_slides_via_provider(
            text=text,
            guidance=guidance or "",
            provider=provider.lower(),
            api_key=(api_key or "").strip(),
            gen_notes=bool(gen_notes),
        )
    except Exception as e:
        # Never include user inputs or API keys in errors
        raise HTTPException(status_code=500, detail=f"Slide planning failed: {e}")

    if not isinstance(plan, dict) or "slides" not in plan or not plan["slides"]:
        raise HTTPException(status_code=500, detail="Invalid slide plan returned")

    # Build PPT
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as out:
            output_path = out.name
        build_ppt(template_path=template_path, slides=plan["slides"], output_path=output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PowerPoint build failed: {e}")
    finally:
        # Clean up template file
        try:
            os.unlink(template_path)
        except Exception:
            pass

    filename = "generated_presentation.pptx"
    return FileResponse(output_path, filename=filename, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
