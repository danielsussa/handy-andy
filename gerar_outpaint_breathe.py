#!/usr/bin/env python3
"""Outpaint landscape 1.5:1 com 'respiro' garantido no canto superior-esquerdo.

O source é posicionado no canto INFERIOR-DIREITO do canvas (com 5% de margem)
e escalado pra que sobre uma 'safe zone' de ~38% × 38% no canto TL pra texto.
A AI preenche todo o entorno (top, left, plus margens right/bottom) com fundo
a lápis no mesmo estilo.

Resultado: layout padronizado em todas as páginas, texto sempre TL, sem cobrir
veículo nenhum."""
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

import os as _os
CANVAS_W, CANVAS_H = 1536, 1024  # 1.5:1
# Defaults: 18% × 15% safe zone (veículo ~79% do canvas)
# Override via env: BREATHE_SAFE_W=0.08 → veículo bem maior
SAFE_W_PCT = float(_os.environ.get("BREATHE_SAFE_W", "0.18"))
SAFE_H_PCT = float(_os.environ.get("BREATHE_SAFE_H", "0.15"))
MARGIN_PCT = float(_os.environ.get("BREATHE_MARGIN", "0.03"))

PROMPT = (
    "Extend this pencil drawing scene to fill the full frame. The vehicle in "
    "the bottom-right area stays EXACTLY as it is — do not redraw, recolor, "
    "or modify it. "
    "Fill the empty TOP and LEFT areas (the L-shaped region around the "
    "vehicle) with a complementary pencil drawing background that continues "
    "the scene seamlessly: open sky with light pencil clouds and atmospheric "
    "perspective filling most of the top area, gentle distant landscape "
    "(faint hills, atmospheric haze, soft horizon line) on the left side, "
    "and ground/terrain extending leftward from under the vehicle into the "
    "foreground. Keep the LEFT and TOP regions COMPOSITIONALLY OPEN — no "
    "secondary subjects, no busy elements there — just atmosphere. "
    "Style: realistic graphite pencil on white paper, light gray shading "
    "(10-30% gray), visible pencil strokes, hand-drawn texture. Match the "
    "exact line weight and shading density of the original drawing. "
    "No text, no borders, no frame, no watermark."
)


def autocrop(im: Image.Image, threshold: int = 240, pad: int = 4) -> Image.Image:
    """Corta as bordas brancas do desenho (área onde o lápis não atingiu).
    Mantém uma margem pequena pra não cortar linhas finas."""
    import numpy as np
    gray = np.array(im.convert("L"))
    mask = gray < threshold
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    if not rows.any():
        return im
    y0, y1 = np.where(rows)[0][[0, -1]]
    x0, x1 = np.where(cols)[0][[0, -1]]
    w, h = im.size
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(w, x1 + pad + 1)
    y1 = min(h, y1 + pad + 1)
    return im.crop((x0, y0, x1, y1))


def composite(input_path: Path) -> tuple[Path, Path]:
    src = Image.open(input_path).convert("RGB")
    # Auto-crop: tira margens brancas antes do outpaint pra veículo dominar
    src = autocrop(src)
    sw, sh = src.size

    # Espaço disponível pro source (após reservar safe zone TL + margem right/bottom)
    max_w = int(CANVAS_W * (1 - SAFE_W_PCT - MARGIN_PCT))
    max_h = int(CANVAS_H * (1 - SAFE_H_PCT - MARGIN_PCT))

    # Escalar mantendo aspect ratio do source
    scale_w = max_w / sw
    scale_h = max_h / sh
    scale = min(scale_w, scale_h)
    new_w = int(sw * scale)
    new_h = int(sh * scale)
    src = src.resize((new_w, new_h), Image.LANCZOS)

    # Posicionar no canto inferior-direito com margem
    margin_x = int(CANVAS_W * MARGIN_PCT)
    margin_y = int(CANVAS_H * MARGIN_PCT)
    off_x = CANVAS_W - new_w - margin_x
    off_y = CANVAS_H - new_h - margin_y

    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (255, 255, 255))
    canvas.paste(src, (off_x, off_y))
    mask = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    keep = Image.new("RGBA", (new_w, new_h), (255, 255, 255, 255))
    mask.paste(keep, (off_x, off_y))

    tmp = ROOT / ".tmp_outpaint"
    tmp.mkdir(exist_ok=True)
    canvas_path = tmp / f"{input_path.stem}_b_canvas.png"
    mask_path = tmp / f"{input_path.stem}_b_mask.png"
    canvas.save(canvas_path)
    mask.save(mask_path)
    return canvas_path, mask_path


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Uso: gerar_outpaint_breathe.py <input.jpg>")
    input_path = Path(sys.argv[1])
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    out_dir = ROOT / "imagens" / "outpainted-breathe"
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
