#!/usr/bin/env python3
"""Gera versão SÓ COR — sem linhas, sem hatching, sem detalhes de lápis —
pra usar como base do overlay multiply. O original grayscale entra em
cima e traz todas as linhas, então a IA só precisa preencher as cores."""
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
    "Convert this pencil drawing into a FLAT COLORED illustration with the "
    "SAME composition. CRITICAL: produce ONLY soft color regions — "
    "ABSOLUTELY NO pencil lines, NO outlines, NO hatching, NO line drawings, "
    "NO edges, NO contours, NO pencil texture, NO shading lines. "
    "Each region of the image must be a single SMOOTH WASH of color, with "
    "soft transitions between regions (like watercolor blending). "
    "Vintage 1940s palette — desaturated, muted, faded: "
    "- The vehicle: faded military olive drab (greenish-brown). "
    "- The sky area: soft warm cream with hint of dusty blue. "
    "- The ground area: dusty olive-tan, warm earth tones. "
    "- Shadows: muted brown-gray washes. "
    "Think: a flat-color paint-by-numbers WITHOUT the black outlines. Or a "
    "soft watercolor underpainting with no ink on top. Or a vintage 1940s "
    "tinted photograph where the colors are smooth tints with no detail. "
    "Compose the regions to match the original drawing's layout exactly — "
    "vehicle silhouette in the same place, same proportions, same shapes — "
    "but as SOLID smooth colored shapes, NOT as drawn lines. "
    "No text, no watermark, no borders, no frame."
)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Uso: gerar_color_only.py <input.png>")
    input_path = Path(sys.argv[1])
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    out_dir = ROOT / "imagens" / "color-only"
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
