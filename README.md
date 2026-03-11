# Memegen 🎭

A modern, clean meme generation API built with **FastAPI** and **Pillow**. Inspired by [jacebrowning/memegen](https://github.com/jacebrowning/memegen) but rewritten from scratch with a simpler, more modern architecture.

## Features

- 🚀 **FastAPI** with auto-generated OpenAPI docs
- 🖼️ **20 built-in templates** with properly configured text zones
- 📐 **Smart text rendering** — auto-sizing, word wrap, stroke outlines
- 🔗 **Stateless URL-based generation** — shareable meme URLs
- 📮 **JSON API** — POST endpoint for programmatic use
- 🎨 **Multiple formats** — JPG, PNG, WebP output
- 🐳 **Docker ready** — single command deployment
- ⚡ **Template hot-reload** — add templates without restart

## Quick Start

```bash
# Install dependencies
uv pip install fastapi uvicorn pillow pyyaml pydantic pydantic-settings

# Run the server
uvicorn app.main:app --reload

# Open http://localhost:8000/docs for interactive API docs
```

### Docker

```bash
docker compose up -d
# API available at http://localhost:8000
```

## API Usage

### Generate a meme via URL

```bash
# Simple top/bottom text
curl -o meme.jpg http://localhost:8000/images/drake/Old_code/New_code.jpg

# With special characters: _ = space, ~q = ?, ~n = newline, ~h = #
curl -o meme.jpg http://localhost:8000/images/roll-safe/Can't_fail/If_you_don't_try.jpg

# Resize
curl -o meme.jpg "http://localhost:8000/images/drake/Hello/World.jpg?width=800"

# PNG format
curl -o meme.png http://localhost:8000/images/fine/_/This_is_fine.png
```

### Generate via POST

```bash
curl -X POST http://localhost:8000/images \
  -H "Content-Type: application/json" \
  -d '{"template": "evil-kermit", "text": ["Be productive", "Watch Netflix"]}' \
  -o meme.jpg
```

### List templates

```bash
curl http://localhost:8000/templates
```

### Template details

```bash
curl http://localhost:8000/templates/drake
```

### Health check

```bash
curl http://localhost:8000/health
```

## CLI

```bash
# Generate a meme
python -m app.cli generate evil-kermit "Be good" "Be evil" -o output.jpg

# List templates
python -m app.cli list
```

## Text Encoding

For URL-based generation, text is encoded in path segments:

| Character | Encoding |
|-----------|----------|
| Space     | `_`      |
| `?`       | `~q`     |
| `%`       | `~p`     |
| `#`       | `~h`     |
| `/`       | `~s`     |
| `"`       | `''`     |
| Newline   | `~n`     |

## Built-in Templates

| Template | Name | Zones |
|----------|------|-------|
| `drake` | Drakeposting | 2 |
| `buzz` | X, X Everywhere | 2 |
| `evil-kermit` | Evil Kermit | 2 |
| `distracted` | Distracted Boyfriend | 3 |
| `change-my-mind` | Change My Mind | 2 |
| `two-buttons` | Two Buttons | 2 |
| `expanding-brain` | Expanding Brain | 4 |
| `is-this` | Is This a Pigeon? | 3 |
| `always-has-been` | Always Has Been | 2 |
| `stonks` | Stonks | 2 |
| `uno-reverse` | UNO Draw 25 | 2 |
| `bernie` | Bernie Sanders Asking | 2 |
| `disaster-girl` | Disaster Girl | 2 |
| `fine` | This Is Fine | 2 |
| `batman-slap` | Batman Slapping Robin | 2 |
| `left-exit` | Left Exit 12 Off Ramp | 3 |
| `woman-yelling` | Woman Yelling at Cat | 2 |
| `surprised-pikachu` | Surprised Pikachu | 2 |
| `roll-safe` | Roll Safe Think About It | 2 |
| `think-about-it` | Think About It | 2 |

## Adding Custom Templates

1. Create a directory under `templates/` with your template ID:
   ```
   templates/my-template/
   ├── config.yml
   └── default.jpg
   ```

2. Write `config.yml`:
   ```yaml
   name: My Custom Template
   keywords: [custom, funny]
   example: ["Top text", "Bottom text"]
   text:
     - anchor_x: 0.0
       anchor_y: 0.0
       scale_x: 1.0
       scale_y: 0.2
       alignment: center
       color: white
       stroke_color: black
       stroke_width: 3
       style: upper
       max_font_size: 60
     - anchor_x: 0.0
       anchor_y: 0.8
       scale_x: 1.0
       scale_y: 0.2
       alignment: center
       color: white
       stroke_color: black
       stroke_width: 3
       style: upper
       max_font_size: 60
   ```

3. Add your source image as `default.jpg` (or `.png`/`.webp`)

4. Reload templates: `POST /templates/reload`

### Text Zone Configuration

| Field | Description | Default |
|-------|-------------|---------|
| `anchor_x` | X position (0.0 = left, 1.0 = right) | 0.0 |
| `anchor_y` | Y position (0.0 = top, 1.0 = bottom) | 0.0 |
| `scale_x` | Width as fraction of image width | 1.0 |
| `scale_y` | Height as fraction of image height | 0.2 |
| `alignment` | Text alignment: left, center, right | center |
| `font` | Font name (impact) | impact |
| `color` | Text color | white |
| `stroke_color` | Outline color | black |
| `stroke_width` | Outline width in pixels | 3 |
| `style` | Text transform: upper, lower, none | upper |
| `max_font_size` | Maximum font size in pixels | 80 |

## Self-Hosting

### Requirements
- Python 3.11+
- Pillow (for image rendering)

### Production Deployment

```bash
# With Docker
docker compose up -d

# Or with uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Behind nginx, add proxy headers
uvicorn app.main:app --host 127.0.0.1 --port 8000 --proxy-headers --forwarded-allow-ips="*"
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MEMEGEN_DEBUG` | Enable debug mode | `false` |
| `MEMEGEN_HOST` | Bind host | `0.0.0.0` |
| `MEMEGEN_PORT` | Bind port | `8000` |

## License

MIT
