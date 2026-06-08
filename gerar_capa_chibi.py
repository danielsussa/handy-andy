#!/usr/bin/env python3
"""Capa do livro com o Andy CHIBI (variante b). Landscape 1.5:1."""
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
    "Children's picture book cover illustration. Style: GRAPHITE PENCIL on "
    "warm cream paper, visible pencil strokes, soft tonal shading. "
    "\n\n"
    "PRESERVE THE BOY EXACTLY as he appears in the reference image — same "
    "CHIBI/CUTE proportions (big head, big round eyes, soft rounded features, "
    "child-friendly cartoon body), same newsboy cap, same denim overalls, "
    "same shirt, same wrench, same freckles, same grease smudge. He must "
    "stay in his STYLIZED CHIBI form — NOT redrawn as realistic. "
    "Ignore any 'ANDY' text on the reference. "
    "\n\n"
    "Position: Andy stands in the LOWER-RIGHT area of the composition, "
    "facing the viewer, holding his wrench. He occupies roughly the right "
    "1/3 of the page. "
    "\n\n"
    "Build a hero scene AROUND and BEHIND him, drawn in the same pencil "
    "hand but in slightly more REALISTIC pencil style (matches the book's "
    "vehicle illustrations): a tank in the lower left, a vintage cargo truck "
    "behind, a tall construction crane rising in mid-right behind Andy, a "
    "vintage propeller airplane flying in the upper-right sky, an excavator "
    "in the lower mid-ground. Vehicles are smaller in scale than Andy "
    "(foreshortened), supporting him as the focal point. "
    "\n\n"
    "Composition rules: "
    "- LEFT HALF of the image must be visually LIGHT and uncluttered — soft "
    "cream sky and faint ground, only minor vehicle silhouettes far in the "
    "distance. This space is reserved for the title text (added later). "
    "- Andy on the RIGHT is the focal point, vehicles support him. "
    "\n\n"
    "Landscape orientation, 1.5:1 (1536x1024). No text, no title, no border, "
    "no frame, no signature, no watermark, no logo. One cohesive piece by "
    "one pencil artist on one sheet of paper."
)


def main() -> None:
    ref = ROOT / "imagens" / "andy" / "andy-cartoon-b.png"
    if not ref.exists():
        sys.exit(f"Andy chibi ref não existe: {ref}")
    out_dir = ROOT / "imagens" / "capa"
    out_dir.mkdir(parents=True, exist_ok=True)
    variant = sys.argv[1] if len(sys.argv) >= 2 else "chibi-v1"
    output_path = out_dir / f"capa-{variant}.png"

    print(f"→ generating capa ({variant}) from {ref.name}")
    with ref.open("rb") as f:
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
        sys.exit("Sem b64_json")
    output_path.write_bytes(base64.b64decode(b64))
    print(f"✓ {output_path} ({output_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
