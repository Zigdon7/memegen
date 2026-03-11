"""Memegen — A modern meme generation API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .config import settings
from .models.template import TemplateRegistry
from .routes import images, templates

app = FastAPI(
    title="Memegen API",
    description="A modern, clean meme generation API inspired by jacebrowning/memegen",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(templates.router)
app.include_router(images.router)


@app.on_event("startup")
async def startup():
    app.state.registry = TemplateRegistry(settings.templates_dir)
    count = len(app.state.registry.list_all())
    print(f"Loaded {count} templates from {settings.templates_dir}")


@app.get("/")
async def root():
    """Redirect to API docs."""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health():
    """Health check endpoint."""
    count = len(app.state.registry.list_all())
    return {"status": "ok", "templates": count}
