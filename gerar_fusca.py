#!/usr/bin/env python3
"""Gera um Fusca (VW Beetle) brasileiro 1959 — substitui o moto-04 (page 12).
Estilo lápis grafite, paisagem 1.5:1, safe zone no topo-esquerdo pro título.
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
    "A detailed graphite pencil illustration on warm cream paper of a "
    "1959 BRAZILIAN VOLKSWAGEN BEETLE (Fusca) — the iconic German-Brazilian "
    "people's car that VW started building in São Bernardo do Campo "
    "(São Paulo) in January 1959. "
    "\n\n"
    "Car characteristics: classic round curved body, split or oval rear "
    "window (early '59 style), round headlights set into the front "
    "fenders, single-bar chrome bumper, slightly puffy fenders with "
    "running boards, small turn signal 'horns' on the front, rear-mounted "
    "air-cooled flat-four engine (hidden inside the rear deck). Shown in "
    "3/4 FRONT-LEFT VIEW (so the curve of the body, headlights, and "
    "windshield are all visible), parked or about to drive off. "
    "\n\n"
    "Setting: a quiet Brazilian street scene from the late 1950s. Behind: "
    "a row of low colonial-style buildings with tiled roofs and arched "
    "windows, a small leafy mango or fig tree, a kid on a wooden chair "
    "in the distance, a hand-painted shop sign (no readable text — just "
    "swooping cursive shapes), telegraph poles and wires receding into "
    "the distance. The cobblestone street under the car. Soft Brazilian "
    "sky with a few wispy cumulus clouds. "
    "\n\n"
    "CRITICAL composition: the Fusca occupies the LOWER-RIGHT 60% of the "
    "canvas. The TOP-LEFT 22% width × 18% height MUST stay MOSTLY EMPTY "
    "cream paper / soft sky (reserved for title text). No dense scenery "
    "in the upper-left corner. "
    "\n\n"
    "Style: graphite pencil on warm cream paper, visible pencil strokes, "
    "soft tonal shading. NO color, NO painterly textures, NO photographic "
    "elements. Match a vintage encyclopedia pencil-drawing aesthetic. "
    "\n\n"
    "Landscape 1.5:1 (1536x1024). No text, no border, no frame, no "
    "watermark, no labels."
)


def main() -> None:
    out_dir = ROOT / "imagens" / "outpainted-breathe"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "fusca-01.png"

    print(f"→ generate Fusca 1959 → {out_path.name}")
    resp = client.images.generate(
        model="gpt-image-1",
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
