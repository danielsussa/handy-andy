#!/usr/bin/env python3
"""Andy de despedida — última página do livro. Andy chibi acenando, com
silhuetas dos veículos do livro atrás dele em distância atmosférica."""
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
    "A farewell illustration for the LAST PAGE of a children's book about "
    "vehicles. Same chibi-style mascot from the reference image (Andy — "
    "young boy with newsboy cap, denim overalls, big head, big eyes, "
    "freckles, holding a wrench). "
    "\n\n"
    "Scene: Andy stands CENTERED in the foreground, FACING THE VIEWER, "
    "WAVING goodbye with his free hand (the other still holds his wrench), "
    "with a warm smile. Behind him, FAINT and SMALLER in the distance (low "
    "contrast, atmospheric perspective), are SILHOUETTES of the vehicles "
    "from the book scattered in the cream sky: a small steam train, a "
    "tank, an airplane in flight, a tractor, an excavator, a fire truck, "
    "and a motorcycle. They are LIGHTLY drawn — barely there, like memories. "
    "Andy is the only crisp foreground figure. "
    "\n\n"
    "Composition: Andy occupies the center of the canvas. Below him there "
    "could be faint ground shading. The TOP CENTER area is mostly open "
    "cream sky for a 'THE END' / 'FIM' style title to be added later. "
    "\n\n"
    "Style: graphite pencil on warm cream paper, visible pencil strokes, "
    "soft shading. Andy in his chibi/cute pencil style EXACTLY as in the "
    "reference. The background vehicles in lighter, softer pencil. "
    "Landscape 1.5:1 (1536x1024). No text, no border, no frame."
)


def main() -> None:
    ref = ROOT / "imagens" / "andy" / "andy-cartoon-b.png"
    if not ref.exists():
        raise SystemExit(f"Ref não existe: {ref}")
    out_dir = ROOT / "imagens" / "andy"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "andy-fim.png"

    print(f"→ andy-fim from {ref.name}")
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
        raise SystemExit("Sem b64_json")
    out_path.write_bytes(base64.b64decode(b64))
    print(f"✓ {out_path.name} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
