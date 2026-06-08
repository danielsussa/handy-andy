#!/usr/bin/env python3
"""Gera Mercedes-Benz LO 1113 'cara-de-cavalo' (Brasil, 1968) do zero.
Ônibus rodoviário/urbano icônico brasileiro."""
from __future__ import annotations

import base64
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
ENV = dotenv_values(ROOT / ".env")
API_KEY = ENV.get("OPENAPI_KEY") or ENV.get("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("Falta OPENAPI_KEY no .env")

client = OpenAI(api_key=API_KEY)

PROMPT = (
    "A detailed graphite pencil illustration on warm cream paper of a "
    "MERCEDES-BENZ LO 1113 BRAZILIAN BUS (1968) — the iconic "
    "'cara-de-cavalo' (horse-face) that carried generations across "
    "Brazilian roads. "
    "\n\n"
    "Bus characteristics: medium-sized intercity/rural bus with a "
    "DISTINCTIVE ROUNDED LONG NOSE (the 'horse face') protruding forward "
    "of the passenger compartment, twin round HIGH-MOUNTED HEADLIGHTS, "
    "a small chrome Mercedes-Benz star/badge on the front grille, "
    "single horizontal chrome strip above grille, large rectangular "
    "windshield split in two by a center pillar, side passenger windows "
    "in a horizontal strip along the body, opening side door behind "
    "the front wheel, simple painted destination roller-blind above "
    "the windshield (no readable text — just abstract shape), classic "
    "Brazilian bus body by Carbrasa or Caio (period-correct boxy "
    "body with rounded corners), big rear engine compartment behind, "
    "exposed exhaust pipe on top corner. Shown in 3/4 FRONT-LEFT VIEW. "
    "\n\n"
    "Setting: a Brazilian interior road scene from the late 1960s. "
    "Background: a dirt or partially paved road winding into rolling "
    "hills, a wooden roadside cross or shrine off to the side, a few "
    "leafy mango or coconut trees, an old farm fence, hills with "
    "scattered low scrub in the distance, a wooden 'BR' road-mile post "
    "(no readable text). Dust kicked up around the rear wheels. Soft "
    "Brazilian countryside sky with cumulus clouds. "
    "\n\n"
    "CRITICAL composition: the bus occupies the LOWER-RIGHT 60% of the "
    "canvas. The TOP-LEFT 22% width × 18% height MUST stay MOSTLY EMPTY "
    "cream paper / soft sky (reserved for title text). No dense scenery "
    "in the upper-left corner. "
    "\n\n"
    "Style: graphite pencil on warm cream paper, visible pencil strokes, "
    "soft tonal shading. NO color, NO painterly textures, NO photographic "
    "elements. Match a vintage encyclopedia pencil-drawing aesthetic. "
    "\n\n"
    "Landscape 1.5:1 (1536x1024). No text, no border, no frame, no "
    "watermark, no labels."
)


def main() -> None:
    out_dir = ROOT / "imagens" / "outpainted-breathe"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "onibus-01.png"

    print(f"→ generate Mercedes LO 1113 → {out_path.name}")
    resp = client.images.generate(
        model="gpt-image-1",
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
