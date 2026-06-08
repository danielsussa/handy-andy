#!/usr/bin/env python3
"""Gera o Andy — personagem do livro — em estilo lápis realista (do zero,
sem imagem-base). Usa images.generate (não edit) porque é from-scratch."""
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
    sys.exit("Falta OPENAPI_KEY no .env")

client = OpenAI(api_key=API_KEY)

PROMPT = (
    "A full-body realistic graphite pencil drawing of a 5-6 year old boy "
    "named Andy, the young mechanic mascot of a children's book about "
    "vehicles. Drawn in the EXACT same style as classic Pinterest pencil "
    "art of vintage tanks and machines: hand-drawn with real graphite, "
    "visible pencil strokes, soft tonal shading, fine hatching for shadow, "
    "realistic proportions and anatomy, NOT cartoon, NOT line art, NOT "
    "coloring page. Like a master illustrator's pencil portrait. "
    "\n\n"
    "Andy's look: tousled short brown hair peeking out from under a soft "
    "newsboy cap (denim or wool), a few light freckles across the nose, "
    "big curious eyes, a small smudge of grease on one cheek, a hint of "
    "a smile. Wearing classic vintage 1940s-50s mechanic overalls (denim "
    "bib overalls over a simple buttoned shirt with sleeves rolled up to "
    "the elbows). Holding a big chunky wrench in one hand, almost too big "
    "for him — adds charm. Sturdy little work boots. "
    "\n\n"
    "Pose: standing, full body visible head to toe, slight three-quarter "
    "angle, weight on one leg, wrench resting on his shoulder or held "
    "casually at his side, looking directly at the viewer with a confident "
    "but warm expression. Hero-shot reference pose. "
    "\n\n"
    "Background: completely plain warm cream/off-white paper with subtle "
    "pencil texture, no scene, no scenery, no objects — Andy is the only "
    "subject so this can be used as a character reference sheet. Soft "
    "ground shadow under his feet drawn in light pencil. "
    "\n\n"
    "Portrait orientation, A4 aspect ratio. No text, no border, no frame, "
    "no signature, no watermark. Centered composition with generous "
    "headroom and footroom. The drawing must look like one cohesive piece "
    "by a single skilled pencil artist."
)


def main() -> None:
    out_dir = ROOT / "imagens" / "andy"
    out_dir.mkdir(parents=True, exist_ok=True)
    variant = sys.argv[1] if len(sys.argv) >= 2 else "v1"
    output_path = out_dir / f"andy-{variant}.png"

    print(f"→ generating Andy ({variant})")
    resp = client.images.generate(
        model="gpt-image-1",
        prompt=PROMPT,
        size="1024x1536",
        quality="high",
        n=1,
    )
    b64 = resp.data[0].b64_json
    if not b64:
        sys.exit("Sem b64_json")
    output_path.write_bytes(base64.b64decode(b64))
    kb = output_path.stat().st_size // 1024
    print(f"✓ {output_path} ({kb} KB)")


if __name__ == "__main__":
    main()
