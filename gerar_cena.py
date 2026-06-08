#!/usr/bin/env python3
"""Re-renderiza um veículo já outpainted em um novo cenário.
Veículo intacto, só troca o background.

Uso:
    SCENE_NAME=<id-curto> SCENE_DESC="..." python gerar_cena.py <input.png>

Output: imagens/outpainted-breathe-<SCENE_NAME>/<input-name>.png
"""
from __future__ import annotations

import base64
import os
import sys
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
ENV = dotenv_values(ROOT / ".env")
API_KEY = ENV.get("OPENAPI_KEY") or ENV.get("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("Falta OPENAPI_KEY no .env")

client = OpenAI(api_key=API_KEY)

SCENE_NAME = os.environ.get("SCENE_NAME", "")
SCENE_DESC = os.environ.get("SCENE_DESC", "")
if not SCENE_NAME or not SCENE_DESC:
    raise SystemExit("Defina SCENE_NAME e SCENE_DESC nas env vars")

PROMPT = (
    "Re-render the MAIN VEHICLE/MACHINE shown in the reference image in a "
    "NEW SETTING described below. "
    "\n\n"
    "Keep the machine EXACTLY as it is — same model, same pose, same "
    "proportions, same shading. Do NOT redraw or modify the machine itself. "
    "ONLY replace the surrounding environment. "
    "\n\n"
    f"New environment: {SCENE_DESC} "
    "\n\n"
    "CRITICAL: keep the TOP-LEFT 18% of the canvas (and top 15%) MOSTLY "
    "OPEN — only soft sky / distant haze there — for a title to be placed "
    "later. Don't put dense scenery in the upper-left corner. "
    "\n\n"
    "Style: graphite pencil on warm cream paper, visible pencil strokes, "
    "soft tonal shading. Match the existing pencil illustration style "
    "exactly. The new environment must be drawn in the SAME pencil style "
    "as the machine — no painterly textures, no color, no photographic "
    "elements. "
    "\n\n"
    "Landscape 1.5:1 (1536x1024). No text, no border, no frame, no watermark."
)


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Uso: gerar_cena.py <input.png>")
    src = Path(sys.argv[1])
    if not src.is_absolute():
        src = ROOT / src
    if not src.exists():
        raise SystemExit(f"Source não encontrada: {src}")

    out_dir = ROOT / "imagens" / f"outpainted-breathe-{SCENE_NAME}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / src.name

    print(f"→ re-cena ({SCENE_NAME}) {src.name}")
    with src.open("rb") as f:
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
        raise SystemExit("Sem b64_json")
    out_path.write_bytes(base64.b64decode(b64))
    print(f"✓ {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
