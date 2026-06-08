#!/usr/bin/env python3
"""Compõe trator + engine cutaway numa única ilustração técnica integrada,
estilo enciclopédia infantil. Engine cutaway flutuando como diagrama à
esquerda + trator à direita."""
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
    "like a vintage children's encyclopedia spread that shows how a tractor "
    "works. ONE unified illustration, NOT two separate images, NOT a split "
    "panel. "
    "\n\n"
    "Composition: "
    "- LEFT SIDE (about 45% of the canvas width): a LARGE EXPLODED CUTAWAY "
    "DIAGRAM of a vintage internal combustion engine, exactly like the one "
    "shown in the SECOND reference image — multiple layers visible, "
    "cylinders, pistons, gears, valve cover lifted off to show the inside. "
    "It FLOATS in the scene as a technical cutaway diagram — NO ground "
    "under it, NO mounting, NO base. Just the engine itself, suspended in "
    "the cream-paper sky as a diagrammatic element. Impressive in size — "
    "the focal point on the left. Re-render in soft pencil shading "
    "matching the rest of the book (the second reference is a hard line-art "
    "diagram — soften it into graphite pencil with tonal shading to match "
    "the first reference's pencil style). "
    "- RIGHT SIDE (about 45% of the canvas width): the TRACTOR exactly as "
    "shown in the FIRST reference image — same model, same pose, same "
    "proportions. Keep its existing ground/setting. "
    "- A subtle dashed PENCIL LINE connects the tractor's engine area to "
    "the large exploded engine on the left, indicating 'this is the engine "
    "of that tractor, opened up'. Hand-drawn pencil dashed line. "
    "\n\n"
    "Background: unified soft cream paper. Faint pencil ground/sky. "
    "\n\n"
    "Style: graphite pencil on warm cream paper, visible pencil strokes, "
    "soft tonal shading. ONE drawing by ONE artist on ONE sheet of paper. "
    "\n\n"
    "Landscape orientation 1.5:1 (1536x1024). Top-RIGHT area should be open "
    "(just sky) for a title to be added later (ficha goes top-right on this "
    "page because the engine cutaway occupies the left). No text, no "
    "labels, no border, no frame, no watermark."
)


def main() -> None:
    trator = ROOT / "imagens" / "outpainted-breathe" / "trator-19.png"
    engine = ROOT / "imagens" / "cutaway" / "trator-cut-pinterest.jpg"
    if not trator.exists() or not engine.exists():
        raise SystemExit("Refs não encontradas")
    out_dir = ROOT / "imagens" / "duo"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "trator-engine.png"

    print(f"→ merging trator-19 + engine-cutaway")
    with trator.open("rb") as t, engine.open("rb") as e:
        resp = client.images.edit(
            model="gpt-image-1",
            image=[t, e],
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
