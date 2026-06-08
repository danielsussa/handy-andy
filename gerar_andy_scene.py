#!/usr/bin/env python3
"""Compõe Andy (mascote) com um veículo já outpainted, mantendo o estilo
de lápis vintage. Passa as duas imagens como referência pro gpt-image-1
e pede pra ele colocar Andy interagindo com o veículo.

Uso:
    python gerar_andy_scene.py <veiculo.png>

O veículo deve ser um PNG do imagens/outpainted-breathe/ (já com cenário).
"""
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

ANDY_REF = ROOT / "imagens" / "andy" / "andy-cartoon-b.png"

import os as _os
ANDY_SIZE = _os.environ.get("ANDY_SIZE", "normal")  # normal | small | tiny

SIZE_NOTES = {
    "normal": "Andy is at child scale next to the vehicle (a tank towers over him).",
    "small":  "Andy is VERY SMALL in the scene — his total height should be only about 25-30% of the vehicle's height. He is a small child dwarfed by a much bigger machine. Take up minimal space in the foreground.",
    "tiny":   "Andy is TINY — his total height should be only about 15-20% of the vehicle's height. Almost a small detail in the scene, like a child looking up at a giant machine.",
}

# Cena/pose custom por env var (override forte)
ANDY_SCENE = _os.environ.get("ANDY_SCENE", "")

PROMPT = (
    "Add the CHIBI-STYLE BOY CHARACTER from the first reference image (Andy "
    "— stylized cute boy with big head, big eyes, newsboy cap, denim "
    "overalls, freckles) into the scene shown in the second reference image. "
    "IMPORTANT: keep Andy in his CHIBI/CUTE STYLE from the first reference "
    "— big head, big eyes, soft rounded features, child-friendly cartoon "
    "proportions. Do NOT redraw him as realistic. Same face and outfit as "
    "the reference. Ignore any 'ANDY' text in the reference image. "
    "Keep the vehicle EXACTLY as it is in the second reference — same model, "
    "same pose, same proportions, same composition, same shading. Do not "
    "redraw or modify the vehicle. "
    f"SIZE: {SIZE_NOTES[ANDY_SIZE]} "
    f"{ANDY_SCENE or 'Andy stands in front of, leans on, or stands next to the vehicle interacting with it.'} "
    "Keep the top-left area open (sky/light background) for text. "
    "Style: graphite pencil on warm white paper, visible pencil strokes, "
    "soft shading. The vehicle stays in its realistic pencil style. Andy "
    "stays in his chibi/illustrative pencil style. "
    "No text labels in the output. No borders, no frame, no watermark."
)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Uso: gerar_andy_scene.py <veiculo.png>")
    veh_path = Path(sys.argv[1])
    if not veh_path.is_absolute():
        veh_path = ROOT / veh_path
    if not veh_path.exists():
        sys.exit(f"Veículo não encontrado: {veh_path}")
    if not ANDY_REF.exists():
        sys.exit(f"Andy ref não encontrado: {ANDY_REF}")

    out_dir = ROOT / "imagens" / "andy-scene"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / veh_path.name

    print(f"→ andy + {veh_path.name}")
    with ANDY_REF.open("rb") as andy, veh_path.open("rb") as veh:
        resp = client.images.edit(
            model="gpt-image-1",
            image=[andy, veh],
            prompt=PROMPT,
            size="1536x1024",
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
