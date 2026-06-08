#!/usr/bin/env python3
"""Merge trator-cut (vista explodida) + Oliver cutaway numerado (Pinterest)
numa única ilustração técnica."""
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
    "a vintage encyclopedia spread showing two ways to understand a tractor "
    "from the inside. ONE unified illustration, NOT split panels. "
    "\n\n"
    "Composition: "
    "- LEFT THIRD (about 35% of canvas width), positioned in the LOWER-LEFT "
    "area: the OLIVER TRACTOR CUTAWAY exactly as in the SECOND reference "
    "image — intact tractor body with internal mechanisms visible through "
    "cutaway sections, gears, shaft, plow, spoked rear wheel. RE-RENDER in "
    "soft graphite pencil shading (the source is hard line-art — soften "
    "into tonal pencil with hatching, matching the first reference's "
    "style). Remove any number labels. The cutaway floats as a diagrammatic "
    "element. CRITICAL: the TOP of the Oliver tractor must be roughly 35-40% "
    "from the top edge of the canvas (NOT touching the upper portion) — the "
    "TOP-LEFT 30% of the canvas must remain EMPTY cream paper (reserved for "
    "title text). Push the Oliver down so its top doesn't reach the upper "
    "third. "
    "- RIGHT THIRD (about 35% of canvas width): the EXPLODED VIEW exactly "
    "as in the FIRST reference image — parts of the tractor floating apart "
    "as if disassembled in the air. Same pencil style. "
    "- CRITICAL: empty space (~30% width) BETWEEN the two illustrations. "
    "They must NOT touch. Connect them with a thin dashed pencil line "
    "labeled by an arrow gesture (no actual text), suggesting 'these are "
    "two views of the same machine'. "
    "\n\n"
    "Background: unified soft cream paper, no ground line, no horizon. Both "
    "drawings float as diagrammatic elements. "
    "\n\n"
    "Style: graphite pencil on warm cream paper, visible pencil strokes, "
    "soft tonal shading. ONE artist, ONE sheet of paper. "
    "\n\n"
    "Landscape 1.5:1 (1536x1024). Top-right area open for title. No text, "
    "no number labels, no border, no frame, no watermark."
)


def main() -> None:
    exploded = ROOT / "imagens" / "outpainted-breathe" / "trator-cut.png"
    oliver = ROOT / "imagens" / "cutaway" / "trator-cut-pinterest2.jpg"
    if not exploded.exists() or not oliver.exists():
        raise SystemExit("Refs não encontradas")
    out_dir = ROOT / "imagens" / "duo"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "trator-cuts.png"

    print(f"→ merging trator-cut (exploded) + oliver-cutaway (Pinterest)")
    with exploded.open("rb") as e, oliver.open("rb") as o:
        resp = client.images.edit(
            model="gpt-image-1",
            image=[e, o],
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
