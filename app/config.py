from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "memegen"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    base_dir: Path = Path(__file__).resolve().parent.parent
    templates_dir: Path = base_dir / "templates"
    fonts_dir: Path = base_dir / "fonts"

    default_font: str = "impact"
    default_width: int = 0
    default_height: int = 0
    max_width: int = 2048
    max_height: int = 2048

    class Config:
        env_prefix = "MEMEGEN_"


settings = Settings()
