#!/usr/bin/env python3
"""Gera 3 imagens de trem em estilo lápis pra fechar o livro."""
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
    raise SystemExit("Falta OPENAPI_KEY no .env")

client = OpenAI(api_key=API_KEY)

BASE = (
    "Realistic graphite pencil drawing on warm cream paper — same style as "
    "vintage Pinterest pencil illustrations of trains, tanks, and machines. "
    "Soft tonal shading, visible pencil strokes, fine hatching. NOT cartoon, "
    "NOT line art, NOT coloring page. Hand-drawn artistic quality. "
)

POSITION = (
    "COMPOSITION: the train fills the LOWER-RIGHT 70% of the canvas. The "
    "UPPER-LEFT 30% area is mostly empty cream sky (only faint pencil clouds "
    "or atmospheric perspective) — RESERVED for a title text that will be "
    "added later. The train is the focal point. Faint ground/track shading "
    "below the train. Landscape 1.5:1 (1536x1024). "
)

NO_TEXT = "No text, no labels, no border, no frame, no watermark, no signature."

VARIANTS = {
    "vapor": (
        BASE + POSITION +
        "Subject: a CLASSIC VINTAGE STEAM LOCOMOTIVE — black boiler, "
        "smokestack with smoke trailing into the sky, big driving wheels "
        "connected by side rods, brass fittings, headlight, cowcatcher on "
        "the front. Shown from a 3/4 angle from the front-side, slightly "
        "low viewpoint so the train looks powerful. The engine alone, no "
        "passenger cars. " + NO_TEXT
    ),
    "moderno": (
        BASE + POSITION +
        "Subject: a MODERN HIGH-SPEED ELECTRIC TRAIN — sleek aerodynamic "
        "nose, smooth body lines, large windshield, pantograph on top, "
        "metal/silver finish, no smoke. Shown from a 3/4 angle from the "
        "front-side, slightly low viewpoint. Just the front locomotive "
        "unit. " + NO_TEXT
    ),
    "corte": (
        BASE +
        "Subject: a STEAM LOCOMOTIVE CUTAWAY/CROSS-SECTION — the side of "
        "the boiler is cut open to reveal the firebox, water tubes, "
        "pistons, cylinders, and the cab interior with the engineer's "
        "controls. Stephen Biesty style of illustrative cross-section. "
        "All internals labeled visually but with NO TEXT labels. "
        "COMPOSITION: cutaway floats centered in the canvas (like a "
        "diagrammatic illustration), with small amounts of cream paper "
        "around. UPPER-LEFT 30% remains open for title text. Landscape "
        "1.5:1 (1536x1024). " + NO_TEXT
    ),
}


def generate(variant: str) -> Path:
    prompt = VARIANTS[variant]
    print(f"→ trem-{variant}")
    resp = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1536x1024",
        quality="high",
        n=1,
    )
    b64 = resp.data[0].b64_json
    if not b64:
        raise SystemExit("Sem b64_json")
    out_dir = ROOT / "imagens" / "trem"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"trem-{variant}.png"
    out_path.write_bytes(base64.b64decode(b64))
    print(f"✓ {out_path.name} ({out_path.stat().st_size // 1024} KB)")
    return out_path


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg == "all":
        for k in VARIANTS:
            generate(k)
    elif arg in VARIANTS:
        generate(arg)
    else:
        raise SystemExit(f"Use: {' | '.join(VARIANTS)} ou all")


if __name__ == "__main__":
    main()
