"""Template listing and detail endpoints."""

from fastapi import APIRouter, HTTPException, Request

from ..models.template import TemplateRegistry

router = APIRouter(prefix="/templates", tags=["templates"])


def get_registry(request: Request) -> TemplateRegistry:
    return request.app.state.registry


@router.get("")
async def list_templates(request: Request):
    """List all available meme templates."""
    registry = get_registry(request)
    base = str(request.base_url).rstrip("/")
    return [
        {
            "id": t.id,
            "name": t.name,
            "keywords": t.keywords,
            "example": t.example,
            "zones": len(t.text),
            "url": f"{base}/templates/{t.id}",
        }
        for t in registry.list_all()
    ]


@router.get("/{template_id}")
async def get_template(request: Request, template_id: str):
    """Get details for a specific template."""
    registry = get_registry(request)
    t = registry.get(template_id)
    if not t:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    base = str(request.base_url).rstrip("/")
    from ..utils.text import encode_text

    example_parts = "/".join(encode_text(e) for e in t.example)
    return {
        "id": t.id,
        "name": t.name,
        "keywords": t.keywords,
        "example": t.example,
        "aliases": t.aliases,
        "text_zones": [z.model_dump() for z in t.text],
        "example_url": f"{base}/images/{t.id}/{example_parts}.jpg",
    }


@router.post("/reload")
async def reload_templates(request: Request):
    """Reload all templates from disk."""
    registry = get_registry(request)
    registry.load()
    return {"status": "ok", "count": len(registry.list_all())}
