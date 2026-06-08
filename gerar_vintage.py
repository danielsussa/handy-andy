#!/usr/bin/env python3
"""Coloriza imagem com paleta vintage — usar em combinação com overlay
do original em blend multiply pra preservar traço de lápis."""
from __future__ import annotations

import base64
import sys
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
ENV = dotenv_values(ROOT / ".env")
API_KEY = ENV.get("OPENAPI_KEY") or ENV.get("OPENAI_API_KEY")
if not API_KEY:
    sys.exit("Falta OPENAPI_KEY no .env")

client = OpenAI(api_key=API_KEY)

PROMPT = (
    "Apply subtle vintage colorization to this pencil drawing while keeping "
    "the EXACT same composition, same subject, same scene, same lines, same "
    "shading. "
    "Color palette: faded earth tones — dusty olive greens, muted ochres and "
    "browns, washed-out sepia tints, soft warm grays, hint of dusty teal in "
    "shadows. Like a hand-tinted 1940s photograph or a vintage children's "
    "encyclopedia illustration. "
    "Low saturation throughout. The vehicle gets its plausible faded color "
    "(military olive drab for tanks, muted browns/greens for trucks, faded "
    "white/red for civilian vehicles, etc). Sky has a soft warm cream-blue "
    "wash, ground has dusty olive-tan. "
    "Preserve ALL pencil lines and shading texture EXACTLY — color is just a "
    "subtle wash on top. No bright saturated colors, no cartoon flatness, "
    "no oversaturation. "
    "No text, no borders, no frame."
)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Uso: gerar_vintage.py <input.png>")
    input_path = Path(sys.argv[1])
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    out_dir = ROOT / "imagens" / "vintage"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"{input_path.stem}.png"

    print(f"→ {input_path.name}")
    with input_path.open("rb") as f:
        resp = client.images.edit(
            model="gpt-image-1",
            image=f,
            prompt=PROMPT,
            size="1536x1024",
            quality="high",
            n=1,
        )
    b64 = resp.data[0].b64_json
    if not b64:
        sys.exit("Sem b64_json")
    output_path.write_bytes(base64.b64decode(b64))
    print(f"✓ {output_path} ({output_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
