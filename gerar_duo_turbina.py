#!/usr/bin/env python3
"""Compõe Airbus + turbina cutaway numa única ilustração técnica integrada,
estilo enciclopédia infantil. AI faz o merge real (não CSS split)."""
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
    "A single COHESIVE engineering illustration in pencil drawing style — "
    "like a vintage children's encyclopedia spread that shows how a jet "
    "plane works. ONE unified illustration, NOT two separate images, NOT a "
    "split panel. "
    "\n\n"
    "Composition: "
    "- LEFT THIRD of the canvas (occupying roughly the LEFT 35% of width): "
    "a JET TURBINE CUTAWAY, exactly like the one shown in the SECOND "
    "reference image — fan blades visible, internal mechanism exposed. It "
    "FLOATS in the scene as a technical cutaway diagram — NO ground under "
    "it, NO landing gear, NO mounting. Just the turbine itself, suspended "
    "in the cream-paper sky. "
    "- RIGHT THIRD of the canvas (occupying roughly the RIGHT 35% of "
    "width): the COMMERCIAL JET AIRPLANE exactly like the one shown in "
    "the FIRST reference image, shown smaller and in flight against the "
    "same cream-paper sky. The plane is angled so the viewer can see one "
    "of its wing-mounted engines clearly. "
    "- CRITICAL: leave a CLEAR EMPTY MIDDLE SECTION (about 30% of the "
    "canvas width) between the turbine and the airplane. The two subjects "
    "must NOT touch or overlap. The empty middle is filled with soft "
    "cream-paper sky and a thin dashed pencil line connecting them. "
    "- A long dashed PENCIL LINE crosses the empty middle space from the "
    "airplane's wing engine to the cutaway turbine on the left, "
    "indicating 'this is the engine of that plane, opened up'. Hand-drawn "
    "pencil dashed line spanning the gap. "
    "\n\n"
    "Background: unified soft cream paper with faint pencil sky clouds. "
    "NO ground line. Just continuous sky unifying both subjects with "
    "breathing room between them. "
    "\n\n"
    "Style: graphite pencil on warm cream paper, visible pencil strokes, "
    "soft tonal shading. ONE drawing by ONE artist on ONE sheet of paper. "
    "\n\n"
    "Landscape 1.5:1 (1536x1024). Top-right area open for title. No text, "
    "no labels, no border, no frame, no watermark."
)


def main() -> None:
    aviao = ROOT / "imagens" / "outpainted-breathe" / "aviao-01.png"
    turbina = ROOT / "imagens" / "outpainted-breathe" / "aviao-cut-turbina.png"
    if not aviao.exists() or not turbina.exists():
        raise SystemExit("Refs não encontradas")
    out_dir = ROOT / "imagens" / "duo"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "aviao-turbina.png"

    print(f"→ merging aviao-01 + aviao-cut-turbina")
    with aviao.open("rb") as a, turbina.open("rb") as t:
        resp = client.images.edit(
            model="gpt-image-1",
            image=[a, t],
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
