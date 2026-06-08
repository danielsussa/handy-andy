#!/usr/bin/env python3
"""Variante square (1:1) do outpainting — gera 1024x1024."""
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

CANVAS_W = CANVAS_H = 1024  # square

PROMPT = (
    "Extend this pencil drawing scene to fill a square frame. The vehicle in "
    "the center stays EXACTLY as it is — do not redraw, recolor, or modify it. "
    "Fill ONLY the empty top and bottom strips with a complementary pencil "
    "drawing background that continues the same scene seamlessly: "
    "above the vehicle, draw sky with light pencil clouds and atmospheric "
    "perspective; below the vehicle, extend the ground (terrain, road, "
    "shadow) into the foreground. "
    "Style: realistic graphite pencil on white paper, light gray shading "
    "(10-30% gray), visible pencil strokes. Match the exact line weight and "
    "shading density of the original drawing. "
    "No text, no borders, no frame. White paper background preserved where "
    "appropriate."
)


def composite(input_path: Path) -> tuple[Path, Path]:
    src = Image.open(input_path).convert("RGB")
    sw, sh = src.size
    scale = CANVAS_W / sw
    new_w = CANVAS_W
    new_h = int(sh * scale)
    if new_h > CANVAS_H:
        scale = CANVAS_H / sh
        new_w = int(sw * scale)
        new_h = CANVAS_H
    src = src.resize((new_w, new_h), Image.LANCZOS)
    off_x = (CANVAS_W - new_w) // 2
    off_y = (CANVAS_H - new_h) // 2

    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (255, 255, 255))
    canvas.paste(src, (off_x, off_y))
    mask = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    keep = Image.new("RGBA", (new_w, new_h), (255, 255, 255, 255))
    mask.paste(keep, (off_x, off_y))

    tmp = ROOT / ".tmp_outpaint"
    tmp.mkdir(exist_ok=True)
    canvas_path = tmp / f"{input_path.stem}_sq_canvas.png"
    mask_path = tmp / f"{input_path.stem}_sq_mask.png"
    canvas.save(canvas_path)
    mask.save(mask_path)
    return canvas_path, mask_path


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Uso: python gerar_outpaint_square.py <input.jpg>")
    input_path = Path(sys.argv[1])
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    out_dir = ROOT / "imagens" / "outpainted-square"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"{input_path.stem}.png"

    print(f"→ {input_path.name}")
    canvas_path, mask_path = composite(input_path)
    with canvas_path.open("rb") as img, mask_path.open("rb") as msk:
        resp = client.images.edit(
            model="gpt-image-1",
            image=img,
            mask=msk,
            prompt=PROMPT,
            size="1024x1024",
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
