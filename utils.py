
import re
from typing import Dict, List

def _split_sentences(text: str) -> List[str]:
    # naive but robust sentence splitter
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]

def _truncate(s: str, max_len: int) -> str:
    return (s[: max_len - 1] + "…") if len(s) > max_len else s

def _mk_title(paragraph: str) -> str:
    sents = _split_sentences(paragraph)
    if not sents:
        return "Slide"
    # short, punchy title
    return _truncate(sents[0], 80)

def _mk_bullets(paragraph: str) -> List[str]:
    # Try markdown bullets
    bullets = []
    for line in paragraph.splitlines():
        if re.match(r'^\s*[-*+]\s+', line):
            bullets.append(re.sub(r'^\s*[-*+]\s+', '', line).strip())
    if bullets:
        return bullets[:6]
    # Else split sentences
    sents = _split_sentences(paragraph)
    if len(sents) <= 1:
        return [paragraph.strip()]
    return [s.strip() for s in sents[:6]]

def _split_by_headings(text: str) -> List[str]:
    # Split on markdown ATX headings, keep content under each
    chunks = re.split(r'(?m)^#{1,6}\s+', text.strip())
    return [c.strip() for c in chunks if c.strip()]

def _split_by_paragraphs(text: str) -> List[str]:
    parts = re.split(r'\n\s*\n+', text.strip())
    return [p.strip() for p in parts if p.strip()]

def fallback_plan_from_text(text: str, guidance: str, gen_notes: bool = False) -> Dict:
    slides = []
    blocks = _split_by_headings(text)
    if not blocks:
        blocks = _split_by_paragraphs(text)
    # clamp rough number of slides 6-12
    if len(blocks) < 6:
        # try to further split by sentences to reach up to 6
        paragraphs = _split_by_paragraphs(text)
        if paragraphs:
            while len(blocks) < min(6, len(paragraphs)):
                blocks.extend(paragraphs[len(blocks):len(blocks)+1])
    blocks = blocks[:20]  # hard cap

    for b in blocks:
        title = _mk_title(b)
        bullets = _mk_bullets(b)
        notes = None
        if gen_notes:
            notes = f"Key talking points for: {title}"
        slides.append({"title": title, "bullets": bullets, "notes": notes})

    return {"slides": slides}

def clamp_slides(slides: List[Dict], max_slides: int = 20) -> List[Dict]:
    return slides[:max_slides]
