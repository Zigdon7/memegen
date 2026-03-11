"""Image generation endpoints."""

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

from ..models.template import TemplateRegistry
from ..utils.images import render_meme
from ..utils.text import decode_text

router = APIRouter(tags=["images"])

MIME_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}


def get_registry(request: Request) -> TemplateRegistry:
    return request.app.state.registry


@router.get("/images/{template_id}/{texts_and_ext:path}")
async def generate_meme_url(
    request: Request,
    template_id: str,
    texts_and_ext: str,
    width: int = Query(0, ge=0, le=2048),
    height: int = Query(0, ge=0, le=2048),
    font: str = Query(""),
):
    """Generate a meme from URL path segments.

    Example: /images/drake/top_text/bottom_text.jpg
    """
    registry = get_registry(request)
    template = registry.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

    # Parse extension from last segment
    parts = texts_and_ext.split("/")
    ext = "jpg"
    if parts and "." in parts[-1]:
        last = parts[-1]
        dot = last.rfind(".")
        ext = last[dot + 1:]
        parts[-1] = last[:dot]

    if ext not in MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {ext}")

    texts = [decode_text(p) for p in parts]

    image_bytes = render_meme(
        template, texts, width=width, height=height,
        font_override=font, output_format=ext,
    )
    return Response(content=image_bytes, media_type=MIME_TYPES[ext])


class MemeRequest(BaseModel):
    template: str
    text: list[str] = Field(default_factory=list)
    font: str = ""
    width: int = 0
    height: int = 0
    format: str = "jpg"


@router.post("/images")
async def generate_meme_post(request: Request, body: MemeRequest):
    """Generate a meme from JSON body."""
    registry = get_registry(request)
    template = registry.get(body.template)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{body.template}' not found")

    ext = body.format.lower()
    if ext not in MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {ext}")

    image_bytes = render_meme(
        template, body.text, width=body.width, height=body.height,
        font_override=body.font, output_format=ext,
    )
    return Response(content=image_bytes, media_type=MIME_TYPES[ext])
