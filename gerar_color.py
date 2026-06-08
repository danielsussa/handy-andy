#!/usr/bin/env python3
"""Versão colorida — pega a imagem já gerada (com fundo) e adiciona cor,
mantendo o traço de lápis. Compara estilos pra decidir colorir vs ler."""
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
    "Take this pencil drawing and re-render it as a fully colored illustration "
    "while keeping the EXACT same composition, same subject, same scene, same "
    "pose and angle. "
    "Style: colored pencil illustration in the style of a high-quality "
    "children's picture book — visible pencil strokes and hand-drawn texture "
    "preserved, but now with rich natural colors on the vehicle (realistic "
    "paint, metals) and the surroundings (sky, ground, vegetation, distant "
    "background). Soft shading, warm tones, slightly textured paper feel. "
    "Keep it suitable for a children's reading book — vivid but not "
    "oversaturated, no cartoon flatness. "
    "Portrait orientation, A4 aspect ratio. No text, no borders, no frame, "
    "no watermark. Vehicle remains the focal point."
)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Uso: python gerar_color.py <input.png>")
    input_path = Path(sys.argv[1])
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    output_path = ROOT / "imagens" / "geradas-color" / f"{input_path.stem}.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"→ {input_path.name}")
    with input_path.open("rb") as f:
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
        sys.exit("Sem b64_json na resposta")
    output_path.write_bytes(base64.b64decode(b64))
    print(f"✓ {output_path} ({output_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
