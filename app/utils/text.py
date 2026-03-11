"""Text encoding/decoding utilities for meme URLs."""

# URL text encoding (jacebrowning compatible):
# _ = space, ~q = ?, ~p = %, ~n = newline, ~h = #, '' = "
ENCODE_MAP = {
    "?": "~q",
    "%": "~p",
    "#": "~h",
    "/": "~s",
    '"': "''",
    "\n": "~n",
}
DECODE_MAP = {v: k for k, v in ENCODE_MAP.items()}


def decode_text(text: str) -> str:
    """Decode URL-encoded meme text."""
    if not text:
        return ""
    # Replace underscores with spaces
    text = text.replace("_", " ")
    # Decode special sequences
    for encoded, decoded in DECODE_MAP.items():
        text = text.replace(encoded, decoded)
    # Handle dash as empty line marker
    if text.strip() == "-":
        return ""
    return text.strip()


def encode_text(text: str) -> str:
    """Encode text for use in meme URLs."""
    if not text:
        return "_"
    for char, encoded in ENCODE_MAP.items():
        text = text.replace(char, encoded)
    text = text.replace(" ", "_")
    return text
