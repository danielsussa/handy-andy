#!/usr/bin/env python3
"""Gerar páginas do livro do Gui via gpt-image-1.

Lê uma imagem-base (estilo lápis realista, do Pinterest), pede pro gpt-image-1
adicionar um fundo de cena complementar e uniformizar o estilo pra ficar
coerente com o resto do livro.

Uso:
    python gerar.py <input.jpg> [output.png]
"""
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
    sys.exit("Falta OPENAPI_KEY ou OPENAI_API_KEY no .env")

client = OpenAI(api_key=API_KEY)

STYLE_PROMPT = (
    "Take this realistic pencil drawing of a vehicle and turn it into a full "
    "coloring book page for a 2-year-old child. Keep the vehicle exactly as it "
    "is — same subject, same pose, same hand-drawn realistic graphite pencil "
    "style with soft shading and visible pencil strokes. "
    "Add a complementary scene around the vehicle drawn in the EXACT same "
    "pencil style: ground/terrain appropriate to the vehicle (road, field, "
    "construction site, sky with clouds, etc.), simple background elements "
    "(distant trees, hills, buildings) drawn with light pencil shading. "
    "The whole page must feel like a single cohesive pencil drawing by one "
    "artist. Portrait orientation, A4 aspect ratio. "
    "Leave generous white/light areas for the child to color in — light "
    "shading only (10-30% gray), no heavy fills, no thick black outlines. "
    "No text, no borders, no frame, no watermark. Centered composition, "
    "vehicle as the main focal point."
)


def gerar(input_path: Path, output_path: Path) -> None:
    print(f"→ {input_path.name} ({input_path.stat().st_size // 1024} KB)")
    with input_path.open("rb") as f:
        resp = client.images.edit(
            model="gpt-image-1",
            image=f,
            prompt=STYLE_PROMPT,
            size="1024x1536",
            quality="high",
            n=1,
        )

    b64 = resp.data[0].b64_json
    if not b64:
        sys.exit("Resposta sem b64_json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(b64))
    kb = output_path.stat().st_size // 1024
    print(f"✓ {output_path} ({kb} KB)")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Uso: python gerar.py <input.jpg> [output.png]")
    input_path = Path(sys.argv[1])
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
        if not output_path.is_absolute():
            output_path = ROOT / output_path
    else:
        output_path = ROOT / "imagens" / "geradas" / f"{input_path.stem}.png"
    gerar(input_path, output_path)


if __name__ == "__main__":
    main()
