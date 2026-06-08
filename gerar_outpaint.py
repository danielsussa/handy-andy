#!/usr/bin/env python3
"""Outpainting — preserva a arte original do Pinterest e só estende o fundo
acima e abaixo até preencher A4 portrait (1024×1536).

A máscara marca a região do desenho original como OPACA (não editar) e as
faixas acima/abaixo como TRANSPARENTES (gpt-image-1 preenche essas áreas
mantendo o estilo lápis).
"""
from __future__ import annotations

import base64
import sys
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI
from PIL import Image

ROOT = Path(__file__).resolve().parent
ENV = dotenv_values(ROOT / ".env")
API_KEY = ENV.get("OPENAPI_KEY") or ENV.get("OPENAI_API_KEY")
if not API_KEY:
    sys.exit("Falta OPENAPI_KEY no .env")

client = OpenAI(api_key=API_KEY)

CANVAS_W, CANVAS_H = 1024, 1536  # A4 portrait (1024×1536) — mesma proporção 2:3

PROMPT = (
    "Extend this pencil drawing scene vertically. The vehicle in the center "
    "stays EXACTLY as it is — do not redraw, recolor, or modify it. "
    "Fill ONLY the empty top and bottom areas with a complementary pencil "
    "drawing background that continues the same scene seamlessly: "
    "above the vehicle, draw sky with light pencil clouds and atmospheric "
    "perspective; below the vehicle, extend the ground (terrain, road, "
    "shadow) into the foreground. "
    "Style: realistic graphite pencil on white paper, light gray shading "
    "(10-30% gray), visible pencil strokes, hand-drawn texture. Match the "
    "exact line weight and shading density of the original drawing. "
    "No text, no borders, no frame, no watermark. White paper background "
    "should be preserved where appropriate (do not flood with dark fills)."
)


def composite(input_path: Path) -> tuple[Path, Path]:
    """Build canvas (with original centered) + mask (transparent top/bottom)."""
    src = Image.open(input_path).convert("RGB")
    sw, sh = src.size
    # Scale source to fit canvas width
    scale = CANVAS_W / sw
    new_w = CANVAS_W
    new_h = int(sh * scale)
    if new_h > CANVAS_H:
        # Source already taller than canvas — scale to fit height instead
        scale = CANVAS_H / sh
        new_w = int(sw * scale)
        new_h = CANVAS_H
    src = src.resize((new_w, new_h), Image.LANCZOS)
    off_x = (CANVAS_W - new_w) // 2
    off_y = (CANVAS_H - new_h) // 2

    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (255, 255, 255))
    canvas.paste(src, (off_x, off_y))

    # Mask: RGBA. Opaque (alpha=255) where the original sits = preserve.
    # Transparent (alpha=0) where we want gpt-image-1 to paint = edit.
    mask = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    keep = Image.new("RGBA", (new_w, new_h), (255, 255, 255, 255))
    mask.paste(keep, (off_x, off_y))

    tmp = ROOT / ".tmp_outpaint"
    tmp.mkdir(exist_ok=True)
    canvas_path = tmp / f"{input_path.stem}_canvas.png"
    mask_path = tmp / f"{input_path.stem}_mask.png"
    canvas.save(canvas_path)
    mask.save(mask_path)
    return canvas_path, mask_path


def outpaint(input_path: Path, output_path: Path) -> None:
    print(f"→ {input_path.name}")
    canvas_path, mask_path = composite(input_path)
    with canvas_path.open("rb") as img, mask_path.open("rb") as msk:
        resp = client.images.edit(
            model="gpt-image-1",
            image=img,
            mask=msk,
            prompt=PROMPT,
            size="1024x1536",
            quality="high",
            n=1,
        )
    b64 = resp.data[0].b64_json
    if not b64:
        sys.exit("Sem b64_json na resposta")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(b64))
    print(f"✓ {output_path} ({output_path.stat().st_size // 1024} KB)")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Uso: python gerar_outpaint.py <input.jpg>")
    input_path = Path(sys.argv[1])
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    output_path = ROOT / "imagens" / "outpainted" / f"{input_path.stem}.png"
    outpaint(input_path, output_path)


if __name__ == "__main__":
    main()
