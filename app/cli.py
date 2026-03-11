"""Simple CLI for generating memes."""

import argparse
import sys
from pathlib import Path

# Add parent to path so we can import app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.models.template import TemplateRegistry
from app.utils.images import render_meme


def main():
    parser = argparse.ArgumentParser(description="Generate memes from the command line")
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Generate a meme image")
    gen.add_argument("template", help="Template ID")
    gen.add_argument("text", nargs="+", help="Text lines for each zone")
    gen.add_argument("-o", "--output", default="output.jpg", help="Output file path")
    gen.add_argument("-f", "--font", default="", help="Font override")
    gen.add_argument("--width", type=int, default=0)
    gen.add_argument("--height", type=int, default=0)
    gen.add_argument("--format", default="", help="Output format (jpg/png/webp)")

    ls = sub.add_parser("list", help="List available templates")

    args = parser.parse_args()
    registry = TemplateRegistry(settings.templates_dir)

    if args.command == "list":
        for t in registry.list_all():
            print(f"  {t.id:25s} {t.name}")
        return

    if args.command == "generate":
        template = registry.get(args.template)
        if not template:
            print(f"Error: Template '{args.template}' not found")
            sys.exit(1)
        ext = args.format or Path(args.output).suffix.lstrip(".") or "jpg"
        data = render_meme(
            template, args.text,
            width=args.width, height=args.height,
            font_override=args.font, output_format=ext,
        )
        Path(args.output).write_bytes(data)
        print(f"Saved to {args.output} ({len(data)} bytes)")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
