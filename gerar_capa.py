#!/usr/bin/env python3
"""Gera a capa do 'Handy Andy and the Big Machines'.

Usa images.edit com andy.png como referência pra preservar identidade do
personagem, e estende a cena com veículos do livro em estilo pôster de filme
infantil. Deixa headroom no topo pro título e bottom pra subtítulo — texto é
sobreposto depois via HTML template, não fica embedded no PNG."""
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
    "Children's book cover illustration in realistic graphite pencil drawing "
    "style — exactly like the source image's pencil technique (soft tonal "
    "shading, fine hatching, visible pencil strokes, warm cream paper "
    "background). NOT cartoon, NOT line art, NOT coloring page. "
    "\n\n"
    "PRESERVE THE BOY EXACTLY as he appears in the source image — same face, "
    "same expression, same hairstyle, same newsboy cap, same freckles, same "
    "grease smudge on the cheek, same denim overalls, same wrench, same "
    "proportions, same pose, same age (~5-6 years old). He must remain "
    "instantly recognizable as the same character. Keep him roughly the same "
    "size as in the source, positioned in the lower-center foreground. "
    "\n\n"
    "Build a hero movie-poster scene AROUND him, drawn in the same pencil "
    "hand: behind and slightly smaller in scale (foreshortened), arrange a "
    "fan/wedge of iconic vintage vehicles — a tank on his lower left, a "
    "classic fire truck behind him, a heavy cargo truck slightly behind that, "
    "a tall construction crane rising on the right side, a vintage propeller "
    "airplane flying in the upper-right sky, a bulldozer or excavator on the "
    "lower right. The vehicles surround him like a supporting cast, all "
    "looking toward the viewer or angled inward toward Andy. "
    "\n\n"
    "Composition rules: "
    "- TOP THIRD of the image must be visually LIGHT and uncluttered — only "
    "soft cream sky with very faint pencil clouds, the airplane small in the "
    "corner. This space is reserved for a title that will be added later. "
    "- Bottom ~10% should also be calmer (light ground shading, no busy "
    "detail) to leave room for a subtitle. "
    "- Andy must remain the clear focal point — vehicles support him, do not "
    "compete with him. "
    "\n\n"
    "Ground: soft graphite-shaded dirt/road. Sky: warm cream paper tone with "
    "delicate pencil cloud suggestions. One cohesive piece by one pencil "
    "artist on one sheet of paper. "
    "\n\n"
    "Portrait orientation, A4 aspect. No text, no title, no border, no frame, "
    "no signature, no watermark, no logo."
)


def main() -> None:
    ref = ROOT / "imagens" / "andy" / "andy.png"
    if not ref.exists():
        sys.exit(f"Referência não existe: {ref}")
    out_dir = ROOT / "imagens" / "capa"
    out_dir.mkdir(parents=True, exist_ok=True)
    variant = sys.argv[1] if len(sys.argv) >= 2 else "v1"
    output_path = out_dir / f"capa-{variant}.png"

    print(f"→ generating capa ({variant}) from {ref.name}")
    with ref.open("rb") as f:
        resp = client.images.edit(
            model="gpt-image-1",
            image=f,
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
