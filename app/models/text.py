"""Text zone model for meme templates."""

from pydantic import BaseModel, Field


class TextZone(BaseModel):
    """Defines a region on a template where text is rendered."""

    anchor_x: float = 0.0
    anchor_y: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 0.2
    alignment: str = Field(default="center", pattern="^(left|center|right)$")
    font: str = "impact"
    color: str = "white"
    stroke_color: str = "black"
    stroke_width: int = 3
    style: str = Field(default="upper", pattern="^(upper|lower|none)$")
    max_font_size: int = 80

    def get_anchor(self, image_width: int, image_height: int) -> tuple[int, int]:
        return int(image_width * self.anchor_x), int(image_height * self.anchor_y)

    def get_size(self, image_width: int, image_height: int) -> tuple[int, int]:
        return int(image_width * self.scale_x), int(image_height * self.scale_y)

    def apply_style(self, text: str) -> str:
        if self.style == "upper":
            return text.upper()
        elif self.style == "lower":
            return text.lower()
        return text
