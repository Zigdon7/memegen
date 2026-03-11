"""Template model and registry loader."""

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field

from .text import TextZone


class Template(BaseModel):
    """A meme template with metadata and text zones."""

    id: str
    name: str = ""
    keywords: list[str] = Field(default_factory=list)
    source: str = ""
    text: list[TextZone] = Field(
        default_factory=lambda: [
            TextZone(anchor_x=0.0, anchor_y=0.0),
            TextZone(anchor_x=0.0, anchor_y=0.8),
        ]
    )
    example: list[str] = Field(default_factory=lambda: ["Top text", "Bottom text"])
    aliases: list[str] = Field(default_factory=list)
    image_path: Optional[str] = None

    def get_image_path(self, templates_dir: Path) -> Path:
        d = templates_dir / self.id
        if self.image_path:
            return d / self.image_path
        for ext in ("jpg", "jpeg", "png", "webp"):
            p = d / f"default.{ext}"
            if p.exists():
                return p
        return d / "default.jpg"


class TemplateRegistry:
    """Loads and caches templates from the templates directory."""

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self._templates: dict[str, Template] = {}
        self._aliases: dict[str, str] = {}
        self.load()

    def load(self):
        self._templates.clear()
        self._aliases.clear()
        if not self.templates_dir.exists():
            return
        for config_path in sorted(self.templates_dir.glob("*/config.yml")):
            template_id = config_path.parent.name
            try:
                data = yaml.safe_load(config_path.read_text()) or {}
                data["id"] = template_id
                # Convert text zone dicts
                if "text" in data:
                    data["text"] = [
                        TextZone(**z) if isinstance(z, dict) else z
                        for z in data["text"]
                    ]
                template = Template(**data)
                self._templates[template_id] = template
                for alias in template.aliases:
                    self._aliases[alias] = template_id
            except Exception as e:
                print(f"Warning: Failed to load template {template_id}: {e}")

    def get(self, template_id: str) -> Optional[Template]:
        if template_id in self._templates:
            return self._templates[template_id]
        real_id = self._aliases.get(template_id)
        if real_id:
            return self._templates.get(real_id)
        return None

    def list_all(self) -> list[Template]:
        return sorted(self._templates.values(), key=lambda t: t.id)
