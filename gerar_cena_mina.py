#!/usr/bin/env python3
"""Re-renderiza guindaste-01 com cenário de mineração/pedreira rochosa.
Veículo intacto, só troca o background.
"""
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
    "Re-render the CRAWLER CRANE / EXCAVATOR shown in the reference image "
    "in a NEW SETTING: a rocky open-pit MINING QUARRY. "
    "\n\n"
    "Keep the machine EXACTLY as it is — same model, same pose, same "
    "proportions, same shading. Do NOT redraw or modify the machine itself. "
    "ONLY replace the surrounding environment. "
    "\n\n"
    "New environment: jagged rocky terrain underfoot, broken stone, gravel, "
    "boulders scattered in the mid-ground. Tall ROCK FACES / quarry walls "
    "rising in the background — layered stone strata, like an open-pit mine. "
    "A subtle haze of dust drifts in the air. The machine sits on a "
    "rocky shelf or quarry floor, with crushed rock around its tracks. "
    "\n\n"
    "CRITICAL: keep the TOP-LEFT 18% of the canvas (and top 15%) MOSTLY "
    "OPEN — only soft sky / distant haze there — for a title to be placed "
    "later. Don't put rock walls in the upper-left corner. "
    "\n\n"
    "Style: graphite pencil on warm cream paper, visible pencil strokes, "
    "soft tonal shading. Match the existing pencil illustration style "
    "exactly. The new rocks and quarry walls should be drawn in the SAME "
    "pencil style as the machine — no painterly textures, no color. "
    "\n\n"
    "Landscape 1.5:1 (1536x1024). No text, no border, no frame, no watermark."
)


def main() -> None:
    src = ROOT / "imagens" / "outpainted-breathe" / "guindaste-01.png"
    if not src.exists():
        raise SystemExit(f"Source não encontrada: {src}")
    out_dir = ROOT / "imagens" / "outpainted-breathe-mina"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "guindaste-01.png"

    print(f"→ re-cena (mineradora) {src.name}")
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
